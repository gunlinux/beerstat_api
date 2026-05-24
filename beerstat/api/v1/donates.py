from dataclasses import asdict

from fastapi import APIRouter, Depends

from beerstat.api.deps import get_donate_repo
from beerstat.repo.donates import DonateRepo
from beerstat.models import Donate, DonateBalance
from beerstat.usecases.donates import CreateDonate, GetBalance
from beerstat.domain.donate import DonateDTO


donates_router = APIRouter()


@donates_router.post("/donate", status_code=201)
async def donate(
    donate_data: Donate,
    donate_repo: DonateRepo = Depends(get_donate_repo),
) -> Donate:
    return Donate(
        **asdict(
            await CreateDonate(repo=donate_repo).execute(
                DonateDTO(
                    name=donate_data.name,
                    date=donate_data.date,
                    value=donate_data.value,
                )
            )
        )
    )


@donates_router.get("/balance")
async def get_donations(
    donate_repo: DonateRepo = Depends(get_donate_repo),
) -> DonateBalance:
    return DonateBalance(**asdict(await GetBalance(repo=donate_repo).execute()))
