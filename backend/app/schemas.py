"""Pydantic request/response schemas (build/api-spec.md, build/api-response-schemas.md)."""
from pydantic import BaseModel, Field


# ── Auth (Feature 1.11) ────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: str
    username: str
    display_name: str
    role: str
    language: str = "en"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ── Sessions / Cases (Features 1.7, 1.2, 1.3) ─────────────────────────
class StartCaseRequest(BaseModel):
    initial_language: str = "en"
    mode: str = "text"  # voice | text | demo
    consent: bool = True
    consent_scope: str = "processing"
    trauma_mode: bool = False
    operator_id: str | None = None
    language_override: str | None = None  # Feature 1.3 operator override


class SegmentIn(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    speaker: str = "caller"  # caller | operator
    timestamp: float = 0.0
    speech: "SpeechFeatures | None" = None  # optional acoustic evidence (Features 2.4 / 2.11)


class SpeechFeatures(BaseModel):
    volume: float | None = None
    pitch_variance: float | None = None
    long_pause_count: int = 0
    timestamp: float = 0.0


class ReviewRequest(BaseModel):
    decision: str  # confirm | modify | escalate | dismiss
    override_ai: bool = False
    notes: str = ""
    final_priority: float | None = None  # when operator modifies the score (Feature 1.6)


class FlagDecisionRequest(BaseModel):
    decision: str  # confirm | modify | escalate | dismiss
    notes: str = ""
    modified_severity: str | None = None


class NoteCreate(BaseModel):
    body: str
    author_role: str | None = None


class ReferralCreate(BaseModel):
    referral_type: str  # counselling | mental_health | medical | legal_aid | protection | emergency | shelter | rehabilitation | welfare
    notes: str = ""
    ai_suggested: bool = False


class FollowupCreate(BaseModel):
    stage: str  # intervention | followup | reassessment
    note: str = ""
    outcome: str | None = None
    due_at: str | None = None  # ISO date — drives follow-up reminders


class FollowupUpdate(BaseModel):
    outcome: str | None = None
    completed: bool | None = None
    due_at: str | None = None


class AnonymizeRequest(BaseModel):
    extra_names: list[str] = []


class CaseUpdate(BaseModel):
    status: str | None = None
    trauma_mode: bool | None = None
    language_override: str | None = None
    assigned_to: str | None = None  # user id; "" unassigns (assignment workflow)


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    language: str | None = None
    current_password: str | None = None
    new_password: str | None = None  # requires current_password


# ── WebSocket payloads (build/api-spec.md §1) ─────────────────────────
class ClientMessage(BaseModel):
    type: str  # text | audio_chunk | typing | speech_features
    data: str | None = None
    text: str | None = None
    timestamp: float | None = None
    is_typed: bool | None = None
    features: SpeechFeatures | None = None
