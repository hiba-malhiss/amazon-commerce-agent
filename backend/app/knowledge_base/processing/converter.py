from pathlib import Path

from haystack import Document

from .converters.pdf import convert_pdf
from .converters.text import convert_text

SUPPORTED_SUFFIXES = {".txt", ".md", ".pdf"}


def extract_document_content(
    path: Path, document_id: str, knowledge_base_code: str
) -> list[Document]:
    """Read a supported file into Haystack Documents, dispatching on the file type. Each
    converter keeps whatever structure it can (Markdown headings, PDF font sizes) so the
    chunker can split by section."""

    metadata = {
        "document_id": document_id,
        "knowledge_base_code": knowledge_base_code,
        "filename": path.name,
    }
    suffix = path.suffix.lower()

    if suffix in {".txt", ".md"}:
        documents = convert_text(path, metadata)
    elif suffix == ".pdf":
        documents = convert_pdf(path, metadata)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    if not documents:
        raise ValueError("No readable text found in the file")

    return documents
