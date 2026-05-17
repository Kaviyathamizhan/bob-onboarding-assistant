"""Persist analyze step state so uvicorn --reload does not lose pending Bob sessions."""

import json
import os
from pathlib import Path

from app.models.schemas import FileNode

_SESSION_DIR = Path(os.getenv("BOB_SESSIONS_DIR", "./bob_sessions"))
_PENDING_FILE = _SESSION_DIR / "pending-session.json"


def _ensure_dir() -> None:
    _SESSION_DIR.mkdir(parents=True, exist_ok=True)


def save_pending(repo_url: str, repo_name: str, file_nodes: list[FileNode]) -> None:
    _ensure_dir()
    payload = {
        "repo_url": repo_url.strip(),
        "repo_name": repo_name,
        "file_nodes": [n.model_dump() for n in file_nodes],
    }
    _PENDING_FILE.write_text(json.dumps(payload), encoding="utf-8")


def load_pending() -> tuple[str, str, list[FileNode]] | None:
    if not _PENDING_FILE.is_file():
        return None
    try:
        data = json.loads(_PENDING_FILE.read_text(encoding="utf-8"))
        repo_url = data.get("repo_url", "").strip()
        repo_name = data.get("repo_name", "")
        nodes = [FileNode(**n) for n in data.get("file_nodes", [])]
        if not repo_url or not nodes:
            return None
        return repo_url, repo_name, nodes
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def clear_pending() -> None:
    if _PENDING_FILE.is_file():
        _PENDING_FILE.unlink(missing_ok=True)
