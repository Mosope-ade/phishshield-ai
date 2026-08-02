import { motion } from 'framer-motion';
import { AlertTriangle, ShieldCheck, Info } from 'lucide-react';

const disclaimerPoints = [
  {
    title: 'Decision-Support Scope',
    desc: 'HookCheck serves as an advisory threat assessment assistant to help you evaluate suspicious content. It is not an absolute security guarantee.',
  },
  {
    title: 'Dynamic Threat Environment',
    desc: 'Threat landscapes evolve rapidly. Scans reflect information available from AI, Heuristics, and VirusTotal at the exact moment of execution.',
  },
  {
    title: 'User Personal Judgment',
    desc: 'Never input passwords, private keys, or financial credentials into websites flagged as Suspicious, Likely Phishing, or High Risk.',
  },
];

export function DisclaimerSection() {
  return (
    <section id="disclaimer" className="py-16 sm:py-24 bg-[#0A0D13] relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="glass-card p-8 sm:p-10 rounded-3xl border border-amber-500/30 relative overflow-hidden"
        >
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-[#1E2638] pb-6 mb-6">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-400">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">
                  Important Advisory Note
                </span>
                <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                  Legal Disclaimer &amp; Usage Boundaries
                </h2>
              </div>
            </div>
            <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-medium self-start md:self-auto">
              <Info className="w-4 h-4" />
              <span>Advisory Assistant</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {disclaimerPoints.map((item) => (
              <div key={item.title} className="p-4 rounded-xl bg-[#0E131F]/80 border border-[#1E2638]">
                <h3 className="text-sm font-semibold text-white mb-1.5 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-cyan-400" />
                  {item.title}
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
