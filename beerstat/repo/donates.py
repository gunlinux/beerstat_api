from dataclasses import dataclass
from datetime import datetime
from aiosqlite import Connection
from beerstat.domain.donate import DonateDTO
from beerstat.repo.exceptions import RepoError


@dataclass
class DonateRepo:
    connection: Connection

    async def add_balance(self, name: str, value: float, date: datetime) -> DonateDTO:
        cursor = await self.connection.execute(
            "INSERT INTO donations (name, value, date) VALUES (?, ?, ?) RETURNING id, name, date, value",
            (name, value, date),
        )
        async with cursor:
            if result := await cursor.fetchone():
                await self.connection.commit()
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
