import configparser
import os
from distutils.util import strtobool
from logging import getLogger

from dbmanager import DbManager
from dotenv import load_dotenv
from halo import Halo
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.modules.create_logger import EasyLogger
from src.modules.language_manager import LanguageManager

Base = declarative_base()

tmp_logger = getLogger("NextHime")
tmp_logger = EasyLogger(tmp_logger, logger_level="DEBUG").create()

if os.path.exists(".env") is True:
    load_dotenv(".env")
else:
    tmp_logger.error(".envが存在しません")

config = configparser.ConfigParser(os.environ)
config.read("./config.ini", encoding="utf-8")

###
#   ログに関するコンフィグ
###
logger_level = config["DEFAULT"]["log"]
use_language = config["DEFAULT"]["lang"]
show_commit_log = config["OPTIONS"]["log_show_commit_"]
force_show_commit_log = config["OPTIONS"]["log_force_show_commit"]

###
#   データベースに関するコンフィグ
###
db_user = config["DATABASE"]["db_user"]
db_port = config["DATABASE"]["db_port"]
db_host = config["DATABASE"]["db_host"]
db_password = config["DATABASE"]["db_password"]
db_default_database = config["DATABASE"]["db_database"]

system_language = LanguageManager(
    base_path="./src/language/", lang=f"{use_language}", module_name="system/info.yml"
).get()

engine = create_engine(
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_default_database}",
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
logger = EasyLogger(logger, logger_level=f"{logger_level}").create()
spinner = Halo(text=f"{system_language['logger']['init_success']}", spinner="dots")
spinner.start()
db_manager = DbManager(
    session=session,
    logger=logger,
    logger_level=f"{logger_level}",
    show_commit_log=bool(strtobool(show_commit_log)),
    force_show_commit_log=bool(strtobool(force_show_commit_log)),
)
spinner.succeed()

spinner = Halo(
    text="Loading Now", spinner={"interval": 300, "frames": ["-", "+", "o", "+", "-"]}
)
