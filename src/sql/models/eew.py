from sqlalchemy import BIGINT, VARCHAR, Column, Integer

from NextHime import Base


class Eew(Base):
    __tablename__ = "eew"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(VARCHAR(256), unique=True)


class EewChannel(Base):
    __tablename__ = "eew_channel"
    channel_id = Column(BIGINT, primary_key=True)
