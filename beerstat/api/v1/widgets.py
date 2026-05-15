from dataclasses import asdict
from typing import Any, Annotated
import typing


import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Request
from fasthx import hx
from beerstat.api.deps import get_db_connection

from beerstat.models import Widget
from beerstat.repo.exceptions import RepoError
from beerstat.repo.widgets import WidgetRepo
from beerstat.usecases.widgets import CreateWidget, GetWidget, GetWidgets

DependsDBConn = Annotated[aiosqlite.Connection, Depends(get_db_connection)]


widgets_router = APIRouter()


async def render_widget(
    _: list[dict[str, str]],
    *,
    context: dict[str, Any],
    request: typing.Any,
) -> str:
    widget_id = context["widget_id"]
    db_conn = context["db_conn"]
    widget = await GetWidget(repo=WidgetRepo(connection=db_conn)).execute(widget_id)
    return widget.template


async def render_widgets(
    _: list[dict[str, str]],
    *,
    context: dict[str, Any],
    request: Request,
) -> str:
    db_conn = context["db_conn"]
    widgets = await GetWidgets(repo=WidgetRepo(connection=db_conn)).execute()
    out = ""
    """
    <div hx-swap="posts" hx-get="/widget/1"
        hx-trigger="load"
        hx-target=".widget">
      </div>
    """
    out = []
    # full_reload = sum(widget.showtime) + sleep*widgets
    # sleep = 30sec
    delay = 0
    sleep_timeout = 30

    for widget in widgets:
        # hx-trigger="load delay:15s"
        out.append(f"""
        <div 
            hx-swap="posts"
            hx-get="{request.url_for("widget_get", widget_id=widget.id)}"
            hx-trigger="load {"" if not delay else f"delay:{delay}"}"
            hx-target=".widget"
        >
        </div>""")
        delay = delay + sleep_timeout + widget.showtime
    return "".join(out)


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


@widgets_router.get("/", status_code=201)
@hx(render_widgets)  # type: ignore[arg-type]
async def widgets_get(
    db_conn: DependsDBConn,
) -> list[Widget]:
    try:
        return [
            Widget(**asdict(r))
            for r in await GetWidgets(repo=WidgetRepo(connection=db_conn)).execute()
        ]

    except RepoError:
        raise HTTPException(status_code=500)


@widgets_router.get("/{widget_id}", status_code=201)
@hx(render_widget)  # type: ignore[arg-type]
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
