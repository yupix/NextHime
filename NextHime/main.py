import asyncio
import traceback

import alfakana
import discord
import i18n
from discord.ext import commands
from fastapi import FastAPI
from fastapi_discord import DiscordOAuthClient
from fastapi_versioning import VersionedFastAPI
from starlette.middleware.cors import CORSMiddleware
from uvicorn import Config, Server
from loguru import logger

from NextHime import config
from src.modules.NextHimeUtils import NextHimeUtils
from src.modules.auto_migrate import AutoMigrate
from src.modules.color import Color
from src.modules.embed_manager import EmbedManager
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
        self.title = f'{config.bot.name} API'

    async def create(self):
        from NextHime.routers.v1 import discord_guild
        app = FastAPI(title=f"{self.title}")
        app.include_router(discord_guild.index.router)
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

INITIAL_EXTENSIONS = ["NextHime.cogs.basic", "NextHime.cogs.warframe", "NextHime.cogs.read"]


class NextHime(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(
            command_prefix, help_command=None, description=None, intents=intents
        )

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        board = len(i18n.t('message.system.account_id', locale=config.options.lang) + str(self.user.id))
        print(f"""┌{'──' * board}┐
│\033[32m{i18n.t('message.system.login_success', locale=config.options.lang)}\033[0m
│\033[1m{i18n.t('message.system.account_name', locale=config.options.lang)}\033[0m: \033[34m{self.user.name}\033[0m
│\033[1m{i18n.t('message.system.account_id', locale=config.options.lang)}\033[0m: \033[34m{self.user.id}\033[0m
└{'──' * board}┘
""")

    async def on_message(self, ctx):
        if config.options.log_show_bot is False and ctx.author.bot is True:
            return
        ctx.content = NextHimeUtils(bot).check_msg_mentions(
            ctx).replace_msg_mention()
        color = Color()
        try:
            logger.info(
                f'{color.custom("48")}[%sMSG {color.white}| \x1B[0m%s{ctx.guild.name}\x1B[0m {color.white}=> \x1B[0m%s'
                f'{ctx.channel.name}{color.custom("48")}]\x1B[0m '
                f'{color.white}{ctx.author.name}: {ctx.content}, %sbot: %s {ctx.author.bot}' %
                (color.custom("154"), color.custom("35"), color.custom(
                    "34"), color.custom("116"), color.custom("117"))
            )
        except AttributeError:
            logger.info(
                f'{color.custom("48")}[%sDM {color.white}| \x1B[0m{color.white}{ctx.author.name}: {ctx.content}, '
                f'%sbot: %s{ctx.author.bot}' %
                (Color().custom("36"), Color().custom("116"), Color().custom("117"))
            )

        await EmbedManager(ctx).parse_to_print()

        check_voice_channel = discord.utils.get(
            self.voice_clients, guild=ctx.guild
        )

        if config.jtalk.aloud and check_voice_channel is not None and ctx.author.bot is False:
            create_wave(
                f"{alfakana.sentence_kana(f'{ctx.author.name}さんからのメッセージ {ctx.content}', './dic.db')}")
            while True:
                source = discord.FFmpegPCMAudio(
                    f"{config.jtalk.output_wav_name}")
                if ctx.guild.voice_client.is_playing() is False:
                    try:
                        ctx.guild.voice_client.play(source)
                        break
                    except AttributeError:
                        break
        await self.process_commands(ctx)  # コマンド動作用


async def migrate():
    logger.info(i18n.t('message.migrate.run.check',
                locale=config.options.lang))
    from inputimeout import inputimeout, TimeoutOccurred

    try:
        y_n = inputimeout(prompt=">>", timeout=int(
            config.options.input_timeout))
    except TimeoutOccurred:
        logger.info(i18n.t('message.migrate.run.timeout',
                    locale=config.options.lang) % config.options.input_timeout)
        y_n = "something"
    except PermissionError:
        logger.error(
            i18n.t('message.migrate.error.unable_operate_terminal.name'))
        logger.error(
            i18n.t('message.migrate.error.unable_operate_terminal.message'))
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
    api_config = Config(app=app, host=f'{config.api.host}', loop=loop1, port=int(
        config.api.port), reload=True)
    server = Server(api_config)
    await server.serve()


def run(loop_bot, loop_api):
    global bot
    global slash_client
    if config.db.auto_migrate:
        asyncio.run(migrate())
    asyncio.set_event_loop(loop_bot)
    intents = discord.Intents.all()
    bot = NextHime(command_prefix=f"{config.bot.prefix}", intents=intents)
    if config.api.use is True:
        future = asyncio.gather(bot_run(loop_bot), api_run(loop_api))
    else:
        future = asyncio.gather(bot_run(loop_bot))
    loop_bot.run_until_complete(future)
