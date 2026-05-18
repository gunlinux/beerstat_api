from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DonateDTO:
    id: int
    name: str
    date: datetime | None
    value: float | None


@dataclass(frozen=True)
class DonateBalanceDTO:
    total: float
