from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from fasthx.jinja import Jinja

from beerstat.api.deps import get_widget_repo, get_settings
from beerstat.models import WidgetCreateIn, WidgetOut
from beerstat.repo.widgets import WidgetRepo
from beerstat.settings import Settings
from beerstat.usecases.widgets import CreateWidget, GetWidget, GetWidgets


widgets_router = APIRouter()
jinja = Jinja(Jinja2Templates("templates"))


@widgets_router.post("/", status_code=201)
async def widget_add(
    widget_data: WidgetCreateIn,
    widget_repo: WidgetRepo = Depends(get_widget_repo),
    settings: Settings = Depends(get_settings),
) -> WidgetOut:
    return WidgetOut.from_dto(
        await CreateWidget(repo=widget_repo).execute(
            widget_data.to_dto(showtime_default=settings.showtime)
        )
    )


@widgets_router.get("/")
async def widgets_get(
    widget_repo: WidgetRepo = Depends(get_widget_repo),
) -> list[WidgetOut]:
    return [WidgetOut.from_dto(r) for r in await GetWidgets(repo=widget_repo).execute()]


@widgets_router.get("/{widget_id}")
@jinja.hx("widget.htmx")
async def widget_get(
    widget_id: int,
    widget_repo: WidgetRepo = Depends(get_widget_repo),
) -> WidgetOut:
    return WidgetOut.from_dto(await GetWidget(repo=widget_repo).execute(widget_id))
