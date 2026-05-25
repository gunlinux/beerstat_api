from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from beerstat.api.deps import get_settings, get_widget_repo
from beerstat.domain.widget import WidgetDTO
from beerstat.infrastructure.widgets import WidgetRepo
from beerstat.models import WidgetOut
from beerstat.settings import Settings
from beerstat.usecases.widgets import (
    CreateWidget,
    DeleteWidget,
    GetWidget,
    GetWidgets,
    UpdateWidget,
)

admin_router = APIRouter()
templates = Jinja2Templates("templates")


@admin_router.get("/")
async def admin_index(
    request: Request,
    widget_repo: WidgetRepo = Depends(get_widget_repo),
):
    widgets = [
        WidgetOut.from_dto(w) for w in await GetWidgets(repo=widget_repo).execute()
    ]
    return templates.TemplateResponse(request, "admin/index.html", {"widgets": widgets})


@admin_router.get("/widget/new")
async def admin_widget_new(
    request: Request,
    settings: Settings = Depends(get_settings),
):
    return templates.TemplateResponse(
        request, "admin/widget_create.html", {"default_showtime": settings.showtime}
    )


@admin_router.post("/widget/new")
async def admin_widget_create(
    name: str = Form(...),
    timeout: int = Form(...),
    showtime: int = Form(...),
    template: str = Form(...),
    widget_repo: WidgetRepo = Depends(get_widget_repo),
):
    await CreateWidget(repo=widget_repo).execute(
        WidgetDTO(name=name, timeout=timeout, showtime=showtime, template=template)
    )
    return RedirectResponse(url="/admin/", status_code=303)


@admin_router.get("/widget/{widget_id}/edit")
async def admin_widget_edit(
    request: Request,
    widget_id: int,
    widget_repo: WidgetRepo = Depends(get_widget_repo),
):
    widget = WidgetOut.from_dto(await GetWidget(repo=widget_repo).execute(widget_id))
    return templates.TemplateResponse(
        request, "admin/widget_edit.html", {"widget": widget}
    )


@admin_router.post("/widget/{widget_id}/edit")
async def admin_widget_update(
    widget_id: int,
    name: str = Form(...),
    timeout: int = Form(...),
    showtime: int = Form(...),
    template: str = Form(...),
    widget_repo: WidgetRepo = Depends(get_widget_repo),
):
    await UpdateWidget(repo=widget_repo).execute(
        widget_id=widget_id,
        widget=WidgetDTO(
            name=name, timeout=timeout, showtime=showtime, template=template
        ),
    )
    return RedirectResponse(url="/admin/", status_code=303)


@admin_router.delete("/widget/{widget_id}", status_code=200)
async def admin_widget_delete(
    widget_id: int,
    widget_repo: WidgetRepo = Depends(get_widget_repo),
):
    await DeleteWidget(repo=widget_repo).execute(widget_id)
    return Response(status_code=200)
