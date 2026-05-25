from dataclasses import dataclass

from beerstat.domain.ports import WidgetRepoPort
from beerstat.infrastructure.exceptions import RepoError
from beerstat.domain.widget import WidgetDTO
from beerstat.domain.exceptions import WidgetNotFoundError, CreateError


@dataclass
class CreateWidget:
    repo: WidgetRepoPort

    async def execute(self, widget: WidgetDTO) -> WidgetDTO:
        try:
            return await self.repo.add(
                name=widget.name,
                timeout=widget.timeout,
                showtime=widget.showtime,
                template=widget.template,
                order=widget.order,
            )
        except RepoError:
            raise CreateError


@dataclass
class GetWidget:
    repo: WidgetRepoPort

    async def execute(self, widget_id: int) -> WidgetDTO:
        try:
            return await self.repo.get_by_id(widget_id=widget_id)
        except RepoError:
            raise WidgetNotFoundError


@dataclass
class GetWidgets:
    repo: WidgetRepoPort

    async def execute(self) -> list[WidgetDTO]:
        try:
            return await self.repo.get_all()
        except RepoError:
            raise CreateError


@dataclass
class UpdateWidget:
    repo: WidgetRepoPort

    async def execute(self, widget_id: int, widget: WidgetDTO) -> WidgetDTO:
        try:
            return await self.repo.update(
                widget_id=widget_id,
                name=widget.name,
                timeout=widget.timeout,
                showtime=widget.showtime,
                template=widget.template,
                order=widget.order,
            )
        except RepoError:
            raise WidgetNotFoundError


@dataclass
class DeleteWidget:
    repo: WidgetRepoPort

    async def execute(self, widget_id: int) -> None:
        try:
            await self.repo.delete(widget_id=widget_id)
        except RepoError:
            raise WidgetNotFoundError
