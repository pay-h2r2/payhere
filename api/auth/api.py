from db.models import UserModel
from constants.http_response_detail import ERROR_ACCESS_TOKEN_NOT_EXPIRED, ERROR_ALREADY_LOGOUT, ERROR_NOT_AN_EMAIL_FORMAT, ERROR_NOT_EXIST_ACCOUNT, ERROR_OLD_TOKEN, ERROR_WRONG_PASSWORD, ERROR_PASSWORD_MIN_LENGTH, ERROR_INTEGRITY
from db.connect import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordBearer
from module.jwt import create_access_token, create_refresh_token, is_expired_jwt, verify_jwt
from sqlalchemy.orm import Session
from utils.hash import check_password_hash, create_random_salt, create_password_hash
from utils.email_validate import is_email
from utils.user_tokens import user_tokens
from .constants import PASSWORD_MIN_LENGTH
from .schemas import UserLogin, User, UserCreate

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@auth_router.post("")
def create_user(req: UserCreate, db: Session = Depends(get_db)):
    try:
        if not is_email(req.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_NOT_AN_EMAIL_FORMAT)

        if len(req.password) < PASSWORD_MIN_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_PASSWORD_MIN_LENGTH)

        query_response = db.query(UserModel).filter(
            UserModel.email == req.email).first()

        if query_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_INTEGRITY)

        salt = create_random_salt()
        hashed_password = create_password_hash(req.password, salt)

        user_model = UserModel(
            email=req.email,
            hashed_password=hashed_password,
            salt=salt
        )

        db.add(user_model)
        db.commit()

        return Response(status_code=status.HTTP_201_CREATED)
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex

        raise


@auth_router.post("/login")
def login(req: UserLogin, db: Session = Depends(get_db)):
    try:
        if not is_email(req.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_NOT_AN_EMAIL_FORMAT)

        query_response: User = db.query(UserModel).filter(
            UserModel.email == req.email).first()

        if not query_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_NOT_EXIST_ACCOUNT)

        if not check_password_hash(req.password, query_response.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_WRONG_PASSWORD)

        result = {
            "access_token": create_access_token(query_response.id),
            "refresh_token": create_refresh_token(query_response.id)
        }

        user_tokens.set_user_token(query_response.id, result)
        return JSONResponse(result, status_code=status.HTTP_200_OK)
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex

        raise


@auth_router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    try:
        verify_result = verify_jwt(token, True)

        user_id = verify_result.get("user_id")

        if not user_tokens.get_is_login(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_ALREADY_LOGOUT)

        if not user_tokens.verify_token(user_id, token, True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_OLD_TOKEN)

        user_tokens.delete_user_token(user_id)

        return Response(status_code=status.HTTP_200_OK)
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex

        raise


@auth_router.post("/refresh")
def refresh(token: str = Depends(oauth2_scheme)):
    try:
        verify_result = verify_jwt(token, False)

        user_id = verify_result.get("user_id")

        if not user_tokens.verify_token(user_id, token, False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_OLD_TOKEN)

        if not is_expired_jwt(user_tokens.get_user_access_token(user_id)):
            user_tokens.delete_user_token(user_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_ACCESS_TOKEN_NOT_EXPIRED)

        result = {
            "access_token": create_access_token(user_id),
        }

        user_tokens.set_user_token(user_id, result)
        return JSONResponse(result, status_code=status.HTTP_200_OK)
    except Exception as ex:
        if isinstance(ex, HTTPException):
            raise ex

        raise
