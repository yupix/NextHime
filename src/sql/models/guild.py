from sqlalchemy import Column, Integer, BIGINT, String, UniqueConstraint, VARCHAR
from sqlalchemy.orm import relationship

from NextHime import Base


class Guilds(Base):
    __tablename__ = "guilds"
    server_id = Column(BIGINT, primary_key=True)
    region = Column(VARCHAR(255), unique=True)
    warframe_fissures_channel = relationship(
        "WarframeFissuresChannel",
        backref="guilds",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

