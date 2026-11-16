from queries.db_queries_duckdb import QueryProcessorDuck

class HTML_Processor:
    def __init__(self, history_list, db):
        self.history_list = history_list
        self.query = QueryProcessorDuck(db)
        self.query.insert_history(self.history_list)
