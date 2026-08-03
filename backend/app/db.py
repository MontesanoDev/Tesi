from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mapi.db"
DEFAULT_STORAGE_PATH = Path(__file__).resolve().parents[1] / "data" / "uploads"
DEFAULT_KNOWLEDGE_PATH = Path(__file__).resolve().parents[1] / "data" / "knowledge"


def get_db_path() -> Path:
    configured = os.getenv("MAPI_DB_PATH")
    return Path(configured) if configured else DEFAULT_DB_PATH


def get_storage_path() -> Path:
    configured = os.getenv("MAPI_STORAGE_PATH")
    return Path(configured) if configured else DEFAULT_STORAGE_PATH


def get_knowledge_path() -> Path:
    configured = os.getenv("MAPI_KNOWLEDGE_PATH")
    return Path(configured) if configured else DEFAULT_KNOWLEDGE_PATH


def _ensure_column(db: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row[1] for row in db.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


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
                storage_path TEXT,
                mime_type TEXT,
                byte_size INTEGER NOT NULL DEFAULT 0,
                page_count INTEGER NOT NULL DEFAULT 0,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                sort_order INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                file_id INTEGER NOT NULL REFERENCES project_files(id) ON DELETE CASCADE,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                char_count INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file_id, chunk_index)
            );

            CREATE INDEX IF NOT EXISTS idx_document_chunks_project
            ON document_chunks(project_id);

            CREATE VIRTUAL TABLE IF NOT EXISTS document_chunks_fts USING fts5(
                project_id UNINDEXED,
                file_id UNINDEXED,
                content,
                tokenize = 'unicode61 remove_diacritics 2'
            );

            CREATE TRIGGER IF NOT EXISTS document_chunks_fts_insert
            AFTER INSERT ON document_chunks BEGIN
                INSERT INTO document_chunks_fts(rowid, project_id, file_id, content)
                VALUES (new.id, new.project_id, new.file_id, new.content);
            END;

            CREATE TRIGGER IF NOT EXISTS document_chunks_fts_delete
            AFTER DELETE ON document_chunks BEGIN
                DELETE FROM document_chunks_fts WHERE rowid = old.id;
            END;

            CREATE TRIGGER IF NOT EXISTS document_chunks_fts_update
            AFTER UPDATE ON document_chunks BEGIN
                DELETE FROM document_chunks_fts WHERE rowid = old.id;
                INSERT INTO document_chunks_fts(rowid, project_id, file_id, content)
                VALUES (new.id, new.project_id, new.file_id, new.content);
            END;

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

            CREATE TABLE IF NOT EXISTS company_facts (
                key TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                value TEXT NOT NULL,
                verified INTEGER NOT NULL DEFAULT 0,
                sort_order INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                metadata TEXT NOT NULL,
                target TEXT,
                sort_order INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS conversation_turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                question TEXT NOT NULL,
                answer TEXT,
                citations_json TEXT NOT NULL DEFAULT '[]',
                missing_information_json TEXT NOT NULL DEFAULT '[]',
                evidence_json TEXT NOT NULL DEFAULT '[]',
                generation_status TEXT NOT NULL,
                model TEXT,
                total_tokens INTEGER,
                notice TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_conversation_turns_conversation
            ON conversation_turns(conversation_id, id);

            CREATE TABLE IF NOT EXISTS knowledge_artifacts (
                id TEXT PRIMARY KEY,
                project_id TEXT REFERENCES projects(id) ON DELETE CASCADE,
                kind TEXT NOT NULL,
                scope TEXT NOT NULL,
                title TEXT NOT NULL,
                filename TEXT NOT NULL,
                storage_path TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                byte_size INTEGER NOT NULL DEFAULT 0,
                version INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS project_artifact_links (
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                artifact_id TEXT NOT NULL REFERENCES knowledge_artifacts(id) ON DELETE CASCADE,
                file_id INTEGER NOT NULL UNIQUE REFERENCES project_files(id) ON DELETE CASCADE,
                PRIMARY KEY (project_id, artifact_id)
            );

            CREATE INDEX IF NOT EXISTS idx_project_artifact_links_artifact
            ON project_artifact_links(artifact_id);

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
        _ensure_column(db, "project_files", "storage_path", "TEXT")
        _ensure_column(db, "project_files", "mime_type", "TEXT")
        _ensure_column(db, "project_files", "byte_size", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(db, "project_files", "page_count", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(db, "project_files", "chunk_count", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(db, "conversations", "created_at", "TEXT")
        _ensure_column(db, "conversations", "updated_at", "TEXT")
        db.execute(
            """
            UPDATE conversations
            SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
                updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)
            """
        )
        db.execute(
            """
            INSERT OR REPLACE INTO document_chunks_fts(rowid, project_id, file_id, content)
            SELECT id, project_id, file_id, content FROM document_chunks
            """
        )
