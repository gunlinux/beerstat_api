"""
basic widget
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""
        CREATE TABLE IF NOT EXISTS widgets (
            id INTEGER NOT NULL,
            name VARCHAR(30),
            timeout INTEGER,
            showtime INTEGER,
            template VARCHAR(2048),
            PRIMARY KEY (id)
        );
    """)
]
