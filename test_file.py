from html_parser import HTML_Parser
from html_processor import HTML_Processor
from db_queries import QueryProcessor
import os

path = os.path.join("data_folder", "watch-history.html")

parser = HTML_Parser(path)
processor = HTML_Processor(parser.history_list)

#query = QueryProcessor()
#query.find_duration_video('https://www.youtube.com/watch?v=z5sf0W5Dn_w')
