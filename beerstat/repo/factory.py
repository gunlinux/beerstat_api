from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import cast

import aiosqlite
from aiosqlitepool import SQLiteConnectionPool

from beerstat.repo.donates import DonateRepo
from beerstat.repo.widgets import WidgetRepo


class RepoFactory:
    def __init__(self, pool: SQLiteConnectionPool):
        self._pool = pool

    @asynccontextmanager
    async def donate_repo(self) -> AsyncGenerator[DonateRepo]:
        async with self._pool.connection() as conn:
            yield DonateRepo(connection=cast(aiosqlite.Connection, conn))

    @asynccontextmanager
    async def widget_repo(self) -> AsyncGenerator[WidgetRepo]:
        async with self._pool.connection() as conn:
            yield WidgetRepo(connection=cast(aiosqlite.Connection, conn))
