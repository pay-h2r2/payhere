from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AccountBookBase(BaseModel):
    spent_amount: int
    memo: str


class AccountBookDuplicate(BaseModel):
    target_account_book_id: int


class AccountBookPatch(BaseModel):
    spent_amount: Optional[str]
    memo: Optional[str]


class AccountBookCreate(AccountBookBase):
    pass


class AccountBook(AccountBookBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
