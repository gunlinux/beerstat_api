from typing import Annotated


import aiosqlite
from fastapi import APIRouter, Depends, Request


from beerstat.settings import Settings

from fastapi.responses import HTMLResponse
from starlette.templating import _TemplateResponse
from beerstat.api.deps import get_db_connection

from fastapi.templating import Jinja2Templates
from beerstat.repo.widgets import WidgetRepo
from beerstat.usecases.widgets import GetWidgetsStat

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
        context={"sleep_time": app_settings.sleep_time * stat.count + stat.timeout},
    )
