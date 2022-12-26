from fastapi import APIRouter

from .account_books.api import account_book_router
from .auth.api import auth_router
from .share.api import share_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(account_book_router, prefix="/account-books")
api_router.include_router(share_router, prefix="/share")
