from datetime import datetime
from typing import Protocol

from beerstat.domain.donate import DonateDTO
from beerstat.domain.widget import WidgetDTO


class DonateRepoPort(Protocol):
    async def add_balance(
        self, name: str, value: float, date: datetime
    ) -> DonateDTO: ...

    async def get_balance(self) -> float | None: ...

    async def get_last(self, limit: int) -> list[DonateDTO]: ...


class WidgetRepoPort(Protocol):
    async def add(
        self, name: str, timeout: int, showtime: int, template: str
    ) -> WidgetDTO: ...

    async def get_by_id(self, widget_id: int) -> WidgetDTO: ...

    async def get_all(self) -> list[WidgetDTO]: ...
