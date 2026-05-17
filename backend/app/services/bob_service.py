import json
import os
import re
from datetime import datetime

from app.models.schemas import FileNode, RepoAnalysis, Module
from app.utils.file_utils import build_bob_context

# ── Bob session log directory ────────────────────────────────────────────────
BOB_REPORTS_DIR = os.getenv("BOB_REPORTS_DIR", "./bob_sessions")
os.makedirs(BOB_REPORTS_DIR, exist_ok=True)


def save_bob_session(prompt: str, response: str) -> None:
    """Save every Bob interaction to /bob_sessions/ for submission proof."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    report_path = os.path.join(BOB_REPORTS_DIR, f"session-{timestamp}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"timestamp": timestamp, "prompt": prompt, "response": response}, f, indent=2)
    print(f"[bob_service] Session saved → {report_path}")


def build_analysis_prompt(file_nodes: list[FileNode], repo_name: str) -> str:
    """Build the master prompt to send to IBM Bob."""
    context = build_bob_context([n.model_dump() for n in file_nodes])
    return f"""You are analyzing the GitHub repository: {repo_name}

Here are the source files (up to 100 files, 200 lines each):

{context}

Please provide a structured analysis with the following sections:

## TECH_STACK
List each detected technology/framework/library on its own line.

## ARCHITECTURE
Write 2–3 paragraphs describing the overall architecture, design patterns, and how components connect.

## MODULES
For each identified module/service, provide:
MODULE_ID: <slug>
MODULE_NAME: <Display Name>
DESCRIPTION: <what this module does>
KEY_FILES: <comma-separated file paths>
IMPORTS: <comma-separated module names this imports>
EXPORTS: <comma-separated functions/classes exported>
---

## ONBOARDING_GUIDE
Write a complete onboarding guide for a new developer:
1. Where to start reading the code
2. Key concepts to understand first
3. Most important files (with brief explanations)
4. Codebase conventions and patterns
"""


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "module"


def _extract_section(text: str, heading: str) -> str:
    for marker in (f"## {heading}", f"## {heading.upper()}", f"# {heading}"):
        start = text.find(marker)
        if start != -1:
            start += len(marker)
            next_heading = re.search(r"\n##?\s+[A-Z]", text[start:])
            end = start + next_heading.start() if next_heading else len(text)
            return text[start:end].strip()
    return ""


def _get_field(text: str, field: str) -> str:
    pattern = re.compile(
        rf"^\s*(?:\*\*)?{re.escape(field)}(?:\*\*)?\s*:\s*(.+)$",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def _get_list_field(text: str, field: str) -> list[str]:
    val = _get_field(text, field)
    if val:
        return [x.strip() for x in re.split(r"[,;]", val) if x.strip()]
    # Bullet lines under a "Key files" / "Imports" style subheading
    items = []
    capture = False
    for line in text.splitlines():
        if re.match(rf"^\s*(?:\*\*)?{field}\s*:?\s*$", line, re.IGNORECASE):
            capture = True
            continue
        if capture:
            if re.match(r"^\s*(?:\*\*)?[A-Z_]+", line) and ":" in line:
                break
            bullet = re.match(r"^\s*[-*•]\s+(.+)$", line)
            if bullet:
                items.append(bullet.group(1).strip())
            elif line.strip() and not line.startswith("#"):
                items.append(line.strip())
    return items


def _parse_modules_structured(modules_section: str) -> list[Module]:
    modules = []
    for raw in re.split(r"\n---+\n", modules_section):
        raw = raw.strip()
        if not raw:
            continue
        mod_id = _get_field(raw, "MODULE_ID") or ""
        name = _get_field(raw, "MODULE_NAME") or ""
        description = _get_field(raw, "DESCRIPTION") or ""
        key_files = _get_list_field(raw, "KEY_FILES")
        imports = _get_list_field(raw, "IMPORTS")
        exports = _get_list_field(raw, "EXPORTS")

        if not mod_id and name:
            mod_id = _slugify(name)
        if not mod_id:
            mod_id = f"module-{len(modules) + 1}"
        if not name:
            name = mod_id.replace("-", " ").title()

        modules.append(
            Module(
                id=mod_id,
                name=name,
                description=description,
                key_files=key_files,
                imports=imports,
                exports=exports,
                where_used=[],
            )
        )
    return modules


def _parse_modules_markdown(modules_section: str) -> list[Module]:
    """Bob often returns ### headings instead of MODULE_ID: lines."""
    modules = []
    chunks = re.split(r"\n#{2,3}\s+", modules_section)
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk or chunk.upper().startswith("MODULES"):
            continue
        lines = chunk.splitlines()
        title = lines[0].strip().strip("#").strip()
        body = "\n".join(lines[1:]).strip()

        mod_id = _get_field(body, "MODULE_ID") or _slugify(title)
        name = _get_field(body, "MODULE_NAME") or title
        description = _get_field(body, "DESCRIPTION")
        if not description:
            # First paragraph(s) before next labeled field or bullet list
            desc_lines = []
            for line in body.splitlines():
                if re.match(r"^\s*[-*•]", line):
                    break
                if re.match(r"^\s*(?:\*\*)?[A-Z_]{3,}", line) and ":" in line:
                    break
                if line.strip():
                    desc_lines.append(line.strip())
            description = " ".join(desc_lines[:6])

        key_files = _get_list_field(body, "KEY_FILES") or _extract_path_bullets(body)
        imports = _get_list_field(body, "IMPORTS")
        exports = _get_list_field(body, "EXPORTS")

        modules.append(
            Module(
                id=mod_id,
                name=name,
                description=description,
                key_files=key_files,
                imports=imports,
                exports=exports,
                where_used=[],
            )
        )
    return modules


def _extract_path_bullets(text: str) -> list[str]:
    paths = []
    for line in text.splitlines():
        bullet = re.match(r"^\s*[-*•]\s+(.+)$", line)
        if not bullet:
            continue
        item = bullet.group(1).strip().strip("`")
        if "/" in item or item.endswith((".py", ".ts", ".js", ".go", ".rs")):
            paths.append(item)
    return paths


def _modules_are_sparse(modules: list[Module]) -> bool:
    if not modules:
        return True
    filled = sum(
        1 for m in modules if m.key_files or m.imports or m.exports or len(m.description) > 40
    )
    return filled < max(1, len(modules) // 2)


def parse_bob_response(response: str, repo_url: str, repo_name: str, file_count: int) -> RepoAnalysis:
    """
    Parse Bob's structured text response into a RepoAnalysis Pydantic model.
    Falls back to markdown-style parsing when Bob does not use MODULE_ID: fields.
    """
    tech_section = _extract_section(response, "TECH_STACK")
    arch_section = _extract_section(response, "ARCHITECTURE")
    modules_section = _extract_section(response, "MODULES")
    guide_section = _extract_section(response, "ONBOARDING_GUIDE")

    tech_stack = []
    for line in tech_section.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^[-*•]\s*", "", line)
        line = re.sub(r"^\d+\.\s*", "", line)
        if line and len(line) < 120:
            tech_stack.append(line)

    modules: list[Module] = []
    if modules_section:
        modules = _parse_modules_structured(modules_section)
        if _modules_are_sparse(modules):
            markdown_modules = _parse_modules_markdown(modules_section)
            if markdown_modules and not _modules_are_sparse(markdown_modules):
                modules = markdown_modules
                print("[bob_service] Used markdown-style module parser")

    if not modules:
        print("[bob_service] Warning: no modules parsed — check Bob response format")

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


def call_bob_api(prompt: str) -> str:
    """
    Call IBM Bob API with the analysis prompt.
    TODO: Replace with actual Bob API call when API key is available at kickoff.

    Scenario A (API): HTTP POST with Authorization: Bearer {IBM_BOB_API_KEY}
    Scenario B (IDE): Return pre-computed result from flask-analysis.json
    Scenario C (CLI): subprocess.run(['bob', 'analyze', ...])
    """
    bob_api_key = os.getenv("IBM_BOB_API_KEY", "")

    # ── SCENARIO B: Pre-computed (IDE-only) ──────────────────────────────────
    # If no API key is set, fall back to pre-computed JSON from bob_sessions/
    if not bob_api_key or bob_api_key == "your_bob_api_key_here":
        print("[bob_service] No API key found — loading pre-computed flask-analysis.json")
        precomputed_path = os.path.join(BOB_REPORTS_DIR, "flask-analysis.json")
        if os.path.exists(precomputed_path):
            with open(precomputed_path, "r", encoding="utf-8") as f:
                return f"PRE_COMPUTED:{precomputed_path}"
        return "[ERROR] No Bob API key and no pre-computed analysis found."

    # ── SCENARIO A: Real Bob API ─────────────────────────────────────────────
    # TODO: Uncomment and fill in the real endpoint at kickoff
    # import httpx
    # response = httpx.post(
    #     "https://api.ibm-bob.com/v1/analyze",  # Replace with real URL
    #     headers={"Authorization": f"Bearer {bob_api_key}"},
    #     json={"prompt": prompt},
    #     timeout=120.0,
    # )
    # response.raise_for_status()
    # return response.json().get("output", "")

    return "[PLACEHOLDER] Bob API call not yet implemented — add real endpoint at kickoff."


def analyze_repo_with_bob(file_nodes: list[FileNode], repo_url: str, repo_name: str) -> RepoAnalysis:
    """
    Main entry point: builds prompt, calls Bob, parses response, logs session.
    """
    prompt = build_analysis_prompt(file_nodes, repo_name)
    print(f"[bob_service] Sending {len(file_nodes)} files to Bob for repo: {repo_name}")

    response = call_bob_api(prompt)

    # Handle pre-computed Scenario B
    if response.startswith("PRE_COMPUTED:"):
        json_path = response.split(":", 1)[1]
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        save_bob_session(prompt=prompt[:500] + "...", response=f"Loaded from {json_path}")

        # Convert JSON to RepoAnalysis
        modules = []
        for m in data.get("modules", []):
            modules.append(
                Module(
                    id=m.get("id", "module"),
                    name=m.get("name", m.get("id", "Module")),
                    description=m.get("description", ""),
                    key_files=m.get("key_files") or m.get("keyFiles", []),
                    imports=m.get("imports", []),
                    exports=m.get("exports", []),
                    where_used=m.get("where_used") or m.get("whereUsed", []),
                )
            )
        return RepoAnalysis(
            repo_url=data.get("repo_url") or data.get("repoUrl", repo_url),
            repo_name=data.get("repo_name") or data.get("repoName", repo_name),
            scanned_at=data.get("scanned_at") or data.get("scannedAt", datetime.utcnow().isoformat()),
            tech_stack=data.get("tech_stack") or data.get("techStack", []),
            architecture_summary=data.get("architecture_summary") or data.get("architectureSummary", ""),
            modules=modules,
            onboarding_guide=data.get("onboarding_guide") or data.get("onboardingGuide", ""),
            file_count=len(file_nodes),
        )

    # Save session log
    save_bob_session(prompt=prompt[:500] + "...", response=response[:2000] + "...")

    # Parse Bob's text response
    return parse_bob_response(response, repo_url, repo_name, len(file_nodes))
