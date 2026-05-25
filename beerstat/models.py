from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from beerstat.domain.donate import DonateDTO, DonateBalanceDTO
    from beerstat.domain.widget import WidgetDTO


class DonateCreateIn(BaseModel):
    name: str
    value: float = Field(gt=0)
    date: datetime

    def to_dto(self) -> DonateDTO:
        from beerstat.domain.donate import DonateDTO

        return DonateDTO(name=self.name, value=self.value, date=self.date)


class DonateOut(BaseModel):
    id: int
    name: str
    value: float
    date: datetime

    @classmethod
    def from_dto(cls, dto: DonateDTO) -> DonateOut:
        return cls(**asdict(dto))


class DonateBalance(BaseModel):
    total: float

    @classmethod
    def from_dto(cls, dto: DonateBalanceDTO) -> DonateBalance:
        return cls(**asdict(dto))


class WidgetCreateIn(BaseModel):
    name: str
    timeout: int = Field(gt=0)
    showtime: int | None = Field(default=None, gt=0)
    template: str

    def to_dto(self, *, showtime_default: int) -> WidgetDTO:
        from beerstat.domain.widget import WidgetDTO

        return WidgetDTO(
            name=self.name,
            timeout=self.timeout,
            showtime=self.showtime if self.showtime is not None else showtime_default,
            template=self.template,
        )


class WidgetOut(BaseModel):
    id: int
    name: str
    timeout: int
    showtime: int
    template: str

    @classmethod
    def from_dto(cls, dto: WidgetDTO) -> WidgetOut:
        return cls(**asdict(dto))


class DonationsOut(BaseModel):
    donations: list[DonateOut]


class WidgetStat(BaseModel):
    sleep_time: int
    showtime: int
