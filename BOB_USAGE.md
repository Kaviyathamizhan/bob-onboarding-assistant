# Bob Usage Documentation

## Summary
BobOnboard uses IBM Bob for ALL major AI features.
Bob analyzes the **entire repository context** — not just single files.
This document tracks every Bob interaction used during the hackathon build.

- **Demo repo analyzed:** https://github.com/pallets/flask
- **Files scanned:** 87 files
- **Total Bob prompts run:** 5
- **Session logs:** See `/bob_sessions/` folder

---

## Feature: Architecture Analysis

- **Prompt used:** Prompt #1 — `bob_sessions/prompts-used.md`
- **Bob response:** `bob_sessions/flask-analysis-raw.md` → Section: Architecture Overview
- **Parsed output:** `bob_sessions/flask-analysis.json` → `architectureSummary`, `techStack`
- **Code that uses this:** `backend/app/services/bob_service.py`
- **Bob output excerpt:**
  > "Flask follows a modular, layered architecture with clear separation of concerns. At its core, Flask implements the WSGI specification… The framework uses a context-based design with two primary contexts: the application context and the request context, managed using Python's contextvars module."

---

## Feature: Module Descriptions

- **Prompt used:** Prompt #2 — `bob_sessions/prompts-used.md`
- **Bob response:** `bob_sessions/flask-analysis-raw.md` → Section: Module Descriptions
- **Parsed output:** `bob_sessions/flask-analysis.json` → `modules[]` (14 modules identified)
- **Code that uses this:** `backend/app/services/bob_service.py`, `backend/app/routes/repo.py`
- **Bob output excerpt:**
  > "Core Application Module (app.py): Main Flask application class implementing WSGI interface… Globals Module (globals.py): Context-local proxy objects for accessing current_app, request, session, and g."

---

## Feature: Onboarding Guide Generation

- **Prompt used:** Prompt #3 — `bob_sessions/prompts-used.md`
- **Bob response:** `bob_sessions/flask-analysis-raw.md` → Section: Onboarding Guide
- **Parsed output:** `bob_sessions/flask-analysis.json` → `onboardingGuide`
- **Code that uses this:** `backend/app/routes/bob.py`, `frontend/src/components/OnboardingGuide.jsx`
- **Bob output excerpt:**
  > "1. Begin with README.md — Understand Flask's philosophy. 2. Read src/flask/__init__.py — See the public API. 3. Study src/flask/app.py lines 109–363 — The Flask class initialization."

---

## Feature: Critical Files Ranking

- **Prompt used:** Prompt #4 — `bob_sessions/prompts-used.md`
- **Bob response:** `bob_sessions/flask-analysis-raw.md` → Section: Critical Files Ranking
- **Code that uses this:** `frontend/src/components/OnboardingGuide.jsx` (priority badges)
- **Bob output excerpt:**
  > "⭐⭐⭐ src/flask/__init__.py — public API exports. ⭐⭐⭐ src/flask/app.py — Main Flask class. ⭐⭐⭐ src/flask/ctx.py — Context management, foundational to Flask's design."

---

## Feature: Where Used / Import Search

- **Prompt used:** Prompt #5 — `bob_sessions/prompts-used.md`
- **Bob response:** `bob_sessions/flask-analysis-raw.md` → Section: Where Used
- **Code that uses this:** `backend/app/services/import_search.py`, `frontend/src/components/WhereUsed.jsx`
- **Bob output excerpt:**
  > "Files importing 'current_app' or the Flask application factory: src/flask/helpers.py, src/flask/templating.py, src/flask/ctx.py, src/flask/wrappers.py, examples/tutorial/flaskr/__init__.py"

---

## Bob-Assisted Code

The following files were written with Bob's assistance:

| File | How Bob helped |
|------|---------------|
| `backend/app/services/git_service.py` | Bob suggested the file filtering skip-list logic and GitPython clone depth=1 pattern |
| `backend/app/services/import_search.py` | Bob wrote the initial Python import regex patterns (`from X import`, `import X`) |
| `backend/app/models/schemas.py` | Bob generated the Pydantic model structure matching the RepoAnalysis JSON shape |
| `backend/app/services/bob_service.py` | Bob reviewed and improved the prompt construction and response parsing logic |

---

## Session Logs

| File | Contents |
|------|----------|
| `bob_sessions/flask-analysis-raw.md` | Complete raw Bob output for all 5 prompts |
| `bob_sessions/flask-analysis.json` | Parsed structured JSON (14 modules, full analysis) |
| `bob_sessions/prompts-used.md` | All 5 exact prompts sent to Bob |
| `bob_sessions/screenshots/` | Screenshots of Bob IDE sessions |

---

## Visual Evidence (Screenshots)

Here are the screenshots demonstrating live IBM Bob IDE usage by the team members.

### Kaviyathamizhan (Backend & AI Pipeline)
![Kaviyathamizhan Usage 1](bob_sessions/screenshots/person-1%20usage%201.png)
![Kaviyathamizhan Usage 2](bob_sessions/screenshots/person-1%20usage%202.png)

### Person 2 (Frontend)
![Person 2 Usage 1](bob_sessions/screenshots/person-2%20usage%201.jpeg)
![Person 2 Usage 2](bob_sessions/screenshots/person-2%20usage%202.jpeg)
![Person 2 Usage 3](bob_sessions/screenshots/person-2%20usage%203.jpeg)
