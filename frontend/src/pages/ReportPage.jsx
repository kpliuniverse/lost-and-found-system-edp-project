import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { createItem } from "../api.js";
import { CATEGORIES, todayISO } from "../utils.js";

export default function ReportPage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();

  const [form, setForm] = useState({
    status: params.get("type") === "found" ? "found" : "lost",
    title: "",
    category: CATEGORIES[0],
    description: "",
    location: "",
    event_date: todayISO(),
    contact_name: "",
    contact_info: "",
    pin: "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const isLost = form.status === "lost";

  function update(e) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  }

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const item = await createItem(form);
      navigate(`/items/${item.id}`, {
        state: { notice: "Your post is live. Keep your PIN safe: you need it to delete or close the post." },
      });
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  }

  return (
    <section className="narrow">
      <Link to="/" className="back">
        Back to all posts
      </Link>
      <h1>Report an item</h1>

      <form onSubmit={submit} className="form">
        <fieldset className="switch">
          <legend>What happened?</legend>
          <label className={isLost ? "is-active is-lost" : ""}>
            <input type="radio" name="status" value="lost" checked={isLost} onChange={update} />I lost something
          </label>
          <label className={!isLost ? "is-active is-found" : ""}>
            <input type="radio" name="status" value="found" checked={!isLost} onChange={update} />I found something
          </label>
        </fieldset>

        <label className="field">
          What is it?
          <input
            name="title"
            value={form.title}
            onChange={update}
            placeholder="Example: Black leather wallet"
            minLength={3}
            maxLength={120}
            required
          />
        </label>

        <label className="field">
          Category
          <select name="category" value={form.category} onChange={update}>
            {CATEGORIES.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </label>

        <label className="field">
          Details (color, brand, marks)
          <textarea
            name="description"
            value={form.description}
            onChange={update}
            rows={4}
            maxLength={2000}
            placeholder={
              isLost
                ? "Anything that helps someone recognize it."
                : "Describe it, but keep one detail secret so you can check the real owner."
            }
          />
        </label>

        <div className="row">
          <label className="field">
            Where was it {isLost ? "lost" : "found"}?
            <input name="location" value={form.location} onChange={update} minLength={2} maxLength={160} required />
          </label>
          <label className="field">
            Date
            <input type="date" name="event_date" value={form.event_date} max={todayISO()} onChange={update} required />
          </label>
        </div>

        <div className="row">
          <label className="field">
            Your name
            <input name="contact_name" value={form.contact_name} onChange={update} minLength={2} maxLength={80} required />
          </label>
          <label className="field">
            Email or phone
            <input name="contact_info" value={form.contact_info} onChange={update} minLength={3} maxLength={120} required />
          </label>
        </div>

        <label className="field">
          Choose a PIN (4 to 20 characters)
          <input
            name="pin"
            type="password"
            value={form.pin}
            onChange={update}
            minLength={4}
            maxLength={20}
            autoComplete="new-password"
            required
          />
          <small>You will need this PIN to delete or close your post. We cannot recover it.</small>
        </label>

        {error && (
          <p className="banner banner--error" role="alert">
            {error}
          </p>
        )}

        <button className="btn" disabled={saving}>
          {saving ? "Posting…" : "Post item"}
        </button>
      </form>
    </section>
  );
}
