"""Primary generative pipeline with graceful failover (Features 1.9, 1.14).

If the provider is unconfigured, unreachable, or returns invalid output, every
caller transparently falls back to the deterministic rule-based engine.
"""
from __future__ import annotations

import json
import re

import httpx

from ..config import get_settings
from .summary import JSON_SCHEMA, SUMMARY_SYSTEM_PROMPT

settings = get_settings()

_TIMEOUT = httpx.Timeout(12.0, connect=5.0)


def ai_available() -> bool:
    return bool(settings.openai_api_key)


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n?|```$", "", raw).strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in response")
    return json.loads(raw[start : end + 1])


async def generate(transcript_text: str, context: dict | None = None, language: str = "en") -> dict:
    """Try the LLM; on ANY failure return {"ok": False} so callers use the fallback."""
    if not ai_available():
        return {"ok": False, "reason": "generative_ai_not_configured"}

    context = context or {}
    user_prompt = (
        f"Detected language: {language}\n"
        f"Context: trauma_mode={context.get('trauma_mode', False)}, "
        f"flags={context.get('flag_categories', [])}, "
        f"profile={json.dumps(context.get('profile', {}), ensure_ascii=False)[:800]}\n\n"
        f"Transcript:\n\"\"\"\n{transcript_text[:6000]}\n\"\"\"\n\n"
        f"Return JSON with schema:\n{JSON_SCHEMA}"
    )

    try:
        async with httpx.AsyncClient(base_url=settings.openai_base_url, timeout=_TIMEOUT) as client:
            resp = await client.post(
                "/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": settings.openai_model,
                    "temperature": 0,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                },
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            data = _extract_json(content)
            return {
                "ok": True,
                "data": data,
                "model": settings.openai_model,
                "language": language,
                "confidence": 0.9,
            }
    except Exception as exc:  # network, auth, rate-limit, malformed JSON
        return {"ok": False, "reason": f"provider_error: {type(exc).__name__}"}
