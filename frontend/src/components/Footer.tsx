/**
 * components/Footer.tsx
 * Simple footer per UI.md §5.10.
 * Text links only: Learn · Privacy · Disclaimer · GitHub.
 */

import { Link } from "react-router-dom";

export function Footer() {
  return (
    <footer className="footer" role="contentinfo">
      <Link to="/learn">Learn</Link>
      <Link to="/privacy">Privacy</Link>
      <Link to="/disclaimer">Disclaimer</Link>
      <a
        href="https://github.com/Mosope-ade/hookcheck.git"
        target="_blank"
        rel="noopener noreferrer"
      >
        GitHub
      </a>
    </footer>
  );
}
