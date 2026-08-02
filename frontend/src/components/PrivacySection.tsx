import { motion } from 'framer-motion';
import { Database, Clock, Server, Shield, UserX, MessageSquare, ExternalLink, Lock } from 'lucide-react';

const sections = [
  {
    icon: Database,
    title: 'What We Collect',
    desc: 'HookCheck does not store the text, URLs, or images you submit for analysis. When you submit content, we compute a SHA-256 cryptographic hash of your input and store only that hash alongside the analysis result. The original content cannot be reconstructed from the hash.',
  },
  {
    icon: Clock,
    title: 'Cache & Reports',
    desc: 'Analysis results are cached by content hash for up to 24 hours. If you submit the same URL or message within that window, we return the cached result instantly without re-running the analysis. Report permalink pages are assigned a random, non-guessable ID and are marked noindex so search engines do not index them.',
  },
  {
    icon: Server,
    title: 'Third-Party Services',
    desc: "URLs you submit are checked against the VirusTotal Public API. VirusTotal receives the URL string (not your message text or image) as part of this check. Please review VirusTotal's privacy policy at virustotal.com.\n\nMessage text and screenshots are sent to a large language model (LLM) provider for analysis. The LLM provider receives only the content you submit for analysis — no identifying information.",
  },
  {
    icon: Shield,
    title: 'Rate Limiting',
    desc: 'Requests are rate-limited by IP address to prevent abuse. IP addresses are used only for this purpose and are not stored or logged beyond the current request session.',
  },
  {
    icon: UserX,
    title: 'No Accounts',
    desc: 'HookCheck has no user accounts, no login, and no mechanism to associate submissions with individuals. There is no personal data processing beyond what is described above.',
  },
  {
    icon: MessageSquare,
    title: 'Contact',
    desc: 'If you have privacy questions, please open an issue on our GitHub repository.',
    link: 'https://github.com/Mosope-ade/phishshield-ai/issues',
    linkLabel: 'Open an issue on GitHub',
  },
];

export function PrivacySection() {
  return (
    <section id="privacy" className="py-16 sm:py-24 bg-[#FAF7F0] relative">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-left"
        >
          <div className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-mono text-[#2E5A44] bg-[#EEF4F0] border border-[#C3D8CC] rounded-full uppercase tracking-wider mb-2">
            <Lock className="w-3.5 h-3.5" />
            Privacy Architecture
          </div>
          <h2 className="font-serif text-3xl sm:text-5xl font-bold text-[#1A1A1A]">
            Privacy Policy
          </h2>
          <p className="mt-2 text-xs sm:text-sm text-[#5A5854]">
            Last updated: July 2026
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {sections.map((s, idx) => (
            <motion.div
              key={s.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: idx * 0.08 }}
              className="paper-card p-6 rounded-md space-y-3 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-sm bg-[#EEF4F0] border border-[#C3D8CC] text-[#2E5A44]">
                    <s.icon className="w-5 h-5" />
                  </div>
                  <h3 className="font-serif text-lg font-bold text-[#1A1A1A]">{s.title}</h3>
                </div>
                <div className="text-xs sm:text-sm text-[#5A5854] leading-relaxed whitespace-pre-line">
                  {s.desc}
                </div>
              </div>

              {s.link && (
                <div className="pt-3 border-t border-[#E6E1D7]">
                  <a
                    href={s.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-[#C1502E] hover:underline"
                  >
                    <span>{s.linkLabel}</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
