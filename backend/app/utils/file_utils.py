import os

# Directories to skip entirely
SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", "__pycache__",
    ".next", "venv", ".venv", "env", ".env", "site-packages",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "coverage",
}

# File extensions to include
INCLUDE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go",
    ".rb", ".rs", ".md", ".yaml", ".yml", ".json", ".toml",
    ".html", ".css", ".txt", ".sh",
}

# Binary/irrelevant extensions to skip
SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
    ".pdf", ".zip", ".whl", ".tar", ".gz", ".exe",
    ".lock", ".pyc", ".pyo", ".map", ".woff", ".woff2",
}

MAX_FILES = 100
MAX_LINES_PER_FILE = 200


def should_skip_dir(dirname: str) -> bool:
    """Return True if this directory should be skipped entirely."""
    return dirname in SKIP_DIRS or dirname.startswith(".")


def should_include_file(filename: str) -> bool:
    """Return True if this file should be included in analysis."""
    _, ext = os.path.splitext(filename)
    if ext in SKIP_EXTENSIONS:
        return False
    if ext in INCLUDE_EXTENSIONS:
        return True
    return False  # Skip unknown extensions by default


def read_file_safe(filepath: str) -> str:
    """Read file content safely, returning empty string on error."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            # Cap at MAX_LINES_PER_FILE
            return "".join(lines[:MAX_LINES_PER_FILE])
    except Exception:
        return ""


def walk_repo(repo_path: str) -> list[dict]:
    """
    Walk the cloned repo and return a list of FileNode dicts.
    Skips ignored dirs/extensions. Caps at MAX_FILES.
    """
    file_nodes = []

    for root, dirs, files in os.walk(repo_path):
        # Prune skipped directories in-place (modifies os.walk behavior)
        dirs[:] = [d for d in sorted(dirs) if not should_skip_dir(d)]

        for filename in sorted(files):
            if len(file_nodes) >= MAX_FILES:
                break

            if not should_include_file(filename):
                continue

            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, repo_path).replace("\\", "/")
            _, ext = os.path.splitext(filename)
            size = os.path.getsize(full_path)
            content = read_file_safe(full_path)

            file_nodes.append({
                "path": rel_path,
                "extension": ext,
                "size_bytes": size,
                "content": content,
            })

        if len(file_nodes) >= MAX_FILES:
            break

    return file_nodes


def build_bob_context(file_nodes: list[dict]) -> str:
    """
    Build the text blob sent to Bob.
    Format: === path === \n content \n for each file.
    """
    parts = []
    for f in file_nodes:
        parts.append(f"=== {f['path']} ===\n{f['content']}\n")
    return "\n".join(parts)
