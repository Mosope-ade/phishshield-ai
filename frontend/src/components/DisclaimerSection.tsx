import { motion } from 'framer-motion';
import { AlertTriangle, ShieldAlert, Info, FileText } from 'lucide-react';

const limitations = [
  "Newly registered phishing domains may not yet appear in VirusTotal's database.",
  'AI analysis can be fooled by carefully crafted adversarial messages.',
  'Heuristic rules do not cover every phishing technique.',
  'The tool analyzes content as-submitted; it does not browse to URLs or render web pages.',
];

export function DisclaimerSection() {
  return (
    <section id="disclaimer" className="py-16 sm:py-24 bg-[#F3EFE6] border-y border-[#E6E1D7] relative">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-left"
        >
          <div className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-mono text-[#D97706] bg-[#FEF3C7] border border-[#FDE68A] rounded-full uppercase tracking-wider mb-2">
            <AlertTriangle className="w-3.5 h-3.5" />
            Legal Terms &amp; Advisory Scope
          </div>
          <h2 className="font-serif text-3xl sm:text-5xl font-bold text-[#1A1A1A]">
            Disclaimer
          </h2>
          <p className="mt-2 text-xs sm:text-sm text-[#5A5854]">
            Please review the decision-support boundaries, technical limitations, and liability terms of HookCheck.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Decision-support tool, not a guarantee */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4 }}
            className="paper-card p-6 sm:p-8 rounded-md space-y-3 border-2 border-[#1A1A1A]"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-sm bg-[#FEF3C7] border border-[#FDE68A] text-[#D97706]">
                <Info className="w-5 h-5" />
              </div>
              <h3 className="font-serif text-lg font-bold text-[#1A1A1A]">
                Decision-support tool, not a guarantee
              </h3>
            </div>
            <p className="text-xs sm:text-sm text-[#5A5854] leading-relaxed">
              HookCheck is a decision-support tool. Its analysis is intended to help you make a more informed judgment, not to replace your own judgment. A result of <strong className="text-[#2E5A44] font-semibold">"Likely Safe"</strong> does not mean the content is definitively safe, and a result of <strong className="text-[#C1502E] font-semibold">"Likely Phishing"</strong> does not mean the content is definitively malicious.
            </p>
          </motion.div>

          {/* Limitations */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.08 }}
            className="paper-card p-6 sm:p-8 rounded-md space-y-3"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-sm bg-[#FAF7F0] border border-[#E6E1D7] text-[#C1502E]">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h3 className="font-serif text-lg font-bold text-[#1A1A1A]">
                Limitations
              </h3>
            </div>
            <ul className="space-y-2 text-xs sm:text-sm text-[#5A5854]">
              {limitations.map((item) => (
                <li key={item} className="flex items-start gap-2.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#C1502E] mt-2 flex-shrink-0" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* No liability */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.16 }}
            className="paper-card p-6 sm:p-8 rounded-md space-y-3"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-sm bg-[#FBF0EC] border border-[#F4D4C9] text-[#C1502E]">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <h3 className="font-serif text-lg font-bold text-[#1A1A1A]">
                No liability
              </h3>
            </div>
            <p className="text-xs sm:text-sm text-[#5A5854] leading-relaxed">
              HookCheck and its operators accept no liability for any harm arising from acting on or ignoring the results of an analysis. Use of this tool is at your own risk. Always exercise independent judgment and, when in doubt, consult your organization's IT or security team.
            </p>
          </motion.div>

          {/* Accuracy */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.24 }}
            className="paper-card p-6 sm:p-8 rounded-md space-y-3"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-sm bg-[#FAF7F0] border border-[#E6E1D7] text-[#1A1A1A]">
                <FileText className="w-5 h-5" />
              </div>
              <h3 className="font-serif text-lg font-bold text-[#1A1A1A]">
                Accuracy
              </h3>
            </div>
            <p className="text-xs sm:text-sm text-[#5A5854] leading-relaxed">
              We make no representations about the accuracy, completeness, or timeliness of any analysis result. The tool is provided <strong className="text-[#1A1A1A] font-semibold">"as is"</strong> without warranty of any kind.
            </p>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
