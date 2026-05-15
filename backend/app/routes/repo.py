from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalyzeRequest, RepoAnalysis, WhereUsedResponse, GuideResponse
from app.services.git_service import clone_repo, cleanup_repo, get_repo_name
from app.services.bob_service import analyze_repo_with_bob
from app.services.import_search import search_where_used

router = APIRouter(prefix="/api", tags=["repo"])

# ── In-memory store (resets on new analysis) ─────────────────────────────────
_last_analysis: RepoAnalysis | None = None
_last_file_nodes = []


@router.post("/analyze", response_model=RepoAnalysis)
async def analyze_repo(request: AnalyzeRequest):
    """
    Main endpoint: accepts a GitHub URL, clones repo, scans files,
    calls IBM Bob, returns full RepoAnalysis.
    """
    global _last_analysis, _last_file_nodes

    repo_url = request.repo_url.strip()
    if not repo_url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Please provide a valid public GitHub URL.")

    repo_name = get_repo_name(repo_url)
    clone_path = None

    try:
        # Step 1: Clone repo and get file nodes
        clone_path, file_nodes = clone_repo(repo_url)

        if not file_nodes:
            raise HTTPException(status_code=422, detail="No source files found in this repository.")

        # Step 2: Analyze with Bob
        analysis = analyze_repo_with_bob(file_nodes, repo_url, repo_name)

        # Step 3: Store in memory
        _last_analysis = analysis
        _last_file_nodes = file_nodes

        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Step 4: Always clean up cloned repo
        if clone_path:
            cleanup_repo(clone_path)


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
