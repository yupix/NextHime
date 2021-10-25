import datetime
import random
import time
import traceback
from enum import Enum

import i18n
from disnake import Interaction
from disnake.ext import commands
from loguru import logger

from NextHime import config, db_manager, start_time
from NextHime.main import INITIAL_EXTENSIONS
from src.modules.embed_manager import EmbedManager
from src.modules.translator import translator
from src.sql.models.user import Users


class Language(str, Enum):
    Japan = 'ja'
    English = 'en'


class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='ping', description='Botのpingを測定します', guild_ids=config.options.slash_command_guild)
    async def ping(self, ctx):
        await ctx.response.send_message(f"ping: {round(self.bot.latency * 1000)}ms")

    @commands.slash_command(name='status', description='Botのステータスを表示します', guild_ids=config.options.slash_command_guild)
    async def status(self, ctx):
        current_time = time.time()
        difference_time = int(round(current_time - start_time))
        uptime = str(datetime.timedelta(seconds=difference_time))
        await ctx.response.send_message(embed=EmbedManager(ctx).generate(embed_title=f"{config.bot.name}のステータス",
                                                                         embed_content=[
                                                                             {'title': '起動時間', 'value': f'{uptime}'}]).embed)

    @commands.slash_command(name='reload', description='Botをリロードします。 ※管理者のみ', guild_ids=config.options.slash_command_guild)
    @commands.is_owner()
    async def reload(self, ctx):
        for cog in INITIAL_EXTENSIONS:
            try:
                self.bot.reload_extension(cog)
            except Exception:
                traceback.print_exc()
        logger.info(i18n.t('message.system.reloadSuccess', locale='ja'))
        await ctx.response.send_message(embed=EmbedManager(ctx).generate(mode='succeed', embed_title=i18n.t(
            'message.system.reloadSuccess', locale='ja')).embed)
        # await ctx.response.send_message

    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await EmbedManager(ctx).generate(mode='succeed', embed_title="エラー",
                                             embed_description="このコマンドはBotの所有者のみが実行できます").send()

    @commands.slash_command(name='user', guild_ids=config.options.slash_command_guild)
    async def user(self, ctx):
        pass

    @user.sub_command(name='profile')
    async def user_profile(self, ctx):
        await ctx.response.send_message(f'{ctx.author.name}')

    @user.sub_command_group(name='locale')
    async def locale(self, ctx):
        pass

    @locale.sub_command(name="set", description='Botで使用したい言語を変更します')
    async def set(self, ctx, language: Language):
        await db_manager.commit(Users(user_id=ctx.author.id, locale=language))
        await ctx.response.send_message(embed=EmbedManager(ctx).generate(
            mode='succeed',
            embed_title=i18n.t(
                'message.locale.ChangeSuccessTitle',
                locale=language)
        ).embed)

    @commands.slash_command(name="random", description='1から100までのランダムな数値を生成します。オプションで最小/最大値を変更できます',
                            guild_ids=config.options.slash_command_guild)
    async def random(self, ctx, min_int: int = 1, max_int: int = 10):
        """

        Parameters
        ----------
        min_int : int
            最小値
        max_int : int
            最大値
        """
        await ctx.response.send_message(random.randint(min_int, max_int))

    @commands.slash_command(name='translate', description='与えられた文章を翻訳します', guild_ids=config.options.slash_command_guild)
    async def translate(self, ctx: Interaction, content: str, from_lang: str = 'en', to_lang: str = 'ja'):
        """

        Parameters
        ----------
        content: str
            翻訳する文章
        from_lang: str, default=en
            元の言語
        to_lang: str, default=ja
        """
        await ctx.response.send_message(translator(content, from_lang, to_lang))


def setup(bot):
    bot.add_cog(BasicCog(bot))
