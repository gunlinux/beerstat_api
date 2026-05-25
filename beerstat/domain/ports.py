from datetime import datetime
from typing import Protocol

from beerstat.domain.donate import DonateDTO, DonatorSummaryDTO
from beerstat.domain.widget import WidgetDTO


class DonateRepoPort(Protocol):
    async def add_balance(
        self, name: str, value: float, date: datetime
    ) -> DonateDTO: ...

    async def get_balance(self) -> float | None: ...

    async def get_last(self, limit: int) -> list[DonateDTO]: ...

    async def count(self) -> int: ...

    async def get_page(self, offset: int, limit: int) -> list[DonateDTO]: ...

    async def get_by_id(self, donate_id: int) -> DonateDTO: ...

    async def update(
        self, donate_id: int, name: str, value: float, date: datetime
    ) -> DonateDTO: ...

    async def delete(self, donate_id: int) -> None: ...

    async def get_top(
        self, limit: int, since: datetime | None = None
    ) -> list[DonatorSummaryDTO]: ...


class WidgetRepoPort(Protocol):
    async def add(
        self, name: str, timeout: int, showtime: int, template: str
    ) -> WidgetDTO: ...

    async def get_by_id(self, widget_id: int) -> WidgetDTO: ...

    async def get_all(self) -> list[WidgetDTO]: ...

    async def update(
        self, widget_id: int, name: str, timeout: int, showtime: int, template: str
    ) -> WidgetDTO: ...

    async def delete(self, widget_id: int) -> None: ...
