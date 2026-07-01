from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import auth, chat, strategies, backtest

app = FastAPI(title="AI Strategy System API", version="0.1.0")

# CORS configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
def health():
    return {"status": "ok"}

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(strategies.router)
app.include_router(backtest.router)

@app.on_event("startup")
def on_startup():
    init_db()
