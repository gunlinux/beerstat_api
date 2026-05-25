from collections.abc import AsyncGenerator

from fastapi import Request

from beerstat.infrastructure.donates import DonateRepo
from beerstat.infrastructure.factory import RepoFactory
from beerstat.infrastructure.widgets import WidgetRepo
from beerstat.settings import Settings


async def get_settings(request: Request) -> Settings:
    return request.app.state.settings


async def get_donate_repo(request: Request) -> AsyncGenerator[DonateRepo, None]:
    factory: RepoFactory = request.app.state.repo_factory
    async with factory.donate_repo() as repo:
        yield repo


async def get_widget_repo(request: Request) -> AsyncGenerator[WidgetRepo, None]:
    factory: RepoFactory = request.app.state.repo_factory
    async with factory.widget_repo() as repo:
        yield repo
