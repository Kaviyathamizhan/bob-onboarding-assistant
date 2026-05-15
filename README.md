# BobOnboard — IBM Bob Hackathon Project

> **AI-powered codebase onboarding assistant** — paste a GitHub URL, get an instant architecture overview, module map, and onboarding guide. Powered by IBM Bob.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + Tailwind CSS + Axios |
| Backend | FastAPI (Python) + Uvicorn + Pydantic |
| Git Integration | GitPython |
| AI Analysis | IBM Bob |
| Deployment | Vercel (frontend) + Render (backend) |

---

## Project Structure

```
bob-onboarding-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + CORS config
│   │   ├── routes/
│   │   │   ├── repo.py          # POST /api/analyze, GET /api/guide
│   │   │   └── bob.py           # Bob-specific routes
│   │   ├── services/
│   │   │   ├── git_service.py   # GitPython clone + file walker
│   │   │   ├── bob_service.py   # Bob prompt builder + API caller
│   │   │   └── import_search.py # Where-used / import search
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic request/response models
│   │   └── utils/
│   │       └── file_utils.py    # Skip lists, file reader, context builder
│   ├── requirements.txt
│   └── .env                     # IBM_BOB_API_KEY, GITHUB_TOKEN, etc.
├── bob_sessions/
│   ├── flask-analysis-raw.md    # Raw Bob output
│   ├── flask-analysis.json      # Structured analysis (14 modules)
│   ├── prompts-used.md          # All prompts sent to Bob
│   └── screenshots/             # Bob IDE session screenshots
├── BOB_USAGE.md                 # Bob integration proof for judges
├── .env.example                 # Environment variable template
└── LICENSE                      # MIT
```

---

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp ../.env.example .env        # Fill in your IBM_BOB_API_KEY
uvicorn app.main:app --reload
```

Backend runs at: **http://localhost:8000**
API docs at: **http://localhost:8000/docs**

### Frontend *(Day 2)*

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/api/health` | Health check JSON |
| `POST` | `/api/analyze` | Analyze a GitHub repo via Bob |
| `GET` | `/api/guide` | Get onboarding guide from last analysis |
| `GET` | `/api/module/{id}` | Get a specific module's details |
| `GET` | `/api/where-used/{id}` | Find all files that import a module |

### Example Request

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/pallets/flask"}'
```

---

## How IBM Bob Is Used

Bob analyzes the **entire repository context** in one prompt — not just individual files.

1. Repo is cloned with `GitPython` (shallow, depth=1)
2. Up to 100 files are scanned (200 lines each) and built into a context blob
3. Bob receives the full context + a structured analysis prompt
4. Bob returns: tech stack, architecture overview, module map, onboarding guide
5. Response is parsed into Pydantic `RepoAnalysis` model and returned as JSON

See `BOB_USAGE.md` for complete Bob interaction documentation.

---

## Bob Session Logs

Every Bob interaction is logged to `bob_sessions/` as JSON files.
This is **required for hackathon submission** to prove Bob usage.

---

## Environment Variables

```
IBM_BOB_API_KEY=    # Required: Bob API key (given at kickoff)
GITHUB_TOKEN=       # Optional: higher GitHub API rate limits
PORT=8000           # Backend port
TEMP_DIR=./temp     # Temp dir for cloned repos
VITE_API_URL=http://localhost:8000  # Frontend → Backend URL
```

---

## Team

| Person | Role |
|--------|------|
| Person 1 | Backend + AI Pipeline (FastAPI, Bob integration, GitPython) |
| Person 2 | Frontend (React, Vite, Tailwind, UI components) |

---

## Hackathon Submission Checklist

- [x] IBM Bob used for core AI features
- [x] Bob session logs saved in `bob_sessions/`
- [x] `BOB_USAGE.md` documents all Bob interactions
- [x] MIT License added
- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Render
- [ ] Demo video recorded
