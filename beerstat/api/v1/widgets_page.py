from typing import Annotated
from dataclasses import asdict

import aiosqlite
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

from beerstat.settings import Settings
from beerstat.api.deps import get_db_connection
from beerstat.repo.widgets import WidgetRepo
from beerstat.repo.exceptions import RepoError
from beerstat.usecases.widgets import GetWidgetsStat, GetWidget
from beerstat.models import Widget


DependsDBConn = Annotated[aiosqlite.Connection, Depends(get_db_connection)]


widgets_page = APIRouter()
templates = Jinja2Templates("templates")
app_settings = Settings.model_validate({})


@widgets_page.get("/", response_class=HTMLResponse)
async def index(request: Request, db_conn: DependsDBConn) -> _TemplateResponse:
    stat = await GetWidgetsStat(repo=WidgetRepo(connection=db_conn)).execute()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "sleep_time": app_settings.showtime * stat.count + stat.timeout,
            "showtime": app_settings.showtime * 1000,
        },
    )


@widgets_page.get("/{widget_id}", response_class=HTMLResponse)
async def widget_page(
    widget_id: int, request: Request, db_conn: DependsDBConn
) -> _TemplateResponse:
    try:
        result = Widget(
            **asdict(
                await GetWidget(repo=WidgetRepo(connection=db_conn)).execute(widget_id)
            )
        )
    except RepoError:
        raise HTTPException(status_code=500)

    return templates.TemplateResponse(
        request=request, name="widget.html", context={"item": result}
    )
