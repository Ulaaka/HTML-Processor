
from nltk.corpus import stopwords
import re, time
from datetime import datetime
import pandas as pd
import numpy as np

from typing import Literal
"""
Needs to be divided into separate files.
Some of the funcs can be combines and better explained
Needs to finish the rest of the query funcs to start the front-end work
"""

class QueryProcessorDuck:

    """
    Contains the functions for querying the database
    """

    def __init__(self, db):
        """
        Constructor for database querying class
        """

        self.stop_words = set(stopwords.words('english'))
        self.con = db.con
        self.table = self.con.execute("select * from watch_history").df()
        self.quarter_month_map = { 
            1: [1, 2, 3],
            2: [4, 5, 6],
            3: [7, 8, 9],
            4: [10, 11, 12]
        }

    def insert_history(self, history_list):
        """
        Inserts parsed info into database

        """
        sql = """INSERT OR IGNORE INTO watch_history (video_url, video_name, video_type, video_category, channel_url, channel_name, time_stamp) VALUES (?,?,?,?,?,?,?)"""
        self.con.executemany(sql, history_list)
 
    def date_range_handler(self, lower_range=None, upper_range=None, as_dataframe=False):
        conditions = []
        params = []

        if lower_range:
            conditions.append("time_stamp >= ?")
            params.append(lower_range)

        if upper_range:
            conditions.append("time_stamp <= ?")
            params.append(upper_range)

        time_query = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        if as_dataframe:
            query = "SELECT * FROM watch_history " + time_query
            return self.con.execute(query, params).df()

        return time_query, params

    def the_most_watched_channel(self, limit = 20, lower_range = None, upper_range = None):
        """
        Finds the most watched channels (top 20)
        """

        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)

        df = df.groupby(['channel_name', 'channel_url'], as_index = False).size()\
                .rename(columns = {'channel_name' : 'Channel Name', 'channel_url' : "URL", 'size' : 'Total Watch'})\
                .sort_values('Total Watch', ascending = False)

        df.index = np.arange(1, len(df) + 1)
        return df.reset_index().head(limit)

    def most_watched_channel_per_month(self, lower_range = None, upper_range = None):

        time_query, params = self.date_range_handler(lower_range, upper_range, as_dataframe=False)

        sql = f"""
            select month, channel_name, total_watched
            from (
                select *, rank() over (partition by month order by  total_watched desc) as ranked
                from (
                        select
                        strftime(time_stamp, '%Y-%m') as month,
                        channel_name,
                        count(*) as total_watched
                        from watch_history
                        {time_query}
                        group by strftime(time_stamp, '%Y-%m'), channel_name, channel_url
                ) as t
            ) as t1
            where ranked =  1
            order by month asc
        """

        df =  self.con.execute(sql, params).df().rename(columns = {'month' : 'Year - Month', 'channel_name' : 'Channel Name', 'total_watched' : 'Total Watch'})
        df.index = np.arange(1, len(df) + 1)
        return df.reset_index()

    def the_most_watched_videos(self, limit = 20, video_type:Literal["reel", "video", "unavailable"] = None, lower_range = None, upper_range = None):
        """
        Finds the most watched videos (top 20)
        """
        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)

        if video_type:
            df = df[df['video_type'] == video_type]

        df = df.groupby(['video_name', 'video_url'], as_index = False).size().sort_values("size", ascending = False).rename(columns = {'video_name' : 'Name', 'video_url' : 'URL', 'size' : 'Total Watch'})

        df.index = np.arange(1, len(df) + 1)
        return df.reset_index().head(limit)


    def the_most_repeated_words(self, limit = 20, lower_range = None, upper_range = None):

        df= self.date_range_handler(lower_range, upper_range, as_dataframe=True).drop_duplicates(subset='video_name')

        df['video_name'] = df['video_name'].str.strip().str.lower().str.split().to_list()
        df = df.explode('video_name')
        df['video_name'] = df['video_name'].str.replace(r'[^a-zA-Z0-9]', '', regex=True)
        df = df[(~df['video_name'].isin(list(self.stop_words))) & (df['video_name'].str.len() >= 2)]

        df = df.groupby('video_name', as_index=False).size()\
                .sort_values('size', ascending=False)\
                .rename(columns = {'video_name' : 'Word', 'size' : 'Total Count'})

        df.index = np.arange(1, len(df) + 1)
        return df.reset_index().head(limit)


    def return_by_name_combination(self, sentence, lower_range = None, upper_range = None):
        """
        Finds videos by the combination of words instead of full description
        """
        time_query, params = self.date_range_handler(lower_range, upper_range, as_dataframe=False)

        words = sentence.split()

        sql = f"SELECT DISTINCT video_name, video_url, time_stamp FROM watch_history WHERE {time_query}"  + " AND ".join(["video_name LIKE ?"] * len(words)) + ' ORDER BY time_stamp DESC'

        params += [f"%{word}%" for word in words]

        df = self.con.execute(sql, params).df().rename(columns = {'video_name' : 'Video Name', 'video_url' : 'URL', 'time_stamp' : 'Timestamp'})
        return df

    def the_busiest_day(self, lower_range=None, upper_range=None):
        """
        Finds the busiest days recorded
        """

        time_query, params = self.date_range_handler(lower_range, upper_range, as_dataframe=False)

        sql = f"""
            select
                date(time_stamp) as date,
                dayname(time_stamp) as week_day,
                count(*) as total_count
            from watch_history
            {time_query}
            group by date, week_day
            order by total_count desc, week_day asc
        """
        df = self.con.execute(sql, params).df().rename(columns = {'date' : 'Date', 'week_day' : 'Day of Week', 'total_count': 'Total Count'})
        return df.head(20)

    def unique_type_find(self):

        type_set = set()
        sql = "SELECT video_url from watch_history"
        self.con.execute(sql)
        output = self.con.fetchall()

        # https://www.youtube.com/watch?v=zFWaI9_ZXJM
        for i in output:
            match = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/([^/?#]+)", i[0])
            if match:
                section = match.group(1)

            if section not in type_set:
                type_set.add(section)

        return type_set


    def date_type_time_func(
            self,
            video_type:Literal["reel", "video", "unavailable"] = None,
            time:Literal["morning", "afternoon", "evening", "night"] = None,
            category = None,
            lower_range=None,
            upper_range=None):

        """
        Should show the result based on the user's toggles

        video types = Reel, Video, Unavailable
        time = Morning, Afternoon, Evening, Night
        category = should be one of the options defined in parser class
        """

        time_dictionary = {
            "morning" : [i for i in range(5, 12)],
            "afternoon": [i for i in range(12, 18)],
            "evening": [i for i in range(18, 21)],
            "night": [i for i in range(21, 25)] + [i for i in range(1, 5)]
        }

        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)
        if video_type:
            df = df[df['video_type'] == video_type]

        if time:
            df['hour'] = df['time_stamp'].dt.hour
            df['time'] =   np.where(df['hour'].isin(time_dictionary['afternoon']), 'afternoon',
                            np.where(df['hour'].isin(time_dictionary['morning']), 'morning',
                            np.where(df['hour'].isin(time_dictionary['evening']), 'evening', 'night')))
            df = df[df['time'] == time]

        if category:
            df = df[df['video_category'] == category]

        return df.sort_values('time_stamp').drop(columns = ['historyID', 'time_stamp']).reset_index(drop = True).head(20)

    def last_day(self):
        """
        Finds the last recorded day
        """
        sql_last_date = """SELECT MAX(time_stamp) as last_day from watch_history"""
        self.con.execute(sql_last_date)
        last_date = self.con.fetchone()[0].date()
        return last_date

    def first_day(self):
        """
        Finds the last recorded day
        """
        sql_first_date = """SELECT MIN(time_stamp) as last_day from watch_history"""
        self.con.execute(sql_first_date)
        first_day = self.con.fetchone()[0].date()
        return first_day


    def daily_trend(self, video_type:Literal["reel", "video", "unavailable"] = None, current_date=None):

        last_date = self.last_day()

        if not current_date or datetime.strptime(current_date, "%Y-%m-%d").date() > last_date:
            current_date = last_date

        add_sql = "COUNT(*)"
        params = []

        if video_type:
            add_sql = "COUNT(CASE WHEN video_type = ? THEN 1 END)"
            params.append(video_type)

        sql = f"""
            SELECT
                DATE(time_stamp) as Day,
                HOUR(time_stamp) as Hour,
                {add_sql} AS hour_count
            FROM watch_history
            WHERE DATE(time_stamp) = ?
            GROUP BY day, hour
            ORDER BY hour ASC
        """

        params.append(current_date)

        df = self.con.execute(sql, params).df().rename(columns = {'hour_count' : 'Total Count'})
        return df

    def weekly_trend(self, video_type:Literal["reel", "video", "unavailable"] = None, week_limit = 4):

        df = self.table.copy()
        last_day = df['time_stamp'].max()
        last_week_start = last_day.normalize() - pd.Timedelta(days=last_day.weekday())
        first_week_start = last_week_start - pd.Timedelta(weeks=week_limit - 1)

        df = df[df['time_stamp'] >= first_week_start].copy().assign(time_stamp =  df['time_stamp'].dt.normalize())
        bins = pd.date_range(first_week_start, periods=week_limit + 1, freq='7D')

        labels = [i + 1 for i in range(week_limit)]
        df['week'] = pd.cut(df['time_stamp'], bins=bins, right=False, labels=labels)

        if video_type:
            df[df['video_type'] == video_type]

        return  df.groupby('week', as_index = False)\
                .agg(first_day = ('time_stamp', 'min'), last_day =  ('time_stamp', 'max'), size = ('historyID', 'nunique'))\
                .rename(columns = {'first_day' : 'First Day', 'last_day' : 'Last Day', 'size' : 'Total Count'})\


    def monthly_trend(self, year_choice = None, video_type:Literal["reel", "video", "unavailable"] = None):
        """
        Should show this month's breakdown of watch by weeks
        """
        df = self.table.copy()
        df = df.assign(year = df['time_stamp'].dt.year, month = df['time_stamp'].dt.month)

        if year_choice is None:
            year_choice = df['year'].max()

        df = df[df['year'] >= year_choice -  1]

        if video_type:
            df = df[df['video_type'] == video_type]

        df = df.groupby(['year', 'month'], as_index = False).size().sort_values(['year', 'month'])
        df['cpc'] = ((df['size'] * 100 / df['size'].shift().fillna(df['size'])) - 100).round(2)
        return df[df['year'] == year_choice].rename(columns = {'year' : 'Year', 'month' : 'Month' , 'size' : 'Total Count', 'cpc' : 'Change (%)'}).reset_index(drop = True)

    def seasonal_trend(self, year_choice=None, video_type:Literal["reel", "video", "unavailable"] = None):
        """
        Finds the trend of view by the seasons
        Change is calculated based on diff between prev season
        """

        df = self.table.copy()

        if year_choice is None:
            year_choice = df['time_stamp'].dt.year.max()

        df = df.assign(Year = df['time_stamp'].dt.year, month = df['time_stamp'].dt.month)

        df['Quarter'] =  np.where(df['month'].isin(self.quarter_month_map[1]), 1,
                        np.where(df['month'].isin(self.quarter_month_map[2]), 2,
                        np.where(df['month'].isin(self.quarter_month_map[3]), 3, 4)))

        if video_type:
            df = df[df['video_type'] == video_type]

        result =  df.groupby(['Year', 'Quarter'], as_index=False).size().sort_values(["Year", "Quarter"])
        result['cpc'] = ((result['size'] * 100 / result['size'].shift().fillna(result['size'])) - 100).round(2)

        result =  result[result['Year'] == year_choice].rename(columns = {'size': 'Total Count', 'cpc' : 'Change (Percentage%)'}).reset_index(drop=True)

        return None if result.empty else result

    def last_year(self):
        """
        Finds the last year recorded
        """
        sql_last_date = """SELECT YEAR(MAX(time_stamp)) from watch_history"""
        self.con.execute(sql_last_date)
        last_year = self.con.fetchone()[0]
        return last_year

    def yearly_trend(self, video_type=None):
        df = self.table.copy()

        if video_type:
            df = df[df['video_type'] == video_type]

        result = df.assign(Year = df['time_stamp'].dt.year).groupby('Year', as_index = False).size().sort_values('Year')
        result['Change (Percentage %)'] = ((result['size'] / result['size'].shift().fillna(result['size']) * 100 ) - 100).round(2)
        return result.rename(columns = {'size' : 'Total Count'})

    def channel_life_cycle(self, channel):

        pass

    def topic_obsession_cluster(self):

        pass

    def interest_analysis(self, limit = 20, video_type=None, lower_range = None, upper_range = None):

        """
        Find the most common interests given time duration
        """

        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)

        if video_type:
            df = df[df['video_type'] == video_type]

        df = df.groupby('video_category', as_index = False).size()\
                .rename(columns = {'video_category' : 'Category', 'size' : 'Total Count'})\
                .sort_values('Total Count', ascending = False)

        df.index = np.arange(1, len(df) + 1)
        return df.reset_index().head(limit)
    def number_of_unique_channels_watched_month(self, year_choice=None, month_choice=None):
        """
        Finds the number of unique channels within the given time
        """
        last_day = self.last_day()
        year_choice = last_day.strftime('%Y')
        month_choice = last_day.strftime('%m')

        sql = """ SELECT DISTINCT channel_name, channel_url, COUNT(*) as count FROM watch_history WHERE YEAR(time_stamp) = ? AND MONTH(time_stamp) = ? GROUP BY channel_name, channel_url ORDER BY count DESC"""
        df = self.con.execute(sql, [year_choice, month_choice]).df().rename(columns = {'channel_name' : 'Channel Name', 'channel_url' : 'URL', 'count' : 'Total Count'})
        return df

    def most_watched_week(self, lower_range=None, upper_range=None, video_type=None):
        """
        Finds start and end of the week where the user watched the most (depending on video type)
        """

        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)
        df['time_stamp'] = df['time_stamp'].dt.normalize()

        df['first_day'] = df['time_stamp'] - df['time_stamp'].dt.weekday * pd.Timedelta(days=1)
        df['last_day'] = df['first_day'] + pd.Timedelta(days=6)

        if video_type:
            df = df[df['video_type'] == video_type]

        result = df.groupby(['first_day', 'last_day'], as_index=False).size()\
                    .sort_values('size', ascending=False).rename(columns = {'size' : 'Total Count'}).reset_index(drop = True)

        return result

    def max_time_of_the_day(self, lower_range=None, upper_range=None, video_type=None):
        """Finds the time of the day where the most videos/reel are watched"""

        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)
        if video_type:
            df = df[df['video_type'] == video_type]

        result = df.assign(hour = df['time_stamp'].dt.hour).groupby('hour', as_index = False).size()\
                .sort_values('size', ascending=False).rename(columns={'size' : 'Total Count'}).reset_index(drop = True)
        return result

    def weekday_vs_weekend(self, lower_range=None, upper_range=None):
        # average number of videos, reels, category, can find top categories of each

        time_query , params  = self.date_range_handler(lower_range, upper_range, as_dataframe=False)


        sql_define_days = f"""
            select
                video_type,
                sum(case when day_type = 'weekday' then avg else 0 end) as weekday_avg,
                sum(case when day_type = 'weekend' then avg else 0 end) as weekend_avg
            from (
                    select
                        day_type,
                        video_type,
                        round(count(*) / (case when day_type = 'weekday' then 5 else 2 end), 2) as avg
                    from (
                            select
                                *,
                                case
                                    when weekday(time_stamp) < 5 THEN 'weekday'
                                    else 'weekend'
                                    end AS day_type
                            from watch_history
                        ) as t
                    group by day_type, video_type
                ) as t
            {time_query}
            group by video_type
        """

        df = self.con.execute(sql_define_days, params).df().rename(columns = {'video_type' : 'Video Type', 'weekday_avg' : 'Weekday Average', 'weekend_avg' : 'Weekend Average'})
        return df

    def binge_watch_detection(self, lower_range=None, upper_range=None):
        pass

    def streak_analysis(self, lower_range=None, upper_range=None):

        time_query , params = self.date_range_handler(lower_range, upper_range, as_dataframe=False)

        sql = f"""
            SELECT
                MIN(d) AS streak_start,
                MAX(d) AS streak_end,
                COUNT(*) AS streak
            FROM (
                    SELECT
                        d,
                        d - (ROW_NUMBER() OVER (ORDER BY d) * INTERVAL 1 DAY) AS grouped
                    FROM (
                            SELECT DISTINCT DATE(time_stamp) AS d
                            FROM watch_history
                        ) AS days
                ) AS t
            {time_query}
            GROUP BY grouped
            ORDER BY streak DESC
        """

        df = self.con.execute(sql, params).df().rename(columns = {'streak_start' : 'Start', 'streak_end' : 'End', 'streak' : 'Total Days'})
        return df

    def video_length_preference(self, lower_range=None, upper_range=None):
        time_query , params = self.date_range_handler(lower_range, upper_range, as_dataframe=False)

        sql = f"""
            select
                video_type,
                count(*) as total
            from watch_history
            {time_query}
            group by video_type
            order by total desc
        """

        df = self.con.execute(sql, params).df().rename(columns = {'video_type' : 'Type', 'total' : 'Total Count'})
        return df

    def video_length_trend_over_month(self):

        sql = """
            select
                strftime(time_stamp, '%Y-%m') as Month,
                video_type,
                count(*) as video_type_month_total
            from watch_history
            group by month, video_type
            order by month
        """

        df = self.con.execute(sql).df().rename(columns = {'video_type' : 'Video Type', 'video_type_month_total' : 'Month Total'})

        pivoted = pd.pivot_table(df, index='Video Type', columns='Month', values='Month Total').reset_index()
        return pivoted

    def unavailable_videos(self, lower_range=None, upper_range=None):

        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)

        df = df[df['video_type'] == 'unavailable']\
                .drop(columns = "historyID")\
                .rename(columns = {'video_name' : 'Name', 'video_url' : 'URL', 'video_type' : 'Type', 'video_category' : 'Category', 'time_stamp' : 'Timestamp'})\
                .sort_values('Timestamp', ascending = False)

        df.index = np.arange(1, len(df) + 1)

        return df.reset_index()
    def first_last_videos_ever_watched(self, video_limit=1, video_type:Literal["reel", "video", "unavailable"] = None, first_or_last = True):
        """
        Finds the first ever video watched
        """

        df = self.table.copy()
        if video_type:
            df = df[df['video_type'] == video_type]

        df = df.sort_values("time_stamp", ascending = first_or_last)[['video_name', 'video_url', 'video_type', 'video_category', 'time_stamp']]\
                .rename(columns = {'video_name' : 'Name', 'video_url' : 'URL', 'video_type' : 'Type', 'video_category' : 'Category', 'time_stamp' : 'Timestamp'})

        df.index = np.arange(1, len(df) + 1)

        return df.reset_index().head(video_limit)

    def the_longest_untouched_channel(self, limit = 20, lower_range=None, upper_range=None):
        """
        Needs to have a neglect score where the user can discover channels they used to watch long before

        Calculation: number of days since the last video was watched * the total number videos watched by a channel
        """

        time_query , params = self.date_range_handler(lower_range, upper_range, as_dataframe=False)

        custom_table = f"""
            SELECT COUNT(*) AS total_count, 
            MAX(time_stamp) AS last_watch,
            channel_name,
            channel_url
            FROM watch_history
            {time_query}
            GROUP BY channel_name, channel_url
        """

        sql = f"""
            SELECT
            channel_name,
            channel_url,
            total_count,
            DATEDIFF('day', last_watch, now()) AS days_since_last,
            DATEDIFF('day', last_watch, now()) * total_count AS neglect_score
            FROM ({custom_table}) AS custom
            ORDER BY neglect_score DESC
        """

        df = self.con.execute(sql, params).df()\
            .rename(columns = {'channel_name': 'Channel Name', 'channel_url' : 'URL', 'total_count' : 'Total Watch', 'days_since_last' : 'Since Last Watched', 'neglect_score' : 'Neglect Score'})
        df.index = np.arange(1, len(df) + 1)
        return df.reset_index().head(limit)

    def random_day_discovery(self):
        """
        Shows the itinerary of one random day
        """
        self.con.execute("SELECT DISTINCT DATE(time_stamp) AS d FROM watch_history ORDER BY random() LIMIT 1")
        random_date = self.con.fetchone()[0]

        sql = """
            SELECT video_name, video_url, video_type, video_category, time_stamp
            FROM watch_history
            WHERE time_stamp >= ? AND time_stamp < ? + INTERVAL 1 DAY
            ORDER BY time_stamp ASC
        """
        df = self.con.execute(sql, (random_date, random_date)).df()\
            .rename(columns = {'video_name' : 'Name', 'video_url' : 'URL', 'video_type' : 'Type', 'time_stamp' : 'Timestamp'})
        df.index = np.arange(1, len(df) + 1)

        return df.reset_index()

    def the_longest_titled_video(self, video_limit=10, video_type=None, lower_range = None, upper_range = None):
        """
        Finds the longest titles video
        """

        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)

        if video_type:
            df = df[df['video_type'] == video_type]

        df = df.assign(length_video = df['video_name'].str.len())[['video_name', 'video_url', 'video_type', 'length_video']]\
                .sort_values('length_video', ascending = False)\
                .rename(columns = {'video_name' : 'Name', 'video_url' : 'URL', 'length_video' : 'Title Length'})

        df.index = np.arange(1, len(df) + 1)
        return df.reset_index().head(video_limit)