import os
import re
import json
from datetime import datetime
from app.models.schemas import FileNode, RepoAnalysis, Module
from app.utils.file_utils import build_bob_context

# ── Bob session log directory ─────────────────────────────────────────────────
BOB_REPORTS_DIR = os.getenv("BOB_REPORTS_DIR", "./bob_sessions")
os.makedirs(BOB_REPORTS_DIR, exist_ok=True)


def save_bob_session(prompt: str, response: str) -> None:
    """Save every Bob interaction to /bob_sessions/ for submission proof."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    report_path = os.path.join(BOB_REPORTS_DIR, f"session-{timestamp}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"timestamp": timestamp, "prompt": prompt[:2000], "response": response[:5000]}, f, indent=2)
    print(f"[bob_service] Session saved -> {report_path}")


def build_analysis_prompt(file_nodes: list[FileNode], repo_name: str) -> str:
    """Build the master prompt to paste into IBM Bob IDE."""
    context = build_bob_context([n.model_dump() for n in file_nodes])
    return f"""You are analyzing the GitHub repository: {repo_name}

Here are the source files (up to 100 files, 200 lines each):

{context}

IMPORTANT FORMATTING RULES — follow these EXACTLY or the app will break:
1. Do NOT use ### markdown headings for modules.
2. Each module MUST use the exact field names below.
3. Each module block MUST end with a line containing ONLY: ---
4. No bullet points inside module blocks.

Please provide your analysis using EXACTLY this structure:

## TECH_STACK
- TechnologyName (version if known)
- TechnologyName
(one technology per line, starting with -)

## ARCHITECTURE
Write 2-3 paragraphs describing the overall architecture, design patterns, and how components connect. Plain text only.

## MODULES
MODULE_ID: short-lowercase-slug
MODULE_NAME: Human Readable Name
DESCRIPTION: One sentence describing what this module does and its role in the system.
KEY_FILES: path/to/file1.py, path/to/file2.py
IMPORTS: module-or-library-name, another-module
EXPORTS: ClassName, function_name, AnotherClass
---
MODULE_ID: another-module-slug
MODULE_NAME: Another Module Name
DESCRIPTION: What this module does.
KEY_FILES: path/to/file.py
IMPORTS: dependency1
EXPORTS: export1, export2
---

## ONBOARDING_GUIDE
Write a complete onboarding guide for a new developer:
1. Where to start reading the code
2. Key concepts to understand first
3. Most important files (with brief explanations)
4. Codebase conventions and patterns
"""


def save_prompt_to_file(prompt: str, repo_name: str) -> str:
    """Save the generated prompt to a file so the user can paste it into Bob IDE."""
    prompt_path = os.path.join(BOB_REPORTS_DIR, f"pending-prompt-{repo_name}.txt")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"[bob_service] Prompt saved -> {prompt_path}")
    return prompt_path


def save_bob_response_to_file(repo_name: str, response: str) -> str:
    """Save Bob's raw IDE response to bob_sessions/ for proof and parsing."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    response_path = os.path.join(BOB_REPORTS_DIR, f"response-{repo_name}-{timestamp}.txt")
    with open(response_path, "w", encoding="utf-8") as f:
        f.write(response)
    print(f"[bob_service] Bob response saved -> {response_path}")
    return response_path


# ─────────────────────────────────────────────────────────────────────────────
# PARSER — Layer 1: Strict key-value format
# ─────────────────────────────────────────────────────────────────────────────
def _parse_strict_modules(modules_section: str) -> list[Module]:
    """
    Parse modules using strict format:
      MODULE_ID: slug
      MODULE_NAME: Name
      DESCRIPTION: ...
      KEY_FILES: file1.py, file2.py
      IMPORTS: mod1, mod2
      EXPORTS: Class1, func2
      ---
    """
    modules = []
    raw_blocks = modules_section.split("---")

    for raw in raw_blocks:
        raw = raw.strip()
        if not raw:
            continue

        def get_field(text, field):
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.lower().startswith(f"{field.lower()}:"):
                    return stripped.split(":", 1)[1].strip()
            return ""

        def get_list_field(text, field):
            val = get_field(text, field)
            return [x.strip() for x in val.split(",") if x.strip()]

        mod_id = get_field(raw, "MODULE_ID")
        mod_name = get_field(raw, "MODULE_NAME")
        description = get_field(raw, "DESCRIPTION")
        key_files = get_list_field(raw, "KEY_FILES")
        imports = get_list_field(raw, "IMPORTS")
        exports = get_list_field(raw, "EXPORTS")

        # Only add if we got at least a name or id
        if mod_id or mod_name or description:
            modules.append(Module(
                id=mod_id or f"module-{len(modules)+1}",
                name=mod_name or mod_id or f"Module {len(modules)+1}",
                description=description,
                key_files=key_files,
                imports=imports,
                exports=exports,
                where_used=[],
            ))

    return modules


# ─────────────────────────────────────────────────────────────────────────────
# PARSER — Layer 2: Markdown fallback format
# ─────────────────────────────────────────────────────────────────────────────
def _parse_markdown_modules(modules_section: str) -> list[Module]:
    """
    Fallback parser for Bob's natural markdown-style response:
      ### Core Routing Module
      Handles request routing...
      Key files: fastapi/routing.py, fastapi/applications.py
      Imports from: starlette, pydantic
      Exports: APIRouter, FastAPI
    """
    modules = []

    # Split on ### headings
    blocks = re.split(r"(?m)^###\s+", modules_section)

    for block in blocks:
        block = block.strip()
        if not block or len(block) < 10:
            continue

        lines = block.splitlines()
        if not lines:
            continue

        # First line = module name
        mod_name = lines[0].strip().rstrip(":").strip()
        remaining = "\n".join(lines[1:]).strip()

        # Build slug id from name
        mod_id = re.sub(r"[^a-z0-9]+", "-", mod_name.lower()).strip("-")

        # Extract description: first non-empty, non-pattern line
        description = ""
        for line in lines[1:]:
            line = line.strip()
            if line and not re.match(r"(?i)^(key files?|imports?|exports?|uses?|depends?)", line):
                description = line.strip("*_").strip()
                break

        # Extract key files — lines containing .py, .js, .ts etc or "key files:"
        key_files = []
        for line in lines:
            line = line.strip("- *").strip()
            if re.match(r"(?i)^(key files?|files?):", line):
                raw = re.split(r"(?i)^(key files?|files?):", line, 1)[-1]
                key_files = [f.strip() for f in raw.split(",") if f.strip()]
            elif re.search(r"\.(py|js|ts|jsx|tsx|go|rb|java|yaml|yml|json|toml)$", line):
                # bare filename reference
                fname = line.split()[-1].strip(",").strip()
                if fname and fname not in key_files:
                    key_files.append(fname)

        # Extract imports
        imports = []
        for line in lines:
            line = line.strip("- *").strip()
            if re.match(r"(?i)^(imports?( from)?|uses?|depends? on):", line):
                raw = re.split(r":", line, 1)[-1]
                imports = [x.strip() for x in raw.split(",") if x.strip()]
                break

        # Extract exports
        exports = []
        for line in lines:
            line = line.strip("- *").strip()
            if re.match(r"(?i)^(exports?|provides?|exposes?):", line):
                raw = re.split(r":", line, 1)[-1]
                exports = [x.strip() for x in raw.split(",") if x.strip()]
                break

        if mod_name:
            modules.append(Module(
                id=mod_id or f"module-{len(modules)+1}",
                name=mod_name,
                description=description,
                key_files=key_files,
                imports=imports,
                exports=exports,
                where_used=[],
            ))

    return modules


# ─────────────────────────────────────────────────────────────────────────────
# PARSER — Main: tries strict first, falls back to markdown
# ─────────────────────────────────────────────────────────────────────────────
def _parse_modules(modules_section: str) -> list[Module]:
    """
    Two-layer module parser:
    1. Try strict key-value format (MODULE_ID:, KEY_FILES:, etc.)
    2. If that yields empty/useless modules, fall back to markdown (### headings)
    """
    if not modules_section.strip():
        return []

    # Try strict format first
    strict_modules = _parse_strict_modules(modules_section)

    # Check if strict parsing was useful:
    # "useful" means at least one module has a real name AND either key_files or description
    useful = [
        m for m in strict_modules
        if (m.name and not m.name.startswith("module-"))
        and (m.key_files or m.description)
    ]

    if useful:
        print(f"[bob_service] Strict parser found {len(strict_modules)} modules ({len(useful)} with content)")
        return strict_modules

    # Fall back to markdown parser
    print("[bob_service] Strict parse yielded empty modules — trying markdown fallback parser")
    md_modules = _parse_markdown_modules(modules_section)

    if md_modules:
        print(f"[bob_service] Markdown parser found {len(md_modules)} modules")
        return md_modules

    # Last resort: return what strict gave us (even if shallow)
    print("[bob_service] Both parsers found no useful modules — returning empty")
    return strict_modules


def parse_bob_response(response: str, repo_url: str, repo_name: str, file_count: int) -> RepoAnalysis:
    """
    Parse Bob's full text response into a RepoAnalysis Pydantic model.
    Handles both strict key-value and markdown-style Bob responses.
    """
    def extract_section(text: str, heading: str) -> str:
        marker = f"## {heading}"
        start = text.find(marker)
        if start == -1:
            return ""
        start += len(marker)
        next_heading = text.find("## ", start)
        end = next_heading if next_heading != -1 else len(text)
        return text[start:end].strip()

    tech_section = extract_section(response, "TECH_STACK")
    arch_section = extract_section(response, "ARCHITECTURE")
    modules_section = extract_section(response, "MODULES")
    guide_section = extract_section(response, "ONBOARDING_GUIDE")

    # Parse tech stack: strip bullets, dashes, asterisks
    tech_stack = [
        line.strip("- *•").strip()
        for line in tech_section.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    # Parse modules with two-layer parser
    modules = _parse_modules(modules_section)

    print(f"[bob_service] Parsed: {len(tech_stack)} tech items, {len(modules)} modules")

    return RepoAnalysis(
        repo_url=repo_url,
        repo_name=repo_name,
        scanned_at=datetime.utcnow().isoformat(),
        tech_stack=tech_stack,
        architecture_summary=arch_section,
        modules=modules,
        onboarding_guide=guide_section,
        file_count=file_count,
    )


def prepare_ide_context(file_nodes: list[FileNode], repo_url: str, repo_name: str) -> dict:
    """
    STEP 1 of IDE workflow:
    Build the Bob prompt, save it to a file, and return it to the frontend.
    """
    prompt = build_analysis_prompt(file_nodes, repo_name)
    prompt_path = save_prompt_to_file(prompt, repo_name)
    print(f"[bob_service] IDE prompt ready for repo: {repo_name} ({len(file_nodes)} files)")
    return {
        "status": "awaiting_bob_response",
        "repo_name": repo_name,
        "repo_url": repo_url,
        "file_count": len(file_nodes),
        "prompt": prompt,
        "prompt_saved_to": prompt_path,
        "instructions": (
            "1. Copy the 'prompt' text above. "
            "2. Open IBM Bob in VS Code (Ask mode). "
            "3. Paste the prompt and send it to Bob. "
            "4. Copy Bob's ENTIRE response. "
            "5. POST it to /api/submit-bob-response with your repo_url and the response text."
        )
    }


def submit_ide_response(
    bob_response_text: str,
    repo_url: str,
    repo_name: str,
    file_count: int
) -> RepoAnalysis:
    """
    STEP 2 of IDE workflow:
    Accept the raw text copied from IBM Bob IDE, save it, parse it.
    """
    response_path = save_bob_response_to_file(repo_name, bob_response_text)
    save_bob_session(
        prompt=f"[IDE workflow] prompt for {repo_name}",
        response=bob_response_text[:5000]
    )
    print(f"[bob_service] Parsing Bob IDE response for repo: {repo_name}")
    return parse_bob_response(bob_response_text, repo_url, repo_name, file_count)
