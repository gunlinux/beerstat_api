from datetime import datetime

from pydantic import BaseModel


class Donate(BaseModel):
    name: str
    value: float
    date: datetime
    id: int | None = None


class DonateBalance(BaseModel):
    total: float


class Widget(BaseModel):
    name: str
    timeout: int
    showtime: int
    template: str
    id: int | None = None


class WidgetStat(BaseModel):
    sleep_time: int
    showtime: int
