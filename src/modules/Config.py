import ast
from distutils.util import strtobool
from typing import List

from src.modules.NextHimeUtils import NextHimeUtils


class HimeConfig(object):
    def __init__(self, config_dict):
        self.bot = self.Bot(config_dict)
        self.db = self.DB(config_dict)
        self.redis = self.Redis(config_dict)
        self.api = self.API(config_dict)
        self.eew = self.EEW(config_dict)
        self.jtalk = self.JTALK(config_dict)
        self.options = self.OPTIONS(config_dict)
        self.sentry = self.SENTRY(config_dict)

    class Bot(object):
        def __init__(self, config_dict):
            self.name: str = config_dict['BOT']['name']
            self.prefix: str = config_dict['BOT']['prefix']
            self.token: str = config_dict['BOT']['token']

    class DB(object):
        def __init__(self, config_dict):
            self.user: str = config_dict['DB']['user']
            self.port: int = config_dict['DB']['port']
            self.host: str = config_dict['DB']['host']
            self.password: str = config_dict['DB']['password']
            self.database: str = config_dict['DB']['database']
            self.auto_migrate: bool = strtobool(config_dict['DB']['auto_migrate'])

    class Redis(object):
        def __init__(self, config_dict):
            self.host: str = config_dict['REDIS']['host']
            self.port: int = config_dict['REDIS']['port']
            self.db: dict = config_dict['REDIS']['db']

    class API(object):
        def __init__(self, config_dict):
            self.use: bool = strtobool(config_dict['API']['use'])
            self.host: str = config_dict['API']['host']
            self.port: int = config_dict['API']['port']
            self.discord_client: str = config_dict['API']['discord_client']
            self.discord_client_secret: str = config_dict['API']['discord_client_secret']
            self.discord_callback_url: str = config_dict['API']['discord_callback_url']
            self.discord_redirect_url: str = config_dict['API']['discord_redirect_url']

    class EEW(object):
        def __init__(self, config_dict):
            self.use: bool = strtobool(config_dict['EEW']['use'])

    class JTALK(object):
        def __init__(self, config_dict):
            self.dic_path: str = config_dict['JTALK']['dic_path']
            self.voice_path: str = config_dict['JTALK']['voice_path']
            self.bin_path: str = config_dict['JTALK']['bin_path']
            self.output_wav_name: str = NextHimeUtils().temp_path + config_dict['JTALK']['output_wav_name']
            self.speed: int = config_dict['JTALK']['speed']
            self.aloud: bool = strtobool(config_dict['JTALK']['aloud'])

    class OPTIONS(object):
        def __init__(self, config_dict):
            self.log_level: str = config_dict['OPTIONS']['log_level']
            self.lang: str = config_dict['OPTIONS']['lang']
            self.input_timeout: int = config_dict['OPTIONS']['input_timeout']
            self.log_show_bot: bool = strtobool(config_dict['OPTIONS']['log_show_bot'])
            self.log_show_commit: bool = strtobool(config_dict['OPTIONS']['log_show_commit'])
            self.log_force_show_commit: bool = config_dict['OPTIONS']['log_force_show_commit']
            self.slash_command_guild: List[int] = ast.literal_eval(config_dict['OPTIONS']['slash_command_guild'])

    class BLOG(object):
        def __init__(self, config_dict):
            self.role: str = config_dict['BLOG']['blogger_role']

    class SENTRY(object):
        def __init__(self, config_dict):
            self.sentry_use: bool = strtobool(config_dict['ADVANCED']['sentry_use'])
            self.sentry_dsn: str = config_dict['ADVANCED']['sentry_dsn']
