import asyncio
from distutils.util import strtobool

import discord


class EmbedManager(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.embed = None

    def generate(self, embed_title: str = None, embed_description: str = '', mode: str = None,
                 color: int = 0x8BC34A, embed_content: list = [], image: str = None,
                 embed_thumbnail: str = None, ):
        """{'title': 'content', 'value': 'content', 'option': {'inline': 'False'}}"""
        if mode is not None:
            if mode == "succeed":
                color = 0x8BC34A
            elif mode == "failed":
                color = 0xD32F2F

        self.embed = discord.Embed(
            title=embed_title, description=embed_description, color=color
        )
        if image is not None:
            self.embed.set_image(url=f"{image}")
        if embed_thumbnail is not None:
            self.embed.set_thumbnail(url=embed_thumbnail)

        for content in embed_content:
            title = content.get("title", "タイトルが指定されていません")
            value = content.get("value", None)
            inline = content.get("option", {"inline": "True"}).get("inline")
            self.embed.add_field(name=title, value=value,
                                 inline=bool(strtobool(inline)))
        return self

    async def send(self, auto_delete: bool = False, sleep_time: int = None):
        msg = await self.ctx.send(embed=self.embed)
        if auto_delete is True:
            await asyncio.sleep(sleep_time)
            await msg.delete()
        return msg
