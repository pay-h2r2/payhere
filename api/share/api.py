from api.share.util import get_short_url_return_data
from constants.short_url_setting import SHORT_URL_EXPIRE_MINUTES
from constants.http_response_detail import ERROR_EXPIRED_SHORT_URL
from db.models import AccountBookModel, ShortUrlModel
from db.connect import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from module.handler import auth_token_handler, check_own, check_exist
from sqlalchemy.orm import Session
from utils.random import random_url_generator
from utils.date import check_expired, get_expired_at, get_now
from .schemas import ShortUrl, ShortUrlCreate
from ..account_books.schemas import AccountBook

share_router = APIRouter()


@share_router.get("/{short_url}", dependencies=[Depends(auth_token_handler)])
def get_account_book_by_short_url(short_url: str, db: Session = Depends(get_db)):
    try:
        short_url_row: ShortUrl = db.query(ShortUrlModel).filter(
            ShortUrlModel.short_url == short_url).first()

        check_exist(short_url_row)

        if check_expired(short_url_row.expired_at):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_EXPIRED_SHORT_URL)

        return RedirectResponse(url=f"/api/account-books/{short_url_row.account_book_id}", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise


@share_router.post("")
def creaete_share_account_book(req: ShortUrlCreate,
                               user_id: int = Depends(auth_token_handler),
                               db: Session = Depends(get_db)):
    try:

        account_book_row: AccountBook = db.get(
            AccountBookModel, req.account_book_id)

        check_exist(account_book_row)
        check_own(account_book_row, user_id)

        short_url_row: ShortUrl = db.query(ShortUrlModel).filter(
            ShortUrlModel.account_book_id == req.account_book_id).first()

        random_str = random_url_generator.generate_random_str()
        expired_at = get_expired_at(get_now(), SHORT_URL_EXPIRE_MINUTES)

        if short_url_row:
            is_expired = check_expired(short_url_row.expired_at)

            if not is_expired:
                return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(
                    get_short_url_return_data(short_url_row.short_url, short_url_row.expired_at))
                )

            short_url_row.short_url = random_str
            short_url_row.expired_at = expired_at
            db.commit()
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(
                get_short_url_return_data(random_str, expired_at))
            )

        short_url_model = ShortUrlModel(
            account_book_id=req.account_book_id,
            short_url=random_str,
            expired_at=expired_at
        )

        db.add(short_url_model)
        db.commit()
        db.refresh(short_url_model)

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(
            get_short_url_return_data(
                short_url_model.short_url, short_url_model.expired_at)
        ))

    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise ex
