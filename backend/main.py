"""Sahaara AI — FastAPI application entrypoint.

Run:  uvicorn main:app --reload   (from backend/)
  or: python main.py
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import SessionLocal, init_db
from app.routers import analytics, audit, auth, cases, demos, notifications, research, stream, users
from app.seed import seed

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
settings = get_settings()

app = FastAPI(
    title="Sahaara AI",
    version="1.0.0",
    description=(
        "AI-assisted, multilingual distress-assessment and support-routing platform for helpline operators. "
        "Decision-support only — AI never diagnoses and never acts autonomously (human-in-the-loop)."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (auth.router, users.router, cases.router, demos.router,
               analytics.router, audit.router, research.router, stream.router,
               notifications.router):
    app.include_router(router)


@app.get("/", tags=["meta"])
def root():
    """API index — replaces the default FastAPI 404 at the server root."""
    return {
        "name": "Sahaara AI",
        "version": app.version,
        "status": "running",
        "message": "AI-assisted helpline decision support. AI advises — humans decide.",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
        "api_base": "/api/v1",
        "endpoints": {
            "auth": ["/api/v1/auth/login", "/api/v1/auth/me"],
            "cases": "/api/v1/cases",
            "demos": "/api/v1/demos",
            "analytics": "/api/v1/analytics",
            "audit": "/api/v1/audit",
            "users": "/api/v1/users",
            "research": "/api/v1/research",
            "live_stream": "ws://<host>/api/v1/stream/{case_id}",
        },
        "frontend": "http://localhost:5173",
        "demo_logins": {
            "operator": "operator123",
            "counsellor": "counsel123",
            "supervisor": "super123",
            "admin": "admin123",
        },
    }


@app.get("/health")
def health():
    from app.ai.llm import ai_available
    from app.database import engine
    from sqlalchemy import text

    db_ok = True
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "up" if db_ok else "down",
        "ai_pipeline": "ai_assisted" if ai_available() else "human_assessment",
        "feature_1_14_graceful_failure": True,
    }


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    if settings.seed_demo_users:
        db = SessionLocal()
        try:
            seed(db)
        finally:
            db.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8010, reload=True)
