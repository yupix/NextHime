from psycopg2.sql import NULL
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    BIGINT,
    UniqueConstraint,
    JSON,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import current_timestamp

from NextHime import Base


class GuildBlogs(Base):
    __tablename__ = "guild_blogs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BIGINT, unique=True)
    blogs_category = relationship(
        "BlogsCategory", backref="guild_blogs", lazy="dynamic"
    )
    replay_channel_id = Column(BIGINT, nullable=True)


class BlogsCategory(Base):
    __tablename__ = "blogs_category"
    __table_args__ = (UniqueConstraint("category_id"),)

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    guild_id = Column(
        BIGINT,
        ForeignKey("guild_blogs.guild_id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    category_id = Column(BIGINT)
    blogs_channel = relationship(
        "BlogsChannel", backref="blogs_category", lazy="dynamic"
    )


class BlogsChannel(Base):
    __tablename__ = "blogs_channel"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(
        BIGINT,
        ForeignKey(
            "blogs_category.category_id", onupdate="CASCADE", ondelete="CASCADE"
        ),
    )
    channel_id = Column(BIGINT, unique=True)
    owner_id = Column(BIGINT)
    sub_user_list = Column(JSON)
    xp = Column(BIGINT)
    level = Column(BIGINT)
    blogs_user = relationship("BlogsUser", backref="blogs_channel", lazy="dynamic")


class BlogsUser(Base):
    __tablename__ = "blogs_user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(
        BIGINT,
        ForeignKey("blogs_channel.channel_id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    user_id = Column(BIGINT)
    xp = Column(BIGINT, default=0)
    level = Column(BIGINT, default=1)
    post_count = Column(BIGINT, default=0)
    joined_at = Column(TIMESTAMP, server_default=current_timestamp())
