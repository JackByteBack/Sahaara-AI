import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { useLiveAnalysis } from "../api/live";
import { useSpeech } from "../hooks/useSpeech";
import FlagsPanel from "../components/FlagsPanel";
import { ProfilePanel, UncertaintyPanel } from "../components/ProfilePanel";
import { Loading, ScoreBar, Segmented, Toasts, useToasts } from "../components/ui";

/* Trauma-informed question bank (Feature 2.13) — never starts with "Why". */
const QUESTIONS = [
  "Can you tell me what you need right now?",
  "Are you somewhere safe at the moment?",
  "What is the situation like where you are?",
  "Is anyone with you right now?",
  "Would it help if I connected you to someone?",
];
const REASSURANCE = "It’s not your fault. You are safe here. Take your time.";

export default function Session() {
  const { caseId } = useParams();
  const [params] = useSearchParams();
  const demoId = params.get("demo");
  const navigate = useNavigate();
  const { toasts, push, dismiss } = useToasts();

  const [caseData, setCaseData] = useState(null);
  const [lines, setLines] = useState([]);          // rendered transcript
  const [input, setInput] = useState("");
  const [volume, setVolume] = useState(null);
  const [flash, setFlash] = useState(false);
  const [summary, setSummary] = useState(null);
  const [qIndex, setQIndex] = useState(0);
  const [lastSpeakerAt, setLastSpeakerAt] = useState(Date.now());
  const [pausedLong, setPausedLong] = useState(false);
  const volumeRef = useRef(0);
  const demoCursor = useRef(0);

  const { connected, mode, modeNote, messages, send } = useLiveAnalysis(caseId);
  const traumaMode = caseData?.trauma_mode;

  const speech = useSpeech({
    language: caseData?.language_info?.primary?.language || "en",
    active: true,
    onResult: (text) => submitLine(text),
    onVolume: (v) => { volumeRef.current = v; setVolume(v); },
  });

  const loadCase = useCallback(async () => {
    try {
      const c = await api(`/api/v1/cases/${caseId}`);
      setCaseData(c);
      setSummary(c.summary && Object.keys(c.summary).length ? c.summary : null);
      setLines(c.transcript || []);
      return c;
    } catch (err) {
      push(err.message, "danger");
      return null;
    }
  }, [caseId, push]);

  useEffect(() => { loadCase(); }, [loadCase]);

  /* Consume WebSocket events */
  useEffect(() => {
    if (!messages.length) return;
    const last = messages[messages.length - 1];
    if (last.type === "transcript") {
      setLines((prev) => [...prev, { text: last.text, speaker: last.speaker, timestamp: last.timestamp }]);
      if (last.speaker === "caller") setLastSpeakerAt(Date.now());
    } else if (last.type === "ai_flag" && last.severity === "critical") {
      triggerOverride();
    } else if (last.type === "profile_update") {
      setCaseData((prev) => (prev ? {
        ...prev,
        review_priority_score: last.review_priority_score,
        safety_override: last.safety_override,
        safety_override_reason: last.safety_override_reason,
        victim_safety_profile: last.victim_safety_profile,
        uncertainty: last.uncertainty,
        language_info: last.language_info,
      } : prev));
      if (last.safety_override) triggerOverride();
    } else if (last.type === "summary") {
      setSummary(last.summary);
    } else if (last.type === "error") {
      push(last.message, "danger");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages]);

  const triggerOverride = useCallback(() => {
    setFlash(true);
    setTimeout(() => setFlash(false), 700);
  }, []);

  /* Trauma-informed pacing: next prompt only after a 3s pause (Feature 2.13) */
  useEffect(() => {
    const t = setInterval(() => {
      setPausedLong(Date.now() - lastSpeakerAt > 3000);
    }, 1000);
    return () => clearInterval(t);
  }, [lastSpeakerAt]);

  /* Scripted demo playback (Feature 1.15) */
  useEffect(() => {
    if (!demoId || !connected || !caseData) return;
    let cancelled = false;
    const run = async () => {
      try {
        const scenario = await api(`/api/v1/demos/${demoId}`);
        for (const line of scenario.lines) {
          if (cancelled) return;
          send({ type: "text", text: line, speaker: "caller", timestamp: demoCursor.current * 6 });
          demoCursor.current += 1;
          await new Promise((r) => setTimeout(r, 2200));
        }
      } catch (err) {
        push(err.message, "danger");
      }
    };
    run();
    return () => { cancelled = true; };
  }, [demoId, connected, caseData, send, push]);

  const submitLine = (text) => {
    const clean = text.trim();
    if (!clean) return;
    const ok = send({
      type: "text",
      text: clean,
      speaker: input.trim() ? "operator" : "caller",
      timestamp: Date.now() / 1000 % 100000,
      features: volumeRef.current ? { volume: volumeRef.current } : undefined,
    });
    if (!ok) push("Not connected — check the stream.", "danger");
    setInput("");
    setLastSpeakerAt(Date.now());
  };

  const generateSummary = async () => {
    try {
      const s = await api(`/api/v1/cases/${caseId}/summary`, { method: "POST" });
      setSummary(s);
      push(`Summary ready — ${s.label}`);
    } catch (err) {
      push(err.message, "danger");
    }
  };

  const sendSuggested = () => {
    const q = QUESTIONS[qIndex % QUESTIONS.length];
    setQIndex((i) => i + 1);
    submitLineAsOperator(q);
  };

  const submitLineAsOperator = (text) => {
    send({ type: "text", text, speaker: "operator", timestamp: Date.now() / 1000 % 100000 });
    setInput("");
    setLastSpeakerAt(Date.now());
  };

  const override = caseData?.safety_override;
  const priority = caseData?.review_priority_score ?? 0;

  const flagCount = useMemo(() => caseData?.ai_flags?.length || 0, [caseData]);

  if (!caseData) return <div className="page"><Loading text="Opening session" /></div>;

  return (
    <div className={`page${flash ? " flash-red" : ""}`}>
      <Toasts toasts={toasts} dismiss={dismiss} />

      {/* Header */}
      <div className="row-between wrap" style={{ gap: 16 }}>
        <div className="row wrap" style={{ gap: 12 }}>
          <h3>{caseData.case_number}</h3>
          <span className="pill pill-outline">{caseData.session_mode}</span>
          {traumaMode && <span className="pill pill-warn">trauma-informed</span>}
          <span className={`pill ${connected ? "pill-ok" : "pill-danger"}`}>
            {connected ? "stream live" : "reconnecting…"}
          </span>
        </div>
        <div className="row" style={{ gap: 8 }}>
          <button className="btn btn-soft" onClick={generateSummary}>Generate summary</button>
          <button className="btn btn-outline" onClick={() => navigate(`/cases/${caseId}`)}>Open review →</button>
        </div>
      </div>

      {/* Human Assessment Mode banner (Feature 1.14) */}
      {mode === "human_assessment" && (
        <div className="card-soft" style={{ marginTop: 16 }}>
          <strong>Human Assessment Mode.</strong>{" "}
          <span className="muted body-sm">
            {modeNote || "Generative AI unavailable — rule-based analysis and the full review workflow remain operational."}
          </span>
        </div>
      )}

      {/* Safety Override banner (Feature 2.5 / UX spec) */}
      {override && (
        <div className="safety-banner" style={{ marginTop: 16 }}>
          <span className="pill pill-danger" style={{ height: 24 }}>SAFETY OVERRIDE</span>
          <div className="col" style={{ gap: 8 }}>
            <span className="reason">{caseData.safety_override_reason}</span>
            <span className="body-sm">
              Dismiss is disabled for safety-critical flags. Escalate to a supervisor now — priority pinned to the top of the queue.
            </span>
          </div>
        </div>
      )}

      <div className="grid-2" style={{ marginTop: 24, alignItems: "start" }}>
        {/* LEFT — live transcript + input */}
        <div className="col" style={{ gap: 16 }}>
          <div className="card">
            <div className="row-between" style={{ marginBottom: 16 }}>
              <h4>Live transcript</h4>
              <span className="caption">
                {caseData.language_info?.primary?.language?.toUpperCase()}
                {caseData.language_info?.code_switching?.is_code_switched && " · code-switched"}
                {volume != null && ` · vol ${volume}`}
              </span>
            </div>

            <div className="transcript" style={{ maxHeight: 420, overflowY: "auto" }}>
              {lines.length === 0 && <p className="muted body-sm">Transcript appears here in real time.</p>}
              {lines.map((l, i) => (
                <div key={i} className={`msg ${l.speaker === "operator" ? "msg-operator" : "msg-caller"}`}>
                  {l.text}
                  <div className="msg-meta">
                    <span className="caption" style={{ color: l.speaker === "operator" ? "#d0d0d0" : undefined }}>
                      {l.speaker} · t+{Number(l.timestamp || 0).toFixed(1)}s
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="divider" />

            <div className="row" style={{ gap: 8 }}>
              <input
                className="input"
                placeholder={traumaMode ? "Type gently, or use the suggested prompt below…" : "Type a line…"}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && submitLineAsOperator(input)}
              />
              <button className="btn btn-primary" disabled={!input.trim()} onClick={() => submitLineAsOperator(input)}>
                Send
              </button>
            </div>

            <div className="row wrap" style={{ gap: 8, marginTop: 12 }}>
              {speech.supported ? (
                speech.listening ? (
                  <button className="btn btn-danger btn-sm" onClick={speech.stop}>● Stop mic</button>
                ) : (
                  <button className="btn btn-outline btn-sm" onClick={() => speech.start()}>Start mic (voice)</button>
                )
              ) : (
                <span className="pill pill-outline">Browser ASR unavailable — typed mode</span>
              )}

              <Segmented
                value={traumaMode ? "on" : "off"}
                onChange={async (v) => {
                  await api(`/api/v1/cases/${caseId}`, { method: "PATCH", body: { trauma_mode: v === "on" } });
                  setCaseData((p) => ({ ...p, trauma_mode: v === "on" }));
                }}
                options={[{ value: "off", label: "Standard" }, { value: "on", label: "Trauma-informed" }]}
              />
            </div>
          </div>

          {/* Trauma-informed prompt helper (Feature 2.13) */}
          <div className="card-soft">
            <div className="row-between" style={{ marginBottom: 10 }}>
              <strong className="body-sm">Next prompt</strong>
              <span className={`pill ${pausedLong ? "pill-ok" : "pill-outline"}`}>
                {pausedLong ? "caller paused — ready" : "waiting for a pause…"}
              </span>
            </div>
            <p className="body-sm muted" style={{ marginBottom: 10 }}>
              {traumaMode
                ? "Trauma-informed mode: “Why” questions are filtered out; pacing follows the caller’s pauses."
                : "Standard questioning."}
            </p>
            <div className="row wrap" style={{ gap: 8 }}>
              <button
                className="btn btn-soft btn-sm"
                disabled={traumaMode && !pausedLong}
                onClick={sendSuggested}
              >
                {QUESTIONS[qIndex % QUESTIONS.length]}
              </button>
              <button
                className="btn btn-outline btn-sm"
                onClick={() => submitLineAsOperator(REASSURANCE)}
              >
                Reassure caller
              </button>
            </div>
          </div>

          {/* Summary (Feature 1.9) with provenance label */}
          {summary && (
            <div className="card">
              <div className="row-between" style={{ marginBottom: 10 }}>
                <h4>Summary</h4>
                <span className={`pill ${summary.generated_by === "ai" ? "pill-ink" : "pill-outline"}`}>
                  {summary.label}
                </span>
              </div>
              <div className="col" style={{ gap: 10 }}>
                <div>
                  <p className="label muted">What the caller said</p>
                  <p className="body-sm">{summary.verbatim_summary?.user_statement || "—"}</p>
                </div>
                <div className="hairline-top" style={{ paddingTop: 10 }}>
                  <p className="label muted">AI inference (not a statement of fact)</p>
                  <p className="body-sm">
                    Distress level: <strong>{summary.ai_inference?.distress_level}</strong>
                    {summary.ai_inference?.risk_factors?.length > 0 && (
                      <> · risk factors: {summary.ai_inference.risk_factors.join(", ")}</>
                    )}
                  </p>
                  {summary.ai_inference?.recommended_pathways?.length > 0 && (
                    <p className="caption">Suggested pathways (human confirms): {summary.ai_inference.recommended_pathways.join(", ")}</p>
                  )}
                </div>
                {summary.fallback_text && (
                  <details>
                    <summary className="caption">Extractive fallback text</summary>
                    <pre className="body-sm" style={{ whiteSpace: "pre-wrap", marginTop: 6 }}>{summary.fallback_text}</pre>
                  </details>
                )}
              </div>
            </div>
          )}
        </div>

        {/* RIGHT — priority, profile, flags, uncertainty */}
        <div className="col" style={{ gap: 16 }}>
          <div className="card">
            <div className="row-between" style={{ marginBottom: 12 }}>
              <div>
                <p className="label muted">Review Priority Score</p>
                <p className="caption">Operational queue urgency — not a clinical measure (Feature 1.4)</p>
              </div>
              <span className="dial-value mono" style={{ color: override ? "var(--danger)" : undefined }}>
                {priority.toFixed(2)}
              </span>
            </div>
            <ScoreBar value={priority} danger={override} />
            <div className="row-between" style={{ marginTop: 14 }}>
              <span className="label muted">Flags · assessment confidence</span>
              <span className="label mono">{flagCount} · {Number(caseData.assessment_confidence || 0).toFixed(2)}</span>
            </div>
            {override && (
              <button
                className="btn btn-danger btn-lg"
                style={{ width: "100%", marginTop: 14 }}
                onClick={async () => {
                  try {
                    await api(`/api/v1/cases/${caseId}/review`, {
                      method: "POST",
                      body: { decision: "escalate", override_ai: false, notes: "Safety override — escalated from live console" },
                    });
                    push("Escalated to supervisor queue.");
                  } catch (err) {
                    push(err.message, "danger");
                  }
                }}
              >
                Escalate now
              </button>
            )}
          </div>

          <div className="card">
            <h4 style={{ marginBottom: 12 }}>Safety & wellbeing profile</h4>
            <ProfilePanel profile={caseData.victim_safety_profile} />
          </div>

          <UncertaintyPanel uncertainty={caseData.uncertainty} />

          <div className="card">
            <div className="row-between" style={{ marginBottom: 12 }}>
              <h4>AI indicators</h4>
              <span className="pill pill-outline">suggestions only</span>
            </div>
            <FlagsPanel
              caseId={caseId}
              flags={caseData.ai_flags}
              safetyOverride={override}
              onUpdate={loadCase}
              notify={push}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
