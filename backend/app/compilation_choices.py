"""Bounded FORM choice groups, SOURCE support and deterministic export effects."""

import re
import unicodedata
from collections import Counter

from app.compilation_global_contract import ChoiceGroup, FormSpan


def _option_text(value):
    return " ".join(unicodedata.normalize("NFC", value).casefold().split())


def _positive_option_quote(source, quote, value):
    """A complete positive attribute value, not a noun cropped out of a negation.

    Other prose stays under review; this is not a semantic synonym classifier.
    Check the actual authorized SOURCE clause even when the model crops its quote.
    """
    from app.compilation_sources import source_span

    for line in re.split(r"[\n;]", source):
        # Preserve punctuation in values/abbreviations. Another colon-delimited
        # attribute after a sentence boundary starts a new clause on the same line.
        pairs = list(re.finditer(r"(?:^|(?<=\.)\s+)([^:;\n]{1,250}):\s*", line))
        for index, pair in enumerate(pairs):
            end = pairs[index + 1].start() if index + 1 < len(pairs) else len(line)
            body, clause = line[pair.end():end], line[pair.start():end].strip()
            if (len(clause) > 800 or _option_text(body.strip(" .*_\t")) !=
                    _option_text(value.strip(" .*_\t"))):
                continue
            try:
                source_span(clause, quote)
                return clause
            except ValueError:
                try:
                    source_span(quote, clause)
                    return clause
                except ValueError:
                    continue
    raise ValueError("SOURCE senza attribuzione positiva completa dell'opzione")


def choice_form(candidate_id, form, catalog, paragraphs):
    from app.compilation_global import _form_quote

    candidate = catalog["candidates"][candidate_id]
    paragraph = next(p for b in catalog["blocks"] for p in b["paragraphs"]
                     if p["id"] == form.paragraph_id)
    if (candidate["type"] != "checkbox" or form.paragraph_id not in
            candidate.get("anchor_paragraph_ids", [candidate["context_id"]])):
        raise ValueError("Opzione esterna al contesto della checkbox")
    if candidate["context_id"] == form.paragraph_id:
        marked = paragraph.get("text_with_choices", "")
        quote = _form_quote(marked, form.quote)
        if re.findall(r"\[\[[^\[\]]+\]\]", quote) != [f"[[{candidate_id}]]"]:
            raise ValueError("Opzione senza il solo marker checkbox corretto")
        restored = quote.replace(f"[[{candidate_id}]]", "")
    else:
        # Separate label cells belong to exactly one checkbox in that physical row.
        location = candidate["location"]
        siblings = [c for c in catalog["candidates"].values() if c["type"] == "checkbox"
                    and c["location"] == location]
        if len(siblings) != 1:
            raise ValueError("Etichetta separata ambigua fra checkbox della stessa riga")
        restored = form.quote
    restored = _form_quote(paragraphs[form.paragraph_id], restored)
    if not restored.strip():
        raise ValueError("Opzione checkbox senza etichetta FORM")
    return FormSpan(paragraph_id=form.paragraph_id, quote=restored)


def assignment_form(candidate_id, item, groups, catalog, paragraphs):
    """Reuse the group's checked marker; don't ask the model to duplicate a binding.

    An unmarked field quote must still identify the same literal option. A wrong
    paragraph, another marker or a contradictory label cannot be repaired here.
    """
    from app.compilation_global import _form_quote

    group = groups.get(getattr(item, "choice_group_id", None), {})
    option = group.get("options", {}).get(candidate_id, {})
    if group.get("validation") != "GROUNDED_GROUP" or not option.get("form_evidence"):
        raise ValueError("Checkbox senza collegamento strutturale di gruppo validato")
    origin = FormSpan.model_validate(option["form_evidence"])
    if item.form.paragraph_id != origin.paragraph_id:
        raise ValueError("Field checkbox citato nel paragrafo di un'altra opzione")
    if "[[" in item.form.quote:
        checked = choice_form(candidate_id, item.form, catalog, paragraphs)
        _form_quote(origin.quote, checked.quote)
    else:
        _form_quote(origin.quote, item.form.quote)
        _form_quote(item.form.quote, option["label"])
    return item.model_copy(update={"form": origin, "label": option["label"]})


def _exclusive_region(group, catalog, paragraphs):
    """Close a physical choice list before clearing any original checked peers.

    Body lists end at a nonempty paragraph without native controls. Tables are
    conservative: a locally instructed row is a group, otherwise the full table
    must be accounted for. Complex/interleaved tables stay under review.
    """
    controls = {cid: c for cid, c in catalog["candidates"].items()
                if c["type"] == "checkbox"}
    first = controls[next(iter(group.options))]
    table = first["location"].get("table_id")
    if table is not None:
        table_controls = {cid: c for cid, c in controls.items()
                          if c["location"].get("table_id") == table}
        rows = {controls[cid]["location"]["row_index"] for cid in group.options}
        if len(rows) == 1:
            row = next(iter(rows))
            structure = next(t for b in catalog["blocks"] for t in b.get("tables", [])
                             if t["id"] == table)
            row_paragraphs = {p for cell in structure["rows"][row]
                              for p in cell["paragraph_ids"]}
            if group.form.paragraph_id in row_paragraphs:
                return {cid for cid, c in table_controls.items()
                        if c["location"]["row_index"] == row}
        return set(table_controls)
    by_paragraph = {}
    for cid, candidate in controls.items():
        if "table_id" not in candidate["location"]:
            by_paragraph.setdefault(candidate["context_id"], set()).add(cid)
    order = list(paragraphs)
    index = order.index(first["context_id"])
    region = set(by_paragraph[order[index]])
    table_paragraphs = {p["id"] for b in catalog["blocks"] if b.get("tables")
                        for p in b["paragraphs"]}
    for direction in (-1, 1):
        pos = index + direction
        while 0 <= pos < len(order):
            pid = order[pos]
            if pid in table_paragraphs or (paragraphs[pid].strip() and pid not in by_paragraph):
                break
            peers = by_paragraph.get(pid, set())
            if any(controls[cid]["section_ids"] != first["section_ids"] for cid in peers):
                break
            region.update(peers)
            pos += direction
    return region


def validate_groups(records, catalog, paragraphs, local, conditions):
    from app.compilation_global import _form_quote

    groups, membership = {}, Counter(cid for r in records.values() if isinstance(r, dict)
                                     and isinstance(r.get("options"), dict)
                                     for cid in r["options"])
    order = {key: index for index, key in enumerate(paragraphs)}
    for key, record in records.items():
        output = {"proposal": record, "validation": "REJECTED", "validation_errors": [],
                  "semantic_review_required": True, "options": {}}
        try:
            group = ChoiceGroup.model_validate(record)
            output.update(group.model_dump())
            quote = _form_quote(paragraphs.get(group.form.paragraph_id, ""), group.form.quote)
            if not quote:
                raise ValueError("Gruppo senza istruzione FORM verificabile")
            # A small contradiction veto for explicit cardinality instructions.
            # Other wording remains a semantic proposal, not a guessed rule.
            instruction = _option_text(paragraphs[group.form.paragraph_id])
            command = r"(?:^|[:;.])\s*(?:selezionare|scegliere|barrare|indicare)\s+"
            single = re.search(command + r"(?:una sola|un['’]unica)\s+opzione\b", instruction)
            multiple = re.search(command + r"(?:una o più|tutte le)\s+opzioni\b", instruction)
            if (single and group.selection == "multiple" or
                    multiple and group.selection == "single"):
                raise ValueError("Cardinalità proposta contraddice l'istruzione FORM esplicita")
            if len(set(group.conditions)) != len(group.conditions) or any(
                c not in conditions for c in group.conditions
            ):
                raise ValueError("Condizioni del gruppo sconosciute o duplicate")
            locations, sections, indices, labels = set(), set(), [], set()
            for cid, option in group.options.items():
                if cid not in catalog["candidates"] or membership[cid] != 1:
                    raise ValueError("Checkbox sconosciuta o appartenente a più gruppi")
                candidate = catalog["candidates"][cid]
                # Match the same local FORM context used by normal field grounding.
                enriched = {**catalog, "candidates": {**catalog["candidates"], cid: {
                    **candidate, "anchor_paragraph_ids": local[candidate["context_id"]]}}}
                form = choice_form(cid, option.form, enriched, paragraphs)
                if _option_text(option.label) not in _option_text(form.quote):
                    raise ValueError("Etichetta opzione assente nell'estratto FORM")
                if _option_text(option.label) in labels:
                    raise ValueError("Opzioni con etichette ambigue")
                labels.add(_option_text(option.label))
                output["options"][cid] = {"label": option.label, "form_evidence": form.model_dump()}
                locations.add(candidate["location"].get("table_id"))
                sections.add(tuple(candidate["section_ids"]))
                indices.append(order[candidate["context_id"]])
            if len(locations) > 1 or len(sections) > 1:
                raise ValueError("Gruppo attraversa tabelle o sezioni differenti")
            origin = order[group.form.paragraph_id]
            if not min(indices) - 64 <= origin <= max(indices):
                raise ValueError("Istruzione del gruppo troppo distante dalle opzioni")
            between = {cid for cid, c in catalog["candidates"].items()
                       if c["type"] == "checkbox" and min(indices) <=
                       order[c["context_id"]] <= max(indices)}
            if between != set(group.options):
                raise ValueError("Gruppo incompleto o intrecciato con altre checkbox")
            if (group.selection == "single" and
                    _exclusive_region(group, catalog, paragraphs) != set(group.options)):
                raise ValueError("Gruppo esclusivo incompleto rispetto alla lista fisica Word")
            output.update(validation="GROUNDED_GROUP", form_evidence={
                "paragraph_id": group.form.paragraph_id, "quote": quote})
        except (ValueError, KeyError) as exc:
            output["validation_errors"].append(str(exc))
        groups[key] = output
    return groups


def check_choice(field, fact, group, candidate_id, source_map):
    """Conservative literal association, not a general semantic equivalence engine."""
    if group.get("validation") != "GROUNDED_GROUP" or group["selection"] == "unknown":
        raise ValueError("Regola di scelta non verificabile")
    if candidate_id not in group["options"] or type(field.choice) is not bool:
        raise ValueError("Checkbox fuori gruppo o scelta non booleana")
    if fact["validation"] != "GROUNDED_PROPOSAL" or any(
        p.get("category") == "general" for p in fact["source_evidence"]
    ):
        raise ValueError("Scelta senza SOURCE fattuale autorizzata")
    if (_option_text(fact["subject"]) != _option_text(group["subject"])
            or _option_text(fact["property"]) != _option_text(group["property"])):
        raise ValueError("SOURCE riferita a soggetto/proprietà differenti dal gruppo")
    supported = {cid for cid, option in group["options"].items()
                 if _option_text(option["label"]) == _option_text(fact["value"])}
    if len(supported) != 1 or field.choice != (candidate_id in supported):
        raise ValueError("SOURCE non sostiene questa opzione e polarità")
    if field.choice is False and group["selection"] != "single":
        raise ValueError("Opzione multipla falsa senza prova negativa indipendente")
    from app.compilation_sources import source_span

    proofs = []
    for proof in fact["source_evidence"]:
        content = source_map[proof["chunk_id"]]["content"]
        try:
            subject = source_span(content, fact["subject"])
        except ValueError as exc:
            raise ValueError("Soggetto della scelta assente nel chunk SOURCE") from exc
        if _option_text(subject) != _option_text(fact["subject"]):
            raise ValueError("Soggetto della scelta non attestato nello stesso chunk SOURCE")
        proofs.append({**proof, "subject_quote": subject, "support_quote":
                       _positive_option_quote(content, proof["quote"], fact["value"])})
    return proofs


def attach_choice_audit(result, groups, items, catalog, source_map):
    for field in result["fields"]:
        cid = field["candidate_id"]
        if catalog["candidates"][cid]["type"] != "checkbox":
            continue
        matching = [(key, g) for key, g in groups.items() if cid in g.get("options", {})]
        if len(matching) == 1:
            key, group = matching[0]
            field["choice_group_id"] = key
            if group["validation"] == "GROUNDED_GROUP":
                option = group["options"][cid]
                field.setdefault("form_evidence", option["form_evidence"])
                field.setdefault("label", option["label"])
                field.setdefault("kind", "choice")
                field["conditions"] = sorted(set(field.get("conditions", [])) |
                                             set(group["conditions"]))
        item = items.get(cid)
        if item is None or item.disposition not in {"value", "conditional"}:
            continue
        try:
            group = groups.get(item.choice_group_id, {})
            proofs = check_choice(item, result["facts"][item.fact_id], group, cid, source_map)
            field["source_evidence"] = proofs
            field["choice_group_id"] = item.choice_group_id
        except ValueError as exc:
            field.update(validation="REJECTED", value=None, fact_id=None)
            field.pop("proposed_value", None)
            field.pop("proposal_grounding", None)
            field.setdefault("validation_errors", []).append(str(exc))
    for key, group in groups.items():
        eligible = [f for f in result["fields"] if f.get("choice_group_id") == key and (
            f["validation"] == "GROUNDED_PROPOSAL"
            or f.get("proposal_grounding") == "GROUNDED_PROPOSAL")]
        count = sum(f.get("proposed_value", f.get("value")) is True for f in eligible)
        if group.get("selection") == "single" and count > 1:
            group["consistency"] = "conflicting"
            for f in eligible:
                f.update(validation="REJECTED", value=None, fact_id=None)
                f.pop("proposed_value", None)
                f.pop("proposal_grounding", None)
                f["validation_errors"].append("Scelte esclusive incompatibili")
    result["choice_groups"] = groups


def materialize_choices(data, source_ids, user_ids):
    """Validate the final subset, including USER overrides and initial checked peers."""
    from app.compilation_branch_evidence import effective_user_values, receipt_choice_value

    fields = {f["candidate_id"]: f for f in data["audit"]["fields"]}
    users = effective_user_values(data)
    chosen = {cid: (users[cid]["value"] if cid in user_ids else
                   fields[cid].get("proposed_value", fields[cid].get("value")))
              for cid in [*source_ids, *user_ids]
              if data["catalog"]["candidates"][cid]["type"] == "checkbox"}
    values, effects = {}, []
    for key, group in data["audit"].get("choice_groups", {}).items():
        selected = {cid: value for cid, value in chosen.items() if cid in group["options"]}
        if not selected:
            continue
        if group["validation"] != "GROUNDED_GROUP":
            raise ValueError("Gruppo di scelta non validato")
        if group["selection"] == "unknown":
            # Cardinality is still unknown. Only an exact positive condition
            # receipt can mark its own control; never clear or infer peers.
            if any(cid not in user_ids or receipt_choice_value(data, cid) != users[cid]
                   or value is not True for cid, value in selected.items()):
                raise ValueError("Cardinalità ignota senza ricevuta positiva verificata")
            values.update(selected)
            continue
        count = sum(v is True for v in selected.values())
        if any(type(v) is not bool for v in selected.values()) or (
            group["selection"] == "single" and count > 1
        ) or count < group["min_selected"]:
            raise ValueError("Selezione finale incompatibile con la cardinalità del gruppo")
        values.update(selected)
        if group["selection"] == "single" and count == 1:
            positive = next(cid for cid, value in selected.items() if value is True)
            for cid in group["options"]:
                if cid not in selected:
                    values[cid] = False
                    effects.append({"candidate_id": cid, "value": False,
                                    "effect": "exclusive_alternative_cleared",
                                    "derived_from_candidate_id": positive,
                                    "choice_group_id": key,
                                    "provenance": "USER" if positive in user_ids else "SOURCE"})
    if not chosen.keys() <= values.keys():
        raise ValueError("Checkbox senza gruppo validato")
    return values, effects


def user_choice(data, slot, reply):
    """Interpretation is model-owned; recipient IDs and cardinality are backend-owned."""
    group = data["audit"]["choice_groups"].get(slot["choice_group_id"], {})
    options = list(group.get("options", {}))
    chosen = reply.selected_options
    if (group.get("validation") != "GROUNDED_GROUP" or group["selection"] == "unknown"
            or slot["field_ids"] != options or chosen is None or reply.normalized_value
            or len(chosen) != len(set(chosen)) or any(not 1 <= i <= len(options) for i in chosen)
            or len(chosen) < group["min_selected"]
            or group["selection"] == "single" and len(chosen) > 1):
        raise ValueError("Scelta USER ambigua o incompatibile col gruppo attivo")
    return {cid: {"value": index + 1 in chosen, "provenance": "USER",
                  "label": group["options"][cid]["label"], "user_quote": reply.user_quote,
                  "choice_group_id": slot["choice_group_id"]}
            for index, cid in enumerate(options)}
