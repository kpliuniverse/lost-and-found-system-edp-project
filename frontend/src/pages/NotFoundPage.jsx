import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <section className="empty">
      <h1>Page not found</h1>
      <p>This page does not exist. Maybe it was lost.</p>
      <Link to="/" className="btn">
        Go to the home page
      </Link>
    </section>
  );
}
