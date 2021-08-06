from discord.ext import commands


class WarframeFissure:
    def __init__(self, fissure_dict):
        tier_int_list = {"1": "Lith", "2": "Meso", "3": "Neo", "4": "Axi", "5": "Requiem"}
        self.id: str = fissure_dict['id']
        self.activation: str = fissure_dict['activation']
        self.startString: str = fissure_dict['startString']
        self.expiry: str = fissure_dict['expiry']
        self.active: bool = bool(fissure_dict['active'])
        self.node: str = fissure_dict['node']
        self.missionType: str = fissure_dict['missionType']
        self.missionKey: str = fissure_dict['missionKey']
        self.enemy: str = fissure_dict['enemy']
        self.enemyKey: str = fissure_dict['enemyKey']
        self.nodeKey: str = fissure_dict['nodeKey']
        self.tier: int = int([key for key, value in tier_int_list.items() if value == fissure_dict['tier']][0])
        self.tierInt: str = fissure_dict['tier']
        self.tierNum: int = int(fissure_dict['tierNum'])
        self.expired: bool = bool(fissure_dict['expired'])
        self.eta: str = fissure_dict['eta']
        self.isStorm: bool = bool(fissure_dict['isStorm'])


class WarframeChannels(object):
    def __init__(self, bot: commands.Bot, fissure: WarframeFissure):
        self.fissure: WarframeFissure = fissure
        self.bot: commands.Bot = bot

    async def send_message(self, channels):
        for channel in channels:
            channel = self.bot.get_channel(channel.id)
            await channel.send(self.fissure.tier)
