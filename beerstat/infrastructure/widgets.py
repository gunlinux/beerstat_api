from aiosqlite import Connection

from beerstat.domain.widget import WidgetDTO
from beerstat.infrastructure.exceptions import RepoError


class WidgetRepo:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    async def add(
        self, name: str, timeout: int, showtime: int, template: str, order: int = 0
    ) -> WidgetDTO:
        cursor = await self.connection.execute(
            'INSERT INTO widgets (name, timeout, showtime, template, "order") VALUES (?, ?, ?, ?, ?) RETURNING id, name, timeout, showtime, template, "order"',
            (name, timeout, showtime, template, order),
        )
        async with cursor:
            if result := await cursor.fetchone():
                return WidgetDTO(
                    id=result[0],
                    name=result[1],
                    timeout=result[2],
                    showtime=result[3],
                    template=result[4],
                    order=result[5],
                )
        raise RepoError

    async def get_by_id(self, widget_id: int) -> WidgetDTO:
        async with await self.connection.execute(
            'SELECT id, name, timeout, showtime, template, "order" FROM widgets WHERE id = ?',
            (widget_id,),
        ) as cursor:
            if result := await cursor.fetchone():
                return WidgetDTO(
                    id=result[0],
                    name=result[1],
                    timeout=result[2],
                    showtime=result[3],
                    template=result[4],
                    order=result[5],
                )
        raise RepoError

    async def update(
        self,
        widget_id: int,
        name: str,
        timeout: int,
        showtime: int,
        template: str,
        order: int = 0,
    ) -> WidgetDTO:
        async with await self.connection.execute(
            'UPDATE widgets SET name=?, timeout=?, showtime=?, template=?, "order"=? WHERE id=? RETURNING id, name, timeout, showtime, template, "order"',
            (name, timeout, showtime, template, order, widget_id),
        ) as cursor:
            if result := await cursor.fetchone():
                return WidgetDTO(
                    id=result[0],
                    name=result[1],
                    timeout=result[2],
                    showtime=result[3],
                    template=result[4],
                    order=result[5],
                )
        raise RepoError

    async def delete(self, widget_id: int) -> None:
        async with await self.connection.execute(
            "DELETE FROM widgets WHERE id=?",
            (widget_id,),
        ) as cursor:
            if cursor.rowcount == 0:
                raise RepoError

    async def get_all(self) -> list[WidgetDTO]:
        async with await self.connection.execute(
            'SELECT id, name, timeout, showtime, template, "order" FROM widgets ORDER BY "order", id'
        ) as cursor:
            return [
                WidgetDTO(
                    id=row[0],
                    name=row[1],
                    timeout=row[2],
                    showtime=row[3],
                    template=row[4],
                    order=row[5],
                )
                for row in await cursor.fetchall()
            ]
