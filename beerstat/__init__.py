from contextlib import asynccontextmanager
from collections.abc import Awaitable, Callable

import aiosqlite
from aiosqlitepool import SQLiteConnectionPool
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from beerstat.api.v1.donates import donates_router
from beerstat.api.v1.widgets import widgets_router
from beerstat.api.v1.widgets_page import widgets_page
from beerstat.api.deps import sqlite_connection
from beerstat.domain.exceptions import DomainError, NotFoundError
from beerstat.settings import Settings
from beerstat.repo.factory import RepoFactory


def make_connection_factory(
    settings: Settings,
) -> Callable[[], Awaitable[aiosqlite.Connection]]:
    async def factory() -> aiosqlite.Connection:
        return await sqlite_connection(settings.sqlite_uri)

    return factory


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the connection pool's lifecycle.
    The pool is created when the application starts and gracefully closed when it stops.
    """
    settings = Settings.model_validate({})
    db_pool = SQLiteConnectionPool(
        connection_factory=make_connection_factory(settings),  # pyright: ignore[reportArgumentType]
        pool_size=10,
    )  # pyright: ignore[reportArgumentType]
    app.state.db_pool = db_pool
    app.state.settings = settings
    app.state.repo_factory = RepoFactory()
    yield
    await db_pool.close()


async def _not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": "not_found", "detail": str(exc) or type(exc).__name__},
    )


async def _domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": "domain_error", "detail": str(exc) or type(exc).__name__},
    )


def create_app(lifespan) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.add_exception_handler(NotFoundError, _not_found_handler)
    app.add_exception_handler(DomainError, _domain_error_handler)
    app.include_router(donates_router)
    app.include_router(widgets_router, prefix="/widget")
    app.include_router(widgets_page, prefix="/page")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    return app


app = create_app(lifespan=lifespan)
