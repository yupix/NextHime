import asyncio
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

from NextHime import logger, spinner, config
from NextHime import system_language
from src.modules.NextHimeUtils import NextHimeUtils
from src.modules.auto_migrate import AutoMigrate
from src.modules.color import Color
from src.modules.voice_generator import create_wave

if config.api.discord_redirect_url and \
        config.api.discord_callback_url and \
        config.api.discord_client and \
        config.api.discord_client_secret:
    discord_auth = DiscordOAuthClient(f'{config.api.discord_client}', f'{config.api.discord_client_secret}',
                                      f'{config.api.discord_callback_url}',
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
        app = VersionedFastAPI(
            app, version_format="{major}", prefix_format="/v{major}")
        return app


bot: commands.Bot = commands.Bot(None)
slash_client = None

"""TODO: 下のやつをサポートする
    "NextHime.cogs.note",
    "NextHime.cogs.blocklist",
    "NextHime.cogs.warframe",
    "NextHime.cogs.blog",
    "NextHime.cogs.read",
    "NextHime.cogs.basic",
"""

INITIAL_EXTENSIONS = ["NextHime.cogs.eew", "NextHime.cogs.basic", "NextHime.cogs.warframe"]


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

    async def on_message(self, ctx):
        if bool(strtobool(config.options.log_show_bot)) is False and ctx.author.bot is True:
            return
        ctx.content = NextHimeUtils(bot).check_msg_mentions(ctx).replace_msg_mention()
        color = Color()
        try:
            logger.info(
                f'{color.custom("48")}[%sMSG {color.white}| \x1B[0m%s{ctx.guild.name}\x1B[0m {color.white}=> \x1B[0m%s'
                f'{ctx.channel.name}{color.custom("48")}]\x1B[0m '
                f'{color.white}{ctx.author.name}: {ctx.content}, %sbot: %s {ctx.author.bot}' %
                (color.custom("154"), color.custom("35"), color.custom("34"), color.custom("116"), color.custom("117"))
            )
        except AttributeError:
            logger.info(
                f'{color.custom("48")}[%sDM {color.white}| \x1B[0m{color.white}{ctx.author.name}: {ctx.content}, '
                f'%sbot: %s{ctx.author.bot}' %
                (Color().custom("36"), Color().custom("116"), Color().custom("117"))
            )

        if ctx.embeds:
            for embed in ctx.embeds:
                logger.info(embed.to_dict())
        check_voice_channel = discord.utils.get(
            self.voice_clients, guild=ctx.guild
        )

        if bool(strtobool(config.jtalk.aloud)) is True and check_voice_channel is not None:
            create_wave(f"{ctx.content}")
            source = discord.FFmpegPCMAudio(f"{config.jtalk.output_wav_name}")
            try:
                ctx.guild.voice_client.play(source)
            except AttributeError:
                pass
        await self.process_commands(ctx)  # コマンド動作用


async def migrate():
    logger.info(system_language['migrate']['action']
                ['run_check']['message']['check'])
    from inputimeout import inputimeout, TimeoutOccurred

    try:
        y_n = inputimeout(prompt=">>", timeout=int(config.options.input_timeout))
    except TimeoutOccurred:
        logger.info(system_language['migrate']['action']['run_check']
                    ['message']['timeout'] % config.options.input_timeout)
        y_n = "something"
    except PermissionError:
        logger.error('端末の操作ができません')
        y_n = None

    if y_n == "y":
        await AutoMigrate().generate().upgrade()


async def bot_run(bot_loop):
    asyncio.set_event_loop(bot_loop)
    await bot.start(f"{config.bot.token}")


async def api_run(loop1):
    app = await API().create()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'])
    asyncio.set_event_loop(loop1)
    api_config = Config(app=app, host=f'{config.api_host}', loop=loop1, port=int(
        config.api_port), reload=True)
    server = Server(api_config)
    await server.serve()


def run(loop_bot, loop_api):
    global bot
    global slash_client
    if bool(strtobool(config.db.auto_migrate)):
        asyncio.run(migrate())
    asyncio.set_event_loop(loop_bot)
    intents = discord.Intents.all()
    bot = NextHime(command_prefix=f"{config.bot.prefix}", intents=intents)
    if bool(strtobool(config.api.use)) is True:
        future = asyncio.gather(bot_run(loop_bot), api_run(loop_api))
    else:
        future = asyncio.gather(bot_run(loop_bot))
    loop_bot.run_until_complete(future)
