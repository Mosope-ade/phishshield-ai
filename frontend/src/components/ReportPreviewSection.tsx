import { motion } from 'framer-motion';
import { Globe, Server, Lock, Sparkles } from 'lucide-react';

const sampleLayers = [
  {
    icon: Globe,
    title: 'Deterministic Heuristics Engine',
    chipClass: 'chip-heuristics',
    tag: 'Heuristics • Safe & Fast',
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
    chipClass: 'chip-virustotal',
    tag: 'VirusTotal • 70+ Scanners',
    items: [
      { label: 'Malicious Votes', val: '14 / 72 Security Vendors' },
      { label: 'Categories', val: 'Phishing, Malware, Social Engineering' },
      { label: 'Reputation Score', val: '-42 (High Threat)' },
    ],
  },
  {
    icon: Lock,
    title: 'AI Language & Intent Engine',
    chipClass: 'chip-ai',
    tag: 'AI Engine • Semantic Reasoning',
    items: [
      { label: 'Classification', val: 'Likely Phishing' },
      { label: 'Urgency Signals', val: 'Artificial fear ("Account suspended in 24 hours")' },
      { label: 'Highlighted Copy', val: '"Verify your identity now or lose access"' },
    ],
  },
];

export function ReportPreviewSection() {
  return (
    <section id="sample-report" className="py-16 sm:py-24 bg-[#F3EFE6] border-y border-[#E6E1D7] relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-12 gap-12 items-center">
          {/* Left Column */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="lg:col-span-6 text-left space-y-4"
          >
            <div className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-mono text-[#C1502E] bg-[#FBF0EC] border border-[#F4D4C9] rounded-full uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5" />
              Distinct Layer Badges
            </div>
            <h2 className="font-serif text-3xl sm:text-4xl font-bold text-[#1A1A1A]">
              Three evidence layers, visually distinct at a glance
            </h2>
            <p className="text-xs sm:text-sm text-[#5A5854] leading-relaxed">
              HookCheck's core differentiator is evidence isolation. We do not blend results into an opaque red or green box — each layer is independently color-coded and labeled.
            </p>
            <ul className="space-y-3 pt-2 text-xs sm:text-sm text-[#1A1A1A]">
              <li className="flex items-center gap-2.5">
                <span className="w-3 h-3 rounded-full bg-[#2E5A44] flex-shrink-0" />
                <span><strong className="font-bold text-[#2E5A44]">Heuristics Engine (Sage):</strong> Deterministic rules, uninjectable local logic</span>
              </li>
              <li className="flex items-center gap-2.5">
                <span className="w-3 h-3 rounded-full bg-[#C1502E] flex-shrink-0" />
                <span><strong className="font-bold text-[#C1502E]">VirusTotal (Terracotta):</strong> Corroborating threat intelligence across 70+ vendors</span>
              </li>
              <li className="flex items-center gap-2.5">
                <span className="w-3 h-3 rounded-full bg-[#1A1A1A] flex-shrink-0" />
                <span><strong className="font-bold text-[#1A1A1A]">AI Analysis (Warm Ink):</strong> Language, urgency, and social engineering reasoning</span>
              </li>
            </ul>
          </motion.div>

          {/* Right Column: Sample Report Card */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="lg:col-span-6"
          >
            <div className="paper-card-asymmetric p-6 rounded-md bg-[#FFFFFF] space-y-4">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-[#E6E1D7] pb-4">
                <div>
                  <div className="text-xs font-mono text-[#5A5854] uppercase tracking-wider">
                    Sample Output
                  </div>
                  <div className="font-serif text-lg font-bold text-[#1A1A1A]">
                    Verdict: High Risk (Score 88/100)
                  </div>
                </div>
                <span className="px-3 py-1 text-xs font-bold text-[#C1502E] bg-[#FBF0EC] border border-[#F4D4C9] rounded-md">
                  Likely Phishing
                </span>
              </div>

              {/* Layers with distinct color-coded chips */}
              <div className="space-y-3">
                {sampleLayers.map((l) => (
                  <div key={l.title} className="p-4 rounded-md bg-[#FAF7F0] border border-[#E6E1D7] space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-xs font-bold text-[#1A1A1A]">
                        <l.icon className="w-4 h-4 text-[#C1502E]" />
                        <span>{l.title}</span>
                      </div>
                      <span className={`px-2.5 py-0.5 text-[10px] font-bold rounded-full ${l.chipClass}`}>
                        {l.tag}
                      </span>
                    </div>
                    <div className="space-y-1 pt-1 font-mono text-[11px]">
                      {l.items.map((it) => (
                        <div key={it.label} className="flex justify-between">
                          <span className="text-[#5A5854]">{it.label}:</span>
                          <span className="font-medium text-[#1A1A1A]">{it.val}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
