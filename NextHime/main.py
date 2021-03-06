import asyncio
import re
import traceback

import alfakana
import disnake
import disnake as discord
import i18n
from disnake.ext import commands
from fastapi import FastAPI
from fastapi_discord import DiscordOAuthClient
from fastapi_versioning import VersionedFastAPI
from loguru import logger
from rich import print as rich_print
from rich.panel import Panel
from starlette.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from NextHime import config, console, log, session
from src.modules import EmbedManager
from src.modules.NextHimeUtils import NextHimeUtils
from src.modules.auto_migrate import AutoMigrate
from src.modules.voice_generator import create_wave
from src.sql.models.user import Users

if (
        config.api.discord_redirect_url
        and config.api.discord_callback_url
        and config.api.discord_client
        and config.api.discord_client_secret
):
    discord_auth = DiscordOAuthClient(
        f"{config.api.discord_client}",
        f"{config.api.discord_client_secret}",
        f"{config.api.discord_callback_url}",
        ("identify", "guilds", "email"),
    )  # scopes


class API:
    def __init__(self):
        self.title = f"{config.bot.name} API"

    async def create(self):
        from NextHime.routers.v1 import discord_guild

        app = FastAPI(title=f"{self.title}")
        app.include_router(discord_guild.index.router)
        app = VersionedFastAPI(
            app, version_format="{major}", prefix_format="/v{major}")
        return app


bot: commands.Bot = commands.Bot(None)
"""TODO: 下のやつをサポートする
    "NextHime.cogs.note",
    "NextHime.cogs.blocklist",
    "NextHime.cogs.warframe",
    "NextHime.cogs.blog",
    "NextHime.cogs.read",
    "NextHime.cogs.basic",
"""

INITIAL_EXTENSIONS = [
    "NextHime.cogs.warframe",
    "NextHime.cogs.eew",
    "NextHime.cogs.read",
    "NextHime.cogs.blog"
]


class NextHime(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(
            command_prefix,
            description=None,
            intents=intents,
            test_guilds=["530299114387406860"],
            sync_commands_debug=True,
        )

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        login_success_msg = i18n.t(
            "message.system.login_success", locale=config.options.lang
        )
        account_name = i18n.t("message.system.account_name",
                              locale=config.options.lang)
        account_id = i18n.t("message.system.account_id",
                            locale=config.options.lang)
        rich_print(
            Panel.fit(
                f"""[green]{login_success_msg}[/green]
[bold]{account_name}[/bold]: [blue]{self.user.name}[/blue]
[bold]{account_id}[/bold]: [blue]{self.user.id}[/blue]"""
            )
        )

    async def on_message(self, ctx):
        if config.options.log_show_bot is False and ctx.author.bot is True:
            return
        ctx.content = NextHimeUtils(bot).check_msg_mentions(
            ctx).replace_msg_mention()
        try:
            log.info(
                f"[[spring_green1]MSG[/spring_green1] | [bright_green]{ctx.guild.name}[/bright_green] => {ctx.channel.name}]"
                f" {ctx.author.name}:"
                f" {ctx.content}, "
                f"bot: {ctx.author.bot}",
                extra={"markup": True},
            )
        except AttributeError:
            log.info(
                f'[[spring_green1]DM[/spring_green1]] | {ctx.author.name}: {ctx.content}, '
                f"bot: {ctx.author.bot}",
                extra={"markup": True}
            )

        if ctx.embeds:
            embed_list = [i.to_dict() for i in ctx.embeds]
            console.log(embed_list, log_locals=True)

        check_voice_channel = discord.utils.get(
            self.voice_clients, guild=ctx.guild)
        if (
                config.jtalk.aloud
                and check_voice_channel is not None
                and ctx.author.bot is False
        ):
            user_voice = session.query(Users).filter(
                Users.user_id == ctx.author.id
            ).first()
            content = re.sub(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+/?',
                             'URL', ctx.content)
            voice_name = user_voice.hts_voice if user_voice else None
            await create_wave(
                f"{alfakana.change_kana(ctx.author.name, 'dic.db')}さんからのメッセージ "
                f"{alfakana.change_kana(content, 'dic.db')}",
                voice_name=voice_name)
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

    async def on_slash_command_error(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            exception: commands.CommandError,
    ) -> None:
        if interaction.response.is_done():
            m = interaction.followup.send
        else:
            m = interaction.response.send_message
        await m(embed=EmbedManager().generate('エラーが発生しました', f'`{exception}`',
                                              mode='failed').embed)


async def migrate():
    logger.info(i18n.t("message.migrate.run.check",
                       locale=config.options.lang))
    from inputimeout import TimeoutOccurred, inputimeout

    try:
        y_n = inputimeout(prompt=">>", timeout=int(
            config.options.input_timeout))
    except TimeoutOccurred:
        logger.info(
            i18n.t("message.migrate.run.timeout", locale=config.options.lang)
            % config.options.input_timeout
        )
        y_n = "something"
    except PermissionError:
        logger.error(
            i18n.t("message.migrate.error.unable_operate_terminal.name"))
        logger.error(
            i18n.t("message.migrate.error.unable_operate_terminal.message"))
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
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    asyncio.set_event_loop(loop1)
    api_config = Config(
        app=app,
        host=f"{config.api.host}",
        loop=loop1,
        port=int(config.api.port),
        reload=True,
    )
    server = Server(api_config)
    await server.serve()


def run(loop_bot, loop_api):
    global bot
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
