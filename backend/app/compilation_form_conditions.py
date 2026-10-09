"""Backend FORM dependencies from the immutable document, including distant tables.

These are writing constraints, separate from an LLM's local interpretation and
from the SOURCE value itself. Existing values are retained and reported if blocked.
"""

import re
from copy import deepcopy

from app.compilation_applicability import known_applicability
from app.compilation_conditions import (
    conflicting_relations,
    expression,
    implication,
    proven_relations,
)
from app.docx_templates import text_of
from app.requirement_checks import normalized

DEPENDENCY_VERSION = 1
BRANCH = re.compile(r"^\s*(\d+)\.([a-z](?:[-.]bis)?)\)\s*(.*)", re.I)
PARTICIPATION = re.compile(
    r"\b(?:consorziat\w*|esecutric\w*|raggruppament\w*|mandant\w*|mandatar\w*|rti)\b")


def attach_form_dependencies(layout, fields):
    """Walk existing XML, without changing DOCX parsing/candidate IDs/positions."""
    from docx.oxml.ns import qn

    paragraphs = list(layout.document.element.body.iter(qn("w:p")))
    positions = {p: i for i, p in enumerate(paragraphs)}
    branches, active, group = {}, None, None
    for element in layout.document.element.body:
        first = element if element.tag == qn("w:p") else next(element.iter(qn("w:p")), None)
        if first is None:
            continue
        text = text_of(first).strip()
        clean = normalized(text)
        if ("operatore" in clean and (
            "identificazione" in clean and "ragione sociale" in clean
            or "tipologia" in clean and re.search(r"\b(?:sola|solo|alternativ\w*)\b", clean)
        )):
            group = {"id": f"paragraph:{positions[first]}", "quote": text}
            active = None
        heading = BRANCH.match(text)
        if heading:
            active = None
            condition = re.search(r"\bda compilare in caso di\s+(.+)", heading[3], re.I)
            if condition:
                quote = condition[1].strip().rstrip(".:")
                active = {"version": DEPENDENCY_VERSION, "template_sha256": layout.sha256,
                          "id": f"paragraph:{positions[first]}", "condition": quote,
                          "quote": text, "kind": "participation" if PARTICIPATION.search(
                              normalized(quote)) else "subject_type",
                          "family": heading[1], "group": deepcopy(group)}
        elif (text.startswith(">>>") or re.match(r"^\d+[.)]\s+", text)):
            active, group = None, None
        for paragraph in element.iter(qn("w:p")):
            branches[paragraph] = active
    for field in fields:
        if field["id"] not in layout.candidate_ids:
            raise ValueError("Dipendenza FORM riferita a una posizione estranea all'originale")
        element = (layout.slots[field["id"]].paragraph if field["id"] in layout.slots
                   else layout.cells[field["id"]])
        first = element if element.tag == qn("w:p") else next(element.iter(qn("w:p")))
        branch = branches.get(first)
        field.pop("form_dependency", None)
        if branch:
            field["form_dependency"] = deepcopy(branch)
            sections = field["structural"].setdefault("form_sections", [])
            if not any(s["id"] == branch["id"] for s in sections):
                sections.append({"id": branch["id"], "text": branch["quote"]})
        # A complete, reviewed map is independent of the legacy heading recognizer.
        if field.get("document_branch"):
            field["form_dependency"] = deepcopy(field["document_branch"])
            section = field["document_branch"]
            sections = field["structural"].setdefault("form_sections", [])
            if not any(s["id"] == section["id"] for s in sections):
                sections.append({"id": section["id"], "text": section["quote"]})


def root_condition(condition):
    return re.split(r"\s+(?:nel caso di|in presenza di|in assenza di)\s+", condition,
                    maxsplit=1, flags=re.I)[0]


def branch_owner(field):
    branch = field.get("form_dependency")
    if not branch:
        return None
    form = field["form_evidence"]
    scope = (form.get("project_id"), form.get("file_id"), form["template_sha256"])
    if branch["kind"] == "subject_type" and branch.get("group"):
        return ("operator", *scope, branch["group"]["id"], branch["family"])
    return ("branch", *scope, branch["id"])


def dependency_owner(field):
    branch = field.get("form_dependency")
    if not branch or not field.get("condition"):
        return None
    # The operator's type never becomes the owner of a local predicate about
    # a representative/director/member merely because it is in the same table.
    root = expression(root_condition(branch["condition"]))
    if root <= expression(field["condition"]) <= expression(branch["condition"]):
        return branch_owner(field)
    return None


def branch_target(field, condition):
    return {**field, "condition": condition}


def synchronize_form_dependencies(state):
    fields = state["fields"]
    facts = proven_relations(fields)
    selected, conflicted_groups = {}, set()
    for field in fields:
        branch = field.get("form_dependency")
        if not branch or branch["kind"] != "subject_type" or not branch.get("group"):
            continue
        root = root_condition(branch["condition"])
        if conflicting_relations(branch_target(field, root), facts):
            conflicted_groups.add(branch_owner(field))
        result = implication(branch_target(field, root), facts)
        if result and result[0]:
            selected.setdefault(branch_owner(field), {})[expression(root)] = result[1]
    for field in fields:
        branch = field.get("form_dependency")
        if branch:
            relation = implication(branch_target(field, branch["condition"]), facts)
            choices = selected.get(branch_owner(field), {})
            conflict = (len(choices) > 1 or branch_owner(field) in conflicted_groups
                        or conflicting_relations(branch_target(field, branch["condition"]), facts))
            if conflict:
                relation = None
            elif (len(choices) == 1
                  and expression(root_condition(branch["condition"])) not in choices):
                relation = (False, next(iter(choices.values())))
            proof = None
            if relation:
                applies, origin = relation
                proof = {"applies": applies, "condition": branch["condition"],
                         "provenance": origin["applicability"]["provenance"],
                         "origin_field_id": origin["id"],
                         "basis": deepcopy(origin["applicability"]),
                         "form": deepcopy(branch),
                         "rule": "FORM_identity_alternative" if len(choices) == 1 and not applies
                         else "verified_predicate_implication"}
            field["form_dependency_decision"] = proof
            field["form_dependency_conflict"] = conflict
            # Never erase a previous SOURCE/USER value to make the state look valid.
            # It stays visible in the session and in blocked_previous_writes.
            if (relation and not relation[0] and field["status"] not in {
                "RESOLVED", "USER_PROVIDED", "NOT_APPLICABLE",
            } and field.get("provenance") != "USER"):
                field["status_before_form_exclusion"] = field["status"]
                field.update(status="NOT_APPLICABLE", value=None,
                             provenance=proof["provenance"], source_evidence=[], alternatives=[],
                             reason="Ramo escluso da condizione FORM e prova verificata")
            elif (not relation or relation[0]) and field.get("status_before_form_exclusion"):
                field["status"] = field.pop("status_before_form_exclusion")
                field["provenance"] = None
        blockers = write_blockers(field)
        if blockers and field["status"] in {"RESOLVED", "USER_PROVIDED"}:
            field["write_blockers"] = blockers
        else:
            field.pop("write_blockers", None)


def required_applicability(field):
    direct = known_applicability(field) if field.get("condition") else True
    if field.get("form_dependency") and field.get("form_dependency_conflict"):
        return None
    if direct is False:
        return False
    branch = field.get("form_dependency")
    if not branch:
        return direct
    proof = field.get("form_dependency_decision") or {}
    if proof.get("applies") is False:
        return False
    if proof.get("applies") is True:
        return direct
    # A newly matched, verified parent proof may precede the full-state sync.
    if direct is True and proven_relations([field]) and field.get("condition"):
        target, established = expression(branch["condition"]), expression(field["condition"])
        if target <= established:
            return True
    return None


def write_blockers(field):
    blockers = []
    applicable = required_applicability(field)
    if applicable is not True:
        blockers.append("Sezione/condizione esclusa" if applicable is False
                        else "Applicabilità della sezione/condizione non accertata")
    # An entirely blank row with no column/property label does not prove that
    # another row's company property belongs to either of these cells.
    if (field.get("location", {}).get("kind") == "table_cell"
            and not field.get("label_hint", "").strip()
            and field.get("structural", {}).get("row")
            and not any(c["text"].strip() for c in field["structural"]["row"])):
        blockers.append("Cella in riga senza etichette: associazione alla proprietà non verificata")
    return blockers


def require_writable(field):
    if blockers := write_blockers(field):
        raise ValueError("; ".join(blockers))


def blocked_previous_writes(state):
    return [{"field_id": f["id"], "value": f["value"], "provenance": f["provenance"],
             "source_evidence": deepcopy(f["source_evidence"]),
             "reasons": f["write_blockers"], "form_dependency": f.get("form_dependency"),
             "decision": f.get("form_dependency_decision")}
            for f in state["fields"] if f.get("write_blockers")]


def question_condition(field):
    branch = field.get("form_dependency")
    if branch and (field.get("form_dependency_decision") or {}).get("applies") is None:
        return branch["condition"]
    return field.get("condition", "") if known_applicability(field) is None else ""
