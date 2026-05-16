import os
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

Please provide a structured analysis with the following sections exactly:

## TECH_STACK
List each detected technology/framework/library on its own line starting with a dash.

## ARCHITECTURE
Write 2-3 paragraphs describing the overall architecture, design patterns, and how components connect.

## MODULES
For each identified module/service, provide the following fields, then a line with just ---:
MODULE_ID: <lowercase-slug>
MODULE_NAME: <Display Name>
DESCRIPTION: <one sentence describing what this module does>
KEY_FILES: <comma-separated file paths>
IMPORTS: <comma-separated module names this imports>
EXPORTS: <comma-separated functions/classes exported>
---

## ONBOARDING_GUIDE
Write a complete onboarding guide for a new developer joining this project:
1. Where to start reading the code
2. Key concepts to understand first
3. Most important files with brief explanations
4. Codebase conventions and patterns used
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
        next_heading = text.find("## ", start)
        end = next_heading if next_heading != -1 else len(text)
        return text[start:end].strip()

    tech_section = extract_section(response, "TECH_STACK")
    arch_section = extract_section(response, "ARCHITECTURE")
    modules_section = extract_section(response, "MODULES")
    guide_section = extract_section(response, "ONBOARDING_GUIDE")

    tech_stack = [line.strip("- *").strip() for line in tech_section.splitlines() if line.strip()]

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


def prepare_ide_context(file_nodes: list[FileNode], repo_url: str, repo_name: str) -> dict:
    """
    STEP 1 of IDE workflow:
    Build the Bob prompt, save it to a file, and return it to the frontend
    so the user can copy-paste it into the IBM Bob IDE (VS Code).
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
            "2. Open IBM Bob in VS Code. "
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
    Accept the raw text the user copied from IBM Bob IDE,
    save it as a session log, parse it, and return RepoAnalysis.
    """
    # Save the raw response as proof of Bob usage
    response_path = save_bob_response_to_file(repo_name, bob_response_text)
    save_bob_session(
        prompt=f"[IDE workflow] prompt for {repo_name}",
        response=bob_response_text[:5000]
    )
    print(f"[bob_service] Parsing Bob IDE response for repo: {repo_name}")
    return parse_bob_response(bob_response_text, repo_url, repo_name, file_count)
