from dataclasses import asdict

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException

from beerstat.api.deps import get_db_connection
from beerstat.domain.exceptions import DomainError
from beerstat.repo.donates import DonateRepo
from beerstat.models import Donate, DonateBalance
from beerstat.repo.exceptions import RepoError
from beerstat.usecases.donates import CreateDonate, GetBalance
from beerstat.domain.donate import DonateDTO


donates_router = APIRouter()


@donates_router.post("/donate", status_code=201)
async def donate(
    donate_data: Donate,
    db_conn: aiosqlite.Connection = Depends(get_db_connection),
) -> Donate:
    try:
        result = Donate(
            **asdict(
                await CreateDonate(repo=DonateRepo(connection=db_conn)).execute(
                    DonateDTO(
                        name=donate_data.name,
                        date=donate_data.date,
                        value=donate_data.value,
                    )
                )
            )
        )
    except RepoError:
        raise HTTPException(status_code=500)
    return result


@donates_router.get("/balance")
async def get_donations(
    db_conn: aiosqlite.Connection = Depends(get_db_connection),
) -> DonateBalance:
    try:
        return DonateBalance(
            **asdict(await GetBalance(repo=DonateRepo(connection=db_conn)).execute())
        )
    except DomainError:
        raise HTTPException(status_code=500)
    except RepoError:
        raise HTTPException(status_code=500)
