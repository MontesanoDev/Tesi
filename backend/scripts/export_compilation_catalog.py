"""Export the proposed FORM input, without AI calls or application data writes."""

import argparse
import hashlib
import json
from pathlib import Path
from time import perf_counter

from app.compilation_catalog import build_compilation_catalog
from app.docx_templates import inspect_docx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--compare-v1", action="store_true")
    args = parser.parse_args()
    original = args.document.read_bytes()
    start = perf_counter()
    layout = inspect_docx(original, require_candidates=False)
    inspected = perf_counter()
    catalog = build_compilation_catalog(layout)
    catalogued = perf_counter()
    serialized = json.dumps(catalog, ensure_ascii=False, separators=(",", ":"))
    counts = {kind: sum(c["type"] == kind for c in catalog["candidates"].values())
              for kind in ("text", "checkbox")}
    metrics = {"document": str(args.document), "original_sha256": layout.sha256,
               "candidate_counts": counts, "catalog_characters": len(serialized),
               "catalog_utf8_bytes": len(serialized.encode()),
               "inspect_seconds": inspected - start, "catalog_seconds": catalogued - inspected,
               "ai_calls": 0, "checkbox_write_supported": False}
    if args.compare_v1:
        from app.compilation_semantics import form_material
        from app.compilation_sessions import candidate_snapshots

        fields = candidate_snapshots(layout, "catalog-comparison", 1, args.document.name)
        repeated = json.dumps({f["id"]: form_material(f) for f in fields},
                              ensure_ascii=False, separators=(",", ":"))
        metrics["v1_all_candidate_form_context_characters"] = len(repeated)
        metrics["comparison_note"] = (
            "Contesti FORM di tutti i candidate V1, non il payload di una singola chiamata "
            "reale. Il catalogo aggiunge checkbox e contesto completo; nessuna misura token."
        )
    metrics["original_unchanged"] = hashlib.sha256(args.document.read_bytes()).hexdigest() == (
        layout.sha256
    )
    args.output_dir.mkdir(parents=True, exist_ok=False)
    (args.output_dir / "catalog.json").write_text(serialized + "\n", encoding="utf-8")
    (args.output_dir / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
