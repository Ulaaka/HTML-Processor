
from database_connection_duckdb import DatabaseDuck
from db_queries_duckdb import QueryProcessorDuck

db = DatabaseDuck()
query = QueryProcessorDuck(db)

"""parser  = HTML_Parser(os.path.join("data_folder", 'watch-history.html'))
processor = HTML_Processor(parser.history_list, db)"""
