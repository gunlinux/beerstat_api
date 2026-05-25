import pytest
from typing import cast
from unittest.mock import AsyncMock

from beerstat.domain.exceptions import WidgetNotFoundError, CreateError
from beerstat.domain.widget import WidgetDTO
from beerstat.infrastructure.exceptions import RepoError
from beerstat.infrastructure.widgets import WidgetRepo
from beerstat.usecases.widgets import (
    CreateWidget,
    GetWidget,
    GetWidgets,
)


class TestCreateWidget:
    async def test_create_widget_returns_dto_with_id(self, db_connection):
        repo = WidgetRepo(connection=db_connection)
        use_case = CreateWidget(repo=repo)
        widget = WidgetDTO(name="slider", timeout=5, showtime=3, template="<div/>")

        result = await use_case.execute(widget)

        assert isinstance(result, WidgetDTO)
        assert result.id is not None
        assert result.name == "slider"
        assert result.timeout == 5
        assert result.showtime == 3
        assert result.template == "<div/>"


class TestGetWidget:
    async def test_get_existing_widget(self, db_connection):
        repo = WidgetRepo(connection=db_connection)
        created = await repo.add(
            name="slider", timeout=5, showtime=3, template="<div/>"
        )

        use_case = GetWidget(repo=repo)
        assert created is not None
        result = await use_case.execute(cast(int, created.id))

        assert result.id == created.id
        assert result.name == "slider"

    async def test_get_nonexistent_widget_raises(self, db_connection):
        repo = WidgetRepo(connection=db_connection)
        use_case = GetWidget(repo=repo)

        with pytest.raises(WidgetNotFoundError):
            await use_case.execute(999)


class TestGetWidgets:
    async def test_get_all_returns_empty_list(self, db_connection):
        repo = WidgetRepo(connection=db_connection)
        use_case = GetWidgets(repo=repo)

        result = await use_case.execute()

        assert len(result) == 4  # 4 seeded default widgets

    async def test_get_all_returns_multiple_widgets(self, db_connection):
        repo = WidgetRepo(connection=db_connection)
        await repo.add(name="w1", timeout=1, showtime=2, template="<w1/>")
        await repo.add(name="w2", timeout=3, showtime=4, template="<w2/>")

        use_case = GetWidgets(repo=repo)
        result = await use_case.execute()

        assert len(result) == 6  # 4 seeded + 2 created
        names = [w.name for w in result]
        assert "w1" in names
        assert "w2" in names

    async def test_repo_error_raises_create_error(self):
        mock_repo = AsyncMock()
        mock_repo.get_all.side_effect = RepoError
        use_case = GetWidgets(repo=mock_repo)

        with pytest.raises(CreateError):
            await use_case.execute()


class TestCreateWidgetErrors:
    async def test_repo_error_raises_create_error(self):
        mock_repo = AsyncMock()
        mock_repo.add.side_effect = RepoError
        use_case = CreateWidget(repo=mock_repo)

        with pytest.raises(CreateError):
            await use_case.execute(
                WidgetDTO(name="x", timeout=1, showtime=1, template="<x/>")
            )
