from datetime import date, datetime
import json
from disnake import CommandInteraction, Embed
from disnake.ext import commands


class SiNoAliceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        with open('./src/assets/data/sinoalice_weeq_quest.json', 'r', encoding='utf-8') as f:
            _weeq_quest_data = json.load(f)
        self.weeq_quest_data = _weeq_quest_data
        

    @commands.slash_command(name='sinoalice')
    async def sinoalice(self, inter):
        pass

    @sinoalice.sub_command(name='weekquest')
    async def weekquest(self, inter: CommandInteraction):
        weekday = date.today().weekday()
        print(self.weeq_quest_data, weekday)
        quests = self.weeq_quest_data['quests'][f'{weekday}']
        print(quests)
        await inter.response.send_message('現在開催中の曜日クエストは以下のとおりです')
        for quest in quests:
            print(quest)
            embed_color = self.weeq_quest_data['color'][quest]
            await inter.channel.send(embed=Embed(color=int(embed_color, base=16), title=f"{quest}", description=""))
        
    


def setup(bot: commands.Bot):
    bot.add_cog(SiNoAliceCog(bot))
