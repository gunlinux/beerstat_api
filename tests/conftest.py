import aiosqlite
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from beerstat import create_app
from beerstat.settings import Settings



@pytest.fixture
def app_settings():
    return Settings.model_validate(({}))


@pytest_asyncio.fixture
async def db_connection():
    """In-memory SQLite connection for repo/use-case tests."""
    return await aiosqlite.connect(":memory:")  # Должен дергать с пула!


@pytest_asyncio.fixture
async def client(app_settings):
    """TestClient with an in-memory DB pool for integration tests."""
    from beerstat.api.deps import sqlite_connection
    from contextlib import asynccontextmanager
    from aiosqlitepool import SQLiteConnectionPool

    async def sql_setup():
        return await sqlite_connection("sqlite:///:memory:")

    @asynccontextmanager
    async def test_lifespan(app):
        db_pool = SQLiteConnectionPool(
            connection_factory=sql_setup,  # pyright: ignore[reportArgumentType]
            pool_size=2,
        )
        app.state.db_pool = db_pool
        app.state.settings = app_settings

        yield
        await db_pool.close()

    app = create_app(test_lifespan)

    # Enter the lifespan to initialize db_pool
    lifespan_cm = app.router.lifespan_context(app)
    await lifespan_cm.__aenter__()  # type: ignore[attr-defined]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await lifespan_cm.__aexit__(None, None, None)  # type: ignore[attr-defined]
