
from decouple import config
import requests, asyncio, aiohttp, re

class Requests:

    """
    Contains request functions
    """

    def __init__(self):
        """
        Constructor for urls
        """

        self.urls ={
            'video': 'https://www.googleapis.com/youtube/v3/videos',
            'category' : 'https://www.googleapis.com/youtube/v3/videoCategories',
            'region' : "https://www.googleapis.com/youtube/v3/i18nRegions"
        }

    async def find_duration_video(self, video_ids):
        """
        based on these links:
        https://dev.to/ashutoshsarangi/aiohttp-asyncio-vs-requests-comparing-python-http-libraries-46j9

        https://www.geeksforgeeks.org/python/asynchronous-http-requests-with-python/

        -- reduced time spent by approximately 20% on top of using batch id technique
        """
        sem = asyncio.Semaphore(10)

        async with aiohttp.ClientSession() as session:

            async def fetch_one(chunk):
                params = {
                    "part": "snippet,contentDetails",
                    "id": ",".join(chunk),
                    "regionCode": "GB",
                    "key": config('YOUTUBE_API'),
                }
                async with sem:
                    async with session.get(self.urls['video'], params=params) as response:
                        response.raise_for_status()

                        return await response.json()

            responses = await asyncio.gather(*(fetch_one(chunk) for chunk in [video_ids[i:i + 50] for i in range(0, len(video_ids), 50)]))

        result = {
            item["id"]: [
                self.duration_converter(item["contentDetails"]["duration"]),
                item["snippet"]["categoryId"],
            ]
            for data in responses
            for item in data.get("items", [])
        }

        return result

    def map_category_numbers(self):
        """
        Return dic containing category id corresponding to their names
        """
        param = {
            "part": "snippet",
            "regionCode": "GB",
            "key": config('YOUTUBE_API')
        }

        response = requests.get(self.urls['category'], params=param)
        data = response.json()

        return {
            item["id"]: item["snippet"]["title"]
            for item in data.get("items", [])
        }

    def regionCodes_search(self):
        """
        Returns ids of the regions
        """
        params = {
            "part": "snippet",
            "key": config('YOUTUBE_API')
        }
        response = requests.get(self.urls['region'], params=params)
        data = response.json()
        return [item["id"] for item in data["items"]]

    def duration_converter(self, duration):
        try:
            match = re.fullmatch(
                r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",
                duration
            )

            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)

            return hours * 3600 + minutes * 60 + seconds
        except:
            return 0