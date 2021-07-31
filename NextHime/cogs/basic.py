import datetime
import time
import traceback

from NextHime import logger, config, start_time
from NextHime.main import INITIAL_EXTENSIONS
from discord.ext import commands
from src.modules.embed_manager import EmbedManager


class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.channel.send(f"ping: {round(self.bot.latency * 1000)}ms")

    @commands.command()
    async def status(self, ctx):
        current_time = time.time()
        difference_time = int(round(current_time - start_time))
        uptime = str(datetime.timedelta(seconds=difference_time))
        await EmbedManager(ctx).generate(embed_title=f"{config.user}のステータス",
                                         embed_content=[{'title': '起動時間', 'value': f'{uptime}'}]).send()

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx):
        for cog in INITIAL_EXTENSIONS:
            try:
                self.bot.reload_extension(cog)
            except Exception:
                traceback.print_exc()
        logger.info("リロードに成功しました")
        await EmbedManager(ctx).generate(mode='succeed', embed_title="リロードに成功しました").send()

    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await EmbedManager(ctx).generate(mode='succeed', embed_title="エラー", embed_description="このコマンドはBotの所有者のみが実行できます")


def setup(bot):
    bot.add_cog(BasicCog(bot))
