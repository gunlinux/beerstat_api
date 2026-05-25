from datetime import datetime
from typing import cast

import pytest

from beerstat.domain.donate import DonateDTO
from beerstat.domain.exceptions import DonateNotFoundError
from beerstat.infrastructure.donates import DonateRepo
from beerstat.infrastructure.exceptions import RepoError
from beerstat.usecases.donates import (
    DeleteDonate,
    GetDonate,
    GetDonationsPage,
    UpdateDonate,
)


async def _seed(repo: DonateRepo, n: int) -> list[DonateDTO]:
    results = []
    for i in range(n):
        d = await repo.add_balance(
            name=f"User{i}", value=float(i + 1), date=datetime(2024, 1, i + 1)
        )
        results.append(d)
    return results


class TestDonateRepoCount:
    async def test_count_empty(self, db_connection):
        repo = DonateRepo(db_connection)
        assert await repo.count() == 0

    async def test_count_after_inserts(self, db_connection):
        repo = DonateRepo(db_connection)
        await _seed(repo, 3)
        assert await repo.count() == 3


class TestDonateRepoGetPage:
    async def test_first_page(self, db_connection):
        repo = DonateRepo(db_connection)
        await _seed(repo, 5)
        page = await repo.get_page(offset=0, limit=3)
        assert len(page) == 3

    async def test_second_page(self, db_connection):
        repo = DonateRepo(db_connection)
        await _seed(repo, 5)
        page = await repo.get_page(offset=3, limit=3)
        assert len(page) == 2

    async def test_empty_db_returns_empty(self, db_connection):
        repo = DonateRepo(db_connection)
        assert await repo.get_page(offset=0, limit=20) == []

    async def test_ordered_by_id_desc(self, db_connection):
        repo = DonateRepo(db_connection)
        await _seed(repo, 3)
        page = await repo.get_page(offset=0, limit=3)
        ids = [cast(int, d.id) for d in page]
        assert ids == sorted(ids, reverse=True)


class TestDonateRepoGetById:
    async def test_get_existing(self, db_connection):
        repo = DonateRepo(db_connection)
        created = (await _seed(repo, 1))[0]
        fetched = await repo.get_by_id(cast(int, created.id))
        assert fetched.id == created.id
        assert fetched.name == created.name

    async def test_get_missing_raises(self, db_connection):
        repo = DonateRepo(db_connection)
        with pytest.raises(RepoError):
            await repo.get_by_id(999)


class TestDonateRepoUpdate:
    async def test_update_changes_fields(self, db_connection):
        repo = DonateRepo(db_connection)
        created = (await _seed(repo, 1))[0]
        new_date = datetime(2025, 6, 1, 12, 0)
        updated = await repo.update(
            donate_id=cast(int, created.id),
            name="Changed",
            value=99.9,
            date=new_date,
        )
        assert updated.name == "Changed"
        assert updated.value == 99.9

    async def test_update_with_commentary(self, db_connection):
        repo = DonateRepo(db_connection)
        created = (await _seed(repo, 1))[0]
        updated = await repo.update(
            donate_id=cast(int, created.id),
            name=created.name,
            value=created.value,
            date=created.date,
            commentary="added note",
        )
        assert updated.commentary == "added note"

    async def test_update_clears_commentary(self, db_connection):
        repo = DonateRepo(db_connection)
        created = await repo.add_balance(
            name="X", value=1.0, date=datetime.now(), commentary="old"
        )
        updated = await repo.update(
            donate_id=cast(int, created.id),
            name=created.name,
            value=created.value,
            date=created.date,
            commentary=None,
        )
        assert updated.commentary is None

    async def test_update_missing_raises(self, db_connection):
        repo = DonateRepo(db_connection)
        with pytest.raises(RepoError):
            await repo.update(999, "x", 1.0, datetime.now())


class TestDonateRepoDelete:
    async def test_delete_removes_record(self, db_connection):
        repo = DonateRepo(db_connection)
        created = (await _seed(repo, 1))[0]
        await repo.delete(cast(int, created.id))
        assert await repo.count() == 0

    async def test_delete_missing_raises(self, db_connection):
        repo = DonateRepo(db_connection)
        with pytest.raises(RepoError):
            await repo.delete(999)


class TestGetDonationsPage:
    async def test_returns_donations_and_total(self, db_connection):
        repo = DonateRepo(db_connection)
        await _seed(repo, 25)
        donations, total = await GetDonationsPage(repo=repo).execute(
            page=1, page_size=20
        )
        assert total == 25
        assert len(donations) == 20

    async def test_second_page(self, db_connection):
        repo = DonateRepo(db_connection)
        await _seed(repo, 25)
        donations, total = await GetDonationsPage(repo=repo).execute(
            page=2, page_size=20
        )
        assert total == 25
        assert len(donations) == 5

    async def test_empty_db(self, db_connection):
        repo = DonateRepo(db_connection)
        donations, total = await GetDonationsPage(repo=repo).execute(
            page=1, page_size=20
        )
        assert total == 0
        assert donations == []


class TestGetDonate:
    async def test_get_existing(self, db_connection):
        repo = DonateRepo(db_connection)
        created = (await _seed(repo, 1))[0]
        result = await GetDonate(repo=repo).execute(cast(int, created.id))
        assert result.id == created.id

    async def test_get_missing_raises(self, db_connection):
        repo = DonateRepo(db_connection)
        with pytest.raises(DonateNotFoundError):
            await GetDonate(repo=repo).execute(999)


class TestUpdateDonate:
    async def test_update_succeeds(self, db_connection):
        repo = DonateRepo(db_connection)
        created = (await _seed(repo, 1))[0]
        updated = await UpdateDonate(repo=repo).execute(
            donate_id=cast(int, created.id),
            donate=DonateDTO(name="New", value=50.0, date=datetime(2025, 1, 1)),
        )
        assert updated.name == "New"
        assert updated.value == 50.0

    async def test_update_missing_raises(self, db_connection):
        repo = DonateRepo(db_connection)
        with pytest.raises(DonateNotFoundError):
            await UpdateDonate(repo=repo).execute(
                donate_id=999,
                donate=DonateDTO(name="X", value=1.0, date=datetime.now()),
            )


class TestDeleteDonate:
    async def test_delete_succeeds(self, db_connection):
        repo = DonateRepo(db_connection)
        created = (await _seed(repo, 1))[0]
        await DeleteDonate(repo=repo).execute(cast(int, created.id))
        with pytest.raises(DonateNotFoundError):
            await GetDonate(repo=repo).execute(cast(int, created.id))

    async def test_delete_missing_raises(self, db_connection):
        repo = DonateRepo(db_connection)
        with pytest.raises(DonateNotFoundError):
            await DeleteDonate(repo=repo).execute(999)


class TestAdminDonationsAPI:
    async def test_list_empty(self, client):
        resp = await client.get("/admin/donations/")
        assert resp.status_code == 200

    async def test_list_shows_donations(self, client):
        await client.post(
            "/donate",
            json={"name": "Alice", "value": 10.0, "date": datetime.now().isoformat()},
        )
        resp = await client.get("/admin/donations/")
        assert resp.status_code == 200
        assert "Alice" in resp.text

    async def test_list_pagination(self, client):
        resp = await client.get("/admin/donations/?page=1")
        assert resp.status_code == 200

    async def test_edit_form_returns_200(self, client):
        create = await client.post(
            "/donate",
            json={"name": "Bob", "value": 5.0, "date": datetime.now().isoformat()},
        )
        donate_id = create.json()["id"]
        resp = await client.get(f"/admin/donations/{donate_id}/edit")
        assert resp.status_code == 200
        assert "Bob" in resp.text

    async def test_edit_form_missing_returns_404(self, client):
        resp = await client.get("/admin/donations/999/edit")
        assert resp.status_code == 404

    async def test_update_redirects(self, client):
        create = await client.post(
            "/donate",
            json={"name": "Carol", "value": 7.0, "date": "2024-03-01T10:00:00"},
        )
        donate_id = create.json()["id"]
        resp = await client.post(
            f"/admin/donations/{donate_id}/edit",
            data={"name": "Carol Updated", "value": "8.0", "date": "2024-03-01T10:00"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/admin/donations/"

    async def test_delete_returns_200(self, client):
        create = await client.post(
            "/donate",
            json={"name": "Dave", "value": 3.0, "date": datetime.now().isoformat()},
        )
        donate_id = create.json()["id"]
        resp = await client.delete(f"/admin/donations/{donate_id}")
        assert resp.status_code == 200

    async def test_delete_missing_returns_404(self, client):
        resp = await client.delete("/admin/donations/999")
        assert resp.status_code == 404
