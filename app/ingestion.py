import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import ChunkRow, DemoUserRow, DocumentRow
from app.personas import PERSONAS

CORPUS_ROOT = Path(__file__).resolve().parents[1] / "corpus"


def load_manifest(root: Path = CORPUS_ROOT) -> list[dict]:
    return json.loads((root / "manifest.json").read_text(encoding="utf-8"))


