import asyncio
import json
from distutils.util import strtobool

import discord


class EmbedManager(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.embed = None

    async def parse_to_print(self, logger) -> None:
        """
        Parameters
        ----------
        logger:
            ログの出力に使用
        """
        if self.ctx.embeds:
            for embed in self.ctx.embeds:
                logger.info(json.dumps(embed.to_dict(), indent=2))

    def generate(self, embed_title: str = None, embed_description: str = '', mode: str = None,
                 color: int = 0x8BC34A, embed_content: list = [], image: str = None,
                 embed_thumbnail: str = None) -> 'EmbedManager':
        """
        Parameters
        ----------
        embed_title: str
            Embedのタイトル
        embed_description: str
            Embedのサブタイトル
        mode: str
            Embedの色をsucceedまたはfailedの2パターンで自動で付ける
        color: int
            16進数で色を指定0xFFFFFFのような形
        embed_content: list
            {'title': 'タイトル文', 'value': '内容'}をリストに複数登録することでEmbedに複数要素を登録する
        image: str
            URLを受け取りEmbedに画像を追加
        embed_thumbnail:
            URLを受け取りEmbedにアイコンのような小さい画像を追加

        Returns
        -------
        EmbedManager
        """
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

    async def send(self, auto_delete: bool = False, sleep_time: int = None) -> discord.message.Message:
        """
        Parameters
        ----------
        auto_delete: bool
            自動で一定時間経過後に削除するかしないか
        sleep_time: int
            auto_delete引数が有効の場合、何秒後に削除するかを指定
        Returns
        ------
        discord.message.Message
            メッセージ要素を返却
        """
        msg = await self.ctx.send(embed=self.embed)
        if auto_delete is True:
            await asyncio.sleep(sleep_time)
            await msg.delete()
        return msg
