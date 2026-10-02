import { Link } from "react-router-dom";
import { ContentPage } from "../components/SiteChrome";
import { useSeo } from "../lib/seo";

export default function About() {
  useSeo({
    title: "About Sahaara AI — Mission, Design Principles & Research",
    description:
      "Why Sahaara AI exists: a decision-support platform for helplines built around human judgement, explainable indicators, multilingual coverage for India, and open evaluation research.",
    path: "/about",
  });

  return (
    <ContentPage>
      <p className="eyebrow">About us</p>
      <h1>Machines that notice. People who decide.</h1>
      <p className="body-lg muted" style={{ marginTop: 16 }}>
        Sahaara AI began as a distress-detection prototype for helpline operators and grew
        into a research platform for AI-assisted victim safety assessment.
      </p>

      <h2 style={{ marginTop: 48 }}>Why we built it</h2>
      <p style={{ marginTop: 12 }}>
        Helpline operators hold hundreds of conversations a week, often in a language that is
        not their own, often under time pressure, and always with incomplete information.
        The moments that matter most — a whispered threat, a mid-sentence language switch, a
        caller who suddenly cannot speak freely — are exactly the moments easiest to miss.
        Sahaara exists to put a second, tireless listener in the room: one that surfaces what
        was said, attaches the evidence, and queues it for a trained human to judge.
      </p>
      <p style={{ marginTop: 12 }}>
        We deliberately did not build an autonomous system. In domains involving trauma,
        safety and rights, an AI that acts on its own is a liability. An AI that explains
        itself is a tool.
      </p>

      <h2 style={{ marginTop: 48 }}>Design principles</h2>
      <div className="col" style={{ gap: 12, marginTop: 16 }}>
        {[
          ["AI as support", "Every flag is a suggestion with evidence, timestamp, confidence and source. Escalation, dismissal, referral and closure are human actions."],
          ["No diagnosis", "The system identifies observable indicators. It never labels a condition and never claims clinical validity."],
          ["Two scores, kept apart", "Review Priority (how urgently to look) is never conflated with the Victim Safety Profile (what the person may need)."],
          ["Safety overrides averages", "Explicit safety rules can force top priority and pin a case to the top of the queue, regardless of the score."],
          ["Graceful failure", "When AI providers fail, Human Assessment Mode keeps transcripts, cases and review fully operational."],
          ["Privacy by default", "Consent first, no raw-audio retention, anonymisation on closure, role-scoped access and a full audit trail."],
        ].map(([title, body]) => (
          <div key={title} className="card" style={{ padding: 20 }}>
            <strong>{title}</strong>
            <p className="body-sm muted" style={{ marginTop: 6 }}>{body}</p>
          </div>
        ))}
      </div>

      <h2 style={{ marginTop: 48 }}>Research &amp; evaluation</h2>
      <p style={{ marginTop: 12 }}>
        Sahaara doubles as an evaluation environment. Every release ships with scripted
        multilingual demonstrations, evaluation metrics from sensitivity and specificity to
        AUROC and calibration, fairness reporting across languages, and human-AI agreement
        tracking — so we can measure whether AI actually improves the human workflow rather
        than merely scoring well in isolation. Dedicated datasets and multimodal benchmarks
        are planned work, developed only with informed consent and appropriate anonymisation.
      </p>

      <h2 style={{ marginTop: 48 }}>Honest limitations</h2>
      <p style={{ marginTop: 12 }}>
        The rule engine is not a validated clinical model. Speech features are observable
        proxies with alternative explanations always recorded. Priority scores are explainable
        heuristics, not psychometric instruments. Language and dialect accuracy vary, and
        code-switching remains an active research problem. We publish these limits because a
        decision-support tool that overstates its certainty is more dangerous than none at all.
      </p>

      <div className="card-soft" style={{ marginTop: 40 }}>
        <p className="body-sm">
          Questions, partnerships or research collaboration?{" "}
          <Link to="/contact" style={{ fontWeight: 600 }}>Contact us →</Link>
        </p>
      </div>
    </ContentPage>
  );
}
