import json
import tempfile

from discord.ext import commands, tasks

from NextHime import redis_conn, session, db_manager
from src.modules.NextHimeUtils import NextHimeUtils
from src.modules.embed_manager import EmbedManager
from src.modules.warframe_api import WarframeAPI
from src.modules.warframe_utils import WarframeFissure, WarframeChannels
from src.sql.models.WarframeFissure import WarframeFissuresChannel


class WarframeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=60)
    async def bot_warframe_loop(self):
        fissure_list = WarframeAPI().get_fissures().save_fissure_json(tempfile.gettempdir() + '/fissure_list.json', check=True)
        pipe = redis_conn.pipeline()
        send_channels = session.query(WarframeFissuresChannel).all()
        for fissure_dict in fissure_list:
            fissure = WarframeFissure(fissure_dict)
            get_old_fissures = pipe.get(f'fissure_{fissure.id}')
            if not get_old_fissures:
                pipe.set(f'fissure_{fissure.id}', json.dumps(fissure_dict))
                await WarframeChannels(self.bot, fissure).send_message(send_channels)

    @commands.group(name='warframe')
    async def warframe(self, ctx):
        await NextHimeUtils(self.bot, ctx).not_args_message()

    @warframe.group(name='fissure')
    async def fissure(self, ctx):
        await NextHimeUtils(self.bot, ctx).not_args_message()

    @fissure.command(name='setup')
    async def setup(self, ctx):
        await db_manager.commit(WarframeFissuresChannel(channel_id=ctx.channel.id))
        await EmbedManager(ctx).generate('セットアップに成功', mode='success').send()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot_warframe_loop.start()


def setup(bot):
    bot.add_cog(WarframeCog(bot))
