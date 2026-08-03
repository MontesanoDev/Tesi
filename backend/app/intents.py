from __future__ import annotations

import re

IDENTITY_QUESTIONS = {
    "che cosa sei",
    "chi sei",
    "chi sei mapi",
    "come ti chiami",
    "cosa sei",
}


def direct_system_answer(question: str) -> str | None:
    normalized = " ".join(re.findall(r"[^\W_]+", question.lower(), flags=re.UNICODE))
    if normalized not in IDENTITY_QUESTIONS:
        return None
    return (
        "Sono Mapi RAG, un assistente tecnico per progetti di ingegneria civile. "
        "Analizzo le fonti collegate al progetto, recupero evidenze citabili e preparo "
        "risposte e documenti da sottoporre a revisione umana."
    )
