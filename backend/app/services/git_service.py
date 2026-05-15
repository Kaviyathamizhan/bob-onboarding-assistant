import os
import shutil
import git
from app.utils.file_utils import walk_repo
from app.models.schemas import FileNode


TEMP_DIR = os.getenv("TEMP_DIR", "./temp")


def get_repo_name(repo_url: str) -> str:
    """Extract repo name from GitHub URL."""
    return repo_url.rstrip("/").split("/")[-1].replace(".git", "")


def clone_repo(repo_url: str) -> tuple[str, list[FileNode]]:
    """
    Clone a public GitHub repo (shallow, depth=1) into temp dir.
    Returns (clone_path, list_of_FileNodes).
    Raises on clone failure.
    """
    repo_name = get_repo_name(repo_url)
    clone_path = os.path.join(TEMP_DIR, repo_name)

    # Clean up if already exists
    if os.path.exists(clone_path):
        shutil.rmtree(clone_path)

    os.makedirs(TEMP_DIR, exist_ok=True)

    print(f"[git_service] Cloning {repo_url} → {clone_path}")
    git.Repo.clone_from(repo_url, clone_path, depth=1)
    print(f"[git_service] Clone complete.")

    raw_nodes = walk_repo(clone_path)
    print(f"[git_service] Found {len(raw_nodes)} files after filtering.")

    file_nodes = [FileNode(**node) for node in raw_nodes]
    return clone_path, file_nodes


def cleanup_repo(clone_path: str) -> None:
    """Remove the cloned repo from temp dir after analysis."""
    if os.path.exists(clone_path):
        shutil.rmtree(clone_path)
        print(f"[git_service] Cleaned up {clone_path}")
