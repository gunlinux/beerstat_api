from dataclasses import dataclass


@dataclass(frozen=True)
class WidgetDTO:
    id: int
    name: str
    timeout: int
    showtime: int
    template: str


@dataclass(frozen=True)
class WidgetStatDTO:
    timeout: int
    count: int
