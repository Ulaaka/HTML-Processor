import duckdb

class DatabaseDuck:
    """
    Creates non-persistent database using duckdb
    """

    def __init__(self):

        """
        Constructor for database creation
        """

        self.con = duckdb.connect("watch_history.duckdb")
        self.con.execute("CREATE SEQUENCE IF NOT EXISTS seq_historyID START 1")
        self.con.execute("""
                CREATE TABLE IF NOT EXISTS watch_history (
                        historyID  INTEGER  PRIMARY KEY DEFAULT nextval('seq_historyID'),
                        video_url VARCHAR(255) NOT NULL,
                        video_name      VARCHAR(255) NOT NULL,
                        video_type VARCHAR(255) NOT NULL,
                        video_category VARCHAR(255) NOT NULL,
                        channel_url         VARCHAR(255) NOT NULL,
                        channel_name        VARCHAR(255) NOT NULL,
                        time_stamp          DATETIME,
                        UNIQUE (video_url, time_stamp)
                )
        """)