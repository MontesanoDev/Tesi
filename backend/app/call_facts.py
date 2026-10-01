from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, replace
from typing import Literal

CallFactStatus = Literal["pending", "verified", "discarded"]
CallFactAction = Literal["verify", "edit", "discard", "restore"]

STATUS_LABELS: dict[CallFactStatus, str] = {
    "pending": "Disponibile",
    "verified": "Verificato",
    "discarded": "Scartato",
}
LABEL_STATUSES = {label.casefold(): status for status, label in STATUS_LABELS.items()}
LABEL_STATUSES["da verificare"] = "pending"
FACT_ID_PATTERN = re.compile(r"^<!--\s*fact-id:\s*([a-z0-9-]+)\s*-->$", re.IGNORECASE)
SOURCE_PATTERN = re.compile(r"^-\s+(.+),\s+frammento\s+(\d+)\s*$", re.IGNORECASE)


class CallFactsFormatError(ValueError):
    pass


@dataclass(frozen=True)
class CallFactSource:
    name: str
    fragment: int


@dataclass(frozen=True)
class CallFact:
    id: str
    title: str
    value: str
    status: CallFactStatus
    sources: list[CallFactSource]
    origin: Literal["extracted", "user_corrected"] = "extracted"


@dataclass(frozen=True)
class CallFactsDocument:
    project_id: str
    model: str
    facts: list[CallFact]
    missing_information: list[str]

    @property
    def pending_count(self) -> int:
        return sum(fact.status == "pending" for fact in self.facts)

    @property
    def verified_count(self) -> int:
        return sum(fact.status == "verified" for fact in self.facts)

    @property
    def discarded_count(self) -> int:
        return sum(fact.status == "discarded" for fact in self.facts)

    @property
    def active_count(self) -> int:
        return self.pending_count + self.verified_count

    @property
    def available_facts(self) -> list[CallFact]:
        return [fact for fact in self.facts if fact.status != "discarded" and fact.sources]


def _single_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def build_fact_id(
    title: str,
    sources: list[CallFactSource],
    ordinal: int,
) -> str:
    source_key = "|".join(f"{source.name}:{source.fragment}" for source in sources)
    digest = hashlib.sha256(f"{ordinal}|{title}|{source_key}".encode()).hexdigest()[:12]
    return f"cf-{digest}"


def new_call_fact(
    title: str,
    value: str,
    sources: list[CallFactSource],
    ordinal: int,
) -> CallFact:
    normalized_title = _single_line(title)
    normalized_value = _single_line(value)
    return CallFact(
        id=build_fact_id(normalized_title, sources, ordinal),
        title=normalized_title,
        value=normalized_value,
        status="pending",
        sources=sources,
    )


def _frontmatter(lines: list[str]) -> tuple[dict[str, str], int]:
    if not lines or lines[0].strip() != "---":
        return {}, 0
    try:
        closing = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as exc:
        raise CallFactsFormatError("Il frontmatter di call-facts.md non e chiuso") from exc
    values: dict[str, str] = {}
    for line in lines[1:closing]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values, closing + 1


def _field_value(block: list[str], label: str) -> str | None:
    prefix = f"**{label}:**"
    for line in block:
        if line.strip().startswith(prefix):
            return line.strip()[len(prefix) :].strip()
    return None


def _parse_fact(block: list[str], ordinal: int) -> CallFact:
    title = _single_line(block[0][3:])
    if not title:
        raise CallFactsFormatError("Un Call Fact non contiene il titolo")
    value = _field_value(block, "Valore")
    if not value:
        raise CallFactsFormatError(f"Il Call Fact '{title}' non contiene un valore")

    status_label = _field_value(block, "Stato") or STATUS_LABELS["pending"]
    status = LABEL_STATUSES.get(status_label.casefold())
    if status is None:
        raise CallFactsFormatError(f"Lo stato '{status_label}' del Call Fact non e valido")

    sources = []
    for line in block:
        match = SOURCE_PATTERN.match(line.strip())
        if match:
            sources.append(
                CallFactSource(
                    name=match.group(1).strip(),
                    fragment=int(match.group(2)),
                )
            )

    fact_id = next(
        (
            match.group(1).lower()
            for line in block
            if (match := FACT_ID_PATTERN.match(line.strip()))
        ),
        build_fact_id(title, sources, ordinal),
    )
    return CallFact(
        id=fact_id,
        title=title,
        value=_single_line(value),
        status=status,
        sources=sources,
        origin="user_corrected" if _field_value(block, "Origine") == "Corretto dall'utente"
        else "extracted",
    )


def parse_call_facts_markdown(content: str) -> CallFactsDocument:
    lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    metadata, body_start = _frontmatter(lines)
    try:
        facts_heading = next(
            index
            for index in range(body_start, len(lines))
            if lines[index].strip() == "# Call Facts"
        )
    except StopIteration as exc:
        raise CallFactsFormatError("call-facts.md non contiene il titolo '# Call Facts'") from exc

    missing_heading = next(
        (
            index
            for index in range(facts_heading + 1, len(lines))
            if lines[index].strip() == "# Informazioni mancanti"
        ),
        len(lines),
    )
    fact_lines = lines[facts_heading + 1 : missing_heading]
    heading_indices = [index for index, line in enumerate(fact_lines) if line.startswith("## ")]
    facts = []
    for ordinal, start in enumerate(heading_indices, start=1):
        end = heading_indices[ordinal] if ordinal < len(heading_indices) else len(fact_lines)
        facts.append(_parse_fact(fact_lines[start:end], ordinal))

    missing_information = []
    if missing_heading < len(lines):
        for line in lines[missing_heading + 1 :]:
            stripped = line.strip()
            if not stripped.startswith("- "):
                continue
            value = stripped[2:].strip()
            if value and not value.startswith("Nessuna informazione mancante"):
                missing_information.append(value)

    return CallFactsDocument(
        project_id=metadata.get("project", ""),
        model=metadata.get("model", "manuale"),
        facts=facts,
        missing_information=list(dict.fromkeys(missing_information)),
    )


def _document_status(document: CallFactsDocument) -> str:
    return "available" if document.available_facts else "empty"


def render_call_facts_document(document: CallFactsDocument) -> str:
    lines = [
        "---",
        "artifact: call_facts",
        "scope: project",
        f"project: {document.project_id}",
        f"status: {_document_status(document)}",
        f"model: {document.model}",
        "---",
        "",
        "# Call Facts",
        "",
        "> Dati estratti dalle fonti del progetto; non costituiscono una verifica dei requisiti.",
    ]
    for fact in document.facts:
        lines.extend(
            (
                "",
                f"## {_single_line(fact.title)}",
                "",
                f"<!-- fact-id: {fact.id} -->",
                "",
                f"**Valore:** {_single_line(fact.value)}",
                "",
                f"**Stato:** {STATUS_LABELS[fact.status]}",
                "",
                "**Origine:** " + (
                    "Corretto dall'utente" if fact.origin == "user_corrected"
                    else "Estratto dalle fonti"
                ),
                "",
                "**Fonti:**",
            )
        )
        lines.extend(
            f"- {_single_line(source.name)}, frammento {source.fragment}"
            for source in fact.sources
        )

    lines.extend(("", "# Informazioni mancanti", ""))
    if document.missing_information:
        lines.extend(f"- {_single_line(item)}" for item in document.missing_information)
    else:
        lines.append("- Nessuna informazione mancante segnalata dall'estrazione automatica.")
    lines.append("")
    return "\n".join(lines)


def revise_call_fact(
    document: CallFactsDocument,
    fact_id: str,
    action: CallFactAction,
    title: str | None = None,
    value: str | None = None,
) -> CallFactsDocument:
    fact = next((item for item in document.facts if item.id == fact_id), None)
    if fact is None:
        raise CallFactsFormatError("Call Fact non trovato nella versione corrente")

    if action == "verify":
        if not fact.sources:
            raise CallFactsFormatError("Un Call Fact senza fonti non puo essere verificato")
        revised = replace(fact, status="verified")
    elif action == "discard":
        revised = replace(fact, status="discarded")
    elif action == "restore":
        revised = replace(fact, status="pending")
    elif action == "edit":
        revised_title = _single_line(title or "")
        revised_value = _single_line(value or "")
        if not revised_title or not revised_value:
            raise CallFactsFormatError("Titolo e valore sono obbligatori per la modifica")
        revised = replace(
            fact,
            title=revised_title,
            value=revised_value,
            status="pending",
            origin="user_corrected",
        )
    else:
        raise CallFactsFormatError("Azione di revisione non supportata")

    facts = [revised if item.id == fact_id else item for item in document.facts]
    return replace(document, facts=facts)


def available_project_facts_markdown(content: str) -> str:
    document = parse_call_facts_markdown(content)
    if not document.available_facts:
        return ""
    lines = ["# Dati del progetto estratti dalle fonti"]
    for fact in document.available_facts:
        origin = (
            "Corretto dall'utente" if fact.origin == "user_corrected"
            else "Estratto automaticamente"
        )
        lines.extend(
            ("", f"## {fact.title}", "", fact.value, "", f"Origine: {origin}.", "Fonti di origine:")
        )
        lines.extend(f"- {source.name}, frammento {source.fragment}" for source in fact.sources)
    return "\n".join(lines) + "\n"
