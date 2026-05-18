from dataclasses import asdict
from typing import Annotated

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fasthx.jinja import Jinja

from beerstat.api.deps import get_db_connection
from beerstat.models import Widget
from beerstat.repo.exceptions import RepoError
from beerstat.repo.widgets import WidgetRepo
from beerstat.usecases.widgets import CreateWidget, GetWidget, GetWidgets
from beerstat.settings import Settings


DependsDBConn = Annotated[aiosqlite.Connection, Depends(get_db_connection)]
widgets_router = APIRouter()
app_settings = Settings.model_validate({})
jinja = Jinja(Jinja2Templates("templates"))


@widgets_router.post("/", status_code=201)
async def widget_add(
    widget_data: Widget,
    db_conn: aiosqlite.Connection = Depends(get_db_connection),
) -> Widget:
    try:
        result = Widget(
            **asdict(
                await CreateWidget(repo=WidgetRepo(connection=db_conn)).execute(
                    widget_data
                )
            )
        )
    except RepoError:
        raise HTTPException(status_code=500)
    return result


@widgets_router.get("/")
@jinja.hx("widgets.htmx")
async def widgets_get(
    db_conn: DependsDBConn,
) -> list[Widget]:
    try:
        out = []
        delay = 0
        sleep_timeout = app_settings.showtime
        for r in await GetWidgets(repo=WidgetRepo(connection=db_conn)).execute():
            out.append(
                Widget(
                    id=r.id,
                    name=r.name,
                    timeout=r.timeout,
                    showtime=r.showtime,
                    template=r.template,
                    sleep=delay,
                )
            )
            delay = delay + sleep_timeout + r.showtime
        return out

    except RepoError:
        raise HTTPException(status_code=500)


@widgets_router.get("/{widget_id}")
@jinja.hx("widget.htmx")
async def widget_get(
    widget_id: int,
    db_conn: DependsDBConn,
) -> Widget:
    try:
        result = Widget(
            **asdict(
                await GetWidget(repo=WidgetRepo(connection=db_conn)).execute(widget_id)
            )
        )
    except RepoError:
        raise HTTPException(status_code=500)
    return result
