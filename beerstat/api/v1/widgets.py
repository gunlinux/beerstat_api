from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from fasthx.jinja import Jinja

from beerstat.api.deps import get_widget_repo, get_settings
from beerstat.models import Widget
from beerstat.repo.widgets import WidgetRepo
from beerstat.settings import Settings
from beerstat.usecases.widgets import CreateWidget, GetWidget, GetWidgets
from beerstat.domain.widget import WidgetDTO


widgets_router = APIRouter()
jinja = Jinja(Jinja2Templates("templates"))


@widgets_router.post("/", status_code=201)
async def widget_add(
    widget_data: Widget,
    widget_repo: WidgetRepo = Depends(get_widget_repo),
    settings: Settings = Depends(get_settings),
) -> Widget:
    result = await CreateWidget(repo=widget_repo).execute(
        WidgetDTO(
            name=widget_data.name,
            timeout=widget_data.timeout,
            showtime=widget_data.showtime
            if widget_data.showtime is not None
            else settings.showtime,
            template=widget_data.template,
        )
    )
    return Widget(**asdict(result))


@widgets_router.get("/")
async def widgets_get(
    widget_repo: WidgetRepo = Depends(get_widget_repo),
) -> list[Widget]:
    return [
        Widget(
            id=r.id,
            name=r.name,
            timeout=r.timeout,
            showtime=r.showtime,
            template=r.template,
        )
        for r in await GetWidgets(repo=widget_repo).execute()
    ]


@widgets_router.get("/{widget_id}")
@jinja.hx("widget.htmx")
async def widget_get(
    widget_id: int,
    widget_repo: WidgetRepo = Depends(get_widget_repo),
) -> Widget:
    return Widget(**asdict(await GetWidget(repo=widget_repo).execute(widget_id)))
