from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import cast

import aiosqlite
from aiosqlitepool import SQLiteConnectionPool

from beerstat.infrastructure.donates import DonateRepo
from beerstat.infrastructure.widgets import WidgetRepo


class RepoFactory:
    def __init__(self, pool: SQLiteConnectionPool):
        self._pool = pool

    @asynccontextmanager
    async def donate_repo(self) -> AsyncGenerator[DonateRepo]:
        async with self._pool.connection() as conn:
            c = cast(aiosqlite.Connection, conn)
            try:
                yield DonateRepo(connection=c)
            except Exception:
                await c.rollback()
                raise
            else:
                await c.commit()

    @asynccontextmanager
    async def widget_repo(self) -> AsyncGenerator[WidgetRepo]:
        async with self._pool.connection() as conn:
            c = cast(aiosqlite.Connection, conn)
            try:
                yield WidgetRepo(connection=c)
            except Exception:
                await c.rollback()
                raise
            else:
                await c.commit()
