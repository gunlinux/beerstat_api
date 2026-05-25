from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from beerstat.domain.donate import DonateDTO, DonateBalanceDTO
from beerstat.infrastructure.donates import DonateRepo
from beerstat.usecases.donates import CreateDonate, GetBalance


class TestCreateDonate:
    async def test_create_donate_returns_dto_with_id(self, db_connection):
        repo = DonateRepo(connection=db_connection)
        use_case = CreateDonate(repo=repo)
        donate = DonateDTO(name="Alice", value=10.0, date=datetime.now())

        result = await use_case.execute(donate)

        assert isinstance(result, DonateDTO)
        assert result.id is not None
        assert result.name == "Alice"
        assert result.value == 10.0

    async def test_anonym_name_default(self, db_connection):
        repo = DonateRepo(connection=db_connection)
        use_case = CreateDonate(repo=repo)
        donate = DonateDTO(name="", value=5.0, date=datetime.now())

        result = await use_case.execute(donate)

        assert result.name == "Anonym"

    async def test_create_with_commentary(self, db_connection):
        repo = DonateRepo(connection=db_connection)
        use_case = CreateDonate(repo=repo)
        donate = DonateDTO(
            name="Alice", value=10.0, date=datetime.now(), commentary="keep it up!"
        )

        result = await use_case.execute(donate)

        assert result.commentary == "keep it up!"

    async def test_create_without_commentary_defaults_to_none(self, db_connection):
        repo = DonateRepo(connection=db_connection)
        use_case = CreateDonate(repo=repo)
        donate = DonateDTO(name="Bob", value=5.0, date=datetime.now())

        result = await use_case.execute(donate)

        assert result.commentary is None


class TestGetBalance:
    async def test_balance_with_donations(self, db_connection):
        repo = DonateRepo(connection=db_connection)
        await repo.add_balance(name="Alice", value=10.0, date=datetime.now())
        await repo.add_balance(name="Bob", value=20.0, date=datetime.now())

        use_case = GetBalance(repo=repo)
        result = await use_case.execute()

        assert isinstance(result, DonateBalanceDTO)
        assert result.total == 30.0

    async def test_empty_balance_returns_zero(self, db_connection):
        repo = DonateRepo(connection=db_connection)
        use_case = GetBalance(repo=repo)

        result = await use_case.execute()

        assert isinstance(result, DonateBalanceDTO)
        assert result.total == 0.0

    async def test_zero_total_balance_returns_dto(self, db_connection):
        repo = DonateRepo(connection=db_connection)
        await repo.add_balance(name="Alice", value=0.0, date=datetime.now())

        use_case = GetBalance(repo=repo)
        result = await use_case.execute()

        assert isinstance(result, DonateBalanceDTO)
        assert result.total == 0.0


class TestDonateDTO:
    def test_dto_is_frozen(self):
        dto = DonateDTO(name="Alice", value=5.0, date=datetime.now())
        with pytest.raises(FrozenInstanceError):
            dto.name = "Bob"  # type: ignore[misc]

    def test_anonym_substitution_via_post_init(self):
        dto = DonateDTO(name="", value=1.0, date=datetime.now())
        assert dto.name == "Anonym"
