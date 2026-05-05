from datetime import datetime

from pydantic import BaseModel


class Donate(BaseModel):
    name: str
    value: float
    date: datetime | None = None


class DonateBalance(BaseModel):
    total: float
