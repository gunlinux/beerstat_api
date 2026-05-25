import os
import tempfile
from contextlib import contextmanager
from pathlib import Path

import pytest_asyncio

from aiosqlitepool import SQLiteConnectionPool
from httpx import ASGITransport, AsyncClient
from beerstat.infrastructure.factory import RepoFactory
from beerstat.infrastructure.sqlite import sqlite_connection

from beerstat import create_app, make_connection_factory
from beerstat.settings import Settings


def _migrate(db_path: str) -> None:
    from yoyo import read_migrations, get_backend

    backend = get_backend(f"sqlite:///{db_path}")
    migrations = read_migrations("./migrations")
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))


@contextmanager
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        _migrate(path)
        yield path
    finally:
        for suffix in ("", "-wal", "-shm"):
            Path(path + suffix).unlink(missing_ok=True)


def _make_settings(db_path: str) -> Settings:
    return Settings.model_validate({"sqlite_uri": db_path})


@pytest_asyncio.fixture(scope="function")
async def db_connection():
    with temp_db() as db_path:
        connection = await sqlite_connection(db_path)
        try:
            yield connection
        finally:
            await connection.close()


@pytest_asyncio.fixture(scope="function")
async def repo_factory():
    with temp_db() as db_path:
        settings = _make_settings(db_path)
        pool = SQLiteConnectionPool(
            connection_factory=make_connection_factory(settings),  # pyright: ignore[reportArgumentType]
            pool_size=2,
        )  # pyright: ignore[reportArgumentType]
        try:
            yield RepoFactory(pool)
        finally:
            await pool.close()


@pytest_asyncio.fixture(scope="function")
async def client():
    with temp_db() as db_path:
        settings = _make_settings(db_path)
        app = create_app(settings=settings)
        async with app.router.lifespan_context(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                yield ac
