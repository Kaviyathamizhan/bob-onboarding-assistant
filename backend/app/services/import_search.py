import re
from app.models.schemas import FileNode


def search_where_used(module_id: str, file_nodes: list[FileNode]) -> list[str]:
    """
    Search all FileNodes for import/reference patterns matching module_id.
    Returns list of file paths that reference this module.
    Supports Python and JS/TS import styles.
    """
    results = []

    # Build patterns to match
    # Python: from X import, import X
    # JS/TS: import X from, require('X'), import('X')
    patterns = [
        rf"from\s+[\w.]*{re.escape(module_id)}[\w.]*\s+import",  # Python: from x import
        rf"import\s+[\w.]*{re.escape(module_id)}",               # Python: import x / JS: import x
        rf"require\(['\"][\w./]*{re.escape(module_id)}[\w./]*['\"]",  # JS: require('x')
    ]

    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]

    for node in file_nodes:
        for pattern in compiled:
            if pattern.search(node.content):
                results.append(node.path)
                break  # Don't double-count same file

    return results
