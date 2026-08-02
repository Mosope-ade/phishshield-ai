import { motion } from 'framer-motion';
import {
  ShieldAlert,
  Globe,
  Lock,
  Server,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Sparkles,
} from 'lucide-react';

const sampleLayers = [
  {
    icon: Globe,
    title: 'Domain & Typosquatting (Heuristics)',
    status: 'fail' as const,
    items: [
      { label: 'Domain', val: 'paypa1-security-update.xyz' },
      { label: 'Levenshtein Distance', val: '1 edit from paypal.com (Flagged)' },
      { label: 'IDN Homoglyphs', val: 'Clean ASCII' },
      { label: 'TLD Risk', val: '.xyz (High-Risk TLD)' },
    ],
  },
  {
    icon: Server,
    title: 'VirusTotal Threat Intelligence',
    status: 'fail' as const,
    items: [
      { label: 'Malicious Votes', val: '14 / 72 Security Vendors' },
      { label: 'Categories', val: 'Phishing, Malware, Social Engineering' },
      { label: 'Reputation Score', val: '-42 (High Threat)' },
    ],
  },
  {
    icon: Lock,
    title: 'AI Semantic Analysis (Gemini LLM)',
    status: 'fail' as const,
    items: [
      { label: 'Classification', val: 'Likely Phishing' },
      { label: 'Urgency Signals', val: 'Artificial fear ("Account suspended in 24 hours")' },
      { label: 'Highlighted Phrase', val: '"Verify your identity now or lose access"' },
    ],
  },
];

const statusBadge = {
  pass: { icon: CheckCircle2, bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400', label: 'Pass' },
  warn: { icon: AlertTriangle, bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400', label: 'Warn' },
  fail: { icon: XCircle, bg: 'bg-red-500/10 border-red-500/30 text-red-400', label: 'Fail' },
};

export function ReportPreviewSection() {
  return (
    <section id="sample-report" className="py-16 sm:py-24 relative overflow-hidden bg-[#070A0F]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Column: Description */}
          <motion.div
            initial={{ opacity: 0, x: -24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold text-cyan-400 bg-cyan-500/10 rounded-full border border-cyan-500/20">
              <Sparkles className="w-3.5 h-3.5" />
              Sample Security Output
            </span>
            <h2 className="mt-4 text-2xl sm:text-4xl font-bold tracking-tight text-white">
              Reports that explain <span className="text-gradient-cyan">WHY</span> content is unsafe
            </h2>
            <p className="mt-4 text-xs sm:text-sm text-slate-400 leading-relaxed">
              HookCheck does not just output an opaque red or green icon. Every report breaks down findings by independent layer so you can see exact evidence, highlighted phrases, and plain-language reasoning.
            </p>
            <ul className="mt-6 space-y-3 text-xs sm:text-sm text-slate-300">
              {[
                'Overall Risk Score (0 - 100) & Threat Level Badge',
                'Layer 1: Deterministic Typosquatting & Homoglyphs',
                'Layer 2: VirusTotal 70+ Security Vendor Verdicts',
                'Layer 3: Gemini AI Semantic Reasons & Highlighted Copy',
                'Shareable permalink URL with private noindex protection',
              ].map((item) => (
                <li key={item} className="flex items-center gap-3">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Right Column: Interactive Card Preview */}
          <motion.div
            initial={{ opacity: 0, x: 24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="relative"
          >
            <div className="absolute -inset-4 bg-gradient-to-br from-brand-500/20 to-cyan-500/20 rounded-3xl blur-2xl pointer-events-none" />
            <div className="relative glass-card rounded-2xl border border-[#1E2638] overflow-hidden shadow-2xl">
              {/* Header Bar */}
              <div className="flex items-center justify-between px-6 py-4 bg-[#0E131F] border-b border-[#1E2638]">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-red-500" />
                  <div className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                </div>
                <span className="text-[11px] font-mono text-cyan-400/80">
                  hookcheck.app/report/r/onudqvgzx7yv
                </span>
              </div>

              {/* Verdict Header */}
              <div className="p-6 space-y-4">
                <div className="flex items-center justify-between pb-4 border-b border-[#1E2638]">
                  <div className="flex items-center gap-3">
                    <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400">
                      <ShieldAlert className="w-6 h-6" />
                    </div>
                    <div>
                      <div className="text-base font-bold text-white">Verdict: High Risk (Score 88/100)</div>
                      <div className="text-xs text-red-400 font-medium">Likely Phishing • Credential Harvesting</div>
                    </div>
                  </div>
                </div>

                {/* Layer Cards */}
                <div className="space-y-3">
                  {sampleLayers.map((l) => {
                    const sb = statusBadge[l.status];
                    return (
                      <div key={l.title} className="p-4 rounded-xl bg-[#0B0E14] border border-[#1E2638] space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 text-xs font-semibold text-white">
                            <l.icon className="w-4 h-4 text-cyan-400" />
                            <span>{l.title}</span>
                          </div>
                          <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-bold rounded border ${sb.bg}`}>
                            <sb.icon className="w-3 h-3" />
                            {sb.label}
                          </span>
                        </div>
                        <div className="space-y-1 pt-1">
                          {l.items.map((it) => (
                            <div key={it.label} className="flex items-center justify-between text-[11px]">
                              <span className="text-slate-400">{it.label}:</span>
                              <span className="font-medium text-slate-200">{it.val}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
