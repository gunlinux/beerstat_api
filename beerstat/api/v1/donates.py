from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from fasthx.jinja import Jinja

from beerstat.api.deps import get_donate_repo
from beerstat.infrastructure.donates import DonateRepo
from beerstat.models import (
    DonateCreateIn,
    DonateOut,
    DonateBalance,
    DonationsOut,
    TopDonatorOut,
    TopDonatorsOut,
)
from beerstat.usecases.donates import (
    CreateDonate,
    GetBalance,
    GetLastDonations,
    GetTopDonators,
)


donates_router = APIRouter()
jinja = Jinja(Jinja2Templates("templates"))


@donates_router.post("/donate", status_code=201)
async def donate(
    donate_data: DonateCreateIn,
    donate_repo: DonateRepo = Depends(get_donate_repo),
) -> DonateOut:
    return DonateOut.from_dto(
        await CreateDonate(repo=donate_repo).execute(donate_data.to_dto())
    )


@donates_router.get("/balance")
async def get_donations(
    donate_repo: DonateRepo = Depends(get_donate_repo),
) -> DonateBalance:
    return DonateBalance.from_dto(await GetBalance(repo=donate_repo).execute())


@donates_router.get("/donations/last")
@jinja.hx("donations.htmx")
async def get_last_donations(
    donate_repo: DonateRepo = Depends(get_donate_repo),
) -> DonationsOut:
    dtos = await GetLastDonations(repo=donate_repo).execute()
    return DonationsOut(donations=[DonateOut.from_dto(dto) for dto in dtos])


@donates_router.get("/donations/top")
@jinja.hx("top_donators.htmx")
async def get_top_donators(
    donate_repo: DonateRepo = Depends(get_donate_repo),
) -> TopDonatorsOut:
    dtos = await GetTopDonators(repo=donate_repo).execute(limit=5)
    return TopDonatorsOut(donators=[TopDonatorOut.from_dto(dto) for dto in dtos])


@donates_router.get("/donations/top/month")
@jinja.hx("top_donators.htmx")
async def get_top_donators_month(
    donate_repo: DonateRepo = Depends(get_donate_repo),
) -> TopDonatorsOut:
    since = datetime.now(timezone.utc) - timedelta(days=30)
    dtos = await GetTopDonators(repo=donate_repo).execute(limit=5, since=since)
    return TopDonatorsOut(donators=[TopDonatorOut.from_dto(dto) for dto in dtos])
