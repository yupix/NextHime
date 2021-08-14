import asyncio
import json
from distutils.util import strtobool
from src.modules.eew.eew_utils import EewMessage, EewInfo

from discord.ext import commands, tasks

from NextHime import db_manager, logger, session, config, redis_conn
from src.modules.eew import EewAPI
from src.modules.embed_manager import EmbedManager
from src.sql.models.eew import EewChannel

logger = logger.getChild('cog.eew')


class EewCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=1)
    async def bot_eew_loop(self):
        api_result = EewAPI().get_eew()
        eew = api_result.eew
        get_old_eew = redis_conn.get(f'eew_{eew["Head"]["EventID"]}')
        intensity_pref_list = []
        for intensity_pref in eew["Body"]["Intensity"]["Observation"]["Pref"]:
            intensity_pref_list.append(intensity_pref)
        if not get_old_eew:
            search_eew_channel_list = session.query(EewChannel)
            image_url = await api_result.get_nhk_image()
            for channel in search_eew_channel_list:
                asyncio.ensure_future(EewMessage(self.bot, EewInfo(eew, intensity_pref_list), channel=channel.channel_id).
                                      create_main_embed(image_url).send())
            redis_conn.set(f'eew_{eew["Head"]["EventID"]}', json.dumps(eew), ex=10)
        else:
            redis_conn.set(f'eew_{eew["Head"]["EventID"]}', json.dumps(eew), ex=10)


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
        if bool(strtobool(config.eew.use)) is True:
            await self.bot_eew_loop.start()


def setup(bot):
    bot.add_cog(EewCog(bot))
