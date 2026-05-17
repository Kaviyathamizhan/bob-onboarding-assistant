from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routes.repo import router as repo_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="BobOnboard API",
    description="IBM Bob-powered Codebase Onboarding Assistant — Backend",
    version="1.0.0",
)

# ── CORS — allow React Vite dev server and Vercel deployment ─────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for hackathon deployment
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ─────────────────────────────────────────────────────────
app.include_router(repo_router)


@app.get("/")
def read_root():
    return {
        "message": "BobOnboard API is running.",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok", "powered_by": "IBM Bob + FastAPI"}
