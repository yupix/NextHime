import configparser
import logging
import os
import time
from logging import getLogger

import i18n
from dbmanager import DbManager
from dotenv import load_dotenv
from halo import Halo
from loguru import logger
import redis
from rich.console import Console
from rich.logging import RichHandler
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.modules.Config import HimeConfig
from src.modules.create_logger import EasyLogger

start_time = time.time()

Base = declarative_base()

tmp_logger = getLogger("NextHime")
tmp_logger = EasyLogger(tmp_logger, logger_level="DEBUG").create()

if os.path.exists(".env") is True:
    load_dotenv(".env")
    logger.debug("VariableMode: .env")
else:
    logger.info(".envが存在しません")
    logger.warning("環境変数に定義されていない場合 config.iniを参照しますが、変更されていない場合プログラムは動作しません")

config = configparser.ConfigParser(os.environ)
config.read("./config.ini", encoding="utf-8")

load_dotenv()
config_ini = configparser.ConfigParser(os.environ)
config_ini.read("./config.ini", encoding="utf-8")
config = HimeConfig(config_ini)

i18n.load_path.append('./src/language')
i18n.set("locale", "ja")
i18n.set("fallback", "ja")
i18n.set("skip_locale_root_data", True)

# --------------------------------
# 1.loggerの設定
# --------------------------------

logging.basicConfig(
    level=config.options.log_level,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger("rich")


redis_conn = redis.Redis(host='localhost', port=6379)
try:
    redis_conn.ping()
except redis.exceptions.ConnectionError:
    log.warning('redisに接続できませんでした。warframeが有効の場合自動的に無効になっています。')
    config.warframe.use = False

engine = create_engine(
    f"postgresql://{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.database}",
    echo=False,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10},
)
# DEBUG時はTrueに
Session = sessionmaker(bind=engine, autoflush=True, expire_on_commit=False)

session = Session()

console = Console()


spinner = Halo(text=f"{i18n.t('message.logger.init_success', locale=config.options.lang)}", spinner="dots")
spinner.start()
db_manager = DbManager(
    session=session,
    logger=logger,
    logger_level=f"{config.options.log_level}",
    show_commit_log=config.options.log_show_commit,
    force_show_commit_log=config.options.log_force_show_commit,
)
spinner.succeed()

spinner = Halo(
    text="Loading Now", spinner={"interval": 300, "frames": ["-", "+", "o", "+", "-"]}
)
