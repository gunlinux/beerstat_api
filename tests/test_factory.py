from datetime import datetime

import pytest


class TestRepoFactoryTransactions:
    async def test_commit_on_clean_exit(self, repo_factory):
        async with repo_factory.donate_repo() as repo:
            await repo.add_balance(name="Alice", value=10.0, date=datetime.now())

        async with repo_factory.donate_repo() as repo:
            balance = await repo.get_balance()

        assert balance == 10.0

    async def test_rollback_on_exception(self, repo_factory):
        with pytest.raises(RuntimeError):
            async with repo_factory.donate_repo() as repo:
                await repo.add_balance(name="Alice", value=10.0, date=datetime.now())
                raise RuntimeError("simulated mid-uow failure")

        async with repo_factory.donate_repo() as repo:
            balance = await repo.get_balance()

        assert balance is None

    async def test_rollback_then_independent_commit(self, repo_factory):
        with pytest.raises(RuntimeError):
            async with repo_factory.donate_repo() as repo:
                await repo.add_balance(name="ghost", value=99.0, date=datetime.now())
                raise RuntimeError("rolled back")

        async with repo_factory.donate_repo() as repo:
            await repo.add_balance(name="real", value=5.0, date=datetime.now())

        async with repo_factory.donate_repo() as repo:
            balance = await repo.get_balance()

        assert balance == 5.0
