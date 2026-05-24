import os
from collections.abc import Callable, Awaitable
from random import randint

import pytest_asyncio

from aiosqlitepool import SQLiteConnectionPool
import aiosqlite
from httpx import ASGITransport, AsyncClient
from beerstat.repo.factory import RepoFactory
from beerstat.api.deps import sqlite_connection

from beerstat import create_app
from beerstat.settings import Settings


def get_temp_db_name() -> str:
    return f"test_db_{randint(0, 999999)}.db"


def migrate(temp_db):
    from yoyo import read_migrations
    from yoyo import get_backend

    backend = get_backend(f"sqlite:///{temp_db}")
    migrations = read_migrations("./migrations")

    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))


def get_app_settings():
    mysettings = Settings.model_validate(({}))
    mysettings.sqlite_uri = get_temp_db_name()
    return mysettings


@pytest_asyncio.fixture(scope="function")
async def db_connection():
    app_settings = get_app_settings()
    migrate(app_settings.sqlite_uri)
    connection = await sqlite_connection(app_settings.sqlite_uri)

    yield connection

    await connection.close()
    os.remove(app_settings.sqlite_uri)


@pytest_asyncio.fixture(scope="function")
async def client():
    """TestClient with an in-memory DB pool for integration tests."""
    from contextlib import asynccontextmanager

    app_settings = get_app_settings()

    def sql_setup_connection(uri: str) -> Callable[[], Awaitable[aiosqlite.Connection]]:
        async def inner() -> aiosqlite.Connection:
            return await sqlite_connection(uri)

        return inner

    @asynccontextmanager
    async def test_lifespan(app):
        app.state.settings = app_settings
        migrate(app_settings.sqlite_uri)
        f = sql_setup_connection(app_settings.sqlite_uri)
        db_pool = SQLiteConnectionPool(
            connection_factory=f,  # pyright: ignore[reportArgumentType]
            pool_size=10,
        )  # pyright: ignore[reportArgumentType]
        app.state.db_pool = db_pool
        app.state.settings = app_settings
        app.state.repo_factory = RepoFactory()

        yield

        await db_pool.close()
        os.remove(app_settings.sqlite_uri)

    app = create_app(test_lifespan)
    lifespan_cm = app.router.lifespan_context(app)
    await lifespan_cm.__aenter__()  # type: ignore[attr-defined]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await lifespan_cm.__aexit__(None, None, None)  # type: ignore[attr-defined]
