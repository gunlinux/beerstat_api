from dataclasses import dataclass

from beerstat.repo.exceptions import RepoError
from beerstat.repo.widgets import WidgetRepo
from beerstat.domain.widget import WidgetDTO
from beerstat.domain.exceptions import WidgetNotFoundError


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
        try:
            return await self.repo.get_by_id(widget_id=widget_id)
        except RepoError:
            raise WidgetNotFoundError


@dataclass
class GetWidgets:
    repo: WidgetRepo

    async def execute(self) -> list[WidgetDTO]:
        return await self.repo.get_all()
