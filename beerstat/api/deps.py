from collections.abc import AsyncGenerator

from fastapi import Request
import aiosqlite

from beerstat.repo.donates import DonateRepo
from beerstat.repo.factory import RepoFactory
from beerstat.repo.widgets import WidgetRepo
from beerstat.settings import Settings


async def sqlite_connection(db_uri: str) -> aiosqlite.Connection:
    """A factory for creating new connections."""
    conn = await aiosqlite.connect(db_uri)
    await conn.execute("PRAGMA foreign_keys = ON")
    await conn.execute("PRAGMA journal_mode = WAL")
    conn.row_factory = aiosqlite.Row
    return conn


async def get_settings(request: Request) -> Settings:
    return request.app.state.settings


async def get_donate_repo(request: Request) -> AsyncGenerator[DonateRepo, None]:
    factory: RepoFactory = request.app.state.repo_factory
    async with factory.donate_repo() as repo:
        yield repo


async def get_widget_repo(request: Request) -> AsyncGenerator[WidgetRepo, None]:
    factory: RepoFactory = request.app.state.repo_factory
    async with factory.widget_repo() as repo:
        yield repo
