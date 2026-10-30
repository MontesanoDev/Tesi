"""A value printed in a declaration never widens a condition's question (E2E, 29-30 Oct).

Real Trapani runs: the model's participation condition governed the company data and the
PEC printed in «di accettare che ogni comunicazione … venga inviata al … PEC». The USER refused
that declaration; the real guard then judged the branch confirmation's scope ambiguous (its
traced verdict: «la PEC è nella sezione delle dichiarazioni … la stessa proposizione non governa
tutte le destinazioni») and the company data stayed empty. Synthetic FORM.
"""

from docx import Document
from test_compilation_catalog import catalog
from test_compilation_option_authorization import by_context, session_data

from app.compilation_global_dialogue import question_pool
from app.compilation_procedural_consent import requirements


def case():
    doc = Document()
    doc.add_paragraph("Telefono dell'operatore ____________")
    doc.add_paragraph("di accettare ogni comunicazione alla PEC ____________ indicata")
    cat = catalog(doc)
    phone, pec = by_context(cat, "Telefono")[0], by_context(cat, "PEC")[0]
    data = session_data(cat, {phone: "+39 080 000 1", pec: "pec@demo.it"}, flag=False)
    data["audit"]["conditions"]["c_branch"] = {
        "result": "unknown", "operator": "semantic", "reason": "Ramo da confermare",
        "form_evidence": {"paragraph_id": "paragraph:0", "quote": "Telefono dell'operatore"}}
    for field in data["audit"]["fields"]:
        if field["candidate_id"] in {phone, pec}:
            field.update(conditions=["c_branch"], label="Dato", form_evidence={
                "paragraph_id": cat["candidates"][field["candidate_id"]]["context_id"],
                "quote": "Telefono" if field["candidate_id"] == phone else "PEC"})
    return data, phone, pec


def condition_ids(data):
    return [set(q["field_ids"]) for q in question_pool(data) if q["key"] == "condition:c_branch"]


def test_a_pending_or_refused_declaration_stays_out_of_the_condition():
    data, phone, pec = case()
    [requirement] = requirements(data)
    assert condition_ids(data) == [{phone}]
    assert any(q["key"] == requirement["key"] for q in question_pool(data))  # Asked on its own.
    data["dialogue"]["answers"][requirement["key"]] = {
        "action": "CONDITION_FALSE", "applies": False, "provenance": "USER",
        "user_quote": "Non autorizzo questa dichiarazione"}
    assert condition_ids(data) == [{phone}]


def test_an_accepted_declaration_joins_the_condition_it_also_needs():
    data, phone, pec = case()
    [requirement] = requirements(data)
    data["dialogue"]["answers"][requirement["key"]] = {
        "action": "CONDITION_TRUE", "applies": True, "provenance": "USER",
        "user_quote": "Sì, autorizzo questa dichiarazione",
        "question": requirement["question"], "authorization": requirement["authorization"]}
    assert condition_ids(data) == [{phone, pec}]


def test_a_condition_over_the_declaration_data_alone_is_still_asked_with_them():
    data, phone, pec = case()
    for field in data["audit"]["fields"]:
        if field["candidate_id"] == phone:
            field["conditions"] = []  # The condition now governs only the declared value.
    assert condition_ids(data) == [{pec}]
