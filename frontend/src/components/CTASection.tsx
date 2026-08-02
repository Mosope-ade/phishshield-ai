import { motion } from 'framer-motion';
import { ShieldCheck, ArrowRight, Sparkles } from 'lucide-react';

export function CTASection() {
  return (
    <section className="py-16 sm:py-24 relative overflow-hidden">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="glass-card p-8 sm:p-12 rounded-3xl border border-cyan-500/30 text-center relative overflow-hidden shadow-2xl"
        >
          {/* Ambient Glow */}
          <div className="absolute -top-24 -left-24 w-64 h-64 bg-cyan-500/20 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 max-w-2xl mx-auto">
            <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 flex items-center justify-center mx-auto mb-4">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
              Ready to verify a link or text message?
            </h2>
            <p className="mt-3 text-xs sm:text-sm text-slate-400 leading-relaxed">
              No registration, no tracking, and zero personal data stored. Protect yourself and your team instantly.
            </p>
            <div className="mt-8 flex justify-center">
              <a
                href="#analyze"
                className="inline-flex items-center gap-2 px-8 py-4 text-sm font-semibold text-white bg-gradient-to-r from-brand-600 via-indigo-600 to-cyan-600 hover:from-brand-500 hover:to-cyan-500 rounded-xl shadow-xl shadow-indigo-500/30 transition-all hover:scale-[1.03]"
              >
                <Sparkles className="w-4 h-4" />
                Analyze Suspicious Content Now
                <ArrowRight className="w-4 h-4" />
              </a>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
