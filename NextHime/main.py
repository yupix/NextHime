import asyncio
import configparser
import os
import sys
import traceback
from distutils.util import strtobool

import discord
from discord.ext import commands
from discord_slash import SlashCommand
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_discord import DiscordOAuthClient
from fastapi_versioning import VersionedFastAPI
from googletrans import Translator
from starlette.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from NextHime import logger, spinner
from NextHime import system_language
from src.modules.Config import ConfigManager
from src.modules.auto_migrate import AutoMigrate, RevisionIdentifiedError, TooFewArguments, AdaptingMigrateFilesError
from src.modules.voice_generator import create_wave

os.environ.clear()
load_dotenv()
config_ini = configparser.ConfigParser(os.environ)
config_ini.read("./config.ini", encoding="utf-8")
config = ConfigManager(config_ini).load()

if config.api_discord_redirect_url and \
        config.api_discord_callback_url and \
        config.api_discord_client and \
        config.api_discord_client_secret:
    discord_auth = DiscordOAuthClient(f'{config.api_discord_client}', f'{config.api_discord_client_secret}',
                                      f'{config.api_discord_callback_url}',
                                      ('identify', 'guilds', 'email'))  # scopes


class API:
    def __init__(self):
        self.title = f'{config.user} API'

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
        name_length = len(self.user.name)
        id_length = len(str(self.user.id))
        if name_length >= id_length:
            length = name_length
        else:
            length = id_length
        equal = '=' * length
        print(f"""\033[32mログインに成功しました\033[0m
#=========={equal}#
\033[1mアカウント名\033[0m: \033[34m{self.user.name}\033[0m
\033[1mアカウントID\033[0m: \033[34m{self.user.id}\033[0m
#=========={equal}#
""")
        # if bool(strtobool(use_eew)) is True:
        # await bot_eew_loop.start()

    async def on_message(self, ctx):
        if bool(strtobool(config.log_show_bot)) is False and ctx.author.bot is True:
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

        if bool(strtobool(config.jtalk_aloud)) is True and check_voice_channel is not None:
            create_wave(f"{ctx.content}")
            source = discord.FFmpegPCMAudio(f"{config.jtalk_output_wav_name}")
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
        y_n = inputimeout(prompt=">>", timeout=int(config.input_timeout))
    except TimeoutOccurred:
        logger.info(system_language['migrate']['action']['run_check']['message']['timeout'] % config.input_timeout)
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
    await bot.start(f"{config.token}")


async def api_run(loop1):
    app = await API().create()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'])
    asyncio.set_event_loop(loop1)
    api_config = Config(app=app, host=f'{config.api_host}', loop=loop1, port=int(config.api_port), reload=True)
    server = Server(api_config)
    await server.serve()


def run(loop_bot, loop_api):
    global bot
    global slash_client
    if bool(strtobool(config.auto_migrate)):
        asyncio.run(migrate())
    asyncio.set_event_loop(loop_bot)
    intents = discord.Intents.all()
    bot = NextHime(command_prefix=f"{config.prefix}", intents=intents)
    if bool(strtobool(config.api_use)) is True:
        future = asyncio.gather(bot_run(loop_bot), api_run(loop_api))
    else:
        future = asyncio.gather(bot_run(loop_bot))
    loop_bot.run_until_complete(future)
