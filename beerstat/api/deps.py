from typing import AsyncGenerator

from fastapi import Request, Depends
import aiosqlite


async def sqlite_connection(db_uri: str) -> aiosqlite.Connection:
    """A factory for creating new connections."""
    conn = await aiosqlite.connect(db_uri)
    return conn


async def get_db_connection(
    request: Request,
) -> AsyncGenerator[aiosqlite.Connection, None]:
    """
    A dependency that provides a connection from the pool.
    It accesses the pool from the application state.
    """
    db_pool = request.app.state.db_pool

    async with db_pool.connection() as conn:
        yield conn


async def get_donate_repo(
    request: Request, db_conn: aiosqlite.Connection = Depends(get_db_connection)
):
    return request.app.state.repo_factory.donate_repo(db_conn)


async def get_widget_repo(
    request: Request, db_conn: aiosqlite.Connection = Depends(get_db_connection)
):
    return request.app.state.repo_factory.widget_repo(db_conn)
