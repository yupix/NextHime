import pickle
import os
import random
import time
from disnake import ApplicationCommandInteraction, Guild, RawReactionActionEvent, Member, User
from disnake.ext import commands


from NextHime import config
from src.modules.embed_manager import EmbedManager

verify_codes = []

if os.path.exists('./tmp/verify_code.pkl'):
    with open('./tmp/verify_code.pkl', 'rb') as f:
        verify_codes = pickle.load(f)


class VerifyManager:
    def __init__(self, user: Member):
        self.user = user

    async def check_duplicate(self, code: int) -> bool:
        for i in verify_codes:
            if i['code'] == code:
                return True
        else:
            return False

    async def random_number(self) -> int:
        return random.randint(1,9)
        

    async def create_code(self) -> str:
        code = ''
        for _ in range(0, 5):
            code += str(await self.random_number())
            
        check_duplicate = await self.check_duplicate(code)
        if check_duplicate is False:
            return code
        else:
            return await self.create_code()

async def pickle_dump():
    with open('./tmp/verify_code.pkl', 'wb') as f:
        pickle.dump(verify_codes, f)


class VerifyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction: RawReactionActionEvent):
        if reaction.message_id == 930064280383004802:
            if isinstance(reaction.member, Member):
                dm = await reaction.member.create_dm()
                verify_manager = VerifyManager(reaction.member)
                code = await verify_manager.create_code()
                await dm.send(f'あなたの認証コードは{code}です\nこのコードの有効期限は**10分**です。もしそれまでに使用できなかった場合は再度メッセージにリアクションを付与してください。')
                verify_codes.append({'code': code, 'user_id': reaction.member.id, 'expire': time.time() + 600})
                await pickle_dump()
                

    @commands.slash_command(description='認証を行う際に使用します', guild_ids=config.options.slash_command_guild)
    async def verify(self, inter: ApplicationCommandInteraction, code: str):
        for i, verify_code in enumerate(verify_codes):
            if verify_code['code'] == code and verify_code['user_id'] == inter.author.id:
                if verify_code['expire'] < time.time():
                    embed = EmbedManager(inter).generate('認証に失敗', f'コードの有効期限が切れています\nコードを再発行した上で再度実行してください', mode='failed').embed
                    await inter.send(embed=embed, ephemeral=True)
                    del verify_codes[i]
                    return
                del verify_codes[i]
                await pickle_dump()
                break
        else:
            embed = EmbedManager(inter).generate('認証に失敗', f'無効なコードです\n再実行しても同じエラーが出る場合は再発行することを推奨します', mode='failed').embed
            await inter.send(embed=embed, ephemeral=True)
            return
        if not isinstance(inter.author, Member):
            raise TypeError('authorはユーザーである必要があります')
        
        if isinstance(inter.guild, Guild):
            role = inter.guild.get_role(535408016397172753)
            await inter.author.add_roles(role)
        embed = EmbedManager(inter).generate('認証に成功', f'ご協力いただきありがとうございました。', mode='success').embed
        await inter.send(embed=embed, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(VerifyCog(bot))
