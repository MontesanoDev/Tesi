from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.db import get_storage_path

MAX_FILE_SIZE = 20 * 1024 * 1024
CHUNK_SIZE = 1_200
CHUNK_OVERLAP = 200
SUPPORTED_EXTENSIONS = {".pdf": "application/pdf", ".txt": "text/plain"}


class IngestionError(ValueError):
    pass


class UnsupportedDocumentError(IngestionError):
    pass


class DocumentTooLargeError(IngestionError):
    pass


class EmptyDocumentError(IngestionError):
    pass


class InvalidDocumentError(IngestionError):
    pass


@dataclass(frozen=True)
class IngestedDocument:
    name: str
    storage_path: str
    mime_type: str
    byte_size: int
    page_count: int
    chunks: list[str]


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    normalized = re.sub(r"[ \t]+", " ", text.replace("\x00", ""))
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip()
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start + chunk_size // 2, end)
            if boundary > start:
                end = boundary
        content = normalized[start:end].strip()
        if content:
            chunks.append(content)
        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks


def _extract_text(path: Path, extension: str) -> tuple[str, int]:
    if extension == ".txt":
        return path.read_text(encoding="utf-8", errors="replace"), 1

    try:
        reader = PdfReader(path)
        pages = [page.extract_text() or "" for page in reader.pages]
    except (PdfReadError, OSError, ValueError) as exc:
        raise InvalidDocumentError("Il PDF non e leggibile o risulta danneggiato") from exc
    return "\n\n".join(pages), len(pages)


def _finish_ingestion(
    path: Path,
    storage_root: Path,
    original_name: str,
    extension: str,
    mime_type: str,
    byte_size: int,
) -> IngestedDocument:
    text, page_count = _extract_text(path, extension)
    chunks = chunk_text(text)
    if not chunks:
        raise EmptyDocumentError(
            "Il documento non contiene testo estraibile; potrebbe essere necessaria la OCR"
        )
    return IngestedDocument(
        name=original_name,
        storage_path=str(path.relative_to(storage_root)),
        mime_type=mime_type,
        byte_size=byte_size,
        page_count=page_count,
        chunks=chunks,
    )


async def ingest_upload(project_id: str, upload: UploadFile) -> IngestedDocument:
    original_name = Path(upload.filename or "").name
    extension = Path(original_name).suffix.lower()
    if not original_name or extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedDocumentError("Sono supportati soltanto file PDF e TXT")

    mime_type = SUPPORTED_EXTENSIONS[extension]
    storage_root = get_storage_path()
    project_directory = storage_root / project_id
    project_directory.mkdir(parents=True, exist_ok=True)
    destination = project_directory / f"{uuid4().hex}{extension}"

    byte_size = 0
    try:
        with destination.open("wb") as target:
            while chunk := await upload.read(1024 * 1024):
                byte_size += len(chunk)
                if byte_size > MAX_FILE_SIZE:
                    raise DocumentTooLargeError("Il file supera il limite di 20 MB")
                target.write(chunk)
        return _finish_ingestion(
            destination,
            storage_root,
            original_name,
            extension,
            mime_type,
            byte_size,
        )
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()


async def ingest_global_upload(category: str, upload: UploadFile) -> IngestedDocument:
    return await ingest_upload(f"_global/{category}", upload)
