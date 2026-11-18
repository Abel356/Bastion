import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import ChunkRow, DemoUserRow, DocumentRow
from app.personas import PERSONAS

CORPUS_ROOT = Path(__file__).resolve().parents[1] / "corpus"


def load_manifest(root: Path = CORPUS_ROOT) -> list[dict]:
    return json.loads((root / "manifest.json").read_text(encoding="utf-8"))


def chunk_text(text: str, max_chars: int = 800) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = paragraph
        else:
