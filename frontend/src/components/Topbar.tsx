/**
 * components/Topbar.tsx
 * Slim top bar per UI.md §5.1.
 * Shield-check icon + "PhishShield AI" wordmark, "Learn" link at ≥600px.
 */

import { Link } from 'react-router-dom';

export function Topbar() {
  return (
    <header className="topbar" role="banner">
      <Link to="/" className="topbar__brand" aria-label="PhishShield AI home">
        {/* Shield-check icon (UI.md §5.1: ti-shield-check equivalent) */}
        <span className="topbar__icon" aria-hidden="true">🛡</span>
        <span className="topbar__wordmark">
          Phish<span>Shield</span> AI
        </span>
      </Link>

      {/* Nav — visible at ≥600px only (UI.md §5.1) */}
      <nav className="topbar__nav" aria-label="Site navigation">
        <Link to="/learn">Learn</Link>
      </nav>
    </header>
  );
}
