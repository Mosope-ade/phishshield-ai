import { motion } from 'framer-motion';
import { ShieldCheck, Zap, Lock, ArrowRight, Sparkles } from 'lucide-react';

const badges = [
  { icon: Zap, text: 'Instant Scan (<50ms Cached)' },
  { icon: Lock, text: 'Zero Raw Data Storage' },
  { icon: ShieldCheck, text: '3 Independent Engines' },
];

const highlights = [
  { label: 'Detection Vectors', value: 'URLs • SMS • Images • QR' },
  { label: 'Privacy Standard', value: 'SHA-256 Content Hashing' },
  { label: 'Security Intelligence', value: 'VirusTotal + LLM + Rules' },
];

export function Hero() {
  return (
    <section id="top" className="relative pt-28 sm:pt-36 pb-16 sm:pb-24 overflow-hidden">
      {/* Background Radial Glow & Grid Pattern */}
      <div className="absolute inset-0 bg-hero-gradient pointer-events-none" />
      <div className="absolute inset-0 bg-grid-pattern [mask-image:radial-gradient(ellipse_70%_50%_at_50%_30%,black,transparent)] pointer-events-none" />

      {/* Floating Cyan/Indigo Ambient Orbs */}
      <div className="absolute top-20 -left-20 w-72 h-72 bg-brand-500/15 rounded-full blur-3xl animate-pulse-slow pointer-events-none" />
      <div className="absolute top-40 -right-20 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse-slow pointer-events-none" style={{ animationDelay: '1.5s' }} />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Category Pill Badge */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex justify-center mb-6"
        >
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#121824]/80 backdrop-blur-md border border-[#1E2638] shadow-lg">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-400"></span>
            </span>
            <span className="text-xs font-medium text-slate-300">
              Open-Source &amp; Free Public Protection
            </span>
          </div>
        </motion.div>

        {/* Main Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-center text-3xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-white leading-[1.1]"
        >
          Spot Phishing Hooks <br className="hidden sm:inline" />
          <span className="text-gradient-cyan">Before They Bite.</span>
        </motion.h1>

        {/* Tagline */}
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-5 text-center text-sm sm:text-base md:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed px-2"
        >
          Paste any suspicious URL, SMS text, email screenshot, or QR code. HookCheck analyzes it across three independent evidence layers — AI, Heuristics, and VirusTotal.
        </motion.p>

        {/* Feature Badges */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-6 flex flex-wrap items-center justify-center gap-2 sm:gap-3"
        >
          {badges.map((b) => (
            <div
              key={b.text}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#121824]/60 backdrop-blur border border-[#1E2638] text-xs font-medium text-slate-300"
            >
              <b.icon className="w-3.5 h-3.5 text-cyan-400" />
              <span>{b.text}</span>
            </div>
          ))}
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 px-4"
        >
          <a
            href="#analyze"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold text-white bg-gradient-to-r from-brand-600 via-indigo-600 to-cyan-600 hover:from-brand-500 hover:to-cyan-500 rounded-xl shadow-xl shadow-indigo-500/25 transition-all hover:scale-[1.02]"
          >
            <Sparkles className="w-4 h-4" />
            Analyze Suspicious Link or Text
            <ArrowRight className="w-4 h-4" />
          </a>
          <a
            href="#how"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold text-slate-300 bg-[#121824] hover:bg-[#1A2234] rounded-xl border border-[#1E2638] transition-all"
          >
            How Detection Works
          </a>
        </motion.div>

        {/* Metrics/Highlights Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="mt-12 sm:mt-16 grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-6 max-w-3xl mx-auto"
        >
          {highlights.map((h) => (
            <div key={h.label} className="glass-card p-4 rounded-xl text-center border border-[#1E2638]">
              <div className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">
                {h.label}
              </div>
              <div className="mt-1 text-xs sm:text-sm font-medium text-slate-300">
                {h.value}
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
