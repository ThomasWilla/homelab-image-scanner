import sqlite3
from pathlib import Path

from dockwatch.models import DockerImage


class StateStore:
    """SQLite-backed scan state."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS images (reference TEXT PRIMARY KEY, image_id TEXT NOT NULL, project_uuid TEXT, last_uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP)"
            )

    def has_current_image(self, image: DockerImage) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT image_id FROM images WHERE reference = ?",
                (image.reference,),
            ).fetchone()
        return bool(row and row[0] == image.image_id)

    def get_project_uuid(self, image: DockerImage) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT project_uuid FROM images WHERE reference = ?",
                (image.reference,),
            ).fetchone()
        return row[0] if row and row[0] else None

    def save_image(self, image: DockerImage, project_uuid: str | None = None) -> None:
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM images WHERE reference = ?",
                (image.reference,),
            )
            conn.execute(
                "INSERT INTO images (reference, image_id, project_uuid, last_uploaded_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
                (image.reference, image.image_id, project_uuid),
            )
