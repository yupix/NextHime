import json

import yaml
from bs4 import BeautifulSoup as bs4
import dataclasses
import requests as requests

from src.modules.embed_manager import EmbedManager

with open("src/language/ja/eew/system.yml", encoding="utf-8") as f:
    language = yaml.safe_load(f)


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
            'depth': language["info"]["run_depth"] % self.result["Body"]["Earthquake"]["Hypocenter"]["Depth"],
            'max_intensity': f"{self.result['Body']['Intensity']['Observation']['MaxInt']}".
            replace("+", f"{language['info']['intensity_strong']}").
            replace("-", f"{language['info']['intensity_weak']}"),
            'intensity_pref_list': intensity_pref_list
        }
        eew_info = EewInfo(**eew_list)
        print(json.dumps(eew_info.intensity_pref_list))
        ctx = self.bot.get_channel(channel_id)
        await EmbedManager(ctx).generate(
            embed_title=f'{language["info"]["eew_info"]}',
            embed_description=language["info"]["eew_headline"] % eew_info.headline,
            embed_content=[
                {'title': f'{language["word"]["epicenter"]}', 'value': f'{eew_info.epicenter}', 
                    'option': {'inline': 'True'}},
                {'title': f'{language["word"]["magnitude"]}', 'value': f'{eew_info.magnitude}', 
                    'option': {'inline': 'True'}},
                {'title': f'{language["word"]["depth"]}', 'value': f'{eew_info.depth}', 
                    'option': {'inline': 'True'}},
                {'title': f'{language["word"]["max_depth"]}', 'value': f'{eew_info.max_intensity}',
                    'option': {'inline': 'True'}}
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
                embed_title=f'{language["info"]["eew_info"]}',
                embed_description=f'{language["info"]["eew_headline"]}',
                embed_content=[
                    {'title': f'{language["word"]["epicenter"]}', 'value': f'{intensity_pref["Name"]}',
                        'option': {'inline': 'True'}},
                    {'title': f'{language["word"]["max_depth"]}', 'value': f'{eew_info.magnitude}',
                        'option': {'inline': 'True'}},
                    {'title': f'{language["word"]["surrounding_area"]}', 'value': f'{intensity_pref_area_city_list[:-1]}',
                        'option': {'inline': 'True'}},
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
