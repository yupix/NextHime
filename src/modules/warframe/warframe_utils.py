import i18n
from disnake.ext import commands

from src.modules.embed_manager import EmbedManager
from src.modules.language_manager import LanguageManager
from src.modules.warframe.exceptions import MissionTypeKeyError


class WarframeFissure:
    def __init__(self, fissure_dict):
        """
        与えられた情報からオブジェクト化します。
        Parameters
        ----------
        fissure_dict: dict
            1つの亀裂情報

        Returns
        -------
        WarframeFissure:
            クラス自身を返却
        """
        tier_int_list = {"1": "Lith", "2": "Meso",
                         "3": "Neo", "4": "Axi", "5": "Requiem"}
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
        self.tier: int = int(
            [key for key, value in tier_int_list.items() if value == fissure_dict['tier']][0])
        self.tierInt: str = fissure_dict['tier']
        self.tierNum: int = int(fissure_dict['tierNum'])
        self.expired: bool = bool(fissure_dict['expired'])
        self.eta: str = fissure_dict['eta']
        self.isStorm: bool = bool(fissure_dict['isStorm'])


class WarframeTranslator(object):
    def __init__(self, lang: str = 'japan'):
        """
        WarframeTranslatorに必要な初期化処理
        Parameters
        ----------
        lang:str
            言語に置き換えるか
        """
        self.lang = lang

    async def translate(self, fissure):
        """
        与えられた亀裂の情報を設定された言語情報に置き換える
        Parameters
        ----------
        fissure: WarframeFissure
            object化されたfissure
        Returns
        -------
        WarframeFissure:
            Warframeの亀裂Object

        """
        mission_type = LanguageManager(base_path="./src/language/", lang=f"{self.lang}",
                                       module_name="/warframe/mission_type.yml").get()
        try:
            fissure.missionType = fissure.missionType.replace(fissure.missionType,
                                                              f'{mission_type["MissionType"][fissure.missionType]}')
        except KeyError:
            raise MissionTypeKeyError('Fissure Mission Type Key NotFound')
        return fissure


class WarframeChannels(object):
    def __init__(self, bot: commands.Bot, fissure: WarframeFissure):
        self.fissure: WarframeFissure = fissure
        self.bot: commands.Bot = bot

    async def send_message(self, channels):
        """
        Parameters
        ----------
        channels:
            送信するチャンネルをlist形式で取得します。

        Returns
        -------
        None:
            送信限定です
        """
        for channel in channels:
            try:
                temp_fissure = await WarframeTranslator(channel.region).translate(self.fissure)
                channel = self.bot.get_channel(channel.channel_id)
                await EmbedManager(channel).generate(self.fissure.node, f'ミッション内容: {temp_fissure.missionType}',
                                                     embed_content=[{'title': '出現エネミー', 'value': f'{self.fissure.enemy}'},
                                                                    {'title': 'レリック',
                                                                     'value': f'{self.fissure.tier}'},
                                                                    {'title': '終了まで',
                                                                     'value': f'{self.fissure.eta}'}
                                                                    ]).send()
            except MissionTypeKeyError:
                channel = self.bot.get_channel(channel.channel_id)
                await EmbedManager(channel).generate(
                    self.fissure.node,
                    i18n.t('message.warframe.NotSupportedType', locale='ja').format(
                        type=self.fissure.missionType),
                    mode='failed'
                ).send()
