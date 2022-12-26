from starlette.requests import Request
from starlette.responses import Response
from constants.http_response_detail import ERROR_SERVER
from fastapi import status


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        return Response(ERROR_SERVER, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
