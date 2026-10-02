import { useState } from "react";
import { ContentPage } from "../components/SiteChrome";
import { useSeo } from "../lib/seo";

export default function Contact() {
  useSeo({
    title: "Contact Us — Sahaara AI",
    description:
      "Get in touch with the Sahaara AI team for helpline deployments, partnerships, research collaboration or support.",
    path: "/contact",
  });

  const [form, setForm] = useState({ name: "", email: "", topic: "General", message: "" });
  const [sent, setSent] = useState(false);

  const submit = (e) => {
    e.preventDefault();
    // Opens the visitor's mail client — no data is stored by this page.
    const subject = encodeURIComponent(`[${form.topic}] Sahaara AI enquiry from ${form.name}`);
    const body = encodeURIComponent(`${form.message}\n\n— ${form.name} (${form.email})`);
    window.location.href = `mailto:hello@sahaara.ai?subject=${subject}&body=${body}`;
    setSent(true);
  };

  return (
    <ContentPage>
      <p className="eyebrow">Contact us</p>
      <h1>Let’s talk helplines.</h1>
      <p className="body-lg muted" style={{ marginTop: 16, maxWidth: 640 }}>
        Deployments, partnerships, research collaboration or support — tell us what you’re
        working on and we’ll respond within two working days.
      </p>

      <div className="grid-2" style={{ marginTop: 40, alignItems: "start" }}>
        <form className="card-soft col" style={{ gap: 16 }} onSubmit={submit}>
          <label className="field">
            <span>Name</span>
            <input className="input" required value={form.name}
                   onChange={(e) => setForm({ ...form, name: e.target.value })}
                   placeholder="Your name" />
          </label>
          <label className="field">
            <span>Email</span>
            <input className="input" type="email" required value={form.email}
                   onChange={(e) => setForm({ ...form, email: e.target.value })}
                   placeholder="you@organisation.org" />
          </label>
          <label className="field">
            <span>Topic</span>
            <select className="input" value={form.topic}
                    onChange={(e) => setForm({ ...form, topic: e.target.value })}>
              <option>General</option>
              <option>Deployment</option>
              <option>Partnership</option>
              <option>Research collaboration</option>
              <option>Support</option>
            </select>
          </label>
          <label className="field">
            <span>Message</span>
            <textarea className="input" rows={5} required value={form.message}
                      onChange={(e) => setForm({ ...form, message: e.target.value })}
                      placeholder="How can we help?" />
          </label>
          <button className="btn btn-primary btn-lg" type="submit">Send message</button>
          {sent && (
            <p className="body-sm" style={{ color: "var(--ok)" }}>
              Your mail client should have opened with the message pre-filled. If nothing
              happened, email <strong>hello@sahaara.ai</strong> directly.
            </p>
          )}
        </form>

        <div className="col" style={{ gap: 16 }}>
          <div className="card">
            <p className="label muted">Email</p>
            <p className="title" style={{ marginTop: 6 }}>hello@sahaara.ai</p>
            <p className="caption" style={{ marginTop: 6 }}>
              Support: support@sahaara.ai · Privacy: privacy@sahaara.ai · Legal: legal@sahaara.ai
            </p>
          </div>
          <div className="card">
            <p className="label muted">Helpline emergencies</p>
            <p className="body-sm" style={{ marginTop: 6 }}>
              Sahaara AI is not an emergency service. If there is immediate danger to life,
              contact local emergency services now.
            </p>
          </div>
          <div className="card">
            <p className="label muted">Office</p>
            <p className="body-sm" style={{ marginTop: 6 }}>
              Sahaara AI · Bengaluru, Karnataka, India<br />
              Mon–Fri, 09:30–18:30 IST
            </p>
          </div>
        </div>
      </div>
    </ContentPage>
  );
}
