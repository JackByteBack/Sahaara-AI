import { ContentPage } from "../components/SiteChrome";
import { useSeo } from "../lib/seo";

export default function Terms() {
  useSeo({
    title: "Terms & Conditions — Sahaara AI",
    description:
      "Terms of use for Sahaara AI: decision-support scope, no-diagnosis limitation, human-in-the-loop responsibilities, acceptable use, availability and liability.",
    path: "/terms",
  });

  return (
    <ContentPage>
      <p className="eyebrow">Legal</p>
      <h1>Terms &amp; Conditions.</h1>
      <p className="caption" style={{ marginTop: 12 }}>Last updated: 2 October 2026</p>

      <div className="col" style={{ gap: 8, marginTop: 32 }}>
        <section>
          <h3>1. What Sahaara AI is</h3>
          <p style={{ marginTop: 8 }}>
            Sahaara AI is a <strong>decision-support</strong> platform for trained helpline
            personnel. It surfaces observable indicators, prioritises human review, and manages
            case workflow. It is not a medical, psychological, legal or emergency service.
          </p>
        </section>

        <section>
          <h3>2. No diagnosis, no autonomous action</h3>
          <p style={{ marginTop: 8 }}>
            The system does not diagnose conditions and does not make decisions on its own.
            Scores and flags are decision support: they are explainable heuristics, not
            validated clinical or psychometric instruments. The reviewing human is responsible
            for every final decision — confirm, modify, escalate, dismiss, refer or close.
          </p>
        </section>

        <section>
          <h3>3. Not for emergencies</h3>
          <p style={{ marginTop: 8 }}>
            Sahaara is not a substitute for emergency services. If there is immediate danger to
            life, contact local emergency services first.
          </p>
        </section>

        <section>
          <h3>4. Accounts &amp; roles</h3>
          <p style={{ marginTop: 8 }}>
            You are responsible for activity under your account and for maintaining the
            confidentiality of your credentials. Access is scoped by role; attempting to access
            records outside your role, or sharing credentials, is a breach of these terms and
            may be recorded in the audit log.
          </p>
        </section>

        <section>
          <h3>5. Acceptable use</h3>
          <p style={{ marginTop: 8 }}>
            You agree not to: process a conversation without appropriate consent; use the
            platform for unlawful profiling or discrimination; attempt to circumvent safety
            overrides, audit logging or access controls; reverse-engineer or resell the
            service without written permission; or enter fabricated data into production
            records (use demonstration scenarios for training instead).
          </p>
        </section>

        <section>
          <h3>6. Data responsibilities</h3>
          <p style={{ marginTop: 8 }}>
            Operators must obtain consent before processing, must not share data outside the
            secured Sahaara environment, and must anonymise or close cases per organisational
            policy. Our handling of that data is described in the{" "}
            <a href="/privacy" style={{ fontWeight: 600 }}>Privacy Policy</a>.
          </p>
        </section>

        <section>
          <h3>7. Availability</h3>
          <p style={{ marginTop: 8 }}>
            Generative AI features depend on third-party providers and may be unavailable; in
            that event the service falls back to Human Assessment Mode with rule-based
            analysis. We do not guarantee uninterrupted availability. “As is” to the fullest
            extent permitted by law.
          </p>
        </section>

        <section>
          <h3>8. Liability</h3>
          <p style={{ marginTop: 8 }}>
            To the fullest extent permitted by law, Sahaara AI is not liable for indirect,
            incidental or consequential damages arising from reliance on AI suggestions rather
            than human judgement. Nothing in these terms limits liability that cannot be
            limited by applicable law.
          </p>
        </section>

        <section>
          <h3>9. Changes &amp; contact</h3>
          <p style={{ marginTop: 8 }}>
            We may update these terms; the “last updated” date reflects the current version.
            Questions: <strong>legal@sahaara.ai</strong> or our{" "}
            <a href="/contact" style={{ fontWeight: 600 }}>contact page</a>.
          </p>
        </section>
      </div>
    </ContentPage>
  );
}
