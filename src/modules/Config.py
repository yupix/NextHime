import dataclasses


@dataclasses.dataclass
class HimeConfig:
    user: str
    prefix: str
    token: str
    log_level: str
    lang: str
    auto_migrate: bool
    input_timeout: int
    db_user: str
    db_port: int
    db_host: str
    db_password: str
    db_database: str
    api_use: bool
    api_host: str
    api_port: int
    api_discord_client: str
    api_discord_client_secret: str
    api_discord_callback_url: str
    api_discord_redirect_url: str
    eew_use: bool
    blog_role: str
    jtalk_dic_path: str
    jtalk_voice_path: str
    jtalk_bin_path: str
    jtalk_output_wav_name: str
    jtalk_speed: int
    jtalk_aloud: bool
    log_show_bot: bool
    log_show_commit: bool
    log_force_show_commit: bool
    sentry_use: bool
    sentry_dsn: str
    reset_status: int


class ConfigManager:
    def __init__(self, config_ini):
        self.config = config_ini

    def load(self):
        block_list = [
            'next_hime_bot_token',
            'next_hime_db_user',
            'next_hime_db_password',
            'next_hime_db_host',
            'next_hime_jtalk_dic_path',
            'next_hime_voice_path',
            'next_hime_jtalk_bin_path',
            'next_hime_sentry_dsn',
            'next_hime_api_host',
            'next_hime_discord_client',
            'next_hime_discord_client_secret',
            'next_hime_discord_callback_url',
            'next_hime_discord_redirect_url',
        ]
        hit_list = {}
        for section in self.config.keys():
            for section_key in self.config[f'{section}']:
                if section_key not in block_list:
                    hit_list[section_key] = self.config[f'{section}'][f'{section_key}']
        config = HimeConfig(**hit_list)
        return config
