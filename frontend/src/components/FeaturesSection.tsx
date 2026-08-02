import { motion } from 'framer-motion';
import {
  ShieldCheck,
  Lock,
  Globe,
  QrCode,
  Cpu,
  Share2,
} from 'lucide-react';

const features = [
  {
    icon: Globe,
    title: 'Typosquatting & IDN Homoglyphs',
    desc: 'Detects lookalike domains (e.g. paypa1.com) and Unicode Punycode character spoofing using Levenshtein edit distance.',
  },
  {
    icon: Cpu,
    title: 'AI Semantic Reasoning',
    desc: 'LLM context engine analyzes text urgency, fear tactics, brand impersonation tone, and credential harvesting intent.',
  },
  {
    icon: ShieldCheck,
    title: '70+ Threat Engines',
    desc: 'Cross-references URLs and file hashes against VirusTotal v3 security databases for global consensus.',
  },
  {
    icon: QrCode,
    title: 'QR Code (Quishing) Decoding',
    desc: 'Scans uploaded or pasted QR code image payloads directly without relying on external third-party decoders.',
  },
  {
    icon: Lock,
    title: 'Cryptographic Privacy Shield',
    desc: 'Hashes submissions with SHA-256 before database lookup. Zero raw user text, images, or IPs are stored.',
  },
  {
    icon: Share2,
    title: 'Shareable Report Permalinks',
    desc: 'Generates random slug permalink links (e.g. /report/r/8f3a2b) with noindex meta headers for safe sharing.',
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="py-16 sm:py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <span className="text-xs font-semibold text-cyan-400 uppercase tracking-widest">
            Security Engineering Features
          </span>
          <h2 className="mt-2 text-2xl sm:text-4xl font-bold text-white tracking-tight">
            Built for Maximum Accuracy &amp; Privacy
          </h2>
          <p className="mt-2 text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            Combining deterministic rules, AI semantic reasoning, and multi-engine threat intelligence.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, idx) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: idx * 0.08 }}
              className="glass-card glass-card-hover p-6 rounded-2xl border border-[#1E2638]"
            >
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center mb-4">
                <f.icon className="w-5 h-5" />
              </div>
              <h3 className="text-sm sm:text-base font-semibold text-white mb-1.5">{f.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
