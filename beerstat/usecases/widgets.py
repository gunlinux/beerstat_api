from dataclasses import dataclass

from beerstat.models import Widget
from beerstat.repo.widgets import WidgetRepo
from beerstat.domain.widget import WidgetDTO


@dataclass
class CreateWidget:
    repo: WidgetRepo

    async def execute(self, widget: Widget) -> WidgetDTO:
        return await self.repo.add(
            name=widget.name,
            timeout=widget.timeout,
            showtime=widget.showtime,
            template=widget.template,
        )


@dataclass
class GetWidget:
    repo: WidgetRepo

    async def execute(self, widget_id: int) -> WidgetDTO:
        return await self.repo.get_by_id(widget_id=widget_id)
