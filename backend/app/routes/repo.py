from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzePromptResponse,
    SubmitBobResponseRequest,
    RepoAnalysis,
    WhereUsedResponse,
    GuideResponse,
)
from app.services.git_service import clone_repo, cleanup_repo, get_repo_name
from app.services.bob_service import build_analysis_prompt, parse_bob_response, save_bob_session
from app.services.import_search import search_where_used
from app.services.session_store import save_pending, load_pending, clear_pending


def _normalize_repo_url(url: str) -> str:
    return url.strip().rstrip("/")

router = APIRouter(prefix="/api", tags=["repo"])

# ── In-memory store (resets on new analysis) ─────────────────────────────────
_last_analysis: RepoAnalysis | None = None
_last_file_nodes = []
_pending_repo_url: str | None = None
_pending_repo_name: str | None = None


@router.post("/analyze", response_model=AnalyzePromptResponse)
async def analyze_repo(request: AnalyzeRequest):
    """
    Step 1: Clone repo, scan files, build Bob prompt.
    User copies prompt into IBM Bob IDE and returns response via submit-bob-response.
    """
    global _last_file_nodes, _pending_repo_url, _pending_repo_name, _last_analysis

    repo_url = _normalize_repo_url(request.repo_url)
    if not repo_url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Please provide a valid public GitHub URL.")

    repo_name = get_repo_name(repo_url)
    clone_path = None

    try:
        clone_path, file_nodes = clone_repo(repo_url)

        if not file_nodes:
            raise HTTPException(status_code=422, detail="No source files found in this repository.")

        prompt = build_analysis_prompt(file_nodes, repo_name)

        _last_file_nodes = file_nodes
        _pending_repo_url = repo_url
        _pending_repo_name = repo_name
        _last_analysis = None
        save_pending(repo_url, repo_name, file_nodes)

        return AnalyzePromptResponse(
            status="awaiting_bob_response",
            repo_url=repo_url,
            repo_name=repo_name,
            file_count=len(file_nodes),
            prompt=prompt,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    finally:
        # Best-effort cleanup — must not turn a successful analyze into 500 on Windows
        if clone_path:
            try:
                cleanup_repo(clone_path)
            except Exception as exc:
                print(f"[repo] cleanup skipped: {exc}")


@router.post("/submit-bob-response", response_model=RepoAnalysis)
async def submit_bob_response(request: SubmitBobResponseRequest):
    """Step 2: Parse Bob IDE text response into RepoAnalysis."""
    global _last_analysis, _pending_repo_url, _pending_repo_name, _last_file_nodes

    repo_url = _normalize_repo_url(request.repo_url)

    if not _last_file_nodes or _pending_repo_url is None:
        restored = load_pending()
        if restored:
            _pending_repo_url, _pending_repo_name, _last_file_nodes = restored
        else:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No pending analysis. Run Analyze again, then submit Bob's response "
                    "(server may have restarted — do not restart uvicorn between steps)."
                ),
            )

    if repo_url != _normalize_repo_url(_pending_repo_url):
        raise HTTPException(
            status_code=400,
            detail=f"repo_url does not match the last analyze request ({_pending_repo_url}).",
        )

    bob_text = request.bob_response.strip()
    if not bob_text:
        raise HTTPException(status_code=400, detail="bob_response cannot be empty.")

    try:
        analysis = parse_bob_response(
            bob_text,
            repo_url,
            _pending_repo_name or get_repo_name(repo_url),
            len(_last_file_nodes),
        )
        save_bob_session(prompt="(from submit-bob-response)", response=bob_text[:2000])
        _last_analysis = analysis
        clear_pending()
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/result", response_model=RepoAnalysis)
async def get_result():
    """Return the last full analysis."""
    if _last_analysis is None:
        raise HTTPException(status_code=404, detail="No analysis found. Complete the Bob flow first.")
    return _last_analysis


@router.get("/module/{module_id}", response_model=dict)
async def get_module(module_id: str):
    """Return a specific module from the last analysis."""
    if _last_analysis is None:
        raise HTTPException(status_code=404, detail="No analysis found. Run /api/analyze first.")

    for module in _last_analysis.modules:
        if module.id == module_id:
            return module.model_dump()

    raise HTTPException(status_code=404, detail=f"Module '{module_id}' not found.")


@router.get("/where-used/{module_id}", response_model=WhereUsedResponse)
async def where_used(module_id: str):
    """Run import search for a module across all scanned files."""
    if _last_analysis is None:
        raise HTTPException(status_code=404, detail="No analysis found. Run /api/analyze first.")

    files = search_where_used(module_id, _last_file_nodes)
    return WhereUsedResponse(module_id=module_id, files=files)


@router.get("/guide", response_model=GuideResponse)
async def get_guide():
    """Return the onboarding guide from the last Bob analysis."""
    if _last_analysis is None:
        raise HTTPException(status_code=404, detail="No analysis found. Run /api/analyze first.")

    return GuideResponse(guide=_last_analysis.onboarding_guide)
