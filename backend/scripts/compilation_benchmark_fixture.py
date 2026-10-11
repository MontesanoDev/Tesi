"""Fixture IO and limited, deterministic scoring; never a semantic acceptance gate."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from collections import Counter
from pathlib import Path


def load_fixture(directory):
    root = Path(directory).resolve()
    manifest = json.loads((root / "manifest.json").read_text())
    for name, expected in manifest["files"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Fixture con percorso esterno")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("Fixture modificata: " + name)
    form = (root / manifest["form"]).resolve()
    if not form.is_relative_to(root) or manifest["form"] not in manifest["files"]:
        raise ValueError("Originale non presente nel manifest")
    gold = json.loads((root / manifest["gold"]).read_text())
    if hashlib.sha256(form.read_bytes()).hexdigest() != gold["original_sha256"]:
        raise ValueError("Gold riferito a un originale diverso")
    if gold["project_id"] != manifest["project_id"]:
        raise ValueError("Progetto gold diverso dalla fixture")
    return {"root": root, "manifest": manifest, "path": form, "gold": gold,
            "sources": json.loads((root / manifest["sources"]).read_text())}


def normalized(value):
    return " ".join(unicodedata.normalize("NFC", value).split()).casefold()


def score_fixture(raw, audit, gold):
    """Compare authored values/choices and citation IDs, not inferred semantics.

    Correct literal values do not establish subject, applicability, complete
    conditions or passage entailment. All rows still require semantic review.
    Missing assignments are omissions, never inferred MISSING/NOT_APPLICABLE.
    """
    proposal = json.loads(raw)
    fields = proposal.get("fields", {})
    facts = proposal.get("facts", {})
    if not isinstance(fields, dict) or not isinstance(facts, dict):
        raise ValueError("Output senza fields/facts validi per il confronto")
    validated = {f["candidate_id"]: f for f in (audit or {}).get("fields", [])}
    results = []
    for expected in gold["fields"]:
        candidate_id = expected["candidate_id"]
        assignment = fields.get(candidate_id)
        present = isinstance(assignment, dict)
        assignment = assignment if present else {}
        fact = facts.get(assignment.get("fact_id"), {})
        fact = fact if isinstance(fact, dict) else {}
        evidence = fact.get("evidence", [])
        citations = [e.get("chunk_id") for e in evidence if isinstance(e, dict)] \
            if isinstance(evidence, list) else []
        disposition = assignment.get("disposition")
        actual = assignment.get("choice") if expected["type"] == "checkbox" else fact.get("value")
        source_ok = bool(citations) and all(c in expected["source_chunk_ids"] for c in citations)
        value_match = False
        if expected["expected_state"] == "RESOLVED" and disposition == "value":
            target = expected["expected_value"]
            value_match = (type(actual) is bool and actual == target) if type(target) is bool else (
                isinstance(actual, str) and normalized(actual) == normalized(target))
            value_match = value_match and source_ok
        na_match = (expected["expected_state"] == "NOT_APPLICABLE"
                    and disposition == "not_applicable")
        unexpected_write = disposition == "value" and not value_match
        unexpected_na = disposition == "not_applicable" and not na_match
        result = validated.get(candidate_id, {}).get("validation", "NOT_VALIDATED")
        results.append({
            "key": expected["key"], "candidate_id": candidate_id,
            "label": expected["label"], "subject": expected["subject"],
            "section": expected["section"], "expected_state": expected["expected_state"],
            "expected_value": expected["expected_value"], "proposed": present,
            "disposition": disposition, "actual_value": actual, "source_chunk_ids": citations,
            "value_and_source_match": value_match, "na_disposition_match": na_match,
            "unexpected_value": unexpected_write, "unexpected_na": unexpected_na,
            "local_validation": result, "semantic_review_required": True,
        })
    expected_ids = {e["candidate_id"] for e in gold["fields"]}
    return {
        "fixture_version": gold["version"], "original_sha256": gold["original_sha256"],
        "scoring_scope": "literal values/booleans and authored SOURCE IDs only; "
                         "NA checks disposition only, not condition evidence",
        "semantic_acceptance": False, "session_writes": 0, "docx_writes": 0,
        "expected_states": dict(Counter(e["expected_state"] for e in gold["fields"])),
        "expected_value_targets": sum(e["expected_state"] == "RESOLVED" for e in gold["fields"]),
        "value_and_source_matches": sum(r["value_and_source_match"] for r in results),
        "grounded_value_and_source_matches": sum(
            r["value_and_source_match"] and r["local_validation"] == "GROUNDED_PROPOSAL"
            for r in results),
        "na_disposition_matches": sum(r["na_disposition_match"] for r in results),
        "unexpected_values": sum(r["unexpected_value"] for r in results),
        "unexpected_na": sum(r["unexpected_na"] for r in results),
        "omitted": sum(not r["proposed"] for r in results),
        "unknown_candidate_ids": sorted(set(fields) - expected_ids), "fields": results,
    }
