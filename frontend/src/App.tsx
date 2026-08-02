import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Landing } from './pages/Landing';
import { Report } from './pages/Report';

export default function App() {
  return (
    <BrowserRouter>
      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:p-4 focus:bg-cyan-500 focus:text-black">
        Skip to main content
      </a>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/report/:id" element={<Report />} />
        {/* Support direct navigational links by redirecting to home page sections */}
        <Route path="/learn" element={<Navigate to="/#how" replace />} />
        <Route path="/privacy" element={<Navigate to="/" replace />} />
        <Route path="/disclaimer" element={<Navigate to="/" replace />} />
        <Route
          path="*"
          element={
            <div className="min-h-screen bg-[#0B0E14] text-white flex flex-col items-center justify-center p-6 text-center">
              <h1 className="text-4xl font-extrabold text-cyan-400 mb-2">404 — Page Not Found</h1>
              <p className="text-slate-400 text-sm mb-6">The page you are looking for does not exist.</p>
              <a
                href="/"
                className="px-5 py-2.5 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-500 rounded-xl transition-all"
              >
                ← Back to HookCheck Home
              </a>
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
