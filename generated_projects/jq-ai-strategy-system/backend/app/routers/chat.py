from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Strategy
from app.schemas import ChatGenerateRequest, ChatGenerateResponse, ChatContinueRequest, ChatContinueResponse
from app.auth import get_current_user
from app.services.ai_service import generate_code, continue_chat

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/generate", response_model=ChatGenerateResponse)
def generate_strategy(req: ChatGenerateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    code = generate_code(req.prompt)
    strategy = Strategy(
        user_id=user.id,
        name="新策略",
        description="通过AI对话生成",
        code=code
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return ChatGenerateResponse(code=code, strategy_id=strategy.id)

@router.post("/continue", response_model=ChatContinueResponse)
def continue_conversation(req: ChatContinueRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    strategy = db.query(Strategy).filter(Strategy.id == req.strategy_id, Strategy.user_id == user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    new_code, reply = continue_chat(req.message, strategy.code, req.history or [])
    # Do not auto-save; only return updated code
    return ChatContinueResponse(code=new_code, reply=reply)
