import os
import json
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


def parse_bob_response(response: str, repo_url: str, repo_name: str, file_count: int) -> RepoAnalysis:
    """
    Parse Bob's structured text response into a RepoAnalysis Pydantic model.
    Falls back gracefully if sections are missing.
    """
    def extract_section(text: str, heading: str) -> str:
        marker = f"## {heading}"
        start = text.find(marker)
        if start == -1:
            return ""
        start += len(marker)
        # Find next ## heading or end of string
        next_heading = text.find("## ", start)
        end = next_heading if next_heading != -1 else len(text)
        return text[start:end].strip()

    # Extract sections
    tech_section = extract_section(response, "TECH_STACK")
    arch_section = extract_section(response, "ARCHITECTURE")
    modules_section = extract_section(response, "MODULES")
    guide_section = extract_section(response, "ONBOARDING_GUIDE")

    # Parse tech stack
    tech_stack = [line.strip("- •*").strip() for line in tech_section.splitlines() if line.strip()]

    # Parse modules
    modules = []
    if modules_section:
        raw_modules = modules_section.split("---")
        for raw in raw_modules:
            raw = raw.strip()
            if not raw:
                continue
            def get_field(text, field):
                for line in text.splitlines():
                    if line.startswith(f"{field}:"):
                        return line.split(":", 1)[1].strip()
                return ""

            def get_list_field(text, field):
                val = get_field(text, field)
                return [x.strip() for x in val.split(",") if x.strip()]

            mod_id = get_field(raw, "MODULE_ID") or f"module-{len(modules)+1}"
            modules.append(Module(
                id=mod_id,
                name=get_field(raw, "MODULE_NAME") or mod_id,
                description=get_field(raw, "DESCRIPTION") or "",
                key_files=get_list_field(raw, "KEY_FILES"),
                imports=get_list_field(raw, "IMPORTS"),
                exports=get_list_field(raw, "EXPORTS"),
                where_used=[],
            ))

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
        modules = [Module(**m) for m in data.get("modules", [])]
        return RepoAnalysis(
            repo_url=data.get("repoUrl", repo_url),
            repo_name=data.get("repoName", repo_name),
            scanned_at=data.get("scannedAt", datetime.utcnow().isoformat()),
            tech_stack=data.get("techStack", []),
            architecture_summary=data.get("architectureSummary", ""),
            modules=modules,
            onboarding_guide=data.get("onboardingGuide", ""),
            file_count=len(file_nodes),
        )

    # Save session log
    save_bob_session(prompt=prompt[:500] + "...", response=response[:2000] + "...")

    # Parse Bob's text response
    return parse_bob_response(response, repo_url, repo_name, len(file_nodes))
