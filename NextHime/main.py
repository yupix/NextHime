import asyncio
import configparser
import os
import sys
import traceback
from distutils.util import strtobool

import discord
from discord.ext import commands
from discord_slash import SlashCommand
from fastapi import FastAPI
from fastapi_discord import DiscordOAuthClient
from fastapi_versioning import VersionedFastAPI
from googletrans import Translator
from starlette.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from NextHime import logger, spinner
from NextHime import system_language
from src.modules.auto_migrate import AutoMigrate, RevisionIdentifiedError, TooFewArguments, AdaptingMigrateFilesError
from src.modules.voice_generator import create_wave

config_ini = configparser.ConfigParser(os.environ)
config_ini.read("./config.ini", encoding="utf-8")

bot_user = config_ini["DEFAULT"]["User"]
bot_prefix = config_ini["DEFAULT"]["Prefix"]
bot_token = config_ini["DEFAULT"]["Token"]
auto_migrate = config_ini["DEFAULT"]["AutoMigrate"]
input_timeout = config_ini["DEFAULT"]["InputTimeOut"]
reset_status = config_ini["RESET"]["Status"]

custom_blogrole = config_ini["CUSTOM"]["Blogrole"]

use_api = config_ini["API"]["use"]
discord_client = config_ini["API"]["discord_client"]
discord_client_secret = config_ini["API"]["discord_client_secret"]
discord_callback_url = config_ini["API"]["discord_callback_url"]

use_eew = config_ini["EEW"]["use"]

Dic_Path = config_ini["JTALK"]["Dic_Path"]
Voice_Path = config_ini["JTALK"]["Voice_Path"]
Jtalk_Bin_Path = config_ini["JTALK"]["Jtalk_Bin_Path"]
Output_wav_name = config_ini["JTALK"]["Output_wav_name"]
read_aloud = config_ini["JTALK"]["read_aloud"]
Speed = config_ini["JTALK"]["Speed"]
show_bot_chat_log = config_ini["OPTIONS"]["show_bot_chat_log"]

if discord_client and discord_client_secret and discord_callback_url:
    discord_auth = DiscordOAuthClient(f'{discord_client}', f'{discord_client_secret}', f'{discord_callback_url}',
                                      ('identify', 'guilds', 'email'))  # scopes


class API:
    def __init__(self):
        self.title = f'{bot_user} API'

    async def create(self):
        from NextHime.routers.v1 import discord_guild
        from NextHime.routers.v1 import auth
        app = FastAPI(title=f"{self.title}")
        app.include_router(discord_guild.index.router)
        app.include_router(auth.index.router)
        app = VersionedFastAPI(app, version_format="{major}", prefix_format="/v{major}")
        return app


bot = None
slash_client = None

"""TODO: 下のやつをサポートする
    "NextHime.cogs.note",
    "NextHime.cogs.blocklist",
    "NextHime.cogs.warframe",
    "NextHime.cogs.blog",
    "NextHime.cogs.read",
    "NextHime.cogs.basic",
"""

INITIAL_EXTENSIONS = ["NextHime.cogs.eew", ]


def translator(content):
    tr = Translator()
    result = tr.translate(text=f"{content}", src="en", dest="ja").text

    return result


def add_list(hit, key, args_list):
    if hit is not None:
        args_list[f"{hit}"] = key
        hit = None
        return hit, args_list
    else:
        hit = key
        return hit, args_list


def check_args(argument):
    split_argument = argument.lower().split(" ")
    hit = None
    args_list = {}
    for i in split_argument:
        if (
                i == "--type"
                or i == "--max"
                or i == "-c"
                or i == "--register"
                or i == "--translate"
                or hit is not None
        ):
            hit, args_list = add_list(hit, i, args_list)
    logger.debug(hit)
    if hit is not None:
        return "1", f"{i}には引数が必要です"
    return args_list


class NextHime(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(
            command_prefix, help_command=None, description=None, intents=intents
        )
        SlashCommand(self, sync_commands=True)

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        spinner.stop()
        print("--------------------------------")
        print(self.user.name)
        print(self.user.id)
        print("--------------------------------")
        # if bool(strtobool(use_eew)) is True:
        # await bot_eew_loop.start()

    async def on_message(self, ctx):
        if bool(strtobool(show_bot_chat_log)) is False and ctx.author.bot is True:
            return
        logger.info(
            f"{ctx.guild.name}=> {ctx.channel.name}=> {ctx.author.name}: {ctx.content}"
        )
        if ctx.embeds:
            for embed in ctx.embeds:
                logger.info(embed.to_dict())
        check_voice_channel = discord.utils.get(
            self.voice_clients, guild=ctx.guild
        )

        if bool(strtobool(read_aloud)) is True and check_voice_channel is not None:
            create_wave(f"{ctx.content}")
            source = discord.FFmpegPCMAudio(f"{Output_wav_name}")
            try:
                ctx.guild.voice_client.play(source)
            except AttributeError:
                pass
        await self.process_commands(ctx)  # コマンド動作用


async def migrate():
    spinner.info(system_language['migrate']['action']['run_check']['message']['check'])
    spinner.stop()
    from inputimeout import inputimeout, TimeoutOccurred

    try:
        y_n = inputimeout(prompt=">>", timeout=int(input_timeout))
    except TimeoutOccurred:
        logger.info(system_language['migrate']['action']['run_check']['message']['timeout'] % input_timeout)
        y_n = "something"
    if y_n == "y":
        try:
            spinner.start('')
            AutoMigrate().generate()

        except RevisionIdentifiedError:
            logger.error(system_language['migrate']['error']['revision identified error']['message'])
            sys.exit(1)

        except TooFewArguments:
            logger.error(system_language['migrate']['error']['too few arguments']['message'])
            sys.exit(1)

        except AdaptingMigrateFilesError:
            logger.error(system_language['migrate']['error']['AdaptingMigrateFilesError']['message'])
            sys.exit(1)


async def bot_run(bot_loop):
    asyncio.set_event_loop(bot_loop)
    await bot.start(f"{bot_token}")


async def api_run(loop1):
    app = await API().create()
    asyncio.set_event_loop(loop1)
    config = Config(app=app, host="0.0.0.0", loop=loop1, port=5000, reload=True)
    server = Server(config)
    await server.serve()


def run(loop_bot, loop_api):
    global bot
    global slash_client
    if bool(strtobool(auto_migrate)):
        asyncio.run(migrate())
    asyncio.set_event_loop(loop_bot)
    intents = discord.Intents.all()
    bot = NextHime(command_prefix=f"{bot_prefix}", intents=intents)
    if bool(strtobool(use_api)) is True:
        future = asyncio.gather(bot_run(loop_bot), api_run(loop_api))
    else:
        future = asyncio.gather(bot_run(loop_bot))
    loop_bot.run_until_complete(future)
