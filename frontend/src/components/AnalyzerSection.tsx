import { useRef, useState, useId, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Loader2,
  ShieldCheck,
  Paperclip,
  X,
  Image as ImageIcon,
  AlertCircle,
  Sparkles,
  Globe,
  RotateCcw,
} from 'lucide-react';
import { useAnalysis } from '../hooks/useAnalysis';
import { ResultsBlock } from './ResultsBlock';

export function AnalyzerSection() {
  const [activeTab, setActiveTab] = useState<'text' | 'image'>('text');
  const [text, setText] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaId = useId();
  const { state, submit, reset } = useAnalysis();

  // Clipboard paste listener for images (Ctrl+V)
  useEffect(() => {
    const handlePaste = (e: ClipboardEvent) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item.type.startsWith('image/')) {
          const file = item.getAsFile();
          if (file) {
            setValidationError(null);
            if (file.size > 2 * 1024 * 1024) {
              setValidationError('Image exceeds maximum allowed size of 2MB.');
              setImageFile(null);
              if (fileInputRef.current) fileInputRef.current.value = '';
              return;
            }
            const pastedFile = new File([file], 'pasted-screenshot.png', { type: file.type });
            setImageFile(pastedFile);
            setActiveTab('image');
            setText('');
            e.preventDefault();
            break;
          }
        }
      }
    };

    window.addEventListener('paste', handlePaste);
    return () => window.removeEventListener('paste', handlePaste);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (state.status === 'loading') return;
    setValidationError(null);

    if (activeTab === 'image' && !imageFile) {
      setValidationError('Please select or attach an image file first.');
      return;
    }
    if (activeTab === 'text' && !text.trim()) {
      setValidationError('Please enter a URL or suspicious text message.');
      return;
    }

    await submit(activeTab === 'text' ? text : '', activeTab === 'image' ? imageFile : null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setValidationError(null);
    if (file) {
      if (file.size > 2 * 1024 * 1024) {
        setValidationError('Image exceeds maximum allowed size of 2MB.');
        setImageFile(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
        return;
      }
      setImageFile(file);
      setActiveTab('image');
      setText('');
    }
  };

  const removeFile = () => {
    setImageFile(null);
    setValidationError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleReset = () => {
    setText('');
    setImageFile(null);
    setValidationError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    reset();
  };

  const isLoading = state.status === 'loading';

  return (
    <section id="analyze" className="relative py-16 sm:py-24">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-8 sm:mb-10"
        >
          <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold text-cyan-400 bg-cyan-500/10 rounded-full border border-cyan-500/20">
            <Sparkles className="w-3.5 h-3.5" />
            Live Detection Engine
          </span>
          <h2 className="mt-3 text-2xl sm:text-4xl font-bold tracking-tight text-white">
            Analyze Suspicious Content
          </h2>
          <p className="mt-2 text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            Paste a link, message text, or attach a screenshot or QR code. No signup required.
          </p>
        </motion.div>

        {/* Input Card Container */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="glass-card rounded-2xl border border-[#1E2638] overflow-hidden shadow-2xl shadow-black/50"
        >
          {/* Input Type Tabs */}
          <div className="flex border-b border-[#1E2638] bg-[#0E131F]/90">
            <button
              type="button"
              onClick={() => {
                setActiveTab('text');
                setValidationError(null);
              }}
              className={`flex-1 flex items-center justify-center gap-2 py-3 sm:py-3.5 text-xs sm:text-sm font-semibold transition-all ${
                activeTab === 'text'
                  ? 'text-cyan-400 border-b-2 border-cyan-400 bg-[#121824]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#121824]/50'
              }`}
            >
              <Globe className="w-4 h-4" />
              <span>URL / Text Message</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setActiveTab('image');
                setValidationError(null);
              }}
              className={`flex-1 flex items-center justify-center gap-2 py-3 sm:py-3.5 text-xs sm:text-sm font-semibold transition-all ${
                activeTab === 'image'
                  ? 'text-cyan-400 border-b-2 border-cyan-400 bg-[#121824]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#121824]/50'
              }`}
            >
              <ImageIcon className="w-4 h-4" />
              <span>Screenshot / QR Code</span>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="p-4 sm:p-6 md:p-8">
            {activeTab === 'text' ? (
              <div className="space-y-4">
                <div className="relative">
                  <textarea
                    id={textareaId}
                    rows={4}
                    value={text}
                    onChange={(e) => {
                      setText(e.target.value);
                      if (imageFile) setImageFile(null);
                    }}
                    disabled={isLoading}
                    maxLength={10000}
                    placeholder="Paste suspicious text message, email link, or URL (e.g. https://paypa1-security-update.xyz/login)..."
                    className="w-full p-4 text-xs sm:text-sm text-white bg-[#0B0E14] border border-[#1E2638] rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-400 transition-all placeholder:text-slate-500 resize-y"
                  />
                  <span className="absolute right-3 bottom-3 text-[10px] text-slate-500">
                    {text.length}/10000
                  </span>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  onChange={handleFileChange}
                  className="hidden"
                />

                {imageFile ? (
                  <div className="flex items-center justify-between p-4 bg-[#0B0E14] border border-cyan-500/40 rounded-xl">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
                        <ImageIcon className="w-5 h-5" />
                      </div>
                      <div className="flex flex-col min-w-0">
                        <span className="text-xs sm:text-sm font-medium text-white truncate">
                          {imageFile.name}
                        </span>
                        <span className="text-[11px] text-slate-400">
                          {(imageFile.size / 1024 / 1024).toFixed(2)} MB • Ready for scan
                        </span>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={removeFile}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#1E2638] transition-colors"
                      title="Remove image"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-[#1E2638] hover:border-cyan-500/40 bg-[#0B0E14]/60 hover:bg-[#0B0E14] p-8 sm:p-10 rounded-xl text-center cursor-pointer transition-all group"
                  >
                    <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-cyan-400 flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                      <Paperclip className="w-6 h-6" />
                    </div>
                    <p className="text-xs sm:text-sm font-semibold text-white">
                      Click to upload image or drag &amp; drop
                    </p>
                    <p className="text-[11px] text-slate-400 mt-1">
                      Supports PNG, JPEG, WEBP screenshots or QR codes (Max 2MB)
                    </p>
                    <p className="text-[11px] text-cyan-400/80 mt-2 font-medium">
                      💡 Tip: Press Ctrl + V anywhere to paste clipboard screenshot directly!
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Validation Error Banner */}
            {validationError && (
              <div className="mt-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{validationError}</span>
              </div>
            )}

            {/* Form Action Controls */}
            <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-2 text-[11px] text-slate-400">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Zero raw text or image binaries stored</span>
              </div>

              <div className="w-full sm:w-auto flex items-center gap-2">
                {(text || imageFile || state.status !== 'idle') && (
                  <button
                    type="button"
                    onClick={handleReset}
                    className="w-1/3 sm:w-auto px-4 py-3 text-xs font-semibold text-slate-400 hover:text-white bg-[#121824] border border-[#1E2638] rounded-xl transition-all"
                  >
                    Clear
                  </button>
                )}
                <button
                  type="submit"
                  disabled={isLoading || (activeTab === 'text' ? !text.trim() : !imageFile)}
                  className="w-full sm:w-auto flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 text-xs sm:text-sm font-semibold text-white bg-gradient-to-r from-brand-600 via-indigo-600 to-cyan-600 hover:from-brand-500 hover:to-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl shadow-lg shadow-indigo-500/20 transition-all hover:scale-[1.02] disabled:hover:scale-100"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Scanning...
                    </>
                  ) : (
                    <>
                      <ShieldCheck className="w-4 h-4" />
                      Run Threat Scan
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        </motion.div>

        {/* Loading Progress State */}
        <AnimatePresence>
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              className="mt-6 glass-card p-6 rounded-2xl border border-cyan-500/30 text-center"
            >
              <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mx-auto mb-3" />
              <p className="text-sm font-semibold text-white">{state.step || 'Running multi-engine analysis...'}</p>
              <p className="text-xs text-slate-400 mt-1">
                Querying Heuristics Engine, VirusTotal v3, and LLM reasoning...
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error State */}
        {state.status === 'error' && (
          <div className="mt-6 p-4 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm flex flex-col items-center text-center">
            <AlertCircle className="w-6 h-6 mb-2" />
            <p className="font-semibold text-white">Analysis Could Not Complete</p>
            <p className="text-xs text-red-300 mt-1">{state.message}</p>
            <button
              onClick={handleReset}
              className="mt-3 px-4 py-1.5 text-xs font-medium text-white bg-red-500/20 hover:bg-red-500/30 rounded-lg border border-red-500/40 transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Results Render In-Place */}
        {state.status === 'success' && (
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 space-y-4"
          >
            <div className="flex justify-end">
              <button
                onClick={handleReset}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold text-slate-300 bg-[#121824] hover:bg-[#1E2638] border border-[#1E2638] rounded-xl transition-all"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Start New Scan
              </button>
            </div>
            <ResultsBlock report={state.report} />
          </motion.div>
        )}
      </div>
    </section>
  );
}
