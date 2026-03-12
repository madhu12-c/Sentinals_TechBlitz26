from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

load_dotenv()

from db.mongo import connect_db, close_db
from scheduler.jobs import start_scheduler, stop_scheduler
from routes.webhook import router as webhook_router
from routes.leads import router as leads_router


# ── Lifespan: startup + shutdown ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    start_scheduler()
    print("[OK] SalesAgent backend ready")
    yield
    # Shutdown
    await close_db()
    stop_scheduler()
    print("[OK] SalesAgent backend shut down")


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SalesAgent API",
    description="AI-powered sales lead automation backend",
    version="1.0.0",
    lifespan=lifespan
)

# ── CORS (allow React frontend) ────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(webhook_router, tags=["Webhooks"])
app.include_router(leads_router,   tags=["Leads"])


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "service": "SalesAgent",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}


# ── Run directly ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
