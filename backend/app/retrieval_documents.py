"""Convert only at the boundary between LangChain and the existing evidence API."""

from langchain_core.documents import Document


def evidence_document(evidence: dict) -> Document:
    return Document(
        id=str(evidence["chunk_id"]),
        page_content=evidence["content"],
        metadata={key: value for key, value in evidence.items() if key != "content"},
    )


def document_evidence(document: Document) -> dict:
    return {**document.metadata, "content": document.page_content}
