from contextlib import asynccontextmanager

from aiosqlitepool import SQLiteConnectionPool
from fastapi import FastAPI
from beerstat.api.v1.donates import donates_router
from beerstat.api.deps import sqlite_connection
from beerstat.settings import Settings


async def sql_setup_connection():
    return await sqlite_connection(Settings().sqlite_uri)  # pyright: ignore[reportCallIssue]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the connection pool's lifecycle.
    The pool is created when the application starts and gracefully closed when it stops.
    """
    db_pool = SQLiteConnectionPool(connection_factory=sql_setup_connection, pool_size=10)  # pyright: ignore[reportArgumentType]
    app.state.db_pool = db_pool
    yield
    await db_pool.close()


def create_app(lifespan) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(donates_router)

    return app


app = create_app(lifespan=lifespan)
