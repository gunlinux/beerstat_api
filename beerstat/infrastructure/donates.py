from datetime import datetime

from aiosqlite import Connection

from beerstat.domain.donate import DonateDTO
from beerstat.infrastructure.exceptions import RepoError


class DonateRepo:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    async def add_balance(self, name: str, value: float, date: datetime) -> DonateDTO:
        cursor = await self.connection.execute(
            "INSERT INTO donations (name, value, date) VALUES (?, ?, ?) RETURNING id, name, date, value",
            (name, value, date),
        )
        async with cursor:
            if result := await cursor.fetchone():
                return DonateDTO(
                    id=result[0], name=result[1], date=result[2], value=result[3]
                )
        raise RepoError

    async def get_balance(self) -> float | None:
        async with await self.connection.execute(
            "SELECT SUM(value) FROM donations"
        ) as cursor:
            if row := await cursor.fetchone():
                return row[0]
        return None

    async def get_last(self, limit: int) -> list[DonateDTO]:
        async with await self.connection.execute(
            "SELECT id, name, date, value FROM donations WHERE value > 0 ORDER BY date DESC LIMIT ?",
            (limit,),
        ) as cursor:
            rows = await cursor.fetchall()
        return [DonateDTO(id=r[0], name=r[1], date=r[2], value=r[3]) for r in rows]

    async def count(self) -> int:
        async with await self.connection.execute(
            "SELECT COUNT(*) FROM donations"
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def get_page(self, offset: int, limit: int) -> list[DonateDTO]:
        async with await self.connection.execute(
            "SELECT id, name, date, value FROM donations ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ) as cursor:
            rows = await cursor.fetchall()
        return [DonateDTO(id=r[0], name=r[1], date=r[2], value=r[3]) for r in rows]

    async def get_by_id(self, donate_id: int) -> DonateDTO:
        async with await self.connection.execute(
            "SELECT id, name, date, value FROM donations WHERE id = ?",
            (donate_id,),
        ) as cursor:
            row = await cursor.fetchone()
        if row is None:
            raise RepoError
        return DonateDTO(id=row[0], name=row[1], date=row[2], value=row[3])

    async def update(
        self, donate_id: int, name: str, value: float, date: datetime
    ) -> DonateDTO:
        async with await self.connection.execute(
            "UPDATE donations SET name=?, value=?, date=? WHERE id=? RETURNING id, name, date, value",
            (name, value, date, donate_id),
        ) as cursor:
            if result := await cursor.fetchone():
                return DonateDTO(
                    id=result[0], name=result[1], date=result[2], value=result[3]
                )
        raise RepoError

    async def delete(self, donate_id: int) -> None:
        async with await self.connection.execute(
            "DELETE FROM donations WHERE id=?",
            (donate_id,),
        ) as cursor:
            if cursor.rowcount == 0:
                raise RepoError
