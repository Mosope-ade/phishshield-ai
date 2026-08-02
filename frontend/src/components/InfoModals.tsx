import { motion, AnimatePresence } from 'framer-motion';
import { X, ShieldCheck, Lock, FileText, BookOpen, Cpu, Database } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'learn' | 'privacy' | 'disclaimer' | null;
}

export function InfoModals({ isOpen, onClose, type }: ModalProps) {
  if (!isOpen || !type) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
        {/* Backdrop Overlay */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-black/80 backdrop-blur-md"
        />

        {/* Modal Container */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.25 }}
          className="relative z-10 w-full max-w-3xl glass-card rounded-3xl border border-[#1E2638] overflow-hidden shadow-2xl my-8 max-h-[85vh] flex flex-col"
        >
          {/* Modal Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-[#1E2638] bg-[#0E131F]">
            <div className="flex items-center gap-2.5">
              {type === 'learn' && <BookOpen className="w-5 h-5 text-cyan-400" />}
              {type === 'privacy' && <Lock className="w-5 h-5 text-emerald-400" />}
              {type === 'disclaimer' && <FileText className="w-5 h-5 text-amber-400" />}
              <h2 className="text-base sm:text-lg font-bold text-white">
                {type === 'learn' && 'How Detection Works (Technical Guide)'}
                {type === 'privacy' && 'Privacy & Hashing Policy'}
                {type === 'disclaimer' && 'Legal Disclaimer & Use Limits'}
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#1E2638] transition-colors"
              aria-label="Close dialog"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Modal Content Body */}
          <div className="p-6 sm:p-8 overflow-y-auto space-y-6 text-xs sm:text-sm text-slate-300 leading-relaxed">
            {type === 'learn' && (
              <>
                <div className="p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-300">
                  <p className="font-semibold text-white mb-1">Three Independent Evidence Layers</p>
                  <p className="text-xs text-slate-300">
                    HookCheck enforces a strict rule: no single detection engine can silently override another. All three layers report findings independently.
                  </p>
                </div>

                <div className="space-y-4">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-cyan-400" />
                    Layer 1: Deterministic Heuristics Engine
                  </h3>
                  <p className="text-slate-400">
                    Runs locally in Python with zero network calls. Evaluates typosquatting Levenshtein edit distance against 600 top domains, Punycode IDN homoglyphs (e.g. non-Latin character lookalikes), subdomain brand impersonation, high-risk TLDs, and path trigger keywords.
                  </p>

                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-cyan-400" />
                    Layer 2: AI Semantic Reasoning (LLM)
                  </h3>
                  <p className="text-slate-400">
                    Invokes Large Language Models (Gemini, OpenAI, Anthropic) via direct REST calls. Receives prompt-isolated content blocks and heuristic context to detect artificial urgency, fear tactics, brand tone mismatches, and credential harvesting intent. Enforces Pydantic JSON schemas.
                  </p>

                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Database className="w-4 h-4 text-cyan-400" />
                    Layer 3: VirusTotal Threat Intelligence
                  </h3>
                  <p className="text-slate-400">
                    Queries VirusTotal Public API v3 to cross-reference target URLs and file hashes against 70+ global antivirus databases and web reputational feeds.
                  </p>
                </div>
              </>
            )}

            {type === 'privacy' && (
              <>
                <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">
                  <p className="font-semibold text-white mb-1">Zero Raw Input Data Storage</p>
                  <p className="text-xs text-slate-300">
                    Your raw text messages, uploaded images, and personal identity are NEVER stored in our database.
                  </p>
                </div>

                <div className="space-y-3">
                  <h3 className="text-sm font-bold text-white">How Cryptographic Caching Works</h3>
                  <p className="text-slate-400">
                    When you submit content, HookCheck computes a SHA-256 cryptographic hash of the normalized input string or file buffer. We query Supabase PostgreSQL using this hash digest.
                  </p>
                  <p className="text-slate-400">
                    If the hash exists, cached results return instantly. If not, the backend generates the report and stores ONLY:
                  </p>
                  <ul className="list-disc pl-5 text-slate-400 space-y-1">
                    <li>Random 12-character slug ID (e.g. `onudqvgzx7yv`)</li>
                    <li>SHA-256 hex string (`input_hash`)</li>
                    <li>Input category (`text`, `url`, `image`, `qr`)</li>
                    <li>Final generated JSON report payload</li>
                    <li>Timestamp (`created_at`)</li>
                  </ul>
                </div>
              </>
            )}

            {type === 'disclaimer' && (
              <>
                <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300">
                  <p className="font-semibold text-white mb-1">Decision-Support Tool Boundaries</p>
                  <p className="text-xs text-slate-300">
                    HookCheck is designed as an advisory decision-support assistant, not an absolute guarantee or security firewall.
                  </p>
                </div>

                <div className="space-y-3">
                  <h3 className="text-sm font-bold text-white">Usage Guidelines &amp; Risk Acceptance</h3>
                  <p className="text-slate-400">
                    1. HookCheck provides security guidance based on heuristics, threat intelligence, and AI reasoning available at the time of the scan. Threat landscapes change dynamically.
                  </p>
                  <p className="text-slate-400">
                    2. Never enter sensitive passwords, financial PINs, or confidential credentials into websites flagged as Suspicious, Likely Phishing, or High Risk.
                  </p>
                  <p className="text-slate-400">
                    3. HookCheck is provided "as is" without warranty. Users are responsible for exercising personal judgment when interacting with unknown links or messages.
                  </p>
                </div>
              </>
            )}
          </div>

          {/* Modal Footer */}
          <div className="px-6 py-4 border-t border-[#1E2638] bg-[#0E131F] flex justify-end">
            <button
              onClick={onClose}
              className="px-5 py-2 text-xs font-semibold text-white bg-[#1E2638] hover:bg-slate-700 rounded-xl transition-colors"
            >
              Close
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
