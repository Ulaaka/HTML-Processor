
from database_connection import Database
from nltk.corpus import stopwords
from collections import defaultdict
import operator, re, requests
from decouple import config



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
        self.cursor = connection.cursor

        self.stop_words = set(stopwords.words('english'))


    def insert_history(self, history_list):
        sql = """INSERT IGNORE INTO watch_history (video_url, video_name, video_type, video_category, channel_url, channel_name, time_stamp) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
        self.cursor.executemany(sql, history_list)
        self.db.commit()


    def the_most_watched_channel(self):

        sql = "SELECT channel_name, channel_url, COUNT(*) AS count FROM watch_history GROUP BY channel_name, channel_url ORDER BY count DESC LIMIT 20"
        self.cursor.execute(sql)
        output = self.cursor.fetchall()
        return output if output else None

    def the_most_watched_videos(self):

        sql = "SELECT video_name, video_url, COUNT(*) AS count FROM watch_history GROUP BY video_name, video_url ORDER BY count DESC LIMIT 20"
        self.cursor.execute(sql)
        output = self.cursor.fetchall()
        return output if output else None


    def the_most_repeated_words(self):

        sql = "SELECT DISTINCT video_name FROM watch_history"
        self.cursor.execute(sql)
        output = self.cursor.fetchall()

        words_dic = defaultdict(int)
        for row in output:
            video_name = row[0]
            for word in video_name.split():
                if word not in self.stop_words:
                    words_dic[word] +=1

        sorted_x = sorted(words_dic.items(), key=operator.itemgetter(1))

        return sorted_x


    def return_by_name_combination(self, sentence):
        words = sentence.split()

        sql = "SELECT DISTINCT video_name, video_url FROM watch_history WHERE " + " AND ".join(["video_name LIKE %s"] * len(words))

        params = [f"%{w}%" for w in words]

        self.cursor.execute(sql, params)

        output = self.cursor.fetchall()

        return output


    def the_busiest_day(self, lower_range=None, upper_range=None, limit=None):
        # needs to be adjusted after updating database column

        sql_main = "SELECT COUNT(*) as count, DATE(time_stamp) as day from watch_history"

        if lower_range and not upper_range:
            sql_main += f"WHERE time_stamp >= {lower_range}"
        if not lower_range and upper_range:
            sql_main += f"WHERE time_stamp >= {upper_range}"

        if lower_range and upper_range:
            sql_main += f"WHERE time_stamp >= {lower_range} AND time_stamp <= {upper_range}"

        sql_end = " GROUP BY day ORDER BY count DESC"
        sql_main+= sql_end

        if limit:
            sql_main+=f" LIMIT {limit}"

        self.cursor.execute(sql_main)

        output = self.cursor.fetchall()

        return output


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



    def complex_function(self, video_type=None, time=None, lower_range=None, upper_range=None):
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

        output = self.cursor.fetchall()

        return output

    def weekly_trend(self, trend_number=None, video_type=None):
        pass

    def monthly_trend(self, trend_number=None, video_type=None):
        pass

    def seasonal_trend(self, season_specify=None, video_type=None):
        pass

    def yearly_trend(self, video_type=None):
        pass

    def binge_watch_detection(self, lower_range=None, upper_range=None):
        pass

    def streak_analysis(self, with_or_without="with", lower_range=None, upper_range=None):
        pass

    def video_length_preference(self, lower_range=None, upper_range=None):
        pass

    def unavailable_videos(self,video_type=None, lower_range=None, upper_range=None):
        pass

    def first_video_ever_watched(self):
        pass

    def last_video_ever_watched(self):
        pass

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
        pass

    def the_longest_titled_video(self, video_type=None, video_limit=None):
        limit = 10
        if video_limit:
            limit = video_limit

        where_query = ""
        if video_type:
            where_query = f" WHERE video_type = {video_type} "

        sql = f"SELECT video_name, video_url, video_type, LENGTH(video_name) as length_video FROM watch_history " + where_query + f"ORDER BY length_video DESC LIMIT {limit} "
        self.cursor.execute(sql)
        output = self.cursor.fetchall()
        return output if output else None

    def video_authenticator(self, url):
        match = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/([^/?#]+)", url)
        if match:
            if match.group(1) == "watch":
                return True

        return False

    def duration_converter(self, duration):
        try:
            match = re.fullmatch(
                r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",
                duration
            )

            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)

            return hours * 3600 + minutes * 60 + seconds
        except:
            return 0

    def define_type(self, seconds):
        if seconds <= 180:
            return "reel"
        elif seconds == -1:
            return "unavailable video"
        else:
            return "video"

    # returns seconds of the video
    def find_duration_video(self, video_id_list):
        API_KEY = config('YOUTUBE_API')

        retrieval_url = 'https://www.googleapis.com/youtube/v3/videos'
        param = {
            "part": "snippet, contentDetails",
            "id": ",".join(video_id_list),
            "regionCode" : "GB",
            "key": API_KEY
        }

        response = requests.get(retrieval_url, params=param)
        data = response.json()
        # converted duration list, category ID
        return {
            str(item["id"]): [self.duration_converter(item["contentDetails"]["duration"]), item["snippet"]["categoryId"]]
            for item in data.get("items", [])
        }

    def map_category_numbers(self):
        API_KEY = config('YOUTUBE_API')
        retrieval_url = 'https://www.googleapis.com/youtube/v3/videoCategories'
        param = {
            "part": "snippet",
            "regionCode": "GB",
            "key": API_KEY
        }

        response = requests.get(retrieval_url, params=param)
        data = response.json()

        return {
            item["id"]: item["snippet"]["title"]
            for item in data.get("items", [])
        }

    def regionCodes_search(self):
        API_KEY = config('YOUTUBE_API')
        retrieval_url = "https://www.googleapis.com/youtube/v3/i18nRegions"
        params = {
            "part": "snippet",
            "key": API_KEY
        }
        response = requests.get(retrieval_url, params=params)
        data = response.json()
        return [item["id"] for item in data["items"]]