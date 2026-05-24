from yoyo import read_migrations
from yoyo import get_backend

from beerstat.settings import Settings

if __name__ == "__main__":
    app_settings = Settings.model_validate({})
    backend = get_backend(f"sqlite:///{app_settings.sqlite_uri}")
    migrations = read_migrations("./migrations")

    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
