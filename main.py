from db.connect import Base, engine

from api import api_router
from fastapi import FastAPI
from middleware.exception import catch_exceptions_middleware


app = FastAPI()


def include_router():
    app.include_router(api_router, prefix="/api")


def set_middleware():
    app.middleware('http')(catch_exceptions_middleware)


def create_table():
    Base.metadata.create_all(bind=engine)


def start_app():
    create_table()
    set_middleware()
    include_router()


start_app()
