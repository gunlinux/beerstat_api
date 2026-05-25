from collections.abc import Awaitable, Callable

import aiosqlite

from beerstat.settings import Settings


async def sqlite_connection(db_uri: str) -> aiosqlite.Connection:
    conn = await aiosqlite.connect(db_uri)
    await conn.execute("PRAGMA foreign_keys = ON")
    await conn.execute("PRAGMA journal_mode = WAL")
    conn.row_factory = aiosqlite.Row
    return conn


def make_connection_factory(
    settings: Settings,
) -> Callable[[], Awaitable[aiosqlite.Connection]]:
    async def factory() -> aiosqlite.Connection:
        return await sqlite_connection(settings.sqlite_uri)

    return factory
