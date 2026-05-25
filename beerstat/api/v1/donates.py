from fastapi import APIRouter, Depends

from beerstat.api.deps import get_donate_repo
from beerstat.infrastructure.donates import DonateRepo
from beerstat.models import DonateCreateIn, DonateOut, DonateBalance
from beerstat.usecases.donates import CreateDonate, GetBalance


donates_router = APIRouter()


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
