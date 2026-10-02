"""Simple fixed-window rate limiter (build/Feature.md §3 — API rate limiting)."""
from datetime import datetime, timezone

from fastapi import HTTPException

from .models import RateLimit


def check_rate_limit(db, key: str, max_requests: int = 5, window_seconds: int = 60) -> None:
    now = datetime.now(timezone.utc)
    row = db.get(RateLimit, key)
    if row is None:
        row = RateLimit(id=key, count=1, window_start=now)
        db.add(row)
        return
    elapsed = (now - (row.window_start or now)).total_seconds()
    if elapsed > window_seconds:
        row.count = 1
        row.window_start = now
        return
    if row.count >= max_requests:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait and try again.")
    row.count += 1
