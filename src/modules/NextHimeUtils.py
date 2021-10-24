import platform
import re
import tempfile

import disnake as discord
from disnake.ext import commands

from src.modules.locale import locales


class NextHimeUtils:
    def __init__(self, bot: commands.Bot = None, ctx=None, config=None):
        self.bot: commands.Bot = bot
        self.ctx = ctx
        self.mentions: str = ''
        self.temp_path = ("/tmp" if platform.system() ==
                          "Darwin" else tempfile.gettempdir())
        self.config = config

    def check_msg_mentions(self, ctx: discord.message.Message) -> 'NextHimeUtils':
        self.ctx = ctx
        self.mentions = re.findall(
            "<@!(.*?)>", f"{ctx.content}") or re.findall("<@(.*?)>", f"{ctx.content}")
        return self

    def replace_msg_mention(self) -> str:
        for mention in self.mentions:
            user = str(self.bot.get_user(int(mention)))
            self.ctx.content = self.ctx.content.replace(
                f'<@!{mention}>', f'@{user}').replace(f'<@{mention}>', f'@{user}')
        return self.ctx.content

    async def not_args_message(self):
        if self.ctx.invoked_subcommand is None:
            await self.ctx.send("this command is sub option required")


class CustomCtx(commands.context.Context):
    def __init__(self, ctx):
        self.ctx = ctx

    def get_user_locale(self) -> 'str | None':
        from src.sql.models.user import Users
        from NextHime import session
        user = session.query(Users).filter(Users.user_id == self.ctx.author.id).first()
        return user.locale

    def get_guild_locale(self) -> 'str | None':
        from src.sql.models.guild import Guilds
        from NextHime import session
        guild = session.query(Guilds).filter(Guilds.region == self.ctx.guild.id).first()
        return guild.region

    def get_locale(self) -> str:
        if locale := self.get_user_locale() is None:
            if locale := self.get_guild_locale() is None:
                locale = locales(self.ctx.guild.region).locale
        return locale
