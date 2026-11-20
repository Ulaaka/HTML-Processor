import os
from html_parser import HTML_Parser
from html_processor import HTML_Processor
from queries.query_connection import db

parser = HTML_Parser(os.path.join("data_folder", "watch-history.html"))
HTML_Processor(parser.history_list, db)