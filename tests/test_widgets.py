import pytest

from beerstat.domain.exceptions import WidgetNotFoundError
from beerstat.domain.widget import WidgetDTO, WidgetStatDTO
from beerstat.repo.widgets import WidgetRepo
from beerstat.usecases.widgets import CreateWidget, GetWidget, GetWidgets, GetWidgetsStat


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
        created = await repo.add(name="slider", timeout=5, showtime=3, template="<div/>")

        use_case = GetWidget(repo=repo)
        result = await use_case.execute(created.id)

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

        assert result == []

    async def test_get_all_returns_multiple_widgets(self, db_connection):
        repo = WidgetRepo(connection=db_connection)
        await repo.add(name="w1", timeout=1, showtime=2, template="<w1/>")
        await repo.add(name="w2", timeout=3, showtime=4, template="<w2/>")

        use_case = GetWidgets(repo=repo)
        result = await use_case.execute()

        assert len(result) == 2
        names = [w.name for w in result]
        assert "w1" in names
        assert "w2" in names


class TestGetWidgetsStat:
    async def test_stat_with_widgets(self, db_connection):
        repo = WidgetRepo(connection=db_connection)
        await repo.add(name="w1", timeout=1, showtime=10, template="<w1/>")
        await repo.add(name="w2", timeout=2, showtime=20, template="<w2/>")

        use_case = GetWidgetsStat(repo=repo)
        result = await use_case.execute()

        assert isinstance(result, WidgetStatDTO)
        assert result.count == 2
        assert result.timeout == 30

    async def test_stat_empty_raises(self, db_connection):
        repo = WidgetRepo(connection=db_connection)
        use_case = GetWidgetsStat(repo=repo)

        with pytest.raises(Exception):  # RepoError propagates as DomainError
            await use_case.execute()
