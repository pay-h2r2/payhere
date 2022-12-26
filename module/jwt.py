import jwt
from datetime import datetime, timedelta
from constants.http_response_detail import ERROR_EXPIRED_SIGNATURE, ERROR_INVAILD_TOKEN
from constants.jwt_setting import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_SECRET_KEY, ALGORITHM, JWT_REFRESH_SECRET_KEY, REFRESH_TOKEN_EXPIRE_MINUTES
from fastapi import HTTPException, status


def create_access_token(user_id: int) -> str:
    expired_at = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"exp": expired_at, "user_id": user_id}

    result = jwt.encode(payload, JWT_SECRET_KEY, ALGORITHM)

    return result


def create_refresh_token(user_id: int) -> str:
    expired_at = datetime.now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    payload = {"exp": expired_at, "user_id": user_id}

    result = jwt.encode(payload, JWT_REFRESH_SECRET_KEY, ALGORITHM)

    return result


def is_expired_jwt(access_token: str) -> bool:
    try:
        jwt.decode(access_token, JWT_SECRET_KEY, ALGORITHM)

        return False
    except:
        return True


def verify_jwt(token: str, is_access: bool):
    try:
        result = None
        if is_access:
            result = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
        else:
            result = jwt.decode(token, JWT_REFRESH_SECRET_KEY, ALGORITHM)

        return result
    except Exception as ex:
        if isinstance(ex, jwt.ExpiredSignatureError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_EXPIRED_SIGNATURE)

        if isinstance(ex, jwt.InvalidTokenError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_INVAILD_TOKEN)

        raise
