import { Link } from "react-router-dom";
import { SiteFooter, SiteHeader } from "../components/SiteChrome";
import { useJsonLd, useSeo } from "../lib/seo";

/* Copy mirrored from docs/seo-copy.md (988 words — SEO source of truth). */

const FAQS = [
  {
    q: "What is Sahaara AI?",
    a: "Sahaara AI is a multilingual, real-time decision-support platform for helpline operators. It detects observable distress and safety indicators during live voice or text conversations, explains every flag with evidence, and manages the case that follows — review, referral and follow-up. It never diagnoses and never acts autonomously.",
  },
  {
    q: "Does Sahaara AI make decisions on its own?",
    a: "No. Every AI output is a suggestion. Escalate, confirm, modify, dismiss and referral actions are performed by trained humans and recorded in an audit trail. This human-in-the-loop requirement is enforced in the interface: safety-critical flags cannot be dismissed while a safety override is active.",
  },
  {
    q: "Which languages are supported?",
    a: "English, Hindi and Marathi ship as core languages, with detection confidence, original-language transcripts and optional English interpretation. Code-switched conversations are detected segment-by-segment so a mid-sentence language change is never mistaken for a pause. Additional Indian languages are recognised at script level as research expands.",
  },
  {
    q: "What happens if the AI service goes down?",
    a: "The system enters Human Assessment Mode. A deterministic rule engine keeps producing indicators, and transcripts, case creation, review, notes and referral workflows remain fully operational. A visible banner tells the operator exactly what changed — the tool never becomes unusable.",
  },
  {
    q: "What is the Safety Override?",
    a: "An explicit rules layer that can override the weighted Review Priority Score. If the conversation indicates immediate physical danger, self-harm risk, possible coercion or an alarming voice-volume change, the case is pinned to the top of the queue and the interface switches to an escalation-first state. A critical signal is never hidden by an average.",
  },
  {
    q: "Is Sahaara AI a diagnostic or clinical tool?",
    a: "No. It identifies observable indicators and prioritises human review. It does not diagnose conditions, does not validate clinical instruments, and clearly labels its outputs as decision support. The Review Priority Score is an operational queue metric, not a psychological measurement.",
  },
  {
    q: "How is caller privacy protected?",
    a: "Consent is captured before processing, raw audio is not retained by default, and closing a case anonymises names, phone numbers and locations. Role-based access limits who can see sensitive records, every significant action is audited, and a Safe Exit control wipes local storage and cached data for callers using a potentially unsafe device.",
  },
  {
    q: "Can it handle voice calls as well as chat?",
    a: "Yes. Sessions support live voice capture with speech-to-text, typed conversations and scripted demonstrations. Observable speech features such as volume changes are treated as supporting evidence with alternative explanations recorded — never as a standalone conclusion.",
  },
];

export default function Landing() {
  useSeo({
    title: "Sahaara AI — AI-Assisted Distress Assessment & Helpline Case Management",
    description:
      "Multilingual, real-time decision support for helplines: explainable distress indicators, victim safety profiling, safety-override triage and human-in-the-loop case management in English, Hindi and Marathi.",
    path: "/",
  });

  useJsonLd({
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: FAQS.map((f) => ({
      "@type": "Question",
      name: f.q,
      acceptedAnswer: { "@type": "Answer", text: f.a },
    })),
  });

  return (
    <div className="site-page">
      <SiteHeader />

      <main>
        {/* ── Hero ── */}
        <section className="hero">
          <p className="eyebrow">Decision support for helplines</p>
          <h1>
            AI that notices distress.<br />
            Humans who decide what happens next.
          </h1>
          <p className="body-lg hero-sub">
            Sahaara AI is a multilingual, real-time distress-assessment and case-management
            platform for helpline operators — explainable indicators, safety-first triage,
            and mandatory human review.
          </p>
          <div className="row wrap" style={{ gap: 12, justifyContent: "center" }}>
            <Link to="/login" className="btn btn-primary btn-lg">Open the console</Link>
            <Link to="/about" className="btn btn-outline btn-lg">How it works</Link>
          </div>
          <div className="row wrap" style={{ gap: 8, justifyContent: "center", marginTop: 24 }}>
            <span className="pill">English · हिन्दी · मराठी</span>
            <span className="pill">Explainable flags</span>
            <span className="pill">Human-in-the-loop</span>
            <span className="pill">Graceful AI fallback</span>
          </div>
        </section>

        {/* ── Stats strip (dark-green band, DESIGN.md rhythm) ── */}
        <section className="band-dark">
          <div className="stats-strip">
            <div className="stat"><span className="stat-n">8</span><span className="stat-l">safety profile dimensions</span></div>
            <div className="stat"><span className="stat-n">4</span><span className="stat-l">reviewer roles with scoped access</span></div>
            <div className="stat"><span className="stat-n">100%</span><span className="stat-l">AI flags carry evidence &amp; confidence</span></div>
            <div className="stat"><span className="stat-n">0</span><span className="stat-l">autonomous AI decisions</span></div>
          </div>
        </section>

        {/* ── SEO article (white content band) ── */}
        <section className="band-white">
        <article className="article">
          <h2>Sahaara AI: AI-assisted distress assessment and case management for helplines</h2>

          <p>
            Every day, helpline operators listen to people on the worst day of their lives. A
            caller may speak softly, switch between languages, pause mid-sentence, or describe
            a threat so quietly that its seriousness is easy to miss. Sahaara AI is a
            decision-support platform built for exactly that moment. It listens alongside the
            operator, surfaces observable distress and safety indicators in real time, and
            organises the work that follows — review, referral, follow-up — while leaving
            every consequential decision in human hands.
          </p>

          <h3>Decision support, not diagnosis</h3>
          <p>
            Sahaara AI identifies indicators, never disorders. Its purpose is to help a trained
            reviewer notice what was said, how urgent it is, and what deserves attention first.
            The system never concludes that a caller “has” a condition, never issues a clinical
            label, and never acts on its own: escalation, referral, dismissal and closure are
            always human actions recorded in an audit trail. This human-in-the-loop design is
            not a fallback philosophy — it is enforced in the product. AI flags arrive as
            suggestions with the supporting transcript excerpt, timestamp, confidence and
            source model attached, so a reviewer can see exactly why something was flagged
            before confirming, modifying, escalating or dismissing it.
          </p>

          <h3>Real-time, explainable analysis</h3>
          <p>
            When a session begins — by voice or typed text — audio and messages stream through
            a live pipeline. Language is detected first, then the conversation is scanned for
            observable indicators: expressions of fear or hopelessness, self-harm concerns,
            immediate-danger language, trauma narratives, and signals that a caller may not be
            speaking freely. Each detection becomes an explainable flag linked to its evidence.
            Nothing appears on screen without a reason attached to it, because in a high-stakes
            environment an unexplained alert is worse than no alert at all.
          </p>
          <p>
            If generative AI is unavailable or a provider fails, Sahaara does not go dark. The
            deterministic rule engine, transcript display, case creation and full review
            workflow continue to operate in Human Assessment Mode, with a visible banner telling
            the operator exactly what changed. Graceful degradation is a safety requirement, not
            a convenience.
          </p>

          <h3>Two scores that are never confused</h3>
          <p>
            Most triage tools collapse everything into a single number. Sahaara deliberately
            does not. The Review Priority Score answers one operational question — how urgently
            should a human look at this case — and is built from weighted linguistic, contextual,
            conversation and speech components. The Victim Safety &amp; Wellbeing Profile answers
            a different question — what might this person need — across eight dimensions
            including psychological distress, trauma indicators, immediate danger, self-harm
            concern, coercion, and social, medical and legal vulnerability. Keeping the two
            apart stops an operational queue metric from being misread as a psychological
            measurement.
          </p>
          <p>
            Crucially, explicit safety rules can override the score entirely. If the transcript
            indicates an immediate physical threat, a self-harm concern, possible coercion, or
            an alarming change in voice volume, the case is pinned to the top of the queue,
            safety-critical flags cannot be dismissed, and the interface itself changes to
            demand attention. A critical signal must never be hidden by an average.
          </p>

          <h3>Built for Indian helplines</h3>
          <p>
            India’s helplines operate across languages, often within a single conversation.
            Sahaara ships with English, Hindi and Marathi support — detection, confidence
            scoring, original-language transcripts and optional English glosses — and detects
            mixed-language speech, tagging switch points rather than misreading them as
            silence. Additional Indian languages are recognised at script level as the research
            programme expands coverage. Code-switched speech like “Mala khup bhiti vatate…
            they are threatening me” is treated as one continuous account, preserving the
            caller’s own words throughout.
          </p>

          <h3>Trauma-informed by default</h3>
          <p>
            The interface can operate in a trauma-informed mode that asks fewer questions,
            avoids “why” prompts that can sound like blame, follows the caller’s pauses instead
            of rushing them, and puts reassurance one tap away. For victims using a potentially
            unsafe device, a discreet Safe Exit — double-press Escape — wipes local storage,
            clipboard and cached data and leaves to a neutral page.
          </p>

          <h3>From conversation to support pathway</h3>
          <p>
            Analysis flows into full case management: consent capture, status lifecycle, notes,
            longitudinal follow-ups, and referral pathways spanning counselling, medical aid,
            legal aid, protection, shelter and welfare. AI may suggest a pathway; only a
            confirmed human creates or confirms it. Summaries separate what the caller said from
            what the system inferred, and always carry a provenance label — “Generated by AI
            (Confidence: x)” or “Extracted Fallback” — so no one is ever unsure who wrote a
            sentence.
          </p>

          <h3>Security, privacy and accountability</h3>
          <p>
            Consent gates every session, raw audio is discarded after processing by default, and
            closing a case scrubs names, phone numbers and locations from the record. Access
            runs through role-based permissions — administrator, supervisor, counsellor and
            operator each see only what their role requires — while login, transcript access,
            AI analysis, modifications, escalations, referrals, exports and deletions are written
            to a durable audit log. Sensitive mental-health and potentially criminal information
            should never travel through a tool that cannot account for who looked at it and when.
          </p>

          <h3>A research foundation</h3>
          <p>
            Sahaara doubles as a research environment for evaluating AI-assisted victim safety
            assessment: evaluation metrics from sensitivity and specificity to AUROC and
            calibration, fairness reporting across languages, human-AI agreement tracking, and a
            monitoring layer designed to surface model drift and subgroup disparities before
            they matter. Synthetic, scripted demonstrations in multiple languages make training
            and evaluation repeatable without exposing a single real caller to risk.
          </p>

          <h3>Getting started</h3>
          <p>
            Sahaara AI runs anywhere a helpline already works: a FastAPI backend with SQLite for
            evaluation or PostgreSQL for production, and a browser-based console that needs
            nothing beyond a modern device and a connection. Sign in with a role, open a session
            with consent, and the queue does the rest — safety-override cases first, everything
            else ordered by review priority. Operators who have never used an AI tool before
            will find the interface familiar: a transcript, a set of flagged suggestions, and
            buttons that make clear the final decision is theirs to make.
          </p>
        </article>
        </section>

        {/* ── FAQ ── */}
        <section className="faq" id="faq">
          <h2>Frequently asked questions.</h2>
          <p className="body-lg muted" style={{ marginTop: 8, marginBottom: 32 }}>
            The short version of what Sahaara AI is, and what it refuses to do.
          </p>
          <div className="faq-list">
            {FAQS.map((f) => (
              <details key={f.q} className="faq-row">
                <summary>{f.q}</summary>
                <p className="body-sm" style={{ marginTop: 10, color: "var(--ink-soft)" }}>{f.a}</p>
              </details>
            ))}
          </div>
        </section>

        {/* ── CTA ── */}
        <section className="cta-band">
          <h2>See the queue in action.</h2>
          <p className="body-lg" style={{ color: "rgba(255,255,255,0.72)", marginTop: 12 }}>
            Four demo accounts, seven scripted multilingual scenarios. No real caller required.
          </p>
          <Link to="/login" className="btn btn-primary btn-lg" style={{ marginTop: 24 }}>
            Get started
          </Link>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
