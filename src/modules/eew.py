import json

from bs4 import BeautifulSoup as bs4
import dataclasses
import requests as requests

from src.modules.embed_manager import EmbedManager


@dataclasses.dataclass
class EewInfo:
    headline: list
    epicenter: str
    magnitude: str
    depth: str
    max_intensity: int
    intensity_pref_list: list


class EewSendChannel:
    def __init__(self, bot, result):
        self.bot = bot
        self.color_list = {
            "1": "0x859fff",
            "2": "0x90caf9",
            "3": "0x66bb6a",
            "4": "0xffb74d",
            "5": "0xf44336",
            "6": "b53128",
            "7": "0x781f19",
        }
        self.result = result

    async def get_color(self, intensity: str):
        color = int(
            self.color_list[
                f"{intensity}".replace(
                    "-", ""
                ).replace("+", "")
            ],
            base=16,
        )
        return color

    async def send(self, image: str, channel_id: str):
        color = await self.get_color(self.result['Body']['Intensity']['Observation']['MaxInt'])
        intensity_pref_list = []
        for intensity_pref in self.result["Body"]["Intensity"]["Observation"]["Pref"]:
            intensity_pref_list.append(intensity_pref)
        eew_list = {
            'headline': f'{self.result["Head"]["Headline"]}',
            'epicenter': f'{self.result["Body"]["Earthquake"]["Hypocenter"]["Name"]}',
            'magnitude': f'M{self.result["Body"]["Earthquake"]["Magnitude"]}',
            'depth': f'約{self.result["Body"]["Earthquake"]["Hypocenter"]["Depth"]}km',
            'max_intensity': f"{self.result['Body']['Intensity']['Observation']['MaxInt']}".replace("+", "強").replace("-",
                                                                                                                      "弱"),
            'intensity_pref_list': intensity_pref_list
        }
        eew_info = EewInfo(**eew_list)
        print(json.dumps(eew_info.intensity_pref_list))
        ctx = self.bot.get_channel(channel_id)
        await EmbedManager(ctx).generate(
            embed_title='地震情報',
            embed_description=f'{eew_info.headline}地域に関しては今後のメッセージを閲覧ください',
            embed_content=[
                {'title': '震央', 'value': f'{eew_info.epicenter}', 'option': {'inline': 'True'}},
                {'title': 'マグニチュード', 'value': f'{eew_info.magnitude}', 'option': {'inline': 'True'}},
                {'title': '深さ', 'value': f'{eew_info.depth}', 'option': {'inline': 'True'}},
                {'title': '最大震度', 'value': f'{eew_info.max_intensity}', 'option': {'inline': 'True'}}
            ],
            color=color,
            image=image
        ).send()
        for intensity_pref in eew_info.intensity_pref_list:
            intensity_pref_area_city_list = ''
            color = await self.get_color(intensity_pref['MaxInt'])
            for intensity_pref_area in intensity_pref["Area"]:
                for intensity_pref_area_city in intensity_pref_area["City"]:
                    intensity_pref_area_city_list += f"{intensity_pref_area_city['Name']}, "
            await EmbedManager(ctx).generate(
                embed_title='地震情報',
                embed_description='地域に関しては今後のメッセージを閲覧ください',
                embed_content=[
                    {'title': '震央', 'value': f'{intensity_pref["Name"]}', 'option': {'inline': 'True'}},
                    {'title': '最大深度', 'value': f'{eew_info.magnitude}', 'option': {'inline': 'True'}},
                    {'title': '周辺地域', 'value': f'{intensity_pref_area_city_list[:-1]}', 'option': {'inline': 'True'}},
                ],
                color=color).send()

    async def get_nhk_image(self, origin_time):
        base_url = "https://www3.nhk.or.jp/sokuho/jishin/data/JishinReport.xml"
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
