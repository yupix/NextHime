from sqlalchemy import BIGINT, Column, String
from NextHime import Base


class Users(Base):
    __tablename__ = 'users'
    user_id = Column(BIGINT, primary_key=True)
    locale = Column(String)
    hts_voice = Column(String)
