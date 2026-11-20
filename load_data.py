import os
from html_parser import HTML_Parser
from html_processor import HTML_Processor
from queries.query_connection import db

# Use the name of your html instead of watch-history.html
parser = HTML_Parser(os.path.join("data_folder", "watch-history.html"))
HTML_Processor(parser.history_list, db)