/**
 * components/Topbar.tsx
 * Slim top bar per UI.md §5.1.
 * Shield-check icon + "HookCheck" wordmark, "Learn" link at ≥600px.
 */

import { Link } from 'react-router-dom';

export function Topbar() {
  return (
    <header className="topbar" role="banner">
      <Link to="/" className="topbar__brand" aria-label="HookCheck home">
        <span className="topbar__mark" aria-hidden="true">H</span>
        <span className="topbar__wordmark">
          Hook<span>Check</span>
        </span>
      </Link>

      <nav className="topbar__nav" aria-label="Site navigation">
        <Link to="/learn">How It Works</Link>
        <Link to="/privacy">Privacy</Link>
      </nav>
    </header>
  );
}
