from dataclasses import dataclass

from beerstat.domain.exceptions import DomainError
from beerstat.repo.donates import DonateRepo
from beerstat.domain.donate import DonateDTO, DonateBalanceDTO


@dataclass
class CreateDonate:
    repo: DonateRepo

    async def execute(self, donate: DonateDTO) -> DonateDTO:
        return await self.repo.add_balance(
            name=donate.name,
            value=donate.value,
            date=donate.date,
        )


@dataclass
class GetBalance:
    repo: DonateRepo

    async def execute(self) -> DonateBalanceDTO:
        if balance := await self.repo.get_balance():
            return DonateBalanceDTO(total=balance)
        raise DomainError
