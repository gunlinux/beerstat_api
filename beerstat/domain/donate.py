from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=False)
class DonateDTO:
    name: str
    value: float
    date: datetime
    id: int | None = None

    def __post_init__(self):
        self.name = self.name or "Anonym"


@dataclass(frozen=True)
class DonateBalanceDTO:
    total: float
