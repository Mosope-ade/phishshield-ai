import { Navbar } from '../components/Navbar';
import { Hero } from '../components/Hero';
import { TrustBanner } from '../components/TrustBanner';
import { AnalyzerSection } from '../components/AnalyzerSection';
import { HowItWorksSection } from '../components/HowItWorksSection';
import { FeaturesSection } from '../components/FeaturesSection';
import { ReportPreviewSection } from '../components/ReportPreviewSection';
import { PrivacySection } from '../components/PrivacySection';
import { DisclaimerSection } from '../components/DisclaimerSection';
import { FAQSection } from '../components/FAQSection';
import { CTASection } from '../components/CTASection';
import { Footer } from '../components/Footer';

export function Landing() {
  return (
    <div className="min-h-screen bg-[#0B0E14] text-slate-100 selection:bg-cyan-500/30 selection:text-cyan-200">
      <Navbar />
      <main id="main-content">
        <Hero />
        <TrustBanner />
        <AnalyzerSection />
        <HowItWorksSection />
        <FeaturesSection />
        <ReportPreviewSection />
        <PrivacySection />
        <DisclaimerSection />
        <FAQSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}
