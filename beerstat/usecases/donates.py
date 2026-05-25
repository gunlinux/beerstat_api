from dataclasses import dataclass
from datetime import datetime

from beerstat.domain.exceptions import DomainError, DonateNotFoundError
from beerstat.domain.ports import DonateRepoPort
from beerstat.infrastructure.exceptions import RepoError
from beerstat.domain.donate import DonateDTO, DonateBalanceDTO, DonatorSummaryDTO


@dataclass
class CreateDonate:
    repo: DonateRepoPort

    async def execute(self, donate: DonateDTO) -> DonateDTO:
        try:
            return await self.repo.add_balance(
                name=donate.name,
                value=donate.value,
                date=donate.date,
                commentary=donate.commentary,
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


@dataclass
class GetDonationsPage:
    repo: DonateRepoPort

    async def execute(self, page: int, page_size: int) -> tuple[list[DonateDTO], int]:
        offset = (page - 1) * page_size
        try:
            donations = await self.repo.get_page(offset=offset, limit=page_size)
            total = await self.repo.count()
            return donations, total
        except RepoError:
            raise DomainError


@dataclass
class GetDonate:
    repo: DonateRepoPort

    async def execute(self, donate_id: int) -> DonateDTO:
        try:
            return await self.repo.get_by_id(donate_id=donate_id)
        except RepoError:
            raise DonateNotFoundError


@dataclass
class UpdateDonate:
    repo: DonateRepoPort

    async def execute(self, donate_id: int, donate: DonateDTO) -> DonateDTO:
        try:
            return await self.repo.update(
                donate_id=donate_id,
                name=donate.name,
                value=donate.value,
                date=donate.date,
                commentary=donate.commentary,
            )
        except RepoError:
            raise DonateNotFoundError


@dataclass
class DeleteDonate:
    repo: DonateRepoPort

    async def execute(self, donate_id: int) -> None:
        try:
            await self.repo.delete(donate_id=donate_id)
        except RepoError:
            raise DonateNotFoundError


@dataclass
class GetTopDonators:
    repo: DonateRepoPort

    async def execute(
        self, limit: int = 5, since: datetime | None = None
    ) -> list[DonatorSummaryDTO]:
        try:
            return await self.repo.get_top(limit=limit, since=since)
        except RepoError:
            raise DomainError
