import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { listItems } from "../api.js";
import ItemCard from "../components/ItemCard.jsx";
import { CATEGORIES } from "../utils.js";

const TABS = [
  { value: "all", label: "All" },
  { value: "lost", label: "Lost" },
  { value: "found", label: "Found" },
];

export default function HomePage() {
  const location = useLocation();
  const notice = location.state?.notice;

  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("all");
  const [category, setCategory] = useState("");
  const [showReturned, setShowReturned] = useState(false);

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const filtersActive = query || status !== "all" || category || showReturned;

  // Re-run the search whenever a filter changes (waits 300ms while the person is typing).
  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      setLoading(true);
      setError("");
      try {
        const data = await listItems(
          { q: query.trim(), status, category, includeResolved: showReturned },
          controller.signal
        );
        setItems(data);
      } catch (err) {
        if (err.name !== "AbortError") setError(err.message);
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }, 300);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query, status, category, showReturned]);

  function clearFilters() {
    setQuery("");
    setStatus("all");
    setCategory("");
    setShowReturned(false);
  }

  return (
    <>
      {notice && (
        <p className="banner banner--ok" role="status">
          {notice}
        </p>
      )}

      <section className="hero">
        <h1>Lost something? Found something?</h1>
        <p>Post it here so the right person can find it. Or search to see if it is already posted.</p>
        <div className="hero__actions">
          <Link to="/report?type=lost" className="btn btn--lost">
            I lost something
          </Link>
          <Link to="/report?type=found" className="btn btn--found">
            I found something
          </Link>
        </div>
      </section>

      <section className="filters" aria-label="Search and filters">
        <label className="field field--grow">
          <span className="sr-only">Search</span>
          <input
            type="search"
            placeholder="Search by word, like “wallet”, “keys” or “library”"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </label>

        <div className="tabs" role="group" aria-label="Show">
          {TABS.map((t) => (
            <button
              key={t.value}
              type="button"
              className={status === t.value ? "is-active" : ""}
              aria-pressed={status === t.value}
              onClick={() => setStatus(t.value)}
            >
              {t.label}
            </button>
          ))}
        </div>

        <label className="field">
          <span className="sr-only">Category</span>
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">All categories</option>
            {CATEGORIES.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </label>

        <label className="check">
          <input
            type="checkbox"
            checked={showReturned}
            onChange={(e) => setShowReturned(e.target.checked)}
          />
          Show returned items
        </label>
      </section>

      {error && (
        <p className="banner banner--error" role="alert">
          {error} Is the backend running on port 8000?
        </p>
      )}

      <p className="count" aria-live="polite">
        {loading ? "Loading…" : `${items.length} ${items.length === 1 ? "post" : "posts"}`}
      </p>

      {!loading && !error && items.length === 0 ? (
        <div className="empty">
          {filtersActive ? (
            <>
              <h2>No posts match your search</h2>
              <p>Try fewer words, or remove a filter.</p>
              <button className="btn btn--ghost" onClick={clearFilters}>
                Clear search and filters
              </button>
            </>
          ) : (
            <>
              <h2>Nothing posted yet</h2>
              <p>Be the first to post a lost or found item.</p>
              <Link to="/report" className="btn">
                Report an item
              </Link>
            </>
          )}
        </div>
      ) : (
        <div className="grid">
          {items.map((item) => (
            <ItemCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </>
  );
}
