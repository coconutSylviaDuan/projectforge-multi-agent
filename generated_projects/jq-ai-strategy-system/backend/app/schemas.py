from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

# Auth
class RegisterRequest(BaseModel):
    username: str
    password: str

class RegisterResponse(BaseModel):
    id: int
    username: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Chat
class ChatGenerateRequest(BaseModel):
    prompt: str
    history: Optional[List[dict]] = None

class ChatGenerateResponse(BaseModel):
    code: str
    strategy_id: int

class ChatContinueRequest(BaseModel):
    strategy_id: int
    message: str
    history: Optional[List[dict]] = None

class ChatContinueResponse(BaseModel):
    code: str
    reply: str

# Strategy
class StrategySaveRequest(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = ""
    code: str

class StrategySaveResponse(BaseModel):
    id: int
    created_at: datetime

class StrategyDetail(BaseModel):
    id: int
    name: str
    description: str
    code: str
    created_at: datetime
    bound_backtest_id: Optional[int] = None

class StrategyListResponse(BaseModel):
    strategies: List[StrategyDetail]

# Backtest
class QuickBacktestRequest(BaseModel):
    code: str
    strategy_id: Optional[int] = None

class QuickBacktestResponse(BaseModel):
    backtest_id: int
    result: dict

class AnalysisRequest(BaseModel):
    strategy_id: int
    code: str

class AnalysisResponse(BaseModel):
    backtest_id: int
    redirect_url: str

class BacktestResultItem(BaseModel):
    id: int
    type: str
    strategy_id: Optional[int] = None
    result_data: dict
    created_at: datetime

class BacktestResultListResponse(BaseModel):
    results: List[BacktestResultItem]

class BacktestResultDetail(BaseModel):
    id: int
    type: str
    result_data: dict
    strategy_id: Optional[int] = None

# Common
class ErrorResponse(BaseModel):
    detail: str
    error_code: str
