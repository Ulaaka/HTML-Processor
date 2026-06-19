from database_connection import Database
from db_queries import QueryProcessor
class HTML_Processor:
    def __init__(self, history_list):
        self.history_list = history_list
        self.query = QueryProcessor()
        self.query.insert_history(self.history_list)
