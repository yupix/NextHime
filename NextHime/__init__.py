import configparser
import os
from distutils.util import strtobool
from logging import getLogger
import time

from dbmanager import DbManager
from dotenv import load_dotenv
from halo import Halo
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.modules.Config import ConfigManager
from src.modules.create_logger import EasyLogger
from src.modules.language_manager import LanguageManager

start_time = time.time()

Base = declarative_base()

tmp_logger = getLogger("NextHime")
tmp_logger = EasyLogger(tmp_logger, logger_level="DEBUG").create()

if os.path.exists(".env") is True:
    load_dotenv(".env")
    tmp_logger.debug("VariableMode: .env")
else:
    tmp_logger.info(".envが存在しません")
    tmp_logger.warning("環境変数に定義されていない場合 config.iniを参照しますが、変更されていない場合プログラムは動作しません")

config = configparser.ConfigParser(os.environ)
config.read("./config.ini", encoding="utf-8")

os.environ.clear()
load_dotenv()
config_ini = configparser.ConfigParser(os.environ)
config_ini.read("./config.ini", encoding="utf-8")
config = ConfigManager(config_ini).load()


system_language = LanguageManager(
    base_path="./src/language/", lang=f"{config.lang}", module_name="system/info.yml"
).get()

engine = create_engine(
    f"postgresql://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_database}",
    echo=False,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10},
)
# DEBUG時はTrueに
Session = sessionmaker(bind=engine, autoflush=True, expire_on_commit=False)

session = Session()

# --------------------------------
# 1.loggerの設定
# --------------------------------
# loggerオブジェクトの宣言
logger = getLogger("main")
logger = EasyLogger(logger, logger_level=f"{config.log_level}").create()
spinner = Halo(text=f"{system_language['logger']['init_success']}", spinner="dots")
spinner.start()
db_manager = DbManager(
    session=session,
    logger=logger,
    logger_level=f"{config.log_level}",
    show_commit_log=bool(strtobool(config.log_show_commit)),
    force_show_commit_log=bool(strtobool(config.log_force_show_commit)),
)
spinner.succeed()

spinner = Halo(
    text="Loading Now", spinner={"interval": 300, "frames": ["-", "+", "o", "+", "-"]}
)
