import gc
import os
import shutil
import stat
import tempfile
import time

import git
from app.utils.file_utils import walk_repo
from app.models.schemas import FileNode

# Outside backend/ so `uvicorn --reload` does not restart when cloning repos
TEMP_DIR = os.getenv("TEMP_DIR", os.path.join(tempfile.gettempdir(), "bob-onboard-clones"))


def get_repo_name(repo_url: str) -> str:
    """Extract repo name from GitHub URL."""
    return repo_url.rstrip("/").split("/")[-1].replace(".git", "")


def _handle_remove_readonly(func, path, _exc_info):
    """Windows: .git pack files are often read-only — make writable then retry."""
    try:
        os.chmod(path, stat.S_IWRITE)
    except OSError:
        pass
    func(path)


def safe_rmtree(path: str, retries: int = 5) -> bool:
    """Remove a directory tree; tolerate Windows file locks with retries."""
    if not os.path.exists(path):
        return True

    for attempt in range(retries):
        try:
            gc.collect()
            shutil.rmtree(path, onerror=_handle_remove_readonly)
            return True
        except PermissionError:
            if attempt < retries - 1:
                time.sleep(0.15 * (attempt + 1))
            else:
                print(f"[git_service] Warning: could not delete {path} (files still locked)")
                return False
        except OSError as e:
            print(f"[git_service] Warning: could not delete {path}: {e}")
            return False
    return False


def clone_repo(repo_url: str) -> tuple[str, list[FileNode]]:
    """
    Clone a public GitHub repo (shallow, depth=1) into temp dir.
    Returns (clone_path, list_of_FileNodes).
    Raises on clone failure.
    """
    repo_name = get_repo_name(repo_url)
    clone_path = os.path.join(TEMP_DIR, repo_name)

    if os.path.exists(clone_path):
        safe_rmtree(clone_path)

    os.makedirs(TEMP_DIR, exist_ok=True)

    print(f"[git_service] Cloning {repo_url} → {clone_path}")
    repo = None
    try:
        repo = git.Repo.clone_from(repo_url, clone_path, depth=1)
        print("[git_service] Clone complete.")

        raw_nodes = walk_repo(clone_path)
        print(f"[git_service] Found {len(raw_nodes)} files after filtering.")

        file_nodes = [FileNode(**node) for node in raw_nodes]
        return clone_path, file_nodes
    finally:
        if repo is not None:
            repo.close()


def cleanup_repo(clone_path: str) -> None:
    """Remove the cloned repo from temp dir after analysis."""
    if safe_rmtree(clone_path):
        print(f"[git_service] Cleaned up {clone_path}")
