
from database_connection import Database
from nltk.corpus import stopwords
import re
from datetime import timedelta, datetime
import pandas as pd 
from typing import Literal
import numpy as np
"""
Needs to be divided into separate files.
Some of the funcs can be combines and better explained
Needs to finish the rest of the query funcs to start the front-end work
"""
class QueryProcessor:

    """
    Contains the functions for querying the database
    """

    def __init__(self):
        """
        Constructor for database querying class
        """
        # database connection
        self.connection = Database()
        connection = self.connection
        self.db = connection.db
        self.table = pd.read_sql("select * from watch_history", self.db)
        self.cursor = connection.cursor

        self.stop_words = set(stopwords.words('english'))
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
        sql = """INSERT IGNORE INTO watch_history (video_url, video_name, video_type, video_category, channel_url, channel_name, time_stamp) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
        self.cursor.executemany(sql, history_list)
        self.db.commit()

    def date_rage_handler(self, lower_range, upper_range, as_dataframe = False):
        time_query = ""
        params = []

        if lower_range and not upper_range:
            time_query = " AND time_stamp >= %s "
            params = [lower_range]

        if not lower_range and upper_range:
            time_query = " AND time_stamp <= %s "
            params = [upper_range]

        if lower_range and upper_range:
            time_query = " AND time_stamp >= %s AND time_stamp <= %s "
            params = [lower_range, upper_range]

        if as_dataframe:
            self.cursor.execute("select * from watch_history", params)
            return  pd.DataFrame(self.cursor.fetchall(), columns = [col[0] for col in self.cursor.description])

        return time_query, params

    def the_most_watched_channel(self):
        """
        Finds the most watched channels (top 20)
        """
        sql = "SELECT channel_name, channel_url, COUNT(*) AS count FROM watch_history GROUP BY channel_name, channel_url ORDER BY count DESC LIMIT 20"

        self.cursor.execute(sql)
        df = pd.DataFrame(self.cursor.fetchall(), columns=['Channel Name', 'Channel URL', 'Total Watch'])
        return df

    def most_watched_channel_per_month(self, lower_range = None, upper_range = None):

        time_query, params = self.date_rage_handler(lower_range, upper_range, as_dataframe=False)

        sql = f"""
            select month, channel_name, total_watched
            from (
                select *, rank() over (partition by month order by  total_watched desc) as ranked
                from (
                        select
                        DATE_FORMAT(time_stamp, "%Y-%m") as month,
                        channel_name,
                        count(*) as total_watched
                        from watch_history
                        {time_query}
                        group by DATE_FORMAT(time_stamp, "%Y-%m"), channel_name, channel_url
                ) as t
            ) as t1
            where ranked =  1
            order by month asc
        """

        self.cursor.execute(sql, params)
        df = pd.DataFrame(self.cursor.fetchall(), columns=['Year - Month', 'Channel Name', 'Total Watch'])
        return df


    def the_most_watched_videos(self, lower_range = None, upper_range = None):
        """
        Finds the most watched videos (top 20)
        """
        time_query, params = self.date_rage_handler(lower_range, upper_range, as_dataframe=False)


        sql = f"SELECT video_name, video_url, COUNT(*) AS count FROM watch_history {time_query} GROUP BY video_name, video_url ORDER BY count DESC LIMIT 20"
        self.cursor.execute(sql, params)

        df = pd.DataFrame(self.cursor.fetchall(), columns=['Video Name', 'Video URL', 'Total Watch'])

        return df


    def the_most_repeated_words(self, lower_range = None, upper_range = None):

        df= self.date_rage_handler(lower_range, upper_range, as_dataframe=True).drop_duplicates(subset='video_name')

        df['video_name'] = df['video_name'].str.strip().str.lower().str.split().to_list()
        df = df.explode('video_name')
        df['video_name'] = df['video_name'].str.replace(r'[^a-zA-Z0-9]', '', regex=True)
        df = df[(~df['video_name'].isin(list(self.stop_words))) & (df['video_name'].str.len() >= 2)]

        result = df.groupby('video_name', as_index=False).size()\
                .sort_values('size', ascending=False)\
                .rename(columns = {'video_name' : 'Word', 'size' : 'Total Count'})\
                .reset_index(drop=True)

        return result.head(20)


    def return_by_name_combination(self, sentence, lower_range = None, upper_range = None):
        """
        Finds videos by the combination of words instead of full description
        """
        time_query, params = self.date_rage_handler(lower_range, upper_range, as_dataframe=False)

        words = sentence.split()

        sql = f"SELECT DISTINCT video_name, video_url, time_stamp FROM watch_history WHERE {time_query}"  + " AND ".join(["video_name LIKE %s"] * len(words)) + 'ORDER BY time_stamp DESC'

        params += [f"%{word}%" for word in words]

        self.cursor.execute(sql, params)
        df = pd.DataFrame(self.cursor.fetchall(), columns = ['Video Name', 'Video URL', 'Timestamp'])
        return df


    def the_busiest_day(self, lower_range=None, upper_range=None):
        """
        Finds the busiest days recorded
        """

        time_query, params = self.date_rage_handler(lower_range, upper_range, as_dataframe=False)

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
        self.cursor.execute(sql, params)
        df = pd.DataFrame( self.cursor.fetchall(), columns=['Date', 'Day of Week', 'Total Count'])
        return df.head(20)

    def unique_type_find(self):

        type_set = set()
        sql = "SELECT video_url from watch_history"
        self.cursor.execute(sql)
        output = self.cursor.fetchall()

        # https://www.youtube.com/watch?v=zFWaI9_ZXJM
        for i in output:
            match = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/([^/?#]+)", i[0])
            if match:
                section = match.group(1)

            if section not in type_set:
                type_set.add(section)

        return type_set


    def date_type_time_func(self, video_type:Literal["reel", "video", "unavailable"] = None, time:Literal["morning", "afternoon", "evening", "night"] = None, lower_range=None, upper_range=None):
        """
        Should show the result based on the user's toggles

        video types = Reel, Video, Unavailable
        time = Morning, Afternoon, Evening, Night

        """

        time_dictionary = {
            "morning" : [5, 12],
            "afternoon": [12, 17],
            "evening": [17, 21],
            "night": [21, 5]
        }

        clauses_list = []
        params_list = []

        video_type_query = "video_type = %s"
        time_query = "HOUR(time_stamp) >= %s AND HOUR(time_stamp) < %s"
        night_time_query = "HOUR(time_stamp) >= %s OR HOUR(time_stamp) < %s"
        lower_range_query = "time_stamp >= %s"
        upper_range_query = "time_stamp <= %s"

        if video_type:
            clauses_list.append(video_type_query)
            params_list.append(video_type)

        if time:
            if time != "night":
                clauses_list.append(time_query)
            else:
                clauses_list.append(night_time_query)

            params_list.extend(time_dictionary[time])

        if lower_range:
            clauses_list.append(lower_range_query)
            params_list.append(lower_range)

        if upper_range:
            clauses_list.append(upper_range_query)
            params_list.append(upper_range)

        condition_clause = ""
        if len(clauses_list) != 0:
            condition_clause+= " WHERE "

        main_query = """
            SELECT video_type, COUNT(*) AS count
            FROM watch_history
        """ + condition_clause + " AND ".join(clauses_list) +  " GROUP BY video_type"

        self.cursor.execute(main_query, params_list)

        df = pd.DataFrame(self.cursor.fetchall(), columns=['Video Type', 'Total Count'])

        return df


    def last_day(self):
        """
        Finds the last recorded day
        """
        sql_last_date = """SELECT MAX(time_stamp) from watch_history"""
        self.cursor.execute(sql_last_date)
        last_date = self.cursor.fetchone()[0].date()
        return last_date


    def daily_trend(self, video_type:Literal["reel", "video", "unavailable"] = None, current_date=None):

        last_date = self.last_day()

        if not current_date or datetime.strptime(current_date, "%Y-%m-%d").date() > last_date:
            current_date = last_date

        add_sql = "COUNT(*)"
        params = []

        if video_type:
            add_sql = "COUNT(CASE WHEN video_type = %s THEN 1 END)"
            params.append(video_type)

        sql = f"""
            SELECT
                DATE(time_stamp) as day,
                HOUR(time_stamp) as hour,
                {add_sql} AS hour_count
            FROM watch_history
            WHERE DATE(time_stamp) = %s
            GROUP BY day, hour
            ORDER BY hour ASC
        """

        params.append(current_date)

        self.cursor.execute(sql, params=params)
        df = pd.DataFrame(self.cursor.fetchall(),columns=['day', 'Hour', 'Total Count'])

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
        return df[df['year'] == year_choice].reset_index(drop = True)

    def seasonal_trend(self, year_choice=None, video_type:Literal["reel", "video", "unavailable"] = None):
        """
        Finds the trend of view by the seasons
        Change is calculated based on diff between prev season
        """

        df = self.table.copy()

        if year_choice is None:
            year_choice = df['time_stamp'].dt.year.max()

        df = df.assign(year = df['time_stamp'].dt.year, month = df['time_stamp'].dt.month)

        df['quarter'] =  np.where(df['month'].isin(self.quarter_month_map[1]), 1,
                        np.where(df['month'].isin(self.quarter_month_map[2]), 2,
                        np.where(df['month'].isin(self.quarter_month_map[3]), 3, 4)))

        if video_type:
            df = df[df['video_type'] == video_type]

        result =  df.groupby(['year', 'quarter'], as_index=False).size().sort_values(["year", "quarter"])
        result['cpc'] = ((result['size'] * 100 / result['size'].shift().fillna(result['size'])) - 100).round(2)

        result =  result[result['year'] == year_choice].rename(columns = {'size': 'Total Count', 'cpc' : 'Change (Percentage%)'}).reset_index(drop=True)

        return None if result.empty else result

    def last_year(self):
        """
        Finds the last year recorded
        """
        sql_last_date = """SELECT YEAR(MAX(time_stamp)) from watch_history"""
        self.cursor.execute(sql_last_date)
        last_year = self.cursor.fetchone()[0]
        return last_year

    def yearly_trend(self, video_type=None):
        df = self.table.copy()

        if video_type:
            df = df[df['video_type'] == video_type]

        result = df.assign(year = df['time_stamp'].dt.year).groupby('year', as_index = False).size().sort_values('year')
        result['Change (Percentage %)'] = ((result['size'] / result['size'].shift().fillna(result['size']) * 100 ) - 100).round(2)
        return result.rename(columns = {'size' : 'Total Count'})

    def channel_life_cycle(self, channel):

        pass

    def topic_obsession_cluster(self):

        pass

    def interest_analysis(self, year, month=None, video_type=None):

        """
        Find the most common interests given time duration
        """
        params = [year]

        month_query = ""
        if month:
            month_query+= " AND MONTH(time_stamp) = %s"
            params.append(month)

        type_sql = ""
        if  video_type:
            type_sql = " AND video_type = %s "
            params.append(video_type)

        sql = "SELECT DISTINCT video_category, COUNT(*)  FROM watch_history WHERE YEAR(time_stamp) = %s" + month_query + type_sql + " GROUP BY video_category ORDER BY COUNT(*) DESC "
        self.cursor.execute(sql, params)

        df = pd.DataFrame(self.cursor.fetchall(), columns=['Video Category', 'Total Count'])

        return df

    def number_of_unique_channels_watched_month(self, year, month):
        """
        Finds the number of unique channels within the given time
        """
        sql = """ SELECT DISTINCT channel_name, channel_url, COUNT(*) as count FROM watch_history WHERE YEAR(time_stamp) = %s AND MONTH(time_stamp) = %s GROUP BY channel_name, channel_url ORDER BY count DESC"""
        self.cursor.execute(sql, [year, month])
        output = self.cursor.fetchall()
        return output

    def most_watched_week(self, lower_range=None, upper_range=None, video_type=None):
        """
        Finds start and end of the week where the user watched the most (depending on video type)
        """

        df = self.date_rage_handler(lower_range, upper_range, as_dataframe=True)
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

        df = self.date_rage_handler(lower_range, upper_range, as_dataframe=True)
        if video_type:
            df = df[df['video_type'] == video_type]

        result = df.assign(hour = df['time_stamp'].dt.hour).groupby('hour', as_index = False).size()\
                .sort_values('size', ascending=False).rename(columns={'size' : 'Total Count'}).reset_index(drop = True)
        return result

    def weekday_vs_weekend(self, lower_range=None, upper_range=None):
        # average number of videos, reels, category, can find top categories of each

        time_query , params  = self.date_rage_handler(lower_range, upper_range, as_dataframe=False)


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

        self.cursor.execute(sql_define_days, params)
        df = pd.DataFrame(self.cursor.fetchall(), columns=['Video Type', 'Weekday Average', 'Weekend Average'])
        return df

    def binge_watch_detection(self, lower_range=None, upper_range=None):
        pass

    def streak_analysis(self, lower_range=None, upper_range=None):

        time_query , params = self.date_rage_handler(lower_range, upper_range, as_dataframe=False)

        sql = f"""
            SELECT
                MIN(d) AS streak_start,
                MAX(d) AS streak_end,
                COUNT(*) AS streak
            FROM (
                    SELECT
                        d,
                        DATE_SUB(d, INTERVAL ROW_NUMBER() OVER (ORDER BY d) DAY) AS grp
                    FROM (
                            SELECT DISTINCT DATE(time_stamp) AS d
                            FROM watch_history
                        ) AS days
                ) AS t
            {time_query}
            GROUP BY grp
            ORDER BY streak DESC
        """

        self.cursor.execute(sql, params)
        df = pd.DataFrame(self.cursor.fetchall(), columns=['Streak Start', 'Streak End', 'Total Count'])
        return df

    def video_length_preference(self, lower_range=None, upper_range=None):
        time_query , params = self.date_rage_handler(lower_range, upper_range, as_dataframe=False)

        sql = f"""
            select
                video_type,
                count(*) as total
            from watch_history
            {time_query}
            group by video_type
            order by total desc
        """

        self.cursor.execute(sql, params)
        df = pd.DataFrame(self.cursor.fetchall(), columns=['Video Type', 'Total Count'])
        return df

    def video_length_trend_over_month(self):

        sql = """
            select
                date_format(time_stamp, "%Y-%m") as month,
                video_type,
                count(*) as video_type_month_total
            from watch_history
            where video_type != 'unavailable'
            group by month, video_type
            order by month
        """

        self.cursor.execute(sql)
        df = pd.DataFrame(self.cursor.fetchall(), columns=['Month', 'Video Type', 'Month Total'])

        pivoted = pd.pivot_table(df, index='Video Type', columns='Month', values='Month Total')
        return pivoted

    def unavailable_videos(self, category_type=None, lower_range=None, upper_range=None):

        time_query, params = self.date_rage_handler(lower_range, upper_range, as_dataframe=False)

        sql = f"""
            select
                count(case when video_type = 'unavailable' then 1 end)
            from watch_history
            {time_query}
        """
        self.cursor.execute(sql, params)
        unavailable = self.cursor.fetchone()
        return unavailable

    def first_video_ever_watched(self, video_limit=1):
        """
        Finds the first ever video watched
        """
        sql = f"SELECT video_name, video_url, video_type, video_category FROM watch_history ORDER BY time_stamp ASC LIMIT {video_limit} "
        self.cursor.execute(sql)
        output = self.cursor.fetchall()
        return output if output else None

    def last_videos_ever_watched(self, video_limit=1):
        """
        Finds the last video watched
        """
        sql = f"SELECT video_name, video_url, video_type, video_category FROM watch_history ORDER BY time_stamp DESC LIMIT {video_limit} "
        self.cursor.execute(sql)
        output = self.cursor.fetchall()
        return output if output else None

    def the_longest_untouched_channel(self, lower_range=None, upper_range=None):
        """
        Needs to have a neglect score where the user can discover channels they used to watch long before

        Calculation: number of days since the last video was watched * the total number videos watched by a channel
        """

        time_query = ""
        params = []

        if lower_range and not upper_range:
            time_query = " WHERE time_stamp >= %s "
            params = [lower_range]

        if not lower_range and upper_range:
            time_query = " WHERE time_stamp <= %s "
            params = [upper_range]

        if lower_range and upper_range:
            time_query = " WHERE time_stamp >= %s AND time_stamp <= %s "
            params = [lower_range, upper_range]

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
            DATEDIFF(NOW(), last_watch) AS days_since_last,
            DATEDIFF(NOW(), last_watch) * total_count AS neglect_score
            FROM ({custom_table}) AS custom
            ORDER BY neglect_score DESC
            LIMIT 10
        """

        self.cursor.execute(sql, params)
        output = self.cursor.fetchall()
        return output if output else None

    def random_day_discovery(self):
        """
        Shows the itinerary of one random day
        """
        self.cursor.execute("SELECT DISTINCT DATE(time_stamp) AS d FROM watch_history ORDER BY RAND() LIMIT 1")
        random_date = self.cursor.fetchone()[0]
        print(random_date)

        sql = """
            SELECT video_name, video_url, video_type, video_category, time_stamp
            FROM watch_history
            WHERE time_stamp >= %s AND time_stamp < %s + INTERVAL 1 DAY
            ORDER BY time_stamp ASC
        """
        self.cursor.execute(sql, (random_date, random_date))
        itinerary = self.cursor.fetchall()
        return itinerary

    def the_longest_titled_video(self, video_type=None, video_limit=10):
        """
        Finds the longest titles video
        """
        where_query = ""
        if video_type:
            where_query = f" WHERE video_type = {video_type} "

        sql = f"SELECT video_name, video_url, video_type, LENGTH(video_name) as length_video FROM watch_history " + where_query + f"ORDER BY length_video DESC LIMIT {video_limit} "
        self.cursor.execute(sql)
        output = self.cursor.fetchall()
        return output if output else None

