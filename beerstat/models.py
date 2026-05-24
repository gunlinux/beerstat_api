from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from beerstat.domain.donate import DonateDTO, DonateBalanceDTO
    from beerstat.domain.widget import WidgetDTO


class Donate(BaseModel):
    name: str
    value: float
    date: datetime
    id: int | None = None

    @classmethod
    def from_dto(cls, dto: DonateDTO) -> Donate:
        return cls(**asdict(dto))

    def to_dto(self) -> DonateDTO:
        from beerstat.domain.donate import DonateDTO

        return DonateDTO(name=self.name, value=self.value, date=self.date)


class DonateBalance(BaseModel):
    total: float

    @classmethod
    def from_dto(cls, dto: DonateBalanceDTO) -> DonateBalance:
        return cls(**asdict(dto))


class Widget(BaseModel):
    name: str
    timeout: int
    showtime: int | None = None
    template: str
    id: int | None = None

    @classmethod
    def from_dto(cls, dto: WidgetDTO) -> Widget:
        return cls(**asdict(dto))

    def to_dto(self, *, showtime_default: int) -> WidgetDTO:
        from beerstat.domain.widget import WidgetDTO

        return WidgetDTO(
            name=self.name,
            timeout=self.timeout,
            showtime=self.showtime if self.showtime is not None else showtime_default,
            template=self.template,
        )


class WidgetStat(BaseModel):
    sleep_time: int
    showtime: int
