from pathlib import Path
from typing import Any

from haystack import Document


def convert_text(path: Path, metadata: dict[str, Any]) -> list[Document]:
    """A plain-text or Markdown file as one Document. Markdown headings (#) are handled
    later by the chunker's structure step."""
    text = path.read_text(encoding="utf-8")
    return [Document(content=text, meta=metadata)] if text.strip() else []
