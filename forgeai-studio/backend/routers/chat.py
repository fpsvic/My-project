from fastapi import APIRouter
from pydantic import BaseModel
from services.brain import generate_response
from services.spell_checker import spell_correct_query

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    mode: str = "forge_code"
    history: list[dict] = []
    quick_mode: bool = False
    workspace: str = "chat"


class ProjectFile(BaseModel):
    name: str
    content: str
    language: str


class ChatResponse(BaseModel):
    text: str
    corrections: list[dict] = []
    web_searched: bool = False
    project_files: list[ProjectFile] = []


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    spell_result = spell_correct_query(req.query)
    processed = spell_result["text"]

    from services import web_search as _ws
    _ws._last_searched = False

    result = generate_response(processed, req.mode, req.history, quick_mode=req.quick_mode, workspace=req.workspace)

    # generate_response now returns either a str or a dict with text + project_files
    if isinstance(result, dict):
        text = result.get("text", "")
        project_files = [ProjectFile(**f) for f in result.get("project_files", [])]
    else:
        text = result
        project_files = []

    return ChatResponse(
        text=text,
        corrections=spell_result.get("corrections", []),
        web_searched=_ws._last_searched,
        project_files=project_files,
    )
