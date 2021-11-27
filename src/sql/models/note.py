from sqlalchemy import BIGINT, VARCHAR, Column, ForeignKey, Integer, UniqueConstraint

from NextHime import Base


class NotesUser(Base):
    __tablename__ = "notes_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, unique=True)

    def __repl__(self):
        return f"NotesUser(id={self.id}, user_id={self.user_id})"


class NotesCategory(Base):
    __tablename__ = "notes_category"
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    category_name = Column(VARCHAR(255), unique=True)

    def __repl__(self):
        return f"NotesCategory(id={self.id}, category_name={self.category_name})"


class NotesDetail(Base):
    __tablename__ = "notes_detail"
    __table_args__ = (UniqueConstraint("user_id", "content",
                                       "category_name"), )

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(
        BIGINT,
        ForeignKey("notes_user.user_id",
                   onupdate="CASCADE",
                   ondelete="CASCADE"))
    content = Column(VARCHAR(255))
    category_name = Column(VARCHAR(255))

    def __repl__(self):
        return f"NotesDetail(id={self.id}, user_id={self.user_id}, content={self.content}, category_name={self.category_name})"
