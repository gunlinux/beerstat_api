from dataclasses import dataclass

from beerstat.repo.widgets import WidgetRepo
from beerstat.domain.widget import WidgetDTO, WidgetStatDTO


@dataclass
class CreateWidget:
    repo: WidgetRepo

    async def execute(self, widget: WidgetDTO) -> WidgetDTO:
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


@dataclass
class GetWidgets:
    repo: WidgetRepo

    async def execute(self) -> list[WidgetDTO]:
        return await self.repo.get_all()


@dataclass
class GetWidgetsStat:
    repo: WidgetRepo

    async def execute(self) -> WidgetStatDTO:
        timeout, count = await self.repo.get_stat()
        return WidgetStatDTO(timeout=timeout, count=count)
