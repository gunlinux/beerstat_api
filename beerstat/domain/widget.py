from dataclasses import dataclass


@dataclass(frozen=True)
class WidgetDTO:
    name: str
    timeout: int
    showtime: int
    template: str
    id: int | None = None
    order: int = 0
