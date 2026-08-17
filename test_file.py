from html_parser import HTML_Parser
from html_processor import HTML_Processor
from db_queries import QueryProcessor
import os

path = os.path.join("data_folder", "watch-history.html")

#parser = HTML_Parser(path)
#processor = HTML_Processor(parser.history_list)

query = QueryProcessor()
print(query.random_day_discovery())
#query.find_duration_video(['8yqp-iOj220', 'Sr6urU4gC3I'])
#print(query.the_most_watched_channel())
#result = query.complex_function(video_type="reel", time="evening")
#print(result)
#query.find_duration_video('https://www.youtube.com/watch?v=z5sf0W5Dn_w')
