import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from backend.database import init_db, get_db
from backend.seed import seed_data
from backend.routes import router

app = FastAPI(title="接口管理平台", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    db = get_db()
    init_db(db)
    seed_data(db)
    db.close()

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/")
def home():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
