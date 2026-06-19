from bs4 import BeautifulSoup
import dateutil.parser

class HTML_Parser:

    def __init__(self, html_path):
        self.path = html_path
        self.html_content = self.html_reader()
        self.soup = BeautifulSoup(self.html_content, "lxml")
        self.history_list = self.html_parser()


    def html_reader(self):
        with open(self.path, "r", encoding="utf-8") as file:
            html_content = file.read()

        return html_content

    def html_parser(self):

        general_list = []
        matches = self.soup.find_all("div", class_="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp")
        for  i in matches:

            # skip the ads
            if i.find(string=lambda t: t and t.strip().startswith("Details:")):
                continue

            sub_content = i.find("div", "content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")
            # find the links (should be 2)
            matches = sub_content.find_all("a")

            # skip abnormalities
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

            general_list.append((video_link, video_name, channel_link, channel_name, timestamp))
        return general_list

