from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DonateDTO:
    name: str
    value: float
    date: datetime
    id: int | None = None
    commentary: str | None = None

    def __post_init__(self):
        object.__setattr__(self, "name", self.name or "Anonym")


@dataclass(frozen=True)
class DonateBalanceDTO:
    total: float


@dataclass(frozen=True)
class DonatorSummaryDTO:
    name: str
    total: float
