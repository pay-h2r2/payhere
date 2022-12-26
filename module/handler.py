from .jwt import verify_jwt
from constants.http_response_detail import ERROR_NOT_YOUR_DATA, ERROR_NOT_EXIST_DATA
from fastapi import HTTPException, status
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.user_tokens import user_tokens
from constants.http_response_detail import ERROR_OLD_TOKEN

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def auth_token_handler(token: str = Depends(oauth2_scheme)):
    verify_result = verify_jwt(token, True)
    user_id = verify_result.get("user_id")
    if not user_tokens.verify_token(user_id, token, True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_OLD_TOKEN)

    return user_id


def check_exist(row: any):
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_NOT_EXIST_DATA)


def check_own(row: any, user_id: int):
    if row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_NOT_YOUR_DATA)
