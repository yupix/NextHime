import re

import discord
from discord.ext import commands


class NextHimeTools:
    def __init__(self, bot: commands.Bot = None):
        self.bot:commands.Bot = bot
        self.ctx = None
        self.mentions:str = ''

    def check_msg_mentions(self, ctx: discord.message.Message) -> 'NextHimeTools':
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
