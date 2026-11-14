from html_parser import HTML_Parser
from html_processor import HTML_Processor
from db_queries import QueryProcessor
from db_queries_duckdb import QueryProcessorDuck
from database_connection_duckdb import DatabaseDuck
import os

path = os.path.join("data_folder", "small_chunk.html")

# Creating only one database
db = DatabaseDuck()
query = QueryProcessorDuck(db)

#parser = HTML_Parser(path)
#processor = HTML_Processor(parser.history_list, db)

print(query.random_day_discovery())