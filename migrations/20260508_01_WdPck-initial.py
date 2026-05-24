"""
initial
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER NOT NULL,
            name VARCHAR(30),
            date DATETIME,
            value FLOAT,
            PRIMARY KEY (id)
        );
        """,
        "DROP TABLE donations;",
    )
]
