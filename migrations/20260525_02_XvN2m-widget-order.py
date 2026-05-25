"""
widget order field
"""

from yoyo import step

__depends__ = {"20260525_01_A7kQp-seed-widgets"}

steps = [
    step(
        'ALTER TABLE widgets ADD COLUMN "order" INTEGER NOT NULL DEFAULT 0',
        "SELECT 1",  # SQLite does not support DROP COLUMN in older versions
    )
]
