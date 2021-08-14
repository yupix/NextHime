import json
import requests

from bs4 import BeautifulSoup as bs4


class EewAPI:
    def __init__(self):
        self.result = None
        self.eew = None

    def fetch_api(self, url: str) -> requests.models.Response:
        self.result = requests.get(url)
        return self.result

    def get_eew(self) -> 'EewAPI':
        url = "https://dev.narikakun.net/webapi/earthquake/post_data.json"
        try:
            self.eew = self.fetch_api(url).json()
        except json.decoder.JSONDecodeError:
            raise json.decoder.JSONDecodeError
        return self

    async def get_nhk_image(self):
        base_url = "https://www3.nhk.or.jp/sokuho/jishin/data/JishinReport.xml"
        origin_time = self.eew["Body"]["Earthquake"]["OriginTime"]
        res = requests.get(base_url)
        soup = bs4(res.content, "lxml-xml")
        origin_time = origin_time.split(" ")
        time = origin_time[1].split(":")
        date = origin_time[0].split("-")
        details_url = (
            soup.find("record", {"date": f"{date[0]}年{date[1]}月{date[2]}日"})
                .find("item", {"time": f"{time[0]}時{time[1]}分ごろ"})
                .get("url")
        )
        details_res = requests.get(details_url)
        details_soup = bs4(details_res.content, "lxml-xml")
        image_url = (
            "https://www3.nhk.or.jp/sokuho/jishin/"
            + details_soup.find("Root").find("Earthquake").find("Detail").get_text()
        )
        return image_url
