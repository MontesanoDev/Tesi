"""Validate the preparation fixture, not the application's generation pipeline."""

import hashlib
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

from pypdf import PdfReader

BASE = Path(__file__).resolve().parent
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = f"{{{NS['w']}}}"


def compact(text):
    return "".join(text.split()).casefold()


def cell_text(element):
    return "".join(node.text or "" for node in element.iter(f"{W}t"))


class CatanzaroFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((BASE / "fonti.json").read_text())
        cls.mapping = json.loads((BASE / "mappa-campi.json").read_text())
        cls.sources = {source["id"]: source for source in cls.manifest["files"]}
        cls.template = BASE / cls.sources["domanda_docx"]["path"]
        with ZipFile(cls.template) as archive:
            cls.body = ET.fromstring(archive.read("word/document.xml"))
            cls.notes = ET.fromstring(archive.read("word/footnotes.xml"))
        cls.tables = cls.body.findall(".//w:body//w:tbl", NS)
        cls.fields = {field["id"]: field for field in cls.mapping["fields"]}

    def test_source_hashes(self):
        for source in self.sources.values():
            with self.subTest(source=source["id"]):
                actual = hashlib.sha256(
                    (BASE / source["path"]).read_bytes()
                ).hexdigest()
                self.assertEqual(actual, source["sha256"])
        self.assertEqual(
            self.mapping["template_sha256"], self.sources["domanda_docx"]["sha256"]
        )

    def test_docx_structure(self):
        with ZipFile(self.template) as archive:
            self.assertIsNone(archive.testzip())
        conversion = self.sources["domanda_docx"]["conversion"]
        self.assertEqual(len(self.tables), conversion["body_table_count"])
        controls = self.body.findall(".//w:checkBox", NS)
        self.assertEqual(len(controls), conversion["legacy_checkbox_count"])
        for control in controls:
            for value in control.findall("w:checked", NS) + control.findall(
                "w:default", NS
            ):
                self.assertIn(value.get(f"{W}val"), ("0", "false", "off"))
        notes = {
            note.get(f"{W}id")
            for note in self.notes
            if note.get(f"{W}type") not in ("separator", "continuationSeparator")
        }
        refs = {
            node.get(f"{W}id")
            for node in self.body.findall(".//w:footnoteReference", NS)
        }
        self.assertEqual(len(notes), conversion["footnote_count"])
        self.assertEqual(refs, notes)

    def test_targets_are_unique_empty_and_match_labels(self):
        self.assertEqual(len(self.fields), len(self.mapping["fields"]))
        targets = set()
        for field in self.fields.values():
            with self.subTest(field=field["id"]):
                target = field["target"]
                key = (target["table"], target["row"], target["column"])
                self.assertNotIn(key, targets)
                targets.add(key)
                rows = self.tables[target["table"]].findall("w:tr", NS)
                cell = rows[target["row"]].findall("w:tc", NS)[target["column"]]
                self.assertEqual(cell_text(cell).strip(), "")
                self.assertFalse(cell.findall(".//w:fldChar", NS))
                label_row = rows[target.get("label_row", target["row"])]
                label = label_row.findall("w:tc", NS)[target["label_column"]]
                self.assertEqual(compact(cell_text(label)), compact(target["label"]))

    def test_evidence_exists_on_declared_page(self):
        readers = {}
        for field in self.fields.values():
            with self.subTest(field=field["id"]):
                self.assertIn(field["state"], self.mapping["states"])
                if field["suggested_value"] is not None:
                    self.assertTrue(field["evidence"])
                for evidence in field["evidence"]:
                    source_id = evidence["source_id"]
                    if source_id not in readers:
                        readers[source_id] = PdfReader(
                            BASE / self.sources[source_id]["path"]
                        )
                    page = evidence["page"]
                    self.assertGreater(page, 0)
                    text = readers[source_id].pages[page - 1].extract_text()
                    self.assertTrue(evidence["quote"].strip())
                    self.assertIn(compact(evidence["quote"]), compact(text))

    def test_missing_and_unconfirmed_fields_are_not_filled(self):
        for field in self.fields.values():
            if field["state"] in ("missing", "needs_confirmation", "conditional"):
                with self.subTest(field=field["id"]):
                    self.assertIsNone(field["suggested_value"])
        for category in ("E06", "S03", "IA01", "IA02", "IA03"):
            self.assertEqual(self.fields[f"servizi.{category}"]["state"], "missing")

    def test_repeated_values_refer_to_same_entity(self):
        pairs = (
            ("impresa.denominazione", "societa_ingegneria.denominazione"),
            ("impresa.forma_giuridica", "societa_ingegneria.forma_giuridica"),
            ("impresa.sede_legale", "societa_ingegneria.sede"),
            ("firmatario.nome", "soggetti.amministratore.nome"),
            ("direttore_tecnico.nome", "soggetti.direttore_tecnico.nome"),
        )
        for left, right in pairs:
            self.assertEqual(
                self.fields[left]["suggested_value"],
                self.fields[right]["suggested_value"],
            )
        self.assertNotEqual(
            self.fields["firmatario.nome"]["suggested_value"],
            self.fields["direttore_tecnico.nome"]["suggested_value"],
        )

    def test_decisions_have_anchors_and_are_unconfirmed(self):
        text = compact(cell_text(self.body))
        decisions = self.mapping["decisions"]
        self.assertEqual(len(decisions), len({item["id"] for item in decisions}))
        for decision in decisions:
            with self.subTest(decision=decision["id"]):
                self.assertEqual(decision["state"], "needs_confirmation")
                self.assertIn(compact(decision["anchor"]), text)
                self.assertTrue(decision["rule"])

    def test_demo_and_conversion_are_not_marked_as_submission_ready(self):
        self.assertTrue(self.manifest["tender"]["historical_case"])
        self.assertTrue(self.sources["visura_mapi_demo"]["synthetic"])
        self.assertGreater(
            self.sources["visura_mapi_demo"]["document_date"],
            self.manifest["tender"]["submission_deadline"],
        )
        self.assertTrue(self.mapping["requires_human_review"])
        self.assertFalse(self.mapping["ready_for_submission"])
        self.assertEqual(
            self.sources["domanda_docx"]["conversion"]["layout_status"], "needs_review"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
