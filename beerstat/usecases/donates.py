from dataclasses import dataclass

from beerstat.domain.exceptions import DomainError
from beerstat.domain.ports import DonateRepoPort
from beerstat.infrastructure.exceptions import RepoError
from beerstat.domain.donate import DonateDTO, DonateBalanceDTO


@dataclass
class CreateDonate:
    repo: DonateRepoPort

    async def execute(self, donate: DonateDTO) -> DonateDTO:
        try:
            return await self.repo.add_balance(
                name=donate.name,
                value=donate.value,
                date=donate.date,
            )
        except RepoError:
            raise DomainError


@dataclass
class GetBalance:
    repo: DonateRepoPort

    async def execute(self) -> DonateBalanceDTO:
        balance = await self.repo.get_balance()
        return DonateBalanceDTO(total=balance if balance is not None else 0.0)


@dataclass
class GetLastDonations:
    repo: DonateRepoPort

    async def execute(self, limit: int = 10) -> list[DonateDTO]:
        try:
            return await self.repo.get_last(limit)
        except RepoError:
            raise DomainError
