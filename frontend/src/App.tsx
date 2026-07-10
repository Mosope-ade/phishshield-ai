/**
 * App.tsx — root router.
 * PLAN.md §6: four pages — Landing, Report/:id, Learn, Privacy, Disclaimer.
 * Topbar is rendered on all pages.
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Topbar } from './components/Topbar';
import { Landing } from './pages/Landing';
import { Report } from './pages/Report';
import { Learn } from './pages/Learn';
import { Privacy } from './pages/Privacy';
import { Disclaimer } from './pages/Disclaimer';

export default function App() {
  return (
    <BrowserRouter>
      <a href="#main-content" className="sr-only" style={{ position: 'absolute', left: '-9999px' }}>
        Skip to main content
      </a>
      <Topbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/report/:id" element={<Report />} />
        <Route path="/learn" element={<Learn />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/disclaimer" element={<Disclaimer />} />
        <Route path="*" element={
          <main style={{ padding: '48px 16px', textAlign: 'center' }}>
            <h1 style={{ fontFamily: 'Space Grotesk, sans-serif', color: 'var(--accent)', marginBottom: '12px' }}>
              404 — Page Not Found
            </h1>
            <p style={{ color: 'var(--text-2)' }}>
              <a href="/">← Back to PhishShield AI</a>
            </p>
          </main>
        } />
      </Routes>
    </BrowserRouter>
  );
}
