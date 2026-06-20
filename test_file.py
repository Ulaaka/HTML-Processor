from html_parser import HTML_Parser
from html_processor import HTML_Processor
from db_queries import QueryProcessor
import os

path = os.path.join("data_folder", "watch-history.html")

#parser = HTML_Parser(path)
#processor = HTML_Processor(parser.history_list)

query = QueryProcessor()
print(query.the_most_watched_videos())