from constants.http_response_detail import ERROR_ACCESS_DENIED
from db.models import AccountBookModel, ShortUrlModel
from db.connect import get_db
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from module.handler import auth_token_handler, check_exist, check_own
from sqlalchemy.orm import Session
from utils.url_validate import check_from_redirect, check_verify_short_url_referer
from .schemas import AccountBook, AccountBookCreate, AccountBookPatch, AccountBookDuplicate
from ..share.schemas import ShortUrl

account_book_router = APIRouter()


@account_book_router.get("")
def get_all_history(user_id: str = Depends(auth_token_handler), db: Session = Depends(get_db)):
    try:
        query_response = db.query(AccountBookModel).filter(
            AccountBookModel.user_id == user_id).all()

        if not query_response:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

        return JSONResponse(content=jsonable_encoder(query_response), status_code=status.HTTP_200_OK)
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex

        raise


@account_book_router.get("/{account_book_id}")
def get_history(req: Request,
                account_book_id: int,
                user_id: str = Depends(auth_token_handler),
                db: Session = Depends(get_db)):
    try:
        history_row = db.get(AccountBookModel, account_book_id)
        check_exist(history_row)

        referer = req.headers.get("referer")
        if referer and referer.find('/'):
            parsed_referer = referer.split('/')
            if check_from_redirect(parsed_referer[-2]) and check_verify_short_url_referer(parsed_referer[-1]):
                short_url_row: ShortUrl = db.query(ShortUrlModel).filter(
                    ShortUrlModel.short_url == parsed_referer[-1]).first()

                check_exist(short_url_row)

                if short_url_row.account_book_id != account_book_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_ACCESS_DENIED)

                return JSONResponse(content=jsonable_encoder(history_row), status_code=status.HTTP_200_OK)

        check_own(history_row, user_id)

        return JSONResponse(content=jsonable_encoder(history_row), status_code=status.HTTP_200_OK)
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise


@account_book_router.post("")
def create_history(req: AccountBookCreate,
                   user_id: str = Depends(auth_token_handler),
                   db: Session = Depends(get_db)):
    try:
        account_book_model = AccountBookModel(
            user_id=user_id,
            spent_amount=req.spent_amount,
            memo=req.memo
        )

        db.add(account_book_model)
        db.commit()
        db.refresh(account_book_model)

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"account_book_id": account_book_model.id})
    except:
        raise


@account_book_router.post('/duplicate')
def duplicate_history(req: AccountBookDuplicate,
                      user_id: int = Depends(auth_token_handler),
                      db: Session = Depends(get_db)):
    try:
        origin_history_row: AccountBook = db.get(
            AccountBookModel, req.target_account_book_id)

        check_exist(origin_history_row)
        check_own(origin_history_row, user_id)

        account_book_model = AccountBookModel(
            user_id=user_id,
            spent_amount=origin_history_row.spent_amount,
            memo=origin_history_row.memo
        )

        db.add(account_book_model)
        db.commit()
        db.refresh(account_book_model)

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"account_book_id": account_book_model.id})
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex

        raise


@account_book_router.patch("/{account_book_id}")
def patch_history(account_book_id: int,
                  req: AccountBookPatch,
                  user_id: str = Depends(auth_token_handler),
                  db: Session = Depends(get_db)):
    try:
        patch_history_row: AccountBook = db.get(
            AccountBookModel, account_book_id)

        check_exist(patch_history_row)
        check_own(patch_history_row, user_id)

        if req.memo:
            patch_history_row.memo = req.memo

        if req.spent_amount:
            patch_history_row.spent_amount = req.spent_amount

        db.commit()

        return Response(status_code=status.HTTP_200_OK)
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex

        raise


@account_book_router.delete("/{account_book_id}")
def delete_history(account_book_id: int,
                   user_id: str = Depends(auth_token_handler),
                   db: Session = Depends(get_db)):
    try:
        delete_history_row = db.get(AccountBookModel, account_book_id)

        check_exist(delete_history_row)
        check_own(delete_history_row, user_id)

        db.delete(delete_history_row)
        db.commit()

        return Response(status_code=status.HTTP_200_OK)
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex
        raise
