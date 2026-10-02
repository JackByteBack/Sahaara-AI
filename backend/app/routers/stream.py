"""WebSocket live stream (Features 1.2, 1.3, 1.5, 2.4, 2.11).

Endpoint: ws://host/api/v1/stream/{case_id}?token=JWT
Client → server: text | audio_chunk | typing | speech_features
Server → client: transcript | ai_flag | status_update | profile_update | mode | error
"""
from __future__ import annotations

import base64
import json

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from ..ai.llm import ai_available
from ..database import SessionLocal
from ..models import Case, User
from ..security import decode_access_token
from ..service import apply_analysis
from ..ws import manager

router = APIRouter()


def _auth(db: Session, token: str | None) -> User | None:
    if not token:
        return None
    try:
        payload = decode_access_token(token)
    except Exception:
        return None
    return db.get(User, payload.get("sub"))


@router.websocket("/api/v1/stream/{case_id}")
async def case_stream(ws: WebSocket, case_id: str, token: str | None = Query(default=None)):
    db = SessionLocal()
    user = _auth(db, token)
    case = db.get(Case, case_id) if user else None
    if user is None or case is None:
        await ws.close(code=4401, reason="Unauthorized or case not found")
        db.close()
        return

    await manager.connect(case_id, ws)
    mode = "ai_assisted" if ai_available() else "human_assessment"
    await ws.send_json({
        "type": "mode",
        "case_id": case_id,
        "mode": mode,
        "note": "" if ai_available() else (
            "Generative AI unavailable — Human Assessment Mode active (Feature 1.14). "
            "Core workflow remains fully operational."
        ),
        "language": ((case.language_info or {}).get("primary") or {}).get("language", "en"),
        "trauma_mode": case.trauma_mode,
    })
    await ws.send_json({
        "type": "profile_update",
        "case_id": case_id,
        "review_priority_score": case.review_priority_score,
        "safety_override": case.safety_override,
        "safety_override_reason": case.safety_override_reason,
        "victim_safety_profile": case.victim_safety_profile or {},
        "uncertainty": case.uncertainty or {},
        "language_info": case.language_info or {},
        "flag_count": len(case.ai_flags or []),
        "mode": mode,
    })

    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "message": "Invalid JSON"})
                continue

            mtype = msg.get("type")

            if mtype == "typing":
                await ws.send_json({
                    "type": "status_update", "case_id": case_id,
                    "typing": bool(msg.get("is_typed")),
                })
                continue

            if mtype == "audio_chunk":
                # Voice pipeline: capture → transcribe → analyze (Feature 1.2)
                text, error = await _transcribe_audio(case, msg)
                if error:
                    await ws.send_json({"type": "error", "message": error})
                if not text:
                    continue
                mtype = "text"
                msg = {"type": "text", "text": text, "timestamp": msg.get("timestamp") or 0.0, "speaker": "caller"}

            if mtype == "speech_features":
                feats = msg.get("features") or {}
                result = apply_analysis(db, case, speech_features=feats, actor_id=user.id)
                await ws.send_json({
                    "type": "profile_update", "case_id": case_id,
                    "review_priority_score": result["review_priority_score"],
                    "safety_override": result["safety_override"],
                    "victim_safety_profile": result["victim_safety_profile"],
                    "uncertainty": result["uncertainty"],
                    "mode": result["mode"],
                })
                continue

            if mtype in ("text", "transcript"):
                text = (msg.get("text") or msg.get("data") or "").strip()
                if not text:
                    continue
                timestamp = float(msg.get("timestamp") or 0.0)
                speaker = msg.get("speaker") or "caller"
                segment = {"text": text, "speaker": speaker, "timestamp": timestamp}
                case.transcript = list(case.transcript or []) + [segment]
                db.commit()

                await manager.broadcast(case_id, {
                    "type": "transcript", "case_id": case_id, "text": text,
                    "speaker": speaker, "timestamp": timestamp,
                })
                feats = msg.get("features")
                apply_analysis(db, case, speech_features=feats, actor_id=user.id)

                # When the caller finishes a turn, refresh the structured summary too
                if msg.get("want_summary"):
                    from ..ai.summary import build_summary

                    full = "\n".join(s.get("text", "") for s in (case.transcript or []))
                    summary = build_summary(full, case.ai_flags or [], case.victim_safety_profile or {})
                    case.summary = summary
                    db.commit()
                    await manager.broadcast(case_id, {"type": "summary", "case_id": case_id, "summary": summary})
                continue

            await ws.send_json({"type": "error", "message": f"Unknown message type: {mtype}"})

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(case_id, ws)
        db.close()


async def _transcribe_audio(case: Case, msg: dict) -> tuple[str | None, str | None]:
    """Transcribe audio if a provider is configured; otherwise guide the operator
    to browser ASR or typed input (Feature 1.14 graceful degradation).

    Returns (transcript_text, error_message). Raw audio is never persisted
    (Feature 1.10 — retain_raw_audio defaults to False).
    """
    if ai_available():
        try:
            import httpx

            from ..config import get_settings

            settings = get_settings()
            raw = base64.b64decode(msg.get("data") or "")
            async with httpx.AsyncClient(base_url=settings.openai_base_url, timeout=20.0) as client:
                resp = await client.post(
                    "/audio/transcriptions",
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                    files={"file": ("chunk.webm", raw, "audio/webm")},
                    data={"model": "whisper-1", "language": msg.get("language", "en")},
                )
                resp.raise_for_status()
                text = resp.json().get("text", "").strip()
            if text:
                return text, None
            return None, "Transcription returned empty text."
        except Exception as exc:
            return None, (
                f"Transcription unavailable ({type(exc).__name__}). "
                "Use browser speech input or typed mode — analysis continues normally."
            )

    return None, (
        "Server-side ASR not configured — using browser speech recognition or typed input (Feature 1.14)."
    )
