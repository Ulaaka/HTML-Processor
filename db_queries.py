
from database_connection import Database

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

    def insert_history(self, history_list):
        sql = """INSERT IGNORE INTO watch_history (video_url, video_name, channel_url, channel_name, time_stamp) VALUES (%s,%s,%s,%s,%s)"""
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
