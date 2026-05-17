from pydantic import BaseModel, HttpUrl
from typing import Optional


class FileNode(BaseModel):
    path: str                  # Relative path from repo root
    extension: str             # e.g. ".py", ".js"
    size_bytes: int
    content: str               # Full file content (sent to Bob)


class Module(BaseModel):
    id: str                    # Unique slug e.g. "auth-module"
    name: str                  # Display name: "Authentication Module"
    description: str           # Bob's explanation of this module
    key_files: list[str]       # File paths most important to this module
    imports: list[str]         # Modules/files this module imports
    exports: list[str]         # Functions/classes this module exports
    where_used: list[str] = [] # Files that import this module


class RepoAnalysis(BaseModel):
    repo_url: str
    repo_name: str
    scanned_at: str
    tech_stack: list[str]
    architecture_summary: str
    modules: list[Module]
    onboarding_guide: str
    file_count: int


class AnalyzeRequest(BaseModel):
    repo_url: str


class AnalyzePromptResponse(BaseModel):
    status: str
    repo_url: str
    repo_name: str
    file_count: int
    prompt: str


class SubmitBobResponseRequest(BaseModel):
    repo_url: str
    bob_response: str


class WhereUsedResponse(BaseModel):
    module_id: str
    files: list[str]


class GuideResponse(BaseModel):
    guide: str


class SubmitBobResponseRequest(BaseModel):
    repo_url: str
    bob_response: str    # The raw text the user copy-pasted from Bob IDE


class PrepareContextResponse(BaseModel):
    status: str
    repo_name: str
    repo_url: str
    file_count: int
    prompt: str
    prompt_saved_to: str
    instructions: str

