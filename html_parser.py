from bs4 import BeautifulSoup
from db_queries import QueryProcessor
import dateutil.parser
import concurrent.futures

class HTML_Parser:

    def __init__(self, html_path):
        self.path = html_path
        self.soup = BeautifulSoup(self.html_reader(), "lxml")
        self.history_list = self.html_parser()

    def html_reader(self):
        with open(self.path, "r", encoding="utf-8") as file:
            html_content = file.read()

        return html_content

    def extract_info(self, section_list, query):
        return_list = []
        for i in section_list:

            # could be quite slow tho
            if i.find(string=lambda t: t and t.strip().startswith("Details:")):
                continue

            sub_content = i.find("div", "content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")

            # find the links (should be 2)
            matches = sub_content.find_all("a")

            if (len(matches)) < 2:
                continue

            # find the link, and title for both video and channel
            video_link = matches[0].get("href")
            video_name = matches[0].get_text(strip=True)
            channel_link = matches[1].get("href")
            channel_name = matches[1].get_text(strip=True)

            # the timestamp
            timestamp = list(sub_content.stripped_strings)[-1].replace("\u202f", " ")
            timestamp = dateutil.parser.parse(timestamp).strftime("%Y-%m-%d %H:%M:%S")

            if not query.video_authenticator(video_link):
                continue

            return_list.append([video_link, video_name, channel_link, channel_name, timestamp])
        return return_list


    def category_mapper(self, categoryID, query):
        try:
            return query.category_mapping(categoryID)
        except:
            return "could not be identified"


    def section_parsing(self, section, query):
        result_list = self.extract_info(section, query)
        id_list = [video[0][-11:] for video in result_list]

        # skips unavailable videos
        duration_list = query.find_duration_video(id_list)
        key_set = set(duration_list.keys())
        for idx, i in enumerate(id_list):
            if i in key_set:
                result_list[idx][2:2] = [query.define_type(duration_list[i][0]), self.category_mapper(duration_list[i][1])]
            else:
                result_list[idx][2:2] = ["unavailable", "unavailable"]

        return tuple(result_list)

    def html_parser(self):
        query = QueryProcessor()
        general_list = []
        matches = list(self.soup.find_all("div", class_="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp"))
        SECTION_SIZE = 40

        sections = [matches[i:i+SECTION_SIZE] for i in range(0, len(matches), SECTION_SIZE)]

        # threads for execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for result in list(executor.map(lambda section: self.section_parsing(section, query), sections)):
                general_list.extend(result)

        return general_list