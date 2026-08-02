import { ShieldCheck, Database, Cpu, Lock } from 'lucide-react';

const engines = [
  { icon: ShieldCheck, name: 'VirusTotal v3', desc: '70+ Security Scanners' },
  { icon: Cpu, name: 'Google Gemini AI', desc: 'Semantic Reasoning Engine' },
  { icon: Database, name: 'Local Heuristics', desc: 'Typosquatting & Homoglyphs' },
  { icon: Lock, name: 'SHA-256 Privacy', desc: 'Zero Storage of Raw Inputs' },
];

export function TrustBanner() {
  return (
    <div className="border-y border-[#1E2638] bg-[#0E131F]/80 backdrop-blur-md py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
          {engines.map((e) => (
            <div key={e.name} className="flex items-center gap-3 p-2.5 sm:p-3 rounded-xl bg-[#121824]/40 border border-[#1E2638]/60">
              <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-cyan-400">
                <e.icon className="w-4 h-4 sm:w-5 sm:h-5" />
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-xs sm:text-sm font-semibold text-white truncate">{e.name}</span>
                <span className="text-[11px] text-slate-400 truncate">{e.desc}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
