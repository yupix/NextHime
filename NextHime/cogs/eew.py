import asyncio
import json
from distutils.util import strtobool

from disnake.ext import commands, tasks

from NextHime import config, db_manager, redis_conn, session
from src.modules.eew import EewAPI
from src.modules.eew.eew_utils import EewInfo, EewMessage
from src.modules.embed_manager import EmbedManager
from src.sql.models.eew import EewChannel


class EewCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=1)
    async def bot_eew_loop(self):
        api_result = EewAPI().get_eew(True)
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

    @commands.slash_command(name='eew')
    async def eew(self, ctx, guild_ids=config.options.slash_command_guild):
        pass

    @eew.sub_command(name='setup', description='地震情報を送信するチャンネルを設定します')
    async def setup(self, ctx, channel_id: int = None):
        """
        Parameters
        ----------
        channel_id : int
            登録したいチャンネルID
        """
        if channel_id is None:
            channel_id = ctx.channel.id

        await db_manager.commit(EewChannel(channel_id=channel_id))
        await ctx.response.send_message(embed=EmbedManager(ctx=ctx).generate('成功', f'<#{channel_id}>を送信チャンネルとして登録しました',
                                                                             'success').embed)

    @commands.Cog.listener()
    async def on_ready(self):
        if config.eew.use is True:
            await self.bot_eew_loop.start()


def setup(bot):
    bot.add_cog(EewCog(bot))
