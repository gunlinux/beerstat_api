from aiosqlite import Connection
from beerstat.domain.widget import WidgetDTO

from beerstat.repo.exceptions import RepoError


class WidgetRepo:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    async def add(
        self, name: str, timeout: int, showtime: int, template: str
    ) -> WidgetDTO:
        cursor = await self.connection.execute(
            "INSERT INTO widgets (name, timeout, showtime, template) VALUES (?, ?, ?, ?) RETURNING id, name, timeout, showtime, template",
            (name, timeout, showtime, template),
        )
        async with cursor:
            if result := await cursor.fetchone():
                return WidgetDTO(
                    id=result[0],
                    name=result[1],
                    timeout=result[2],
                    showtime=result[3],
                    template=result[4],
                )
        raise RepoError

    async def get_by_id(self, widget_id: int) -> WidgetDTO:
        async with await self.connection.execute(
            "SELECT id, name, timeout, showtime, template FROM widgets WHERE id = ?",
            (widget_id,),
        ) as cursor:
            if result := await cursor.fetchone():
                return WidgetDTO(
                    id=result[0],
                    name=result[1],
                    timeout=result[2],
                    showtime=result[3],
                    template=result[4],
                )
        raise RepoError

    async def get_all(self) -> list[WidgetDTO]:
        async with await self.connection.execute(
            "SELECT id, name, timeout, showtime, template FROM widgets"
        ) as cursor:
            return [
                WidgetDTO(
                    id=row[0],
                    name=row[1],
                    timeout=row[2],
                    showtime=row[3],
                    template=row[4],
                )
                for row in await cursor.fetchall()
            ]
