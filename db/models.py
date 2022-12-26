from .connect import Base

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import Integer, DateTime
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True)
    email = Column(VARCHAR(255), nullable=False, unique=True, index=True)
    hashed_password = Column(VARCHAR(60), nullable=False)
    salt = Column(VARCHAR(30), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class AccountBookModel(Base):
    __tablename__ = "account_books"

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    spent_amount = Column(BIGINT(unsigned=True), nullable=False)
    memo = Column(VARCHAR(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class ShortUrlModel(Base):
    __tablename__ = "short_urls"

    id = Column(Integer, autoincrement=True, primary_key=True)
    account_book_id = Column(Integer, ForeignKey(
        "account_books.id"), nullable=False)
    short_url = Column(VARCHAR(10), nullable=False, unique=True)
    expired_at = Column(DateTime, nullable=False)
