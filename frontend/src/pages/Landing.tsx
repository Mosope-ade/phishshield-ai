import { useState } from 'react';
import { Navbar } from '../components/Navbar';
import { Hero } from '../components/Hero';
import { TrustBanner } from '../components/TrustBanner';
import { AnalyzerSection } from '../components/AnalyzerSection';
import { HowItWorksSection } from '../components/HowItWorksSection';
import { FeaturesSection } from '../components/FeaturesSection';
import { FAQSection } from '../components/FAQSection';
import { CTASection } from '../components/CTASection';
import { Footer } from '../components/Footer';
import { InfoModals } from '../components/InfoModals';

export function Landing() {
  const [modalType, setModalType] = useState<'learn' | 'privacy' | 'disclaimer' | null>(null);

  const handleOpenModal = (type: 'learn' | 'privacy' | 'disclaimer') => {
    setModalType(type);
  };

  const handleCloseModal = () => {
    setModalType(null);
  };

  return (
    <div className="min-h-screen bg-[#0B0E14] text-slate-100 selection:bg-cyan-500/30 selection:text-cyan-200">
      <Navbar />
      <main id="main-content">
        <Hero />
        <TrustBanner />
        <AnalyzerSection />
        <HowItWorksSection />
        <FeaturesSection />
        <FAQSection />
        <CTASection />
      </main>
      <Footer onOpenModal={handleOpenModal} />
      <InfoModals
        isOpen={!!modalType}
        type={modalType}
        onClose={handleCloseModal}
      />
    </div>
  );
}
