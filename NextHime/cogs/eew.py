import asyncio
import json
from distutils.util import strtobool

import discord
import requests as requests

from bs4 import BeautifulSoup as bs4
from discord.ext import commands, tasks
from NextHime import db_manager, logger, session, config
from src.modules.embed_manager import EmbedManager
from src.sql.models.eew import EewChannel, Eew


class EewSendChannel:
    def __init__(self, bot):
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

    async def main_title_send(self, channel, result, image_url):
        channel = self.bot.get_channel(channel.channel_id)
        color = int(
            self.color_list[
                f"{result['Body']['Intensity']['Observation']['MaxInt']}".replace(
                    "-", ""
                ).replace("+", "")
            ],
            base=16,
        )
        icon_url = "https://s3.akarinext.org/assets/*/NextHime/kishoutyou.jpg"
        embed = discord.Embed(
            color=color,
            title=f"{result['Head']['InfoKind']}",
            description="地域に関しては今後のメッセージを閲覧ください",
        )
        embed.add_field(
            name=f"震央",
            value=f"{result['Body']['Earthquake']['Hypocenter']['Name']}",
            inline=True,
        )
        embed.add_field(
            name=f"マグニチュード",
            value=f"M{result['Body']['Earthquake']['Magnitude']}",
            inline=True,
        )
        embed.add_field(
            name=f"深さ",
            value=f"約{result['Body']['Earthquake']['Hypocenter']['Depth']}km",
            inline=True,
        )
        embed.add_field(
            name=f"最大震度",
            value=f"{result['Body']['Intensity']['Observation']['MaxInt']}".replace(
                "+", "強"
            ).replace("-", "弱"),
            inline=True,
        )
        embed.set_image(url=f"{image_url}")
        embed.set_thumbnail(url=icon_url)
        embed.set_footer(
            text=f"{result['Body']['Earthquake']['OriginTime']} 情報元: {result['Control']['PublishingOffice']}"
        )
        await channel.send(embed=embed)
        for intensity_pref in result["Body"]["Intensity"]["Observation"]["Pref"]:
            await self.sub_title_send(intensity_pref, result, channel)

    async def sub_title_send(self, intensity_pref, result, channel):
        intensity_color = int(
            self.color_list[
                f"{intensity_pref['MaxInt']}".replace("-", "").replace("+", "")
            ],
            base=16,
        )
        intensity_embed = discord.Embed(
            color=intensity_color, title=f"{result['Head']['InfoKind']}"
        )
        intensity_embed.add_field(
            name=f"震央", value=f"{intensity_pref['Name']}", inline=True
        )
        intensity_embed.add_field(
            name=f"最大深度",
            value=f"{intensity_pref['MaxInt']}".replace("+", "強").replace("-", "弱"),
            inline=True,
        )
        intensity_pref_area_city_list = ""
        for intensity_pref_area in intensity_pref["Area"]:
            for intensity_pref_area_city in intensity_pref_area["City"]:
                intensity_pref_area_city_list += f"{intensity_pref_area_city['Name']}, "
        intensity_embed.add_field(
            name=f"周辺地域", value=f"{intensity_pref_area_city_list[:-1]}", inline=True
        )
        intensity_embed.set_footer(
            text=f"{result['Head']['ReportDateTime']} 情報元: {result['Control']['PublishingOffice']}"
        )
        await channel.send(embed=intensity_embed)


class EewCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=1)
    async def bot_eew_loop(self):
        url = "https://dev.narikakun.net/webapi/earthquake/post_data.json"
        try:
            result = requests.get(url).json()
        except json.decoder.JSONDecodeError:
            logger.error("eewの情報取得にてエラーが発生しました: コンテンツタイプがjsonではありません")
            return
        event_id = result["Head"]["EventID"]
        search_event_id = session.query(Eew).filter(Eew.event_id == event_id).first()
        if search_event_id is None:
            await db_manager.commit(Eew(event_id=event_id))
            eew_manager = EewSendChannel(self.bot)
            image_url = await eew_manager.get_nhk_image(
                result["Body"]["Earthquake"]["OriginTime"]
            )
            search_eew_channel_list = session.query(EewChannel)
            for channel in search_eew_channel_list:
                logger.debug(f"{channel.channel_id}にEew情報を送信します")
                asyncio.ensure_future(
                    eew_manager.main_title_send(channel, result, image_url)
                )

    @commands.group()
    async def eew(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("このコマンドには引数が必要です")

    @eew.command()
    async def setup(self, ctx):
        await db_manager.commit(EewChannel(channel_id=ctx.channel.id))
        await EmbedManager(ctx=ctx).generate('成功', f'<#{ctx.channel.id}>を送信チャンネルとして登録しました', 'success').send()

    @commands.Cog.listener()
    async def on_ready(self):
        if bool(strtobool(config.eew_use)) is True:
            await self.bot_eew_loop.start()


def setup(bot):
    bot.add_cog(EewCog(bot))
