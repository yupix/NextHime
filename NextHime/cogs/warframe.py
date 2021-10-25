import json
import tempfile

from disnake.ext import commands, tasks

from NextHime import config, db_manager, redis_conn, session
from src.modules.embed_manager import EmbedManager
from src.modules.warframe.warframe_api import WarframeAPI
from src.modules.warframe.warframe_utils import WarframeChannels, WarframeFissure
from src.sql.models.WarframeFissure import WarframeFissuresChannel
from src.sql.models.guild import Guilds


class WarframeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=60)
    async def bot_warframe_loop(self):
        fissure_list = WarframeAPI().get_fissures().save_fissure_json(tempfile.gettempdir() + '/fissure_list.json', check=True)
        send_channels = session.query(WarframeFissuresChannel).all()
        for fissure_dict in fissure_list:
            fissure = WarframeFissure(fissure_dict)
            get_old_fissures = redis_conn.get(f'fissure_{fissure.id}')
            if not get_old_fissures:
                await WarframeChannels(self.bot, fissure).send_message(send_channels)
                redis_conn.set(f'fissure_{fissure.id}', json.dumps(fissure_dict))

    @commands.slash_command(name='warframe', guild_ids=config.options.slash_command_guild)
    async def warframe(self, ctx):
        pass

    @warframe.sub_command_group(name='fissure')
    async def fissure(self, ctx):
        pass

    @fissure.sub_command(name='setup', description='亀裂の情報をお知らせするチャンネルを指定します')
    async def setup(self, ctx):
        await db_manager.commit(Guilds(server_id=ctx.guild.id, region=ctx.guild.region[0]))
        await db_manager.commit(WarframeFissuresChannel(channel_id=ctx.channel.id, region=ctx.guild.region[0]))
        await ctx.response.send_message(embed=EmbedManager(ctx).generate('セットアップに成功', mode='success').embed)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot_warframe_loop.start()


def setup(bot):
    bot.add_cog(WarframeCog(bot))
