from datetime import datetime

from pydantic import BaseModel


class Donate(BaseModel):
    name: str
    value: float
    date: datetime


class DonateBalance(BaseModel):
    total: float


class Widget(BaseModel):
    name: str
    timeout: int
    showtime: int
    template: str
    sleep: int | None = None
    id: int | None = None


class WidgetStat(BaseModel):
    sleep_time: int
    showtime: int
