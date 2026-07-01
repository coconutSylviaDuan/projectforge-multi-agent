from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import User, Strategy, BacktestResult
from app.schemas import QuickBacktestRequest, QuickBacktestResponse, AnalysisRequest, AnalysisResponse, BacktestResultListResponse, BacktestResultItem, BacktestResultDetail
from app.auth import get_current_user
from app.services.backtest_engine import run_quick_backtest, run_full_backtest

router = APIRouter(prefix="/api", tags=["backtest"])

@router.post("/backtest/quick", response_model=QuickBacktestResponse)
def quick_backtest(req: QuickBacktestRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    result_data = run_quick_backtest(req.code)
    record = BacktestResult(
        strategy_id=req.strategy_id,
        user_id=user.id,
        type="quick",
        result_data=result_data
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return QuickBacktestResponse(backtest_id=record.id, result=result_data)

@router.post("/backtest/analysis", response_model=AnalysisResponse)
def full_backtest_analysis(req: AnalysisRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    strategy = db.query(Strategy).filter(Strategy.id == req.strategy_id, Strategy.user_id == user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    result_data = run_full_backtest(req.code)
    record = BacktestResult(
        strategy_id=req.strategy_id,
        user_id=user.id,
        type="full",
        result_data=result_data
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    # Bind the backtest to the strategy
    strategy.bound_backtest_id = record.id
    db.commit()
    return AnalysisResponse(backtest_id=record.id, redirect_url=f"/strategy/performance/{record.id}")

@router.get("/backtest-results", response_model=BacktestResultListResponse)
def list_backtest_results(type: Optional[str] = Query(None, regex="^(quick|full)?$"), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(BacktestResult).filter(BacktestResult.user_id == user.id)
    if type:
        query = query.filter(BacktestResult.type == type)
    results = query.order_by(BacktestResult.created_at.desc()).all()
    items = []
    for r in results:
        items.append(BacktestResultItem(
            id=r.id,
            type=r.type,
            strategy_id=r.strategy_id,
            result_data=r.result_data,
            created_at=r.created_at
        ))
    return BacktestResultListResponse(results=items)

@router.get("/backtest-results/{id}", response_model=BacktestResultDetail)
def get_backtest_detail(id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = db.query(BacktestResult).filter(BacktestResult.id == id, BacktestResult.user_id == user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Backtest result not found")
    return BacktestResultDetail(
        id=record.id,
        type=record.type,
        result_data=record.result_data,
        strategy_id=record.strategy_id
    )
