import asyncio
from src.modules.embed_manager import EmbedManager
import i18n

from discord.ext import commands


class EewInfo(object):
    def __init__(self, result, intensity_pref_list, locale: str = 'ja'):
        self.headline: str = f'{result["Head"]["Headline"]}'
        self.epicenter: str = f'{result["Body"]["Earthquake"]["Hypocenter"]["Name"]}'
        self.magnitude: str = f'M{result["Body"]["Earthquake"]["Magnitude"]}'
        self.depth: str = i18n.t('message.eew.word.run_depth', locale=locale) % result["Body"]["Earthquake"]["Hypocenter"][
            "Depth"],
        self.intensity = result['Body']['Intensity']['Observation']['MaxInt']
        self.max_intensity: str = f"{result['Body']['Intensity']['Observation']['MaxInt']}".replace(
            "+", i18n.t('message.eew.intensity_strong', locale=locale)).replace(
            "-", i18n.t('message.eew.intensity_weak', locale=locale))
        self.intensity_pref_list: list = intensity_pref_list


class EewMessage(object):
    def __init__(self, bot: commands.Bot, eew: EewInfo, locale: str = 'ja', channel: int = None):
        self.eew: EewInfo = eew
        self.bot: commands.Bot = bot
        self.locale: str = locale
        self.embed = None
        self.color_list = {
            "1": "0x859fff",
            "2": "0x90caf9",
            "3": "0x66bb6a",
            "4": "0xffb74d",
            "5": "0xf44336",
            "6": "b53128",
            "7": "0x781f19",
        }
        self.ctx = self.bot.get_channel(channel)

    def get_color(self, intensity: str):
        color = int(self.color_list[f"{intensity}".replace("-", "").replace("+", "")], base=16, )
        return color

    def create_main_embed(self, image_url: str):
        self.embed = EmbedManager(ctx=self.ctx).generate(
            embed_title=i18n.t('message.eew.word.info', locale=self.locale),
            embed_description=i18n.t('message.eew.word.headline', locale=self.locale) % self.eew.headline,
            embed_content=[
                {'title': i18n.t('message.eew.word.epicenter', locale=self.locale), 'value': f'{self.eew.epicenter}',
                 'option': {'inline': 'True'}},
                {'title': i18n.t('message.eew.word.magnitude', locale=self.locale), 'value': f'{self.eew.magnitude}',
                 'option': {'inline': 'True'}},
                {'title': i18n.t('message.eew.word.depth', locale=self.locale), 'value': f'{self.eew.depth}',
                 'option': {'inline': 'True'}},
                {'title': i18n.t('message.eew.word.max_depth', locale=self.locale), 'value': f'{self.eew.max_intensity}',
                 'option': {'inline': 'True'}}
            ],
            color=self.get_color(self.eew.intensity),
            image=image_url
        )
        return self

    async def create_sub_embed(self):
        for intensity_pref in self.eew.intensity_pref_list:
            intensity_pref_area_city_list = ''
            color = self.get_color(intensity_pref['MaxInt'])
            for intensity_pref_area in intensity_pref["Area"]:
                for intensity_pref_area_city in intensity_pref_area["City"]:
                    intensity_pref_area_city_list += f"{intensity_pref_area_city['Name']}, "
            await EmbedManager(self.ctx).generate(
                embed_title=i18n.t('message.eew.word.info', locale=self.locale),
                embed_content=[
                    {'title': i18n.t('message.eew.word.epicenter', locale=self.locale), 'value': f'{intensity_pref["Name"]}',
                        'option': {'inline': 'True'}},
                    {'title': i18n.t('message.eew.word.max_depth', locale=self.locale), 'value': f'{self.eew.magnitude}',
                        'option': {'inline': 'True'}},
                    {'title': i18n.t('message.eew.word.surrounding_area', locale=self.locale), 'value': f'{intensity_pref_area_city_list[:-1]}',
                        'option': {'inline': 'True'}},
                ],
                color=color).send()
        return self

    async def send(self):
        asyncio.ensure_future(self.embed.send())
        await self.create_sub_embed()
