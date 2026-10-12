import { Link, NavLink, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage.jsx";
import ReportPage from "./pages/ReportPage.jsx";
import ItemPage from "./pages/ItemPage.jsx";
import NotFoundPage from "./pages/NotFoundPage.jsx";

export default function App() {
  return (
    <>
      <header className="site-header">
        <div className="wrap site-header__inner">
          <Link to="/" className="brand">
            Lost &amp; Found
          </Link>
          <nav className="nav" aria-label="Main">
            <NavLink to="/" end>
              Browse
            </NavLink>
            <Link to="/report" className="btn btn--small">
              Report an item
            </Link>
          </nav>
        </div>
      </header>

      <main className="wrap">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/report" element={<ReportPage />} />
          <Route path="/items/:id" element={<ItemPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>

      <footer className="wrap site-footer">
        Be kind and stay safe: meet in a public place when you return an item.
      </footer>
    </>
  );
}
