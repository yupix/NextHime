import asyncio
import json
from distutils.util import strtobool

import requests as requests
from discord.ext import commands, tasks

from NextHime import db_manager, logger, session, config
from src.modules.eew import EewSendChannel
from src.modules.embed_manager import EmbedManager
from src.sql.models.eew import EewChannel, Eew

logger = logger.getChild('cog.eew')


class EewCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=1)
    async def bot_eew_loop(self):
        url = "https://dev.narikakun.net/webapi/earthquake/post_data.json"
        try:
            result = requests.get(url).json()
            logger.debug(result)
        except json.decoder.JSONDecodeError:
            logger.error("eewの情報取得にてエラーが発生しました: コンテンツタイプがjsonではありません")
            return
        event_id = result["Head"]["EventID"]
        search_event_id = session.query(Eew).filter(Eew.event_id == event_id).first()
        if search_event_id is None:
            await db_manager.commit(Eew(event_id=event_id))
            eew_manager = EewSendChannel(self.bot, result)
            image_url = await eew_manager.get_nhk_image(result["Body"]["Earthquake"]["OriginTime"])
            search_eew_channel_list = session.query(EewChannel)
            for channel in search_eew_channel_list:
                logger.debug(f"{channel.channel_id}にEew情報を送信します")
                asyncio.ensure_future(
                    eew_manager.send(image_url, channel.channel_id)
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
