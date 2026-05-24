from dataclasses import dataclass

from beerstat.domain.exceptions import DomainError
from beerstat.domain.ports import DonateRepoPort
from beerstat.repo.exceptions import RepoError
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
        if balance is not None:
            return DonateBalanceDTO(total=balance)
        raise DomainError
