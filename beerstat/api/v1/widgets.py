import aiosqlite
from fastapi import APIRouter, Depends, HTTPException
from beerstat.api.deps import get_db_connection

from beerstat.models import Widget
from beerstat.repo.exceptions import RepoError
from beerstat.repo.widgets import WidgetRepo
from beerstat.usecases.widgets import CreateWidget, GetWidget
from dataclasses import asdict


widgets_router = APIRouter()


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


@widgets_router.get("/{widget_id}", status_code=201)
async def widget_get(
    widget_id: int,
    db_conn: aiosqlite.Connection = Depends(get_db_connection),
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
