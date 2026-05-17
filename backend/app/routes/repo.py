from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    AnalyzeRequest, RepoAnalysis, WhereUsedResponse, GuideResponse,
    SubmitBobResponseRequest, PrepareContextResponse
)
from app.services.git_service import clone_repo, cleanup_repo, get_repo_name
from app.services.bob_service import prepare_ide_context, submit_ide_response
from app.services.import_search import search_where_used

router = APIRouter(prefix="/api", tags=["repo"])

# ── In-memory store (resets on each new analysis) ────────────────────────────
_last_analysis: RepoAnalysis | None = None
_last_file_nodes = []
_pending_context: dict | None = None  # Holds Step 1 context while awaiting Bob response


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Clone repo + prepare Bob prompt for IDE
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/analyze", response_model=PrepareContextResponse)
async def analyze_repo(request: AnalyzeRequest):
    """
    Step 1 of IDE workflow:
    - Clones the GitHub repo
    - Scans up to 100 files
    - Builds a Bob prompt and returns it

    The user then pastes this prompt into IBM Bob IDE (VS Code),
    copies Bob's response, and submits it to POST /api/submit-bob-response.
    """
    global _pending_context, _last_file_nodes

    repo_url = request.repo_url.strip()
    if not repo_url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Please provide a valid public GitHub URL.")

    repo_name = get_repo_name(repo_url)
    clone_path = None

    try:
        clone_path, file_nodes = clone_repo(repo_url)

        if not file_nodes:
            raise HTTPException(status_code=422, detail="No source files found in this repository.")

        # Store file nodes for Step 2
        _last_file_nodes = file_nodes

        # Build and return the IDE prompt context
        context = prepare_ide_context(file_nodes, repo_url, repo_name)
        _pending_context = {
            "repo_url": repo_url,
            "repo_name": repo_name,
            "file_count": len(file_nodes),
        }

        return PrepareContextResponse(**context)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if clone_path:
            cleanup_repo(clone_path)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Accept Bob IDE response + parse into RepoAnalysis
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/submit-bob-response", response_model=RepoAnalysis)
async def submit_bob_response(request: SubmitBobResponseRequest):
    """
    Step 2 of IDE workflow:
    - Accepts the raw text pasted from IBM Bob IDE
    - Parses it into a structured RepoAnalysis
    - Stores it in memory for subsequent GET requests

    Required fields:
    - repo_url: the GitHub URL that was analyzed
    - bob_response: the full text copied from Bob IDE
    """
    global _last_analysis

    if not request.bob_response.strip():
        raise HTTPException(status_code=400, detail="bob_response cannot be empty.")

    repo_url = request.repo_url.strip()
    repo_name = get_repo_name(repo_url)
    file_count = len(_last_file_nodes) if _last_file_nodes else 0

    try:
        analysis = submit_ide_response(
            bob_response_text=request.bob_response,
            repo_url=repo_url,
            repo_name=repo_name,
            file_count=file_count,
        )
        _last_analysis = analysis
        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# GET endpoints (use result from last completed analysis)
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/result", response_model=RepoAnalysis)
async def get_result():
    """Return the last completed RepoAnalysis."""
    if _last_analysis is None:
        raise HTTPException(
            status_code=404,
            detail="No analysis available. POST to /api/analyze then /api/submit-bob-response first."
        )
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
