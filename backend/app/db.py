from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mapi.db"


def get_db_path() -> Path:
    configured = os.getenv("MAPI_DB_PATH")
    return Path(configured) if configured else DEFAULT_DB_PATH


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
        db.commit()
    finally:
        db.close()


def init_database() -> None:
    with connection() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                status_tone TEXT NOT NULL,
                updated_label TEXT NOT NULL,
                instructions TEXT NOT NULL,
                shared_source_count INTEGER NOT NULL DEFAULT 0,
                model_count INTEGER NOT NULL DEFAULT 0,
                call_fact_count INTEGER NOT NULL DEFAULT 0,
                missing_fact_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS project_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                metadata TEXT NOT NULL,
                kind TEXT NOT NULL,
                status TEXT NOT NULL,
                sort_order INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS knowledge_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                detail TEXT NOT NULL,
                scope TEXT NOT NULL,
                tone TEXT NOT NULL,
                item_count INTEGER NOT NULL DEFAULT 0,
                sort_order INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                metadata TEXT NOT NULL,
                target TEXT,
                sort_order INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS document_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                section TEXT NOT NULL,
                label TEXT NOT NULL,
                value TEXT,
                provenance TEXT,
                source_kind TEXT NOT NULL,
                status TEXT NOT NULL,
                sort_order INTEGER NOT NULL DEFAULT 0
            );
            """
        )
