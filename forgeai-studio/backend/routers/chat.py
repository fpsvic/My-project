from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_router import generate_response
from services.spell_checker import spell_correct_query
router = APIRouter()
class ChatRequest(BaseModel):
    query: str
    mode: str = "forge_code"
    history: list[dict] = []
    quick_mode: bool = False
class ChatResponse(BaseModel):
    text: str
    corrections: list[dict] = []
@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    spell_result = spell_correct_query(req.query)
    processed = spell_result["text"]
    text = generate_response(processed, req.mode, req.history, quick_mode=req.quick_mode)
    return ChatResponse(text=text, corrections=[])
