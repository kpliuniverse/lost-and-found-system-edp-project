import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { deleteItem, getItem, markReturned } from "../api.js";
import { formatDate, statusLabel } from "../utils.js";

export default function ItemPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const [item, setItem] = useState(null);
  const [loadError, setLoadError] = useState("");
  const [notice, setNotice] = useState(location.state?.notice || "");

  const [pin, setPin] = useState("");
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState("");
  const [confirmDelete, setConfirmDelete] = useState(false);

  useEffect(() => {
    getItem(id)
      .then(setItem)
      .catch((err) => setLoadError(err.message));
  }, [id]);

  async function handleReturned() {
    setBusy(true);
    setActionError("");
    try {
      setItem(await markReturned(id, pin));
      setNotice("Marked as returned. It is hidden from the main list now.");
      setPin("");
    } catch (err) {
      setActionError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete() {
    setBusy(true);
    setActionError("");
    try {
      await deleteItem(id, pin);
      navigate("/", { state: { notice: "Your post was deleted." } });
    } catch (err) {
      setActionError(err.message);
      setBusy(false);
    }
  }

  if (loadError) {
    return (
      <section className="empty">
        <h1>Post not found</h1>
        <p>{loadError}</p>
        <Link to="/" className="btn">
          Back to all posts
        </Link>
      </section>
    );
  }
  if (!item) return <p className="count">Loading…</p>;

  return (
    <section className="narrow">
      <Link to="/" className="back">
        Back to all posts
      </Link>

      {notice && (
        <p className="banner banner--ok" role="status">
          {notice}
        </p>
      )}

      <article className={`detail detail--${item.status}`}>
        <div className="tag__top">
          <span className={`chip chip--${item.status}`}>{statusLabel(item.status)}</span>
          {item.is_resolved && <span className="chip chip--returned">Returned</span>}
        </div>
        <h1>{item.title}</h1>

        <dl className="facts">
          <div>
            <dt>Category</dt>
            <dd>{item.category}</dd>
          </div>
          <div>
            <dt>Where</dt>
            <dd>{item.location}</dd>
          </div>
          <div>
            <dt>{item.status === "lost" ? "Lost on" : "Found on"}</dt>
            <dd>{formatDate(item.event_date)}</dd>
          </div>
        </dl>

        {item.description && <p className="detail__text">{item.description}</p>}

        <div className="contact">
          <h2>Contact {item.contact_name}</h2>
          <p>{item.contact_info}</p>
        </div>
      </article>

      <section className="manage">
        <h2>Is this your post?</h2>
        <p>Enter the PIN you chose when you posted.</p>
        <label className="field">
          <span className="sr-only">PIN</span>
          <input
            type="password"
            value={pin}
            onChange={(e) => setPin(e.target.value)}
            placeholder="Your PIN"
            autoComplete="off"
          />
        </label>

        {actionError && (
          <p className="banner banner--error" role="alert">
            {actionError}
          </p>
        )}

        <div className="manage__buttons">
          {!item.is_resolved && (
            <button className="btn btn--ghost" disabled={busy || !pin} onClick={handleReturned}>
              Mark as returned
            </button>
          )}
          {confirmDelete ? (
            <>
              <button className="btn btn--danger" disabled={busy || !pin} onClick={handleDelete}>
                Yes, delete for good
              </button>
              <button className="btn btn--ghost" onClick={() => setConfirmDelete(false)}>
                Keep post
              </button>
            </>
          ) : (
            <button className="btn btn--ghost" disabled={busy || !pin} onClick={() => setConfirmDelete(true)}>
              Delete post
            </button>
          )}
        </div>
      </section>
    </section>
  );
}
