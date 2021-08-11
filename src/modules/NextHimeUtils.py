import platform
import re
import tempfile

import discord
from discord.ext import commands


class NextHimeUtils:
    def __init__(self, bot: commands.Bot = None, ctx=None):
        self.bot: commands.Bot = bot
        self.ctx = ctx
        self.mentions: str = ''
        self.temp_path = ("/tmp" if platform.system() == "Darwin" else tempfile.gettempdir())

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
