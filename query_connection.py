
from database_connection_duckdb import DatabaseDuck
from db_queries_duckdb import QueryProcessorDuck
from html_parser import HTML_Parser
from html_processor import HTML_Processor

db = DatabaseDuck()

"""parser  = HTML_Parser(os.path.join("data_folder", 'watch-history.html'))
processor = HTML_Processor(parser.history_list, db)"""
query = QueryProcessorDuck(db)

