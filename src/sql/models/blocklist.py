from sqlalchemy import Column, ForeignKey, Integer, String, INT, VARCHAR, BIGINT, Table
from sqlalchemy.orm import relationship

from NextHime import Base


class BlocklistServer(Base):
    __tablename__ = "blocklist_server"
    server_id = Column(BIGINT, primary_key=True)
    blocklist_settings = relationship(
        "BlocklistSettings",
        backref="blocklist_settings",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class BlocklistSettings(Base):
    __tablename__ = "blocklist_settings"
    server_id = Column(
        BIGINT,
        ForeignKey(
            "blocklist_server.server_id", onupdate="CASCADE", ondelete="CASCADE"
        ),
        primary_key=True,
    )
    mode = Column(VARCHAR(255))
    add_role = Column(VARCHAR(255))
    remove_role = Column(VARCHAR(255))


class BlocklistUser(Base):
    __tablename__ = "blocklist_user"
    server_id = Column(
        BIGINT,
        ForeignKey(
            "blocklist_server.server_id", onupdate="CASCADE", ondelete="CASCADE"
        ),
    )
    user_id = Column(BIGINT, primary_key=True)
    mode = Column(VARCHAR(255))
