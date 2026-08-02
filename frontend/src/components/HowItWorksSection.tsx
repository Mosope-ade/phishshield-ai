import { motion } from 'framer-motion';
import { Search, ShieldAlert, CheckCircle2 } from 'lucide-react';

const steps = [
  {
    number: '01',
    icon: Search,
    title: 'Submit Content',
    desc: 'Paste a suspicious URL, message text, or attach a screenshot/QR code image. No signups or permissions needed.',
  },
  {
    number: '02',
    icon: ShieldAlert,
    title: '3-Engine Parallel Scan',
    desc: 'HookCheck inspects domain typosquatting, IDN homoglyphs, VirusTotal 70+ security engines, and Gemini AI semantic reasoning.',
  },
  {
    number: '03',
    icon: CheckCircle2,
    title: 'Actionable Report',
    desc: 'Receive a plain-language verdict, risk score (0-100), highlighted suspicious phrases, and clear protective recommendations.',
  },
];

export function HowItWorksSection() {
  return (
    <section id="how" className="py-16 sm:py-24 bg-[#0A0D13]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <span className="text-xs font-semibold text-cyan-400 uppercase tracking-widest">
            Simple &amp; Transparent Pipeline
          </span>
          <h2 className="mt-2 text-2xl sm:text-4xl font-bold text-white tracking-tight">
            How Detection Works
          </h2>
          <p className="mt-2 text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            Three independent layers evaluate your submission in parallel to eliminate false safe verdicts.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
          {steps.map((s, idx) => (
            <motion.div
              key={s.number}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: idx * 0.1 }}
              className="glass-card glass-card-hover p-6 sm:p-8 rounded-2xl border border-[#1E2638] relative"
            >
              <span className="text-4xl font-black text-slate-800/80 absolute top-4 right-6 font-mono pointer-events-none">
                {s.number}
              </span>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 border border-cyan-500/30 text-cyan-400 flex items-center justify-center mb-5">
                <s.icon className="w-6 h-6" />
              </div>
              <h3 className="text-base sm:text-lg font-semibold text-white mb-2">{s.title}</h3>
              <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
