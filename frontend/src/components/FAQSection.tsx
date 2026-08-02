import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, HelpCircle } from 'lucide-react';

const faqs = [
  {
    q: 'Does HookCheck store my personal messages or uploaded screenshots?',
    a: 'No. HookCheck operates on a strict zero-raw-storage privacy policy. Submissions are normalized and converted to a SHA-256 cryptographic hash string. Only the hash and generated security verdict are cached to accelerate duplicate scans.',
  },
  {
    q: 'How does HookCheck handle prompt injection attacks?',
    a: 'Our architecture separates deterministic heuristics (which run locally in Python) from the AI layer. AI responses are strictly parsed using Pydantic JSON schemas. Even if an attacker crafts prompt injection copy inside a message, hard rule triggers (like typosquatting or homoglyphs) cannot be silently overwritten by the AI.',
  },
  {
    q: 'What types of inputs can I scan?',
    a: 'You can scan URLs, full text messages, email copy, pasted screenshots, attached image files (PNG/JPEG/WEBP under 2MB), and QR codes (quishing).',
  },
  {
    q: 'Is HookCheck completely free to use?',
    a: 'Yes! HookCheck is an open-source, free decision-support platform requiring no account, login, or subscription.',
  },
  {
    q: 'Can I share a report with a colleague or friend?',
    a: 'Yes. Every completed scan generates a permalink URL (e.g. /report/onudqvgzx7yv). Permalink pages include noindex meta headers to keep your shared report private from public search engine indexes.',
  },
];

export function FAQSection() {
  const [openIdx, setOpenIdx] = useState<number | null>(0);

  const toggle = (idx: number) => {
    setOpenIdx(openIdx === idx ? null : idx);
  };

  return (
    <section id="faq" className="py-16 sm:py-24 bg-[#0A0D13]">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <span className="text-xs font-semibold text-cyan-400 uppercase tracking-widest flex items-center justify-center gap-1">
            <HelpCircle className="w-3.5 h-3.5" />
            Frequently Asked Questions
          </span>
          <h2 className="mt-2 text-2xl sm:text-4xl font-bold text-white tracking-tight">
            Got Questions? We Have Answers.
          </h2>
        </motion.div>

        <div className="space-y-3">
          {faqs.map((faq, idx) => {
            const isOpen = openIdx === idx;
            return (
              <motion.div
                key={faq.q}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: idx * 0.05 }}
                className="glass-card rounded-2xl border border-[#1E2638] overflow-hidden"
              >
                <button
                  type="button"
                  onClick={() => toggle(idx)}
                  className="w-full p-5 sm:p-6 text-left flex items-center justify-between gap-4 font-semibold text-xs sm:text-base text-white hover:text-cyan-400 transition-colors"
                >
                  <span>{faq.q}</span>
                  <ChevronDown
                    className={`w-4 h-4 text-cyan-400 flex-shrink-0 transition-transform duration-300 ${
                      isOpen ? 'rotate-180' : ''
                    }`}
                  />
                </button>
                <AnimatePresence>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.25 }}
                    >
                      <div className="px-5 pb-5 sm:px-6 sm:pb-6 text-xs sm:text-sm text-slate-400 leading-relaxed border-t border-[#1E2638]/50 pt-3">
                        {faq.a}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
