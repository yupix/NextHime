import disnake
from async_timeout import Optional
from disnake import ApplicationCommandInteraction
from disnake.ext import commands
from src.modules.embed_manager import EmbedManager

from NextHime import session, config, db_manager
from src.sql.models.blog import BlogsCategory, GuildBlogs


class BlogCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="blog",
                            guild_ids=config.options.slash_command_guild)
    async def blog(self, ctx):
        pass

    @blog.sub_command_group(name="setup")
    async def setup(self, ctx: ApplicationCommandInteraction):
        pass

    @setup.sub_command(name="category")
    async def setup_category(self, ctx: ApplicationCommandInteraction):
        await db_manager.commit(GuildBlogs(guild_id=ctx.guild.id))
        await db_manager.commit(
            BlogsCategory(guild_id=ctx.guild.id,
                          category_id=ctx.channel.category.id)
        )
        await ctx.response.send_message(
            embed=EmbedManager(ctx=ctx).generate('成功',
                                                 f'{ctx.channel.category.name}`をブログカテゴリとして登録しました',
                                                 'success').embed)

    @setup.sub_command(name="replay", description="ブログに対する返信チャンネルを設定します")
    async def setup_replay_channel(self, ctx: ApplicationCommandInteraction,
                                   channel_id: Optional[int] = None):
        """
        Parameters
        ----------
        channel_id : int
            登録したいチャンネルID
        """
        if channel_id is None:
            channel_id = ctx.channel.id
        guild = session.query(GuildBlogs).filter(GuildBlogs.guild_id ==
                                                 ctx.guild.id).first()
        guild.replay_channel_id = ctx.channel.id
        session.commit()
        await ctx.response.send_message(
            embed=EmbedManager(ctx=ctx).generate('成功',
                                                 f'<#{channel_id}>を返信チャンネルとして登録しました',
                                                 'success').embed)

    @commands.Cog.listener()
    async def on_message(self, ctx: disnake.Message):
        if ctx.author.bot:
            return
        print(ctx.content)
        category = session.query(BlogsCategory).filter(BlogsCategory.guild_id == ctx.guild.id).first()
        if category:
            replay_channel = session.query(GuildBlogs).filter(GuildBlogs.guild_id == ctx.guild.id).first()
            if replay_channel and ctx.channel_mentions:
                await ctx.create_thread(name="返信！")





def setup(bot):
    bot.add_cog(BlogCog(bot))
