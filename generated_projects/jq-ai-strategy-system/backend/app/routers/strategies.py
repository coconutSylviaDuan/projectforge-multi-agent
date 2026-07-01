from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Strategy
from app.schemas import StrategySaveRequest, StrategySaveResponse, StrategyDetail, StrategyListResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/strategies", tags=["strategies"])

@router.get("", response_model=StrategyListResponse)
def list_strategies(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    strategies = db.query(Strategy).filter(Strategy.user_id == user.id).order_by(Strategy.updated_at.desc()).all()
    items = []
    for s in strategies:
        items.append(StrategyDetail(
            id=s.id,
            name=s.name,
            description=s.description or "",
            code=s.code,
            created_at=s.created_at,
            bound_backtest_id=s.bound_backtest_id
        ))
    return StrategyListResponse(strategies=items)

@router.get("/{id}", response_model=StrategyDetail)
def get_strategy(id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    strategy = db.query(Strategy).filter(Strategy.id == id, Strategy.user_id == user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return StrategyDetail(
        id=strategy.id,
        name=strategy.name,
        description=strategy.description or "",
        code=strategy.code,
        created_at=strategy.created_at,
        bound_backtest_id=strategy.bound_backtest_id
    )

@router.post("", response_model=StrategySaveResponse, status_code=status.HTTP_201_CREATED)
def save_strategy(req: StrategySaveRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if req.id:
        strategy = db.query(Strategy).filter(Strategy.id == req.id, Strategy.user_id == user.id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        strategy.name = req.name
        strategy.description = req.description
        strategy.code = req.code
        db.commit()
        db.refresh(strategy)
        return StrategySaveResponse(id=strategy.id, created_at=strategy.created_at)
    else:
        strategy = Strategy(
            user_id=user.id,
            name=req.name,
            description=req.description,
            code=req.code
        )
        db.add(strategy)
        db.commit()
        db.refresh(strategy)
        return StrategySaveResponse(id=strategy.id, created_at=strategy.created_at)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_strategy(id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    strategy = db.query(Strategy).filter(Strategy.id == id, Strategy.user_id == user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    db.delete(strategy)
    db.commit()
