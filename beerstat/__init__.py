from contextlib import asynccontextmanager

import aiosqlite
from aiosqlitepool import SQLiteConnectionPool
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from beerstat.api.v1.donates import donates_router
from beerstat.api.v1.widgets import widgets_router
from beerstat.api.v1.widgets_page import widgets_page
from beerstat.api.deps import sqlite_connection
from beerstat.settings import Settings


app_settings = Settings.model_validate({})


async def sql_setup_connection() -> aiosqlite.Connection:
    return await sqlite_connection(app_settings.sqlite_uri)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the connection pool's lifecycle.
    The pool is created when the application starts and gracefully closed when it stops.
    """
    db_pool = SQLiteConnectionPool(
        connection_factory=sql_setup_connection,  # pyright: ignore[reportArgumentType]
        pool_size=10,
    )  # pyright: ignore[reportArgumentType]
    app.state.db_pool = db_pool
    yield
    await db_pool.close()


def create_app(lifespan) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(donates_router)
    app.include_router(widgets_router, prefix="/widget")
    app.include_router(widgets_page, prefix="/page")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    return app


app = create_app(lifespan=lifespan)
