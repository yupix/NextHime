import traceback

from NextHime import logger
from NextHime.main import INITIAL_EXTENSIONS
from discord.ext import commands
from src.modules.embed_manager import EmbedManager


class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.channel.send(f"ping: {round(self.bot.latency * 1000)}ms")

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
