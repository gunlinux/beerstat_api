from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DonateDTO:
    name: str
    date: datetime | None
    value: float
    id: int | None = None


@dataclass(frozen=True)
class DonateBalanceDTO:
    total: float
