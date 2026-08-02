import { Shield } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t border-[#1E2638] bg-[#070A0F] py-12 text-xs text-slate-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Brand & Tagline */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 p-0.5">
              <div className="w-full h-full bg-[#070A0F] rounded-[6px] flex items-center justify-center">
                <Shield className="w-4 h-4 text-cyan-400" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-white text-sm tracking-tight">
                Hook<span className="text-cyan-400">Check</span>
              </span>
              <span className="text-[11px] text-slate-500">
                Open-source, privacy-first threat detection
              </span>
            </div>
          </div>

          {/* Single Page Smooth Scroll Navigation Links */}
          <div className="flex flex-wrap items-center justify-center gap-6 text-slate-300 font-medium">
            <a href="#how" className="hover:text-cyan-400 transition-colors">
              How It Works
            </a>
            <a href="#features" className="hover:text-cyan-400 transition-colors">
              Features
            </a>
            <a href="#sample-report" className="hover:text-cyan-400 transition-colors">
              Sample Report
            </a>
            <a href="#privacy" className="hover:text-cyan-400 transition-colors">
              Privacy Architecture
            </a>
            <a href="#disclaimer" className="hover:text-cyan-400 transition-colors">
              Disclaimer
            </a>
            <a href="#faq" className="hover:text-cyan-400 transition-colors">
              FAQ
            </a>
            <a
              href="https://github.com/Mosope-ade/phishshield-ai"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-slate-300 hover:text-white transition-colors"
            >
              <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
              </svg>
              <span>GitHub</span>
            </a>
          </div>

          {/* Copyright & Disclaimer note */}
          <div className="text-center md:text-right text-[11px] text-slate-500">
            <p>&copy; {new Date().getFullYear()} HookCheck. All rights reserved.</p>
            <p className="mt-0.5">Advisory decision-support platform.</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
