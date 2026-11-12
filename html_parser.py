from bs4 import BeautifulSoup
from db_queries import QueryProcessor
from requests import Requests
import dateutil.parser, concurrent.futures, asyncio, os, re

class HTML_Parser:

    def __init__(self, html_path):
        self.path = html_path
        self.soup = BeautifulSoup(self.html_reader(), "lxml")

        self.category_mapping = {
            '1': 'Film & Animation', 
            '2': 'Autos & Vehicles', 
            '10': 'Music', 
            '15': 'Pets & Animals', 
            '17': 'Sports', 
            '18': 'Short Movies', 
            '19': 'Travel & Events', 
            '20': 'Gaming', 
            '21': 'Videoblogging', 
            '22': 'People & Blogs', 
            '23': 'Comedy', 
            '24': 'Entertainment', 
            '25': 'News & Politics', 
            '26': 'Howto & Style', 
            '27': 'Education', 
            '28': 'Science & Technology',
            '30': 'Movies', 
            '31': 'Anime/Animation', 
            '32': 'Action/Adventure', 
            '33': 'Classics', 
            '34': 'Comedy', 
            '35': 'Documentary', 
            '36': 'Drama', 
            '37': 'Family', 
            '38': 'Foreign', 
            '39': 'Horror', 
            '40': 'Sci-Fi/Fantasy', 
            '41': 'Thriller', 
            '42': 'Shorts', 
            '43': 'Shows', 
            '44': 'Trailers'
        }

        self.region_codes_list = [
            'AE', 'BH', 'DZ', 'EG', 'IQ', 'JO', 'KW', 
            'LB', 'LY', 'MA', 'OM', 'QA', 'SA', 'TN', 
            'YE', 'AZ', 'BY', 'BG', 'BD', 'BA', 'CZ', 
            'DK', 'AT', 'CH', 'DE', 'GR', 'AU', 'BE', 
            'CA', 'GB', 'GH', 'IE', 'IL', 'IN', 'JM', 
            'KE', 'MT', 'NG', 'NZ', 'SG', 'UG', 'US', 
            'ZA', 'ZW', 'AR', 'BO', 'CL', 'CO', 'CR', 
            'DO', 'EC', 'ES', 'GT', 'HN', 'MX', 'NI', 
            'PA', 'PE', 'PR', 'PY', 'SV', 'UY', 'VE', 
            'EE', 'FI', 'PH', 'FR', 'SN', 'HR', 'HU', 
            'AM', 'ID', 'IS', 'IT', 'JP', 'GE', 'KZ', 
            'KR', 'LU', 'LA', 'LT', 'LV', 'MK', 'MY', 
            'NO', 'NP', 'NL', 'PL', 'BR', 'PT', 'MD', 
            'RO', 'RU', 'LK', 'SK', 'SI', 'ME', 'RS', 
            'SE', 'TZ', 'TH', 'TR', 'UA', 'PK', 'VN', 
            'HK', 'TW', 'CY', 'KH', 'LI', 'PG']

        self.history_list = self.html_parser()

    def html_reader(self):
        with open(self.path, "r", encoding="utf-8") as file:
            html_content = file.read()

        return html_content

    def html_parser(self):
        query = QueryProcessor()
        request = Requests()
        general_list = []
        matches = list(self.soup.find_all("div", class_="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp"))
        SECTION_SIZE = 40

        sections = [matches[i:i+SECTION_SIZE] for i in range(0, len(matches), SECTION_SIZE)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for result in list(executor.map(lambda section: self.section_parsing(section, request), sections)):
                general_list.extend(result)

        return general_list

    def section_parsing(self, section, request):

        result_list = self.extract_info(section)
        id_list = [video[0][-11:] for video in result_list]

        # skips unavailable videos
        # should really try to optimize pandas using vectorization, mapping, and numpy libs
        duration_list = asyncio.run(request.find_duration_video(id_list))
        key_set = set(duration_list.keys())
        for idx, i in enumerate(id_list):
            if i in key_set:
                video_type = self.define_type(duration_list[i][0])
                video_category = self.category_mapper(duration_list[i][1])
                result_list[idx][2:2] = [video_type, video_category]
            else:
                result_list[idx][2:2] = ["unavailable", "unavailable"]

        return tuple(result_list)

    def extract_info(self, section_list):
        return_list = []
        for i in section_list:

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

            if not self.video_authenticator(video_link):
                continue

            return_list.append([video_link, video_name, channel_link, channel_name, timestamp])
        return return_list

    def video_authenticator(self, url):
        match = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/([^/?#]+)", url)
        if match:
            if match.group(1) == "watch":
                return True

        return False

    def define_type(self, seconds):
        if seconds <= 180:
            return "reel"
        elif seconds == -1:
            return "unavailable video"
        else:
            return "video"

    def category_mapper(self, categoryID):
        """
        Maps the category id of video to its description

        input: category ID
        param: mapped description
        """
        try:
            return self.category_mapping[categoryID]
        except:
            return "could not be identified"


    def html_chunker(self, size = 1000000):
        # total size is 46230891
        chunk = str(self.soup)[: size]
        with open(os.path.join("data_folder", "small_chunk.html"), "w", encoding="utf-8") as f:
            f.write(chunk)

