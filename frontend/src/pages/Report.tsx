import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getReport, ApiError } from '../services/api';
import type { FullReport } from '../types/api';
import { ResultsBlock } from '../components/ResultsBlock';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { InfoModals } from '../components/InfoModals';
import { ArrowLeft, Loader2, AlertCircle } from 'lucide-react';

export function Report() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<FullReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [modalType, setModalType] = useState<'learn' | 'privacy' | 'disclaimer' | null>(null);

  useEffect(() => {
    if (!id) {
      setError('Invalid report ID.');
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    getReport(id)
      .then((r) => {
        if (!cancelled) {
          setReport(r);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          if (err instanceof ApiError && err.status === 404) {
            setError('Report not found. It may have expired or the link may be incorrect.');
          } else {
            setError('Could not load this report. Please try again.');
          }
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [id]);

  // Inject noindex meta tag for permalink safety
  useEffect(() => {
    let meta = document.querySelector('meta[name="robots"]');
    let created = false;
    if (!meta) {
      meta = document.createElement('meta');
      meta.setAttribute('name', 'robots');
      document.head.appendChild(meta);
      created = true;
    }
    meta.setAttribute('content', 'noindex, nofollow');

    return () => {
      if (created && meta && meta.parentNode) {
        meta.parentNode.removeChild(meta);
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-[#0B0E14] text-slate-100 flex flex-col justify-between">
      <Navbar />

      <main id="main-content" className="pt-28 pb-16 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto w-full flex-1">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-xs sm:text-sm font-medium text-cyan-400 hover:text-cyan-300 mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to HookCheck Home
        </Link>

        {loading && (
          <div className="glass-card p-12 rounded-3xl border border-[#1E2638] text-center my-12">
            <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mx-auto mb-3" />
            <p className="text-sm font-semibold text-white">Loading Security Report...</p>
          </div>
        )}

        {error && (
          <div className="p-6 rounded-2xl bg-red-500/10 border border-red-500/30 text-center my-12">
            <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-2" />
            <h2 className="text-base font-bold text-white mb-1">Report Unavailable</h2>
            <p className="text-xs text-red-300 max-w-md mx-auto">{error}</p>
          </div>
        )}

        {report && !loading && (
          <div className="space-y-6">
            <ResultsBlock report={report} />
          </div>
        )}
      </main>

      <Footer onOpenModal={(t) => setModalType(t)} />

      <InfoModals
        isOpen={!!modalType}
        type={modalType}
        onClose={() => setModalType(null)}
      />
    </div>
  );
}
