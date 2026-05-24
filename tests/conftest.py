import os
from random import randint

import pytest_asyncio

from aiosqlitepool import SQLiteConnectionPool
from httpx import ASGITransport, AsyncClient
from beerstat.repo.factory import RepoFactory
from beerstat.api.deps import sqlite_connection

from beerstat import create_app, make_connection_factory
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
async def repo_factory():
    app_settings = get_app_settings()
    migrate(app_settings.sqlite_uri)
    pool = SQLiteConnectionPool(
        connection_factory=make_connection_factory(app_settings),  # pyright: ignore[reportArgumentType]
        pool_size=2,
    )  # pyright: ignore[reportArgumentType]

    yield RepoFactory(pool)

    await pool.close()
    os.remove(app_settings.sqlite_uri)


@pytest_asyncio.fixture(scope="function")
async def client():
    """TestClient with an in-memory DB pool for integration tests."""
    from contextlib import asynccontextmanager

    app_settings = get_app_settings()

    @asynccontextmanager
    async def test_lifespan(app):
        migrate(app_settings.sqlite_uri)
        db_pool = SQLiteConnectionPool(
            connection_factory=make_connection_factory(app_settings),  # pyright: ignore[reportArgumentType]
            pool_size=10,
        )  # pyright: ignore[reportArgumentType]
        app.state.db_pool = db_pool
        app.state.settings = app_settings
        app.state.repo_factory = RepoFactory(db_pool)

        yield

        await db_pool.close()
        os.remove(app_settings.sqlite_uri)

    app = create_app(test_lifespan)
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
