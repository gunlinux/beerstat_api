from typing import Annotated
from dataclasses import asdict

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fasthx.jinja import Jinja

from beerstat.domain.exceptions import DomainError, NotFoundError
from beerstat.api.deps import get_db_connection
from beerstat.repo.widgets import WidgetRepo
from beerstat.usecases.widgets import GetWidgetsStat, GetWidget
from beerstat.models import Widget, WidgetStat


DependsDBConn = Annotated[aiosqlite.Connection, Depends(get_db_connection)]


widgets_page = APIRouter()
jinja = Jinja(Jinja2Templates("templates"))


@widgets_page.get("/")
@jinja.page("index.html")
async def index(db_conn: DependsDBConn, request: Request) -> WidgetStat:
    try:
        stat = await GetWidgetsStat(repo=WidgetRepo(connection=db_conn)).execute()
    except DomainError:
        raise HTTPException(status_code=500)
    return WidgetStat(
        sleep_time=request.app.state.settings.showtime * stat.count + stat.timeout,
        showtime=request.app.state.settings.showtime * 1000,
    )


@widgets_page.get("/{widget_id}")
@jinja.hx("widget.htmx")
async def widget_page(widget_id: int, db_conn: DependsDBConn) -> Widget:
    try:
        result = Widget(
            **asdict(
                await GetWidget(repo=WidgetRepo(connection=db_conn)).execute(widget_id)
            )
        )
    except NotFoundError:
        raise HTTPException(status_code=404)
    return result
