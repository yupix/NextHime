import asyncio
import alfakana

import disnake as discord
from disnake.ext import commands
from loguru import logger
import i18n

from NextHime import config
from src.modules.NextHimeUtils import NextHimeUtils
from src.modules.voice_generator import create_wave


class ReadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='read')
    async def read(self, ctx):
        await NextHimeUtils(bot=self.bot, ctx=ctx).not_args_message()

    @read.command(pass_context=True, name="status")
    async def status(self, ctx):
        member = await ctx.guild.fetch_member(ctx.author.id)
        print(member.status)

    @read.command()
    async def join(self, ctx):
        vc = ctx.author.voice
        if not vc or not vc.channel:
            await ctx.send(i18n.t('message.read.notJoinVoiceChannel', locale=ctx.author.locale))
            return
        logger.debug(f"ボイスチャンネル {vc} に参加しました")
        await create_wave("こんにちは! 読み上げを開始します。")
        source = discord.FFmpegPCMAudio(f"{config.jtalk.output_wav_name}")
        try:
            await vc.channel.connect()
            await asyncio.sleep(3)
            ctx.guild.voice_client.play(source)
        except discord.ClientException:
            await create_wave("既に参加しています")

            source = discord.FFmpegPCMAudio(f"{config.jtalk.output_wav_name}")
            ctx.guild.voice_client.play(source)

    @commands.command()
    async def leave(self, ctx):
        await create_wave("読み上げを終了します。お疲れ様でした。")
        source = discord.FFmpegPCMAudio(f"{config.jtalk.output_wav_name}")
        ctx.guild.voice_client.play(source)
        await asyncio.sleep(4)
        await ctx.voice_client.disconnect()
        logger.debug(f"ボイスチャンネル {ctx.voice_client.name} から退出しました")

    @commands.group(name='dic')
    async def dic(self, ctx):
        await NextHimeUtils(bot=self.bot, ctx=ctx).not_args_message()

    @dic.command()
    async def add(self, ctx, key, value):
        alfakana.add_dic(str(key).upper(), value, './dic.db')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        logger.debug(f"{member.id}, {self.bot.user.id}")
        if member.id == self.bot.user.id:
            return
        elif member.bot:
            input_text = "ボット: "
        else:
            input_text = "ユーザー: "

        if before.channel is None:
            logger.debug(f"{member.name} さんがボイスチャンネル {after.channel.name} に参加しました")
            await create_wave(alfakana.sentence_kana(input_text + f"{member.name} さんがボイスチャンネルに参加しました", './dic.db'))
        elif after.channel is None:
            logger.debug(alfakana.sentence_kana(f"{member.name} さんがボイスチャンネル {before.channel.name} から退出しました", './dic.db'))
            await create_wave(input_text + f"{member.name} さんがボイスチャンネルから退出しました")

        if before.channel is None or after.channel is None:
            source = discord.FFmpegPCMAudio(f"{config.jtalk.output_wav_name}")
            while True:
                if member.guild.voice_client:
                    if member.guild.voice_client.is_playing() is False:
                        member.guild.voice_client.play(source)
                        break
                    await asyncio.sleep(3)
                else:
                    break


def setup(bot):
    bot.add_cog(ReadCog(bot))
