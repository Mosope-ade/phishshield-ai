import { motion } from 'framer-motion';
import { Lock, EyeOff, Database, FileKey } from 'lucide-react';

const privacyPoints = [
  {
    icon: EyeOff,
    title: 'Zero Raw Message Storage',
    desc: 'The URL, text message, or image buffer you submit is processed in-memory and immediately discarded. We never log or store your raw communications.',
  },
  {
    icon: Database,
    title: 'SHA-256 Cryptographic Hashes',
    desc: 'To prevent duplicate API traffic, HookCheck converts your input into a SHA-256 cryptographic hash string. Only the hash and security verdict JSON are stored in Supabase.',
  },
  {
    icon: Lock,
    title: 'No Accounts, No Tracking',
    desc: 'We never ask for your email, password, or credentials. Scans are completely anonymous and require no user registration.',
  },
  {
    icon: FileKey,
    title: 'Private Permalinks (Noindex)',
    desc: 'Shared report permalinks contain dynamic noindex meta headers, keeping your shared report private from public search engine indexes.',
  },
];

export function PrivacySection() {
  return (
    <section id="privacy" className="py-16 sm:py-24 bg-[#080B10] relative overflow-hidden">
      <div className="absolute inset-0 bg-grid-pattern opacity-10 pointer-events-none" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold text-emerald-400 bg-emerald-500/10 rounded-full border border-emerald-500/20">
            <Lock className="w-3.5 h-3.5" />
            Privacy Architecture
          </span>
          <h2 className="mt-3 text-2xl sm:text-4xl font-bold tracking-tight text-white">
            Scanning a link shouldn't mean surrendering your data
          </h2>
          <p className="mt-2 text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            HookCheck is engineered for maximum privacy and data hygiene. Here is exactly how your data is handled.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {privacyPoints.map((p, i) => (
            <motion.div
              key={p.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className="glass-card glass-card-hover p-6 rounded-2xl border border-[#1E2638]"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4">
                <p.icon className="w-5 h-5" />
              </div>
              <h3 className="text-sm sm:text-base font-semibold text-white mb-2">{p.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{p.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
