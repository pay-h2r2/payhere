from datetime import datetime
from constants.short_url_setting import SHORT_URL_EXPIRE_MINUTES
from pydantic import BaseModel


class ShortUrlCreate(BaseModel):
    account_book_id: int
    expire_minutes: int = SHORT_URL_EXPIRE_MINUTES


class ShortUrl(BaseModel):
    id: int
    account_book_id: int
    short_url: str
    expired_at: datetime

    class Config:
        orm_mode = True
