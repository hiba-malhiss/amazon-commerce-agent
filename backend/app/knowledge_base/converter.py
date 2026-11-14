from pathlib import Path

import pymupdf
from haystack import Document


def convert_file(
    path: Path,
    document_id: str,
    knowledge_base_code: str,
) -> list[Document]:
    """Read a supported file and return Haystack Documents."""

    metadata = {
        "document_id": document_id,
        "knowledge_base_code": knowledge_base_code,
        "filename": path.name,
    }

    if path.suffix.lower() in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8")

        documents = [Document(content=text, meta=metadata)] if text.strip() else []

    elif path.suffix.lower() == ".pdf":
        documents = []

        with pymupdf.open(path) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text("text", sort=True)

                if text.strip():
                    documents.append(
                        Document(
                            content=text,
                            meta={
                                **metadata,
                                "page_start": page_number,
                                "page_end": page_number,
                            },
                        )
                    )
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    if not documents:
        raise ValueError("No readable text found in the file")

    return documents
