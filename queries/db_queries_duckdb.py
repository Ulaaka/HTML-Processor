
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

    def the_most_watched_videos(self, limit = 20, video_category = None, video_type =  None, lower_range = None, upper_range = None):
        """
        Finds the most watched videos
        """
        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)


        default_group = ['video_name', 'video_url']
        columns = {'video_name' : 'Name', 'video_url' : 'URL', 'size' : 'Total Watch'}

        if video_type:
            df = df[df['video_type'] == video_type]

        if video_category:
            df = df[df['video_category'] == video_category]

        df = df.groupby(default_group, as_index = False).size().sort_values("size", ascending = False).rename(columns = columns)

        df.index = np.arange(1, len(df) + 1)
        return df.reset_index().head(limit)


    def the_most_repeated_words(self, limit=20, video_category=None, video_type=None, lower_range=None, upper_range=None):
        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)

        if 'video_name' not in df.columns:
            return pd.DataFrame(columns=['Word', 'Total Count'])

        if video_category:
            df = df[df['video_category'] == video_category]

        if video_type:
            df = df[df['video_type'] == video_type]

        df['video_name'] = (df['video_name'].fillna('').astype(str).str.strip().str.lower().str.split())

        df = df.explode('video_name')

        df['video_name'] = df['video_name'].str.replace(
            r'[^\w]', '', regex=True
        )

        df = df[(df['video_name'].str.len() >= 2) &(~df['video_name'].isin(self.stop_words))]

        df = (df.groupby('video_name').size().reset_index(name='Total Count').sort_values('Total Count', ascending=False).rename(columns={'video_name': 'Word'}))

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

    def the_busiest_day(self, category_or_type, limit=20, lower_range=None, upper_range=None):
        """
        Finds the busiest days recorded (pandas version)
        """
        chosen = "video_category" if category_or_type == "Category" else "video_type"

        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)
        df["time_stamp"] = pd.to_datetime(df["time_stamp"])
        df["date"] = df["time_stamp"].dt.date
        df["week_day"] = df["time_stamp"].dt.day_name()

        daily = df.groupby(["date", "week_day", chosen]).size().reset_index(name="type_count")
        daily["total_count"] = daily.groupby("date")["type_count"].transform("sum")

        top_days = daily[["date", "total_count"]].drop_duplicates()\
                    .sort_values(["total_count", "date"], ascending=False).head(limit)["date"]

        result = daily[daily["date"].isin(top_days)].sort_values(["total_count", "date", "type_count"], ascending=False)\
                    .rename(columns={"date": "Date", "week_day": "Day of Week",
                                    chosen: category_or_type,   "type_count": "Sub Count",
                                    "total_count": "Total Count"
                                    })\
                    .reset_index(drop=True)
        return result

    def last_days_trend(self, category_or_type, limit = 7):
        """
        Finds the trend for the 7 days
        """
        chosen = "video_category" if category_or_type == "Category" else "video_type"

        df = self.table.copy()

        last_day = self.last_day()
        df['time_stamp'] = df['time_stamp'].dt.normalize()

        df = pd.merge(
                pd.DataFrame(pd.date_range(last_day - pd.Timedelta(days=limit - 1), last_day), columns=['time_stamp']),
                df,
                on = 'time_stamp'
        )

        df["week_day"] = df["time_stamp"].dt.day_name()
        daily = df.groupby(["time_stamp", "week_day", chosen]).size().reset_index(name="type_count")
        daily["total_count"] = daily.groupby("time_stamp")["type_count"].transform("sum")
        daily["time_stamp"] = daily["time_stamp"].dt.strftime("%Y-%m-%d")
        result = daily.rename(columns={"time_stamp": "Date", "week_day": "Day of Week",
                                    chosen: category_or_type,   "type_count": "Sub Count",
                                    "total_count": "Total Count"
                                    })\
                    .sort_values('Date').reset_index(drop = True)
        return result
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
            limit = 2,
            video_type = None,
            video_category = None,
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

        if video_category:
            df = df[df['video_category'] == video_category]
        if time:
            df['hour'] = df['time_stamp'].dt.hour
            df['time'] =   np.where(df['hour'].isin(time_dictionary['afternoon']), 'afternoon',
                            np.where(df['hour'].isin(time_dictionary['morning']), 'morning',
                            np.where(df['hour'].isin(time_dictionary['evening']), 'evening', 'night')))
            df = df[df['time'] == time]

        if category:
            df = df[df['video_category'] == category]

        df = df.sort_values('time_stamp', ascending = False).drop(columns = 'historyID')\
                .rename(columns = {
                            'video_url' : 'Video URL',
                            'video_name' : 'Video Name',
                            'video_type' : 'Type',
                            'video_category' : 'Category',
                            'channel_name' : 'Channel Name',
                            'channel_url' : 'Channel URL',
                            'time_stamp' : 'Timestamp'
                            })

        df.index = np.arange(1, len(df) + 1)
        return df.reset_index().head(limit)

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


    def daily_trend(self, category_or_type, current_date):

        sql = """
            SELECT video_name, video_url, video_type, video_category, time_stamp
            FROM watch_history
            WHERE time_stamp >= CAST(? AS DATE)
            AND time_stamp <  CAST(? AS DATE) + INTERVAL  DAY
            ORDER BY time_stamp ASC
        """

        df = self.con.execute(sql, (current_date, current_date)).df()\
            .rename(columns={'video_name': 'Name', 'video_url': 'URL', 'video_category': 'Category',
                            'video_type': 'Type', 'time_stamp': 'Timestamp'})

        pivoted = (
            pd.crosstab(df['Timestamp'].dt.hour, df[category_or_type])
            .reindex(range(24), fill_value=0)
            .rename_axis('Hour')
        )

        df.index = np.arange(1, len(df) + 1)
        return df.reset_index(), pivoted

    def weekly_trend(self, video_type:Literal["reel", "video", "unavailable"] = None, week_limit = 4):
        # needs to be able to choose from which date to another date, and just calcualt ehte weeks between and show maybe
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

    def weekly_trend_updated(self, category_or_type, limit = 4):
        """
        Finds the trend last given number of weeks
        """
        chosen = "video_category" if category_or_type == "Category" else "video_type"

        df = self.table.copy()

        df['time_stamp'] = df['time_stamp'].dt.normalize()

        df['first_day'] = df['time_stamp'] - df['time_stamp'].dt.weekday * pd.Timedelta(days=1)
        df['combined'] = df['first_day'].astype(str) + ' - ' +(df['first_day'] + pd.Timedelta(days=6)).astype(str)

        df['ranked'] = df['first_day'].rank(method = 'dense', ascending = False)

        df = df[df['ranked'] <= limit]
        daily = df.groupby(['combined', chosen]).size().reset_index(name="type_count")

        daily["total_count"] = daily.groupby(['combined'])['type_count'].transform('sum')


        result = daily.sort_values(["combined", "total_count", "type_count"])\
                    .rename(columns={
                        "combined": "Week",
                        chosen: category_or_type,
                        "type_count": "Sub Count",
                        "total_count": "Total Count"
                    })\
                    .reset_index(drop=True)

        return result

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

    def monthly_trend_updated(self, category_or_type, limit = 4):
        """
        Finds the trend last given number of months
        """
        chosen = "video_category" if category_or_type == "Category" else "video_type"

        df = self.table.copy()

        df['combined'] = df['time_stamp'].dt.strftime("%Y-%m")
        df['ranked'] =  df['combined'].rank(method = 'dense', ascending = False)

        df = df[df['ranked'] <= limit]
        daily = df.groupby(['combined', chosen]).size().reset_index(name="type_count")

        daily["total_count"] = daily.groupby(['combined'])['type_count'].transform('sum')

        result = daily.sort_values(["combined", "total_count", "type_count"])\
                    .rename(columns={
                        "combined": "Month",
                        chosen: category_or_type,
                        "type_count": "Sub Count",
                        "total_count": "Total Count"
                    })\
                    .reset_index(drop=True)

        return result

    def quarter_trend(self, year_choice=None, video_type:Literal["reel", "video", "unavailable"] = None):
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

    def quarter_trend_updated(self, category_or_type, year):
        chosen = "video_category" if category_or_type == "Category" else "video_type"

        df = self.table.copy()

        df = df.assign(Year=df['time_stamp'].dt.year, month=df['time_stamp'].dt.month)

        df['Quarter'] = np.where(df['month'].isin(self.quarter_month_map[1]), 1,
                        np.where(df['month'].isin(self.quarter_month_map[2]), 2,
                        np.where(df['month'].isin(self.quarter_month_map[3]), 3, 4)))


        df['Quarter_Start'] = df.groupby(['Year', 'Quarter'])['time_stamp'].transform('min').dt.strftime("%Y-%m-%d")
        df['Quarter_End'] = df.groupby(['Year', 'Quarter'])['time_stamp'].transform('max').dt.strftime("%Y-%m-%d")

        daily = df.groupby(['Year', 'Quarter', chosen]).agg(
            type_count=('historyID', 'nunique'), 
            min_date=('Quarter_Start', 'first'), 
            max_date=('Quarter_End', 'first')
        ).reset_index()

        daily["total_count"] = daily.groupby(['Year', 'Quarter'])['type_count'].transform('sum')

        daily = daily[daily['Year'] == year]

        result = daily.sort_values(['Year', 'Quarter', "total_count", "type_count"])\
                    .rename(columns={
                        'min_date': 'Start Date',
                        'max_date': 'End Date',
                        chosen: category_or_type,
                        "type_count": "Sub Count",
                        "total_count": "Total Count"
                    })\
                    .reset_index(drop=True)

        result['Year-Quarter'] = result['Year'].astype('str') + " - " + result['Quarter'].astype('str')
        return result.drop(columns=['Year', 'Quarter'])

    def last_year(self):
        """
        Finds the last year recorded
        """
        sql_last_date = """SELECT YEAR(MAX(time_stamp)) from watch_history"""
        self.con.execute(sql_last_date)
        last_year = self.con.fetchone()[0]
        return last_year

    def all_years(self):
        """
        Finds all year sorted
        """
        sql_last_date = """SELECT DISTINCT YEAR(time_stamp)from watch_history ORDER BY YEAR(time_stamp) DESC"""
        self.con.execute(sql_last_date)
        return [row[0] for row in self.con.fetchall()]

    def yearly_trend(self, video_type=None):
        df = self.table.copy()

        if video_type:
            df = df[df['video_type'] == video_type]

        result = df.assign(Year = df['time_stamp'].dt.year).groupby('Year', as_index = False).size().sort_values('Year')
        result['Change (Percentage %)'] = ((result['size'] / result['size'].shift().fillna(result['size']) * 100 ) - 100).round(2)
        return result.rename(columns = {'size' : 'Total Count'})

    def yearly_trend_update(self, category_or_type, limit = 6):
        """
        Finds the trend given months
        """

        chosen = "video_category" if category_or_type == "Category" else "video_type"

        df = self.table.copy()

        df['year'] = df['time_stamp'].dt.year

        df['ranked'] =  df['year'].rank(method = 'dense', ascending = False)

        df = df[df['ranked'] <= limit]

        df['yearly_start'] = df.groupby('year')['time_stamp'].transform('min').dt.strftime("%Y-%m-%d")
        df['yearly_end'] = df.groupby('year')['time_stamp'].transform('max').dt.strftime("%Y-%m-%d")

        daily = df.groupby(['year', chosen]).agg(
            type_count=('historyID', 'nunique'), 
            min_date=('yearly_start', 'first'), 
            max_date=('yearly_end', 'first')
        ).reset_index()

        daily["total_count"] = daily.groupby('year')['type_count'].transform('sum')

        result = daily.sort_values(["year", "total_count", "type_count"])\
                    .rename(columns={
                        "year": "Year",
                        chosen: category_or_type,
                        "type_count": "Sub Count",
                        "total_count": "Total Count",
                        "min_date" : 'Year Start',
                        "max_date" : "Year End"
                    })\
                    .reset_index(drop=True)

        return result

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

    def most_watched_week(self, category_or_type, limit = 20, lower_range=None, upper_range=None):
        """
        Finds start and end of the week where the user watched the most (depending on video type)
        """

        chosen = "video_category" if category_or_type == "Category" else "video_type"

        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)

        df['time_stamp'] = df['time_stamp'].dt.normalize()

        df['first_day'] = df['time_stamp'] - df['time_stamp'].dt.weekday * pd.Timedelta(days=1)
        df['combined'] = df['first_day'].astype(str) + ' - ' +(df['first_day'] + pd.Timedelta(days=6)).astype(str)

        daily = df.groupby(['combined', chosen]).size().reset_index(name="type_count")

        daily["total_count"] = daily.groupby(['combined'])['type_count'].transform('sum')

        top_weeks = daily[['combined', 'total_count']].drop_duplicates().sort_values(["total_count", "combined"], ascending=False).head(limit)["combined"]

        result = (
            daily[daily["combined"].isin(top_weeks)]
            .sort_values(["total_count", "combined", "type_count"], ascending=False)
            .rename(columns={
                "combined": "Week",
                chosen: category_or_type,
                "type_count": "Sub Count",
                "total_count": "Total Count"
            })
            .reset_index(drop=True)
        )

        return result

    def time_of_the_day(self, lower_range=None, upper_range=None, video_type=None, video_category = None):
        """
        Total count for each of the hour
        """

        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)
        if video_type:
            df = df[df['video_type'] == video_type]

        if video_category:
            df = df[df['video_category'] == video_category]

        result = df.assign(hour = df['time_stamp'].dt.hour).groupby('hour', as_index = False).size()\
                .sort_values('size', ascending=False).rename(columns={'size' : 'Total Count'}).reset_index(drop = True)
        return result

    def weekday_vs_weekend(self, category_or_type, lower_range=None, upper_range=None):
        # average number of videos, reels, category, can find top categories of each

        time_query , params  = self.date_range_handler(lower_range, upper_range, as_dataframe=False)

        chosen = 'video_category' if category_or_type == 'Category' else 'video_type'

        sql_define_days = f"""
            select
                {chosen},
                sum(case when day_type = 'weekday' then avg else 0 end) as weekday_avg,
                sum(case when day_type = 'weekend' then avg else 0 end) as weekend_avg
            from (
                    select
                        day_type,
                        {chosen},
                        round(count(*) / (case when day_type = 'weekday' then 5 else 2 end), 2) as avg
                    from (
                            select
                                *,
                                case
                                    when weekday(time_stamp) < 5 THEN 'weekday'
                                    else 'weekend'
                                    end AS day_type
                            from watch_history
                            {time_query}
                        ) as t
                    group by day_type, {chosen}
                ) as t
            group by {chosen}
        """

        df = self.con.execute(sql_define_days, params).df().rename(columns = {'video_type' : 'Type', "video_category" : 'Category',  'weekday_avg' : 'Weekday Average', 'weekend_avg' : 'Weekend Average'})
        return df

    def binge_watch_detection(self, lower_range=None, upper_range=None):
        pass

    def streak_analysis(self, limit = 20, lower_range=None, upper_range=None):

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
                            {time_query}  
                        ) AS days
                ) AS t
            GROUP BY grouped
            ORDER BY streak DESC
        """

        df = self.con.execute(sql, params).df().rename(columns = {'streak_start' : 'Start', 'streak_end' : 'End', 'streak' : 'Total Days'})
        df.index = np.arange(1, len(df) + 1)
        return df.reset_index().head(limit)

    def video_length_preference(self, video_category = None, lower_range=None, upper_range=None):
        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)

        if video_category:
            df = df[df['video_category'] == video_category]

        df = df.groupby('video_type', as_index = False).size()\
                .rename(columns = {'video_type' : 'Type', 'size' : 'Total Count'})\
                .sort_values('Total Count', ascending = False)

        return df

    def video_length_trend_over_month(self, video_category = None):

        sql_category = ""
        params = []
        if video_category:
            sql_category+="where video_category = ?"
            params.append(video_category)

        sql = f"""
            select
                strftime(time_stamp, '%Y-%m') as Month,
                video_type,
                count(*) as video_type_month_total
            from watch_history
            {sql_category}
            group by month, video_type
            order by month
        """

        df = self.con.execute(sql, params).df().rename(columns = {'video_type' : 'Video Type', 'video_type_month_total' : 'Month Total'})

        pivoted = pd.pivot_table(df, index='Video Type', columns='Month', values='Month Total').reset_index()
        return pivoted

    def unavailable_videos(self, lower_range=None, upper_range=None):

        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)

        df = df[df['video_type'] == 'unavailable'][['video_name', 'video_type', 'channel_url', 'channel_name', 'time_stamp']]\
                .rename(columns = {'video_name' : 'Name',  'video_type' : 'Type', 'channel_name' : 'Channel Name', 'channel_url' : 'Channel URL', 'time_stamp' : 'Timestamp'})\
                .sort_values('Timestamp', ascending = False)

        df.index = np.arange(1, len(df) + 1)

        return df.reset_index()

    def first_last_videos_ever_watched(self, video_limit=20, video_category = None, video_type = None, first_or_last = True):
        """
        Finds the first ever video watched
        """

        df = self.table.copy()

        if video_type:
            df = df[df['video_type'] == video_type]

        if video_category:
            df = df[df['video_category'] == video_category]

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

    def random_date(self):
        self.con.execute("SELECT DISTINCT DATE(time_stamp) FROM watch_history ORDER BY random() LIMIT 1")
        return str(self.con.fetchone()[0])

    def random_day_discovery(self, category_or_type, date):
        sql = """
            SELECT video_name, video_url, video_type, video_category, time_stamp
            FROM watch_history
            WHERE time_stamp >= CAST(? AS DATE)
            AND time_stamp <  CAST(? AS DATE) + INTERVAL 1 DAY
            ORDER BY time_stamp ASC
        """
        df = self.con.execute(sql, (date, date)).df()\
            .rename(columns={'video_name': 'Name', 'video_url': 'URL', 'video_category': 'Category',
                            'video_type': 'Type', 'time_stamp': 'Timestamp'})

        pivoted = (
            pd.crosstab(df['Timestamp'].dt.hour, df[category_or_type])
            .reindex(range(24), fill_value=0)
            .rename_axis('Hour')
        )

        df.index = np.arange(1, len(df) + 1)
        return df.reset_index(), pivoted

    def the_longest_titled_video(self, video_limit=20, video_category = None, video_type=None, lower_range = None, upper_range = None):
        """
        Finds the longest titles video
        """

        df = self.date_range_handler(lower_range, upper_range, as_dataframe=True)

        if video_type:
            df = df[df['video_type'] == video_type]

        if video_category:
            df = df[df['video_category'] == video_category]

        df = df.assign(length_video = df['video_name'].str.len())[['video_name', 'video_url', 'video_type', 'length_video', 'time_stamp']]\
                .sort_values('length_video', ascending = False)\
                .rename(columns = {'video_name' : 'Name', 'video_url' : 'URL', 'length_video' : 'Title Length', 'time_stamp' : 'Timestamp'})

        df.index = np.arange(1, len(df) + 1)
        return df.reset_index().head(video_limit)

    def calendar_heatmap(self, year, month, video_category = None, video_type = None):

        month_order = [
            'January', 'February', 'March', 'April', 'May', 'June', 
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        df = self.table.copy()
        df = df[(df['time_stamp'].dt.year == year) & (df['time_stamp'].dt.month_name() == month)]

        if video_category:
            df = df[df['video_category'] == video_category]

        if video_type:
            df = df[df['video_type'] == video_type]

        if df.empty:
            return pd.DataFrame(0, index=pd.CategoricalIndex(day_order, categories=day_order, ordered=True),
                columns=pd.CategoricalIndex(month_order, categories=month_order, ordered=True)
            )

        df['Date'] = df['time_stamp'].dt.normalize()

        df = df.groupby('Date').size()

        dates = pd.date_range(start=df.index.min(), end=df.index.max())

        df = df.reindex(dates, fill_value=0).rename_axis('Date').reset_index(name='Total Count')

        df = df.assign(
            week_number = df['Date'].apply(lambda x : (x.day - 1)//7+1),
            day_name = pd.Categorical(df['Date'].dt.day_name(), categories=day_order, ordered=True),
        )

        pivot_df = df.pivot_table(
            index="day_name",
            columns="week_number",
            values="Total Count",
            aggfunc='sum',
            fill_value=0
        )

        return pivot_df

    def all_months(self, year):
        df = self.table.copy()
        df = df[df['time_stamp'].dt.year == year]
        df = df.assign(
            month_name = df['time_stamp'].dt.month_name(),
            month_number = df['time_stamp'].dt.month
            ).sort_values("month_number").drop_duplicates(subset = 'month_number')[['month_name']].reset_index(drop = True)
        return df['month_name'].to_list()