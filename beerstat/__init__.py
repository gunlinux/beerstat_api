from typing import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import asdict

import aiosqlite
from aiosqlitepool import SQLiteConnectionPool
from aiosqlite import Connection
from fastapi import (
    Request,
    Depends,
    FastAPI,
    HTTPException,
)
from beerstat.domain.exceptions import DomainError
from beerstat.repo.donates import DonateRepo
from beerstat.models import Donate, DonateBalance
from beerstat.repo.exceptions import RepoError
from beerstat.usecases.donates import CreateDonate, GetBalance


async def sqlite_connection() -> aiosqlite.Connection:
    """A factory for creating new connections."""
    conn = await aiosqlite.connect("beer.db")
    return conn


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the connection pool's lifecycle.
    The pool is created when the application starts and gracefully closed when it stops.
    """
    db_pool = SQLiteConnectionPool(connection_factory=sqlite_connection, pool_size=10)  # pyright: ignore[reportArgumentType]
    app.state.db_pool = db_pool
    yield
    await db_pool.close()


app = FastAPI(lifespan=lifespan)


async def get_db_connection(request: Request) -> AsyncGenerator[Connection, None]:
    """
    A dependency that provides a connection from the pool.
    It accesses the pool from the application state.
    """
    db_pool = request.app.state.db_pool

    async with db_pool.connection() as conn:
        yield conn


@app.post("/donate", status_code=201)
async def donate(
    donate_data: Donate,
    db_conn: Connection = Depends(get_db_connection),
) -> Donate:
    try:
        result = Donate(
            **asdict(
                await CreateDonate(repo=DonateRepo(connection=db_conn)).execute(
                    donate_data
                )
            )
        )
    except RepoError:
        raise HTTPException(status_code=500)
    return result


@app.get("/balance")
async def get_donations(
    db_conn: Connection = Depends(get_db_connection),
) -> DonateBalance:
    try:
        return DonateBalance(
            **asdict(await GetBalance(repo=DonateRepo(connection=db_conn)).execute())
        )
    except DomainError:
        raise HTTPException(status_code=500)
    except RepoError:
        raise HTTPException(status_code=500)
