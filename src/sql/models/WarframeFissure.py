from sqlalchemy import BIGINT, VARCHAR, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from NextHime import Base


class WarframeFissuresId(Base):
    __tablename__ = "warframe_fissures_id"

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(VARCHAR(255), unique=True)
    warframe_fissures_detail = relationship(
        "WarframeFissuresDetail",
        backref="warframe_fissures_id",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class WarframeFissuresDetail(Base):
    __tablename__ = "warframe_fissures_detail"
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    api_id = Column(
        VARCHAR(255),
        ForeignKey("warframe_fissures_id.api_id",
                   onupdate="CASCADE",
                   ondelete="CASCADE"),
        unique=True,
    )
    node = Column(VARCHAR(255))
    enemy = Column(VARCHAR(255))
    type = Column(VARCHAR(255))
    tier = Column(VARCHAR(255))
    tier_original = Column(VARCHAR(255))
    star_name = Column(VARCHAR(255))
    eta = Column(VARCHAR(255))
    status = Column(VARCHAR(255))
    warframe_fissures_message = relationship(
        "WarframeFissuresMessage",
        backref="warframe_fissures_detail",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class WarframeFissuresChannel(Base):
    __tablename__ = "warframe_fissures_channel"
    channel_id = Column(BIGINT, primary_key=True)
    warframe_fissures_message = relationship(
        "WarframeFissuresMessage",
        backref="warframe_fissures_id",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    region = Column(
        VARCHAR(255),
        ForeignKey("guilds.region", onupdate="CASCADE", ondelete="CASCADE"),
        unique=True,
    )


class WarframeFissuresMessage(Base):
    __tablename__ = "warframe_fissures_message"
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    detail_id = Column(
        BIGINT,
        ForeignKey("warframe_fissures_detail.id",
                   onupdate="CASCADE",
                   ondelete="CASCADE"),
    )
    channel_id = Column(
        BIGINT,
        ForeignKey(
            "warframe_fissures_channel.channel_id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )
    message_id = Column(BIGINT)
