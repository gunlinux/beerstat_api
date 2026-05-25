from datetime import datetime

from fastapi import APIRouter, Depends, Form, Query, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from beerstat.api.deps import get_donate_repo, get_settings, get_widget_repo
from beerstat.domain.donate import DonateDTO
from beerstat.domain.widget import WidgetDTO
from beerstat.infrastructure.donates import DonateRepo
from beerstat.infrastructure.widgets import WidgetRepo
from beerstat.models import DonateOut, WidgetOut
from beerstat.settings import Settings
from beerstat.usecases.donates import (
    CreateDonate,
    DeleteDonate,
    GetDonate,
    GetDonationsPage,
    UpdateDonate,
)
from beerstat.usecases.widgets import (
    CreateWidget,
    DeleteWidget,
    GetWidget,
    GetWidgets,
    UpdateWidget,
)

PAGE_SIZE = 20

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


# --- Widget routes ---


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
    order: int = Form(default=0),
    widget_repo: WidgetRepo = Depends(get_widget_repo),
):
    await CreateWidget(repo=widget_repo).execute(
        WidgetDTO(
            name=name,
            timeout=timeout,
            showtime=showtime,
            template=template,
            order=order,
        )
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
    order: int = Form(default=0),
    widget_repo: WidgetRepo = Depends(get_widget_repo),
):
    await UpdateWidget(repo=widget_repo).execute(
        widget_id=widget_id,
        widget=WidgetDTO(
            name=name,
            timeout=timeout,
            showtime=showtime,
            template=template,
            order=order,
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


# --- Donation routes ---


@admin_router.get("/donations/new")
async def admin_donation_new(request: Request):
    now = datetime.now().strftime("%Y-%m-%dT%H:%M")
    return templates.TemplateResponse(
        request, "admin/donation_create.html", {"now": now}
    )


@admin_router.post("/donations/new")
async def admin_donation_create(
    name: str = Form(default=""),
    value: float = Form(...),
    date: str = Form(...),
    commentary: str | None = Form(default=None),
    donate_repo: DonateRepo = Depends(get_donate_repo),
):
    await CreateDonate(repo=donate_repo).execute(
        DonateDTO(
            name=name,
            value=value,
            date=datetime.fromisoformat(date),
            commentary=commentary or None,
        )
    )
    return RedirectResponse(url="/admin/donations/", status_code=303)


@admin_router.get("/donations/")
async def admin_donations(
    request: Request,
    page: int = Query(default=1, ge=1),
    donate_repo: DonateRepo = Depends(get_donate_repo),
):
    donations, total = await GetDonationsPage(repo=donate_repo).execute(
        page=page, page_size=PAGE_SIZE
    )
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    return templates.TemplateResponse(
        request,
        "admin/donations.html",
        {
            "donations": [DonateOut.from_dto(d) for d in donations],
            "page": page,
            "total_pages": total_pages,
            "total": total,
        },
    )


@admin_router.get("/donations/{donate_id}/edit")
async def admin_donation_edit(
    request: Request,
    donate_id: int,
    donate_repo: DonateRepo = Depends(get_donate_repo),
):
    donate = DonateOut.from_dto(await GetDonate(repo=donate_repo).execute(donate_id))
    return templates.TemplateResponse(
        request, "admin/donation_edit.html", {"donate": donate}
    )


@admin_router.post("/donations/{donate_id}/edit")
async def admin_donation_update(
    donate_id: int,
    name: str = Form(...),
    value: float = Form(...),
    date: str = Form(...),
    commentary: str | None = Form(default=None),
    donate_repo: DonateRepo = Depends(get_donate_repo),
):
    await UpdateDonate(repo=donate_repo).execute(
        donate_id=donate_id,
        donate=DonateDTO(
            name=name,
            value=value,
            date=datetime.fromisoformat(date),
            commentary=commentary or None,
        ),
    )
    return RedirectResponse(url="/admin/donations/", status_code=303)


@admin_router.delete("/donations/{donate_id}", status_code=200)
async def admin_donation_delete(
    donate_id: int,
    donate_repo: DonateRepo = Depends(get_donate_repo),
):
    await DeleteDonate(repo=donate_repo).execute(donate_id)
    return Response(status_code=200)
