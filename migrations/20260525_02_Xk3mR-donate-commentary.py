"""
donate commentary
"""

from yoyo import step

__depends__ = {"20260508_01_WdPck-initial"}

steps = [
    step(
        "ALTER TABLE donations ADD COLUMN commentary TEXT DEFAULT NULL;",
        "ALTER TABLE donations DROP COLUMN commentary;",
    )
]
