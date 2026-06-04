from pathlib import Path

from src.config import KNOWLEDGE_PATH

_cache: str | None = None


def load_knowledge(path: Path | None = None) -> str:
    global _cache
    if _cache is not None:
        return _cache

    file_path = path or KNOWLEDGE_PATH
    if not file_path.exists():
        raise FileNotFoundError(f"База знаний не найдена: {file_path}")

    _cache = file_path.read_text(encoding="utf-8").strip()
    return _cache


def reload_knowledge() -> str:
    global _cache
    _cache = None
    return load_knowledge()
