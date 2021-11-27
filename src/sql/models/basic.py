from sqlalchemy import (
    Column,
    Integer,
    VARCHAR,
    BIGINT,
    UniqueConstraint,
    JSON,
)

from NextHime import Base


class Reactions(Base):
    __tablename__ = "reactions"
    __table_args__ = (UniqueConstraint(
        "guild_id", "channel_id", "message_id"),)

    id = Column(Integer, autoincrement=True, primary_key=True)
    guild_id = Column(BIGINT)
    channel_id = Column(BIGINT)
    message_id = Column(BIGINT)
    type = Column(VARCHAR(255))
    action = Column(VARCHAR(255))
    content = Column(JSON)
    module_path = Column(VARCHAR(255))
    class_name = Column(VARCHAR(255))
