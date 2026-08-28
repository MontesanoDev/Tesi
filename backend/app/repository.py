from __future__ import annotations

import json
import math
import re
import sqlite3
import unicodedata
from uuid import uuid4

from app.artifacts import get_project_artifact
from app.call_facts import CallFactsFormatError, parse_call_facts_markdown
from app.db import connection
from app.ingestion import IngestedDocument
from app.schemas import ProjectCreate

SEARCH_STOP_WORDS = {
    "che",
    "chi",
    "come",
    "con",
    "cosa",
    "dei",
    "del",
    "della",
    "delle",
    "gli",
    "nel",
    "nella",
    "per",
    "qual",
    "quale",
    "quali",
    "sono",
    "una",
}
TEMPORAL_QUERY_TERMS = {
    "data",
    "date",
    "entro",
    "quando",
    "scadenza",
    "scadenze",
    "termine",
    "termini",
}
DATE_PATTERN = re.compile(r"\b(?:\d{1,2}[./-]){2}\d{2,4}\b")
TIME_PATTERN = re.compile(r"\bore\s+\d{1,2}(?:[.:]\d{2})?", flags=re.IGNORECASE)
FOLLOWUP_TERMS = {
    "anche",
    "e",
    "esso",
    "essa",
    "invece",
    "lei",
    "lui",
    "quella",
    "quello",
    "questa",
    "questo",
    "sua",
    "sue",
    "suo",
    "suoi",
}
FOLLOWUP_CLITIC_PATTERN = re.compile(r"(?:ar|er|ir)(?:gli|la|le|li|lo|ne)$")


def _rows(db: sqlite3.Connection, query: str, params: tuple = ()) -> list[dict]:
    return [dict(row) for row in db.execute(query, params).fetchall()]


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    return slug or f"progetto-{uuid4().hex[:8]}"


def _conversation_title(question: str) -> str:
    compact = re.sub(r"\s+", " ", question).strip()
    title = compact[:72].rstrip()
    return f"{title[0].upper()}{title[1:]}" if title else "Nuova conversazione"


def _format_size(byte_size: int) -> str:
    if byte_size >= 1024 * 1024:
        return f"{byte_size / (1024 * 1024):.1f} MB".replace(".0 ", " ")
    if byte_size >= 1024:
        return f"{round(byte_size / 1024)} KB"
    return f"{byte_size} B"


def _normalized_tokens(value: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return set(re.findall(r"[^\W_]+", normalized.lower(), flags=re.UNICODE))


def _meaningful_search_tokens(value: str) -> list[str]:
    return [
        token
        for token in _normalized_tokens(value)
        if token not in SEARCH_STOP_WORDS
        and (len(token) >= 3 or any(char.isdigit() for char in token))
    ]


def _search_stem(token: str) -> str:
    if len(token) >= 5 and token[-1] in "aeiou":
        return token[:-1]
    return token


def _build_fts_query(query: str) -> str:
    terms = []
    for token in _meaningful_search_tokens(query):
        stem = _search_stem(token)
        if stem != token:
            terms.append(f'"{stem}"*')
        else:
            terms.append(f'"{token}"')
    return " OR ".join(terms)


def _rerank_evidence(query: str, candidates: list[dict], limit: int) -> list[dict]:
    query_tokens = _normalized_tokens(query)
    search_tokens = _meaningful_search_tokens(query)
    temporal_query = bool(query_tokens & TEMPORAL_QUERY_TERMS)

    for candidate in candidates:
        bm25_score = max(0.0, -candidate.pop("rank"))
        content = candidate["content"]
        content_tokens = _normalized_tokens(content)
        matched_count = sum(
            any(content_token.startswith(_search_stem(token)) for content_token in content_tokens)
            for token in search_tokens
        )
        coverage = matched_count / len(search_tokens) if search_tokens else 0.0
        relevance = math.log1p(bm25_score) + matched_count * 1.5 + coverage * 6.0
        if temporal_query:
            if DATE_PATTERN.search(content):
                relevance += 6.0
            if TIME_PATTERN.search(content):
                relevance += 3.0
        candidate["relevance"] = round(relevance, 6)
    candidates.sort(key=lambda item: item["relevance"], reverse=True)

    selected: list[dict] = []
    deferred: list[dict] = []
    for candidate in candidates:
        duplicates_adjacent_chunk = any(
            item["file_id"] == candidate["file_id"]
            and abs(item["chunk_index"] - candidate["chunk_index"]) <= 1
            for item in selected
        )
        if duplicates_adjacent_chunk:
            deferred.append(candidate)
        elif len(selected) < limit:
            selected.append(candidate)
    if len(selected) < limit:
        selected.extend(deferred[: limit - len(selected)])
    return selected


def _neighbor_excerpt(content: str, offset: int, window: int = 480) -> str:
    normalized = re.sub(r"\s+", " ", content).strip()
    if len(normalized) <= window:
        return normalized
    if offset < 0:
        return f"... {normalized[-window:]}"
    return f"{normalized[:window]} ..."


def _expand_neighbor_evidence(
    project_id: str,
    anchors: list[dict],
    max_results: int,
) -> list[dict]:
    if len(anchors) >= max_results:
        return anchors[:max_results]

    expanded = list(anchors)
    seen_chunk_ids = {item["chunk_id"] for item in anchors}
    with connection() as db:
        for offset in (-1, 1):
            for anchor in anchors:
                if anchor["file_id"] < 0:
                    row = db.execute(
                        """
                        SELECT
                            -c.id AS chunk_id,
                            -d.id AS file_id,
                            d.name AS source_name,
                            c.chunk_index,
                            c.content
                        FROM global_document_chunks c
                        JOIN global_documents d ON d.id = c.document_id
                        LEFT JOIN project_global_document_links l
                          ON l.document_id = d.id AND l.project_id = ?
                        WHERE c.document_id = ? AND c.chunk_index = ?
                          AND (d.category = 'company' OR l.project_id IS NOT NULL)
                        """,
                        (
                            project_id,
                            -anchor["file_id"],
                            anchor["chunk_index"] + offset,
                        ),
                    ).fetchone()
                else:
                    row = db.execute(
                        """
                        SELECT
                            c.id AS chunk_id,
                            c.file_id,
                            f.name AS source_name,
                            c.chunk_index,
                            c.content
                        FROM document_chunks c
                        JOIN project_files f ON f.id = c.file_id
                        WHERE c.project_id = ? AND c.file_id = ? AND c.chunk_index = ?
                        """,
                        (project_id, anchor["file_id"], anchor["chunk_index"] + offset),
                    ).fetchone()
                if row is None or row["chunk_id"] in seen_chunk_ids:
                    continue
                neighbor = dict(row)
                neighbor["excerpt"] = _neighbor_excerpt(neighbor["content"], offset)
                neighbor["relevance"] = round(anchor["relevance"] - 0.25, 6)
                expanded.append(neighbor)
                seen_chunk_ids.add(neighbor["chunk_id"])
                if len(expanded) >= max_results:
                    return expanded
    return expanded


def list_projects() -> list[dict]:
    with connection() as db:
        return _rows(
            db,
            """
            SELECT
                p.id, p.title, p.description, p.status, p.status_tone,
                p.updated_label, p.shared_source_count AS source_count,
                p.model_count
            FROM projects p
            ORDER BY p.rowid
            """,
        )


def get_global_knowledge() -> dict:
    with connection() as db:
        documents = _rows(
            db,
            """
            SELECT id, name, category, metadata, status, mime_type, byte_size,
                   page_count, chunk_count, created_at, updated_at
            FROM global_documents
            ORDER BY datetime(created_at) DESC, id DESC
            """,
        )
    return {
        "documents": documents,
        "document_count": len(documents),
        "chunk_count": sum(document["chunk_count"] for document in documents),
    }


def _global_document_metadata(mime_type: str, byte_size: int, chunk_count: int) -> str:
    chunk_label = "frammento" if chunk_count == 1 else "frammenti"
    file_type = {
        "application/pdf": "PDF",
        "text/markdown": "MD",
    }.get(mime_type, "TXT")
    return f"{file_type} · {_format_size(byte_size)} · {chunk_count} {chunk_label}"


def add_global_document(document: IngestedDocument, category: str) -> dict:
    chunk_count = len(document.chunks)
    metadata = _global_document_metadata(
        document.mime_type,
        document.byte_size,
        chunk_count,
    )
    with connection() as db:
        cursor = db.execute(
            """
            INSERT INTO global_documents (
                name, category, metadata, status, storage_path, mime_type,
                byte_size, page_count, chunk_count
            ) VALUES (?, ?, ?, 'Indicizzato', ?, ?, ?, ?, ?)
            """,
            (
                document.name,
                category,
                metadata,
                document.storage_path,
                document.mime_type,
                document.byte_size,
                document.page_count,
                chunk_count,
            ),
        )
        document_id = cursor.lastrowid
        if document_id is None:
            raise RuntimeError("Il documento globale non ha ricevuto un identificativo")
        db.executemany(
            """
            INSERT INTO global_document_chunks (
                document_id, chunk_index, content, char_count
            ) VALUES (?, ?, ?, ?)
            """,
            [
                (document_id, index, content, len(content))
                for index, content in enumerate(document.chunks)
            ],
        )
        row = db.execute(
            """
            SELECT id, name, category, metadata, status, mime_type, byte_size,
                   page_count, chunk_count, created_at, updated_at
            FROM global_documents WHERE id = ?
            """,
            (document_id,),
        ).fetchone()
    if row is None:
        raise RuntimeError("Il documento globale appena creato non e disponibile")
    return dict(row)


def get_global_document_record(document_id: int) -> dict | None:
    with connection() as db:
        row = db.execute(
            """
            SELECT id, name, category, metadata, status, storage_path, mime_type,
                   byte_size, page_count, chunk_count, created_at, updated_at
            FROM global_documents WHERE id = ?
            """,
            (document_id,),
        ).fetchone()
    return dict(row) if row is not None else None


def update_global_document_content(
    document_id: int,
    byte_size: int,
    chunks: list[str],
) -> dict | None:
    with connection() as db:
        document = db.execute(
            "SELECT mime_type FROM global_documents WHERE id = ?",
            (document_id,),
        ).fetchone()
        if document is None:
            return None

        db.execute(
            "DELETE FROM global_document_chunks WHERE document_id = ?",
            (document_id,),
        )
        db.executemany(
            """
            INSERT INTO global_document_chunks (
                document_id, chunk_index, content, char_count
            ) VALUES (?, ?, ?, ?)
            """,
            [
                (document_id, index, chunk, len(chunk))
                for index, chunk in enumerate(chunks)
            ],
        )
        db.execute(
            """
            UPDATE global_documents
            SET metadata = ?, status = 'Indicizzato', byte_size = ?,
                page_count = 1, chunk_count = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                _global_document_metadata(document["mime_type"], byte_size, len(chunks)),
                byte_size,
                len(chunks),
                document_id,
            ),
        )
        row = db.execute(
            """
            SELECT id, name, category, metadata, status, mime_type, byte_size,
                   page_count, chunk_count, created_at, updated_at
            FROM global_documents WHERE id = ?
            """,
            (document_id,),
        ).fetchone()
    return dict(row) if row is not None else None


def delete_global_document(document_id: int) -> dict | None:
    with connection() as db:
        row = db.execute(
            "SELECT id, storage_path FROM global_documents WHERE id = ?",
            (document_id,),
        ).fetchone()
        if row is None:
            return None
        db.execute("DELETE FROM global_documents WHERE id = ?", (document_id,))
    return dict(row)


def list_project_global_documents(project_id: str) -> list[dict] | None:
    with connection() as db:
        if db.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
            return None
        return _rows(
            db,
            """
            SELECT d.id, d.name, d.category, d.metadata, d.status, d.mime_type,
                   d.byte_size, d.page_count, d.chunk_count,
                   CASE
                       WHEN d.category = 'company' THEN 1
                       WHEN l.project_id IS NULL THEN 0
                       ELSE 1
                   END AS linked
            FROM global_documents d
            LEFT JOIN project_global_document_links l
              ON l.document_id = d.id AND l.project_id = ?
            ORDER BY datetime(d.created_at) DESC, d.id DESC
            """,
            (project_id,),
        )


def get_company_context(
    max_characters: int = 45_000,
) -> list[dict]:
    with connection() as db:
        rows = _rows(
            db,
            """
            SELECT d.name AS source_name, c.chunk_index, c.content
            FROM global_documents d
            JOIN global_document_chunks c ON c.document_id = d.id
            WHERE d.category = 'company'
            ORDER BY d.id, c.chunk_index
            """,
        )

    selected: list[dict] = []
    used_characters = 0
    for row in rows:
        remaining = max_characters - used_characters
        if remaining <= 0:
            break
        content = row["content"][:remaining]
        if not content:
            continue
        selected.append({**row, "content": content})
        used_characters += len(content)
    return selected


def set_project_global_document_link(
    project_id: str,
    document_id: int,
    linked: bool,
) -> dict | None:
    with connection() as db:
        if db.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
            return None
        document = db.execute(
            "SELECT category FROM global_documents WHERE id = ?",
            (document_id,),
        ).fetchone()
        if document is None:
            return None
        if document["category"] == "general":
            if linked:
                db.execute(
                    """
                    INSERT OR IGNORE INTO project_global_document_links (project_id, document_id)
                    VALUES (?, ?)
                    """,
                    (project_id, document_id),
                )
            else:
                db.execute(
                    """
                    DELETE FROM project_global_document_links
                    WHERE project_id = ? AND document_id = ?
                    """,
                    (project_id, document_id),
                )
    documents = list_project_global_documents(project_id)
    if documents is None:
        return None
    return next((item for item in documents if item["id"] == document_id), None)


def get_project(project_id: str) -> dict | None:
    with connection() as db:
        project = db.execute(
            """
            SELECT
                p.*,
                p.shared_source_count AS source_count
            FROM projects p
            WHERE p.id = ?
            """,
            (project_id,),
        ).fetchone()
        if project is None:
            return None

        result = dict(project)
        result["files"] = _rows(
            db,
            """
            SELECT id, name, metadata, kind, status, mime_type, byte_size,
                   page_count, chunk_count
            FROM project_files
            WHERE project_id = ? AND kind != 'artifact'
            ORDER BY sort_order
            """,
            (project_id,),
        )
        result["knowledge_sources"] = _rows(
            db,
            """
            SELECT id, name, detail, scope, tone, item_count
            FROM knowledge_sources WHERE project_id = ? ORDER BY sort_order
            """,
            (project_id,),
        )
        active_global_knowledge = _rows(
            db,
            """
            SELECT d.category, COUNT(*) AS document_count,
                   COALESCE(SUM(d.chunk_count), 0) AS chunk_count
            FROM global_documents d
            LEFT JOIN project_global_document_links l
              ON l.document_id = d.id AND l.project_id = ?
            WHERE d.category = 'company'
               OR (d.category = 'general' AND l.project_id IS NOT NULL)
            GROUP BY d.category
            """,
            (project_id,),
        )
        counts = {row["category"]: row for row in active_global_knowledge}
        for source_id, category, name in (
            (-1, "company", "Company KB"),
            (-2, "general", "General KB"),
        ):
            values = counts.get(category, {"document_count": 0, "chunk_count": 0})
            document_count = values["document_count"]
            chunk_count = values["chunk_count"]
            result["knowledge_sources"].append(
                {
                    "id": source_id,
                    "name": name,
                    "detail": (
                        (
                            "1 frammento disponibile"
                            if chunk_count == 1
                            else f"{chunk_count} frammenti disponibili"
                        )
                        if document_count
                        else "Nessun documento collegato"
                    ),
                    "scope": "global",
                    "tone": "success" if document_count else "info",
                    "item_count": document_count,
                }
            )
        result["conversations"] = _rows(
            db,
            """
            SELECT id, title, metadata, target
            FROM conversations
            WHERE project_id = ?
            ORDER BY datetime(updated_at) DESC, rowid DESC, sort_order
            """,
            (project_id,),
        )
        return result


def get_or_create_conversation(
    project_id: str,
    conversation_id: str | None,
    first_question: str,
) -> dict | None:
    with connection() as db:
        if conversation_id:
            row = db.execute(
                """
                SELECT id, project_id, title, metadata, target
                FROM conversations
                WHERE id = ? AND project_id = ?
                """,
                (conversation_id, project_id),
            ).fetchone()
            return dict(row) if row is not None else None

        new_id = f"conv-{uuid4().hex[:16]}"
        db.execute(
            """
            INSERT INTO conversations (
                id, project_id, title, metadata, target, sort_order
            ) VALUES (?, ?, ?, 'Ora · nuova conversazione', 'chat', 0)
            """,
            (new_id, project_id, _conversation_title(first_question)),
        )
        row = db.execute(
            """
            SELECT id, project_id, title, metadata, target
            FROM conversations WHERE id = ?
            """,
            (new_id,),
        ).fetchone()
    return dict(row) if row is not None else None


def get_conversation_history(conversation_id: str, limit: int = 6) -> list[dict]:
    with connection() as db:
        rows = _rows(
            db,
            """
            SELECT question, answer, evidence_json
            FROM conversation_turns
            WHERE conversation_id = ? AND answer IS NOT NULL
            ORDER BY id DESC
            LIMIT ?
            """,
            (conversation_id, limit),
        )
    rows.reverse()
    for row in rows:
        row["evidence"] = json.loads(row.pop("evidence_json"))
    return rows


def is_follow_up_question(question: str) -> bool:
    tokens = _normalized_tokens(question)
    return bool(
        tokens & FOLLOWUP_TERMS or any(FOLLOWUP_CLITIC_PATTERN.search(token) for token in tokens)
    )


def contextualize_search_query(question: str, history: list[dict]) -> str:
    if history and is_follow_up_question(question):
        return f"{history[-1]['question']} {question}"
    return question


def recent_conversation_evidence(history: list[dict]) -> list[dict]:
    if not history:
        return []
    evidence = history[-1].get("evidence") or []
    return [
        {
            **item,
            "content": item["excerpt"],
        }
        for item in evidence
    ]


def _public_evidence(evidence: list[dict]) -> list[dict]:
    fields = (
        "chunk_id",
        "file_id",
        "source_name",
        "chunk_index",
        "excerpt",
        "relevance",
    )
    return [{field: item[field] for field in fields} for item in evidence]


def save_conversation_turn(conversation_id: str, response: dict) -> int:
    evidence = _public_evidence(response.get("evidence", []))
    with connection() as db:
        cursor = db.execute(
            """
            INSERT INTO conversation_turns (
                conversation_id, question, answer, citations_json,
                missing_information_json, evidence_json, generation_status,
                model, total_tokens, notice
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                conversation_id,
                response["question"],
                response.get("answer"),
                json.dumps(response.get("citations", [])),
                json.dumps(response.get("missing_information", []), ensure_ascii=False),
                json.dumps(evidence, ensure_ascii=False),
                response["generation_status"],
                response.get("model"),
                response.get("total_tokens"),
                response.get("notice"),
            ),
        )
        turn_id = cursor.lastrowid
        if turn_id is None:
            raise RuntimeError("Il turno non ha ricevuto un identificativo")
        turn_count = db.execute(
            "SELECT COUNT(*) FROM conversation_turns WHERE conversation_id = ?",
            (conversation_id,),
        ).fetchone()[0]
        label = "messaggio" if turn_count == 1 else "messaggi"
        db.execute(
            """
            UPDATE conversations
            SET metadata = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (f"Ora · {turn_count} {label}", conversation_id),
        )
    return int(turn_id)


def get_conversation(project_id: str, conversation_id: str) -> dict | None:
    with connection() as db:
        conversation = db.execute(
            """
            SELECT id, project_id, title, metadata, target
            FROM conversations
            WHERE id = ? AND project_id = ?
            """,
            (conversation_id, project_id),
        ).fetchone()
        if conversation is None:
            return None
        turns = _rows(
            db,
            """
            SELECT
                id, question, answer, citations_json,
                missing_information_json, evidence_json,
                generation_status, model, total_tokens, notice
            FROM conversation_turns
            WHERE conversation_id = ?
            ORDER BY id
            """,
            (conversation_id,),
        )

    result = dict(conversation)
    result["turns"] = [
        {
            "id": turn["id"],
            "question": turn["question"],
            "answer": turn["answer"],
            "citations": json.loads(turn["citations_json"]),
            "missing_information": json.loads(turn["missing_information_json"]),
            "evidence": json.loads(turn["evidence_json"]),
            "generation_status": turn["generation_status"],
            "model": turn["model"],
            "total_tokens": turn["total_tokens"],
            "notice": turn["notice"],
        }
        for turn in turns
    ]
    return result


def create_project(payload: ProjectCreate) -> dict:
    base_id = _slugify(payload.title)
    with connection() as db:
        project_id = base_id
        suffix = 2
        while db.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone():
            project_id = f"{base_id}-{suffix}"
            suffix += 1
        db.execute(
            """
            INSERT INTO projects (
                id, title, description, status, status_tone, updated_label,
                instructions, shared_source_count, model_count,
                call_fact_count, missing_fact_count
            ) VALUES (?, ?, ?, 'In configurazione', 'info', 'Aggiornato ora',
                      'Usa solo informazioni presenti nelle fonti.', 0, 0, 0, 0)
            """,
            (project_id, payload.title, payload.description),
        )
    project = get_project(project_id)
    if project is None:
        raise RuntimeError("Il progetto appena creato non e stato trovato")
    return project


def delete_project(project_id: str) -> bool:
    with connection() as db:
        cursor = db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        return cursor.rowcount > 0


def add_project_file(project_id: str, document: IngestedDocument) -> dict | None:
    chunk_count = len(document.chunks)
    metadata = _global_document_metadata(
        document.mime_type,
        document.byte_size,
        chunk_count,
    )

    with connection() as db:
        if db.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
            return None
        sort_order = db.execute(
            "SELECT COALESCE(MAX(sort_order), 0) + 1 FROM project_files WHERE project_id = ?",
            (project_id,),
        ).fetchone()[0]
        cursor = db.execute(
            """
            INSERT INTO project_files (
                project_id, name, metadata, kind, status, storage_path,
                mime_type, byte_size, page_count, chunk_count, sort_order
            ) VALUES (?, ?, ?, 'source', 'Indicizzato', ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                document.name,
                metadata,
                document.storage_path,
                document.mime_type,
                document.byte_size,
                document.page_count,
                chunk_count,
                sort_order,
            ),
        )
        file_id = cursor.lastrowid
        if file_id is None:
            raise RuntimeError("Il file indicizzato non ha ricevuto un identificativo")
        db.executemany(
            """
            INSERT INTO document_chunks (
                project_id, file_id, chunk_index, content, char_count
            ) VALUES (?, ?, ?, ?, ?)
            """,
            [
                (project_id, file_id, index, content, len(content))
                for index, content in enumerate(document.chunks)
            ],
        )
        db.execute(
            """
            UPDATE projects
            SET shared_source_count = shared_source_count + 1,
                updated_label = 'Aggiornato ora'
            WHERE id = ?
            """,
            (project_id,),
        )
        row = db.execute(
            """
            SELECT id, name, metadata, kind, status, mime_type, byte_size,
                   page_count, chunk_count
            FROM project_files WHERE id = ?
            """,
            (file_id,),
        ).fetchone()
    return dict(row) if row is not None else None


def get_project_file_record(project_id: str, file_id: int) -> dict | None:
    with connection() as db:
        row = db.execute(
            """
            SELECT id, project_id, name, metadata, kind, status, storage_path,
                   mime_type, byte_size, page_count, chunk_count
            FROM project_files
            WHERE project_id = ? AND id = ? AND kind != 'artifact'
            """,
            (project_id, file_id),
        ).fetchone()
    return dict(row) if row is not None else None


def update_project_file_content(
    project_id: str,
    file_id: int,
    byte_size: int,
    chunks: list[str],
) -> dict | None:
    with connection() as db:
        document = db.execute(
            """
            SELECT mime_type
            FROM project_files
            WHERE project_id = ? AND id = ? AND kind != 'artifact'
            """,
            (project_id, file_id),
        ).fetchone()
        if document is None:
            return None

        db.execute("DELETE FROM document_chunks WHERE file_id = ?", (file_id,))
        db.executemany(
            """
            INSERT INTO document_chunks (
                project_id, file_id, chunk_index, content, char_count
            ) VALUES (?, ?, ?, ?, ?)
            """,
            [
                (project_id, file_id, index, chunk, len(chunk))
                for index, chunk in enumerate(chunks)
            ],
        )
        db.execute(
            """
            UPDATE project_files
            SET metadata = ?, status = 'Indicizzato', byte_size = ?,
                page_count = 1, chunk_count = ?
            WHERE project_id = ? AND id = ?
            """,
            (
                _global_document_metadata(document["mime_type"], byte_size, len(chunks)),
                byte_size,
                len(chunks),
                project_id,
                file_id,
            ),
        )
        db.execute(
            "UPDATE projects SET updated_label = 'Aggiornato ora' WHERE id = ?",
            (project_id,),
        )
        row = db.execute(
            """
            SELECT id, name, metadata, kind, status, mime_type, byte_size,
                   page_count, chunk_count
            FROM project_files WHERE project_id = ? AND id = ?
            """,
            (project_id, file_id),
        ).fetchone()
    return dict(row) if row is not None else None


def update_call_fact_metrics(
    project_id: str,
    fact_count: int,
    missing_count: int,
) -> bool:
    return update_call_fact_review_metrics(
        project_id=project_id,
        active_count=fact_count,
        verified_count=0,
        pending_count=fact_count,
        discarded_count=0,
        missing_count=missing_count,
    )


def update_call_fact_review_metrics(
    project_id: str,
    active_count: int,
    verified_count: int,
    pending_count: int,
    discarded_count: int,
    missing_count: int,
) -> bool:
    fully_reviewed = active_count > 0 and pending_count == 0
    project_status = "Call Facts verificati" if fully_reviewed else "Da verificare"
    tone = "success" if fully_reviewed else "warning"
    with connection() as db:
        cursor = db.execute(
            """
            UPDATE projects
            SET call_fact_count = ?, missing_fact_count = ?,
                status = ?, status_tone = ?,
                updated_label = 'Aggiornato ora'
            WHERE id = ?
            """,
            (active_count, missing_count, project_status, tone, project_id),
        )
        if cursor.rowcount == 0:
            return False

        source = db.execute(
            """
            SELECT id FROM knowledge_sources
            WHERE project_id = ?
              AND (name = 'Call Facts' OR name = 'Dati estratti dal bando')
            ORDER BY id
            LIMIT 1
            """,
            (project_id,),
        ).fetchone()
        detail_parts = [f"{verified_count} verificati su {active_count}"]
        if discarded_count:
            detail_parts.append(f"{discarded_count} scartati")
        if missing_count:
            detail_parts.append(f"{missing_count} mancanti")
        detail = " · ".join(detail_parts)
        if source is None:
            sort_order = db.execute(
                """
                SELECT COALESCE(MAX(sort_order), 0) + 1
                FROM knowledge_sources WHERE project_id = ?
                """,
                (project_id,),
            ).fetchone()[0]
            db.execute(
                """
                INSERT INTO knowledge_sources (
                    project_id, name, detail, scope, tone, item_count, sort_order
                ) VALUES (?, 'Call Facts', ?, 'project', ?, ?, ?)
                """,
                (project_id, detail, tone, verified_count, sort_order),
            )
        else:
            db.execute(
                """
                UPDATE knowledge_sources
                SET name = 'Call Facts', detail = ?, tone = ?, item_count = ?
                WHERE id = ?
                """,
                (detail, tone, verified_count, source["id"]),
            )
    return True


def sync_call_fact_review_metrics() -> None:
    with connection() as db:
        project_ids = [row["id"] for row in db.execute("SELECT id FROM projects").fetchall()]
    for project_id in project_ids:
        artifact = get_project_artifact(project_id, f"{project_id}--call-facts")
        if artifact is None:
            continue
        try:
            document = parse_call_facts_markdown(artifact["content"])
        except CallFactsFormatError:
            continue
        if not document.facts:
            continue
        update_call_fact_review_metrics(
            project_id=project_id,
            active_count=document.active_count,
            verified_count=document.verified_count,
            pending_count=document.pending_count,
            discarded_count=document.discarded_count,
            missing_count=len(document.missing_information),
        )


def search_project_evidence(
    project_id: str,
    query: str,
    limit: int = 4,
    include_neighbors: bool = False,
) -> list[dict] | None:
    fts_query = _build_fts_query(query)
    with connection() as db:
        if db.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
            return None
        if not fts_query:
            return []
        project_candidates = _rows(
            db,
            """
            SELECT
                c.id AS chunk_id,
                c.file_id,
                f.name AS source_name,
                c.chunk_index,
                c.content,
                snippet(document_chunks_fts, 2, '', '', ' … ', 36) AS excerpt,
                bm25(document_chunks_fts) AS rank
            FROM document_chunks_fts
            JOIN document_chunks c ON c.id = document_chunks_fts.rowid
            JOIN project_files f ON f.id = c.file_id
            WHERE document_chunks_fts MATCH ? AND c.project_id = ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts_query, project_id, max(limit * 6, 24)),
        )
        global_candidates = _rows(
            db,
            """
            SELECT
                -c.id AS chunk_id,
                -d.id AS file_id,
                d.name AS source_name,
                c.chunk_index,
                c.content,
                snippet(global_document_chunks_fts, 1, '', '', ' … ', 36) AS excerpt,
                bm25(global_document_chunks_fts) AS rank
            FROM global_document_chunks_fts
            JOIN global_document_chunks c ON c.id = global_document_chunks_fts.rowid
            JOIN global_documents d ON d.id = c.document_id
            LEFT JOIN project_global_document_links l
              ON l.document_id = d.id AND l.project_id = ?
            WHERE global_document_chunks_fts MATCH ?
              AND (d.category = 'company' OR l.project_id IS NOT NULL)
            ORDER BY rank
            LIMIT ?
            """,
            (project_id, fts_query, max(limit * 6, 24)),
        )
        candidates = project_candidates + global_candidates
    anchors = _rerank_evidence(query, candidates, limit)
    if include_neighbors:
        return _expand_neighbor_evidence(project_id, anchors, max_results=limit * 2)
    return anchors


def get_document_review(project_id: str) -> dict | None:
    project = get_project(project_id)
    if project is None:
        return None
    with connection() as db:
        fields = _rows(
            db,
            """
            SELECT id, section, label, value, provenance, source_kind, status
            FROM document_fields WHERE project_id = ? ORDER BY sort_order
            """,
            (project_id,),
        )
    completed = sum(field["status"] != "missing" for field in fields)
    return {
        "title": "Modulo di candidatura A",
        "subtitle": "Bozza generata dal modello ufficiale",
        "completed_fields": completed,
        "total_fields": len(fields),
        "fields": fields,
    }
