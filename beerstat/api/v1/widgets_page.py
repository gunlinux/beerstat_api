from dataclasses import asdict

from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from fasthx.jinja import Jinja

from beerstat.api.deps import get_widget_repo
from beerstat.repo.widgets import WidgetRepo
from beerstat.usecases.widgets import GetWidget
from beerstat.models import Widget, WidgetStat


widgets_page = APIRouter()
jinja = Jinja(Jinja2Templates("templates"))


@widgets_page.get("/")
@jinja.page("index.html")
async def index() -> WidgetStat: ...


@widgets_page.get("/{widget_id}")
@jinja.hx("widget.htmx")
async def widget_page(
    widget_id: int, widget_repo: WidgetRepo = Depends(get_widget_repo)
) -> Widget:
    return Widget(**asdict(await GetWidget(repo=widget_repo).execute(widget_id)))
