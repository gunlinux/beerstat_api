from beerstat.repo.widgets import WidgetRepo
from beerstat.repo.donates import DonateRepo
from aiosqlite import Connection


class RepoFactory:
    def donat_repo(self, connection: Connection) -> DonateRepo:
        return DonateRepo(connection=connection)

    def widget_repo(self, connection: Connection) -> WidgetRepo:
        return WidgetRepo(connection=connection)
