from bs4 import BeautifulSoup
from db_queries import QueryProcessor
import dateutil.parser

class HTML_Parser:

    def __init__(self, html_path):
        self.path = html_path
        self.html_content = self.html_reader()
        self.soup = BeautifulSoup(self.html_content, "lxml")
        self.history_list = self.html_parser()
        self.query = QueryProcessor()

    def html_reader(self):
        with open(self.path, "r", encoding="utf-8") as file:
            html_content = file.read()

        return html_content

    def extract_info(self, i):
        if i.find(string=lambda t: t and t.strip().startswith("Details:")):
            return None

        sub_content = i.find("div", "content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")

        # find the links (should be 2)
        matches = sub_content.find_all("a")

        if (len(matches)) < 2:
            return None

        # find the link, and title for both video and channel
        video_link = matches[0].get("href")
        video_name = matches[0].get_text(strip=True)
        channel_link = matches[1].get("href")
        channel_name = matches[1].get_text(strip=True)

        # the timestamp
        timestamp = list(sub_content.stripped_strings)[-1].replace("\u202f", " ")
        timestamp = dateutil.parser.parse(timestamp).strftime("%Y-%m-%d %H:%M:%S")

        if not self.query.video_authenticator(video_link):
            return None

        #general_list.append((video_link, video_name, channel_link, channel_name, timestamp))

        return (video_link, video_name, channel_link, channel_name, timestamp)

    def html_parser(self):
        general_list = []
        matches = list(self.soup.find_all("div", class_="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp"))
        SECTION_SIZE = 10

        for i in range(0, len(matches), SECTION_SIZE):
            section = matches[i:i+SECTION_SIZE]
            mapped = map(self.extract_info, section)
            result_list = list(filter(lambda x: x is not None, mapped))
            id_list = [video[0][-11:] for video in result_list]

            duration_list = self.query.find_duration_video(id_list)

            general_list.extend(result_list)

        return general_list