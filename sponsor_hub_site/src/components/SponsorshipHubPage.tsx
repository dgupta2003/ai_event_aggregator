import React, { useRef } from 'react';
import HubHero from './HubHero';
import HubIntro from './HubIntro';
import HostFlowSection from './HostFlowSection';
import SponsorFlowSection from './SponsorFlowSection';
import OpportunityGrid from './OpportunityGrid';
import PackagePreview from './PackagePreview';
import FinalCta from './FinalCta';
import { useSponsorshipHubData } from '../hooks/useSponsorshipHubData';

const SponsorshipHubPage: React.FC = () => {
  const hostRef = useRef<HTMLDivElement>(null);
  const sponsorRef = useRef<HTMLDivElement>(null);

  const { sponsorableEvents, isLoading } = useSponsorshipHubData();

  const scrollTo = (ref: React.RefObject<HTMLDivElement>) =>
    ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });

  return (
    <div className="pt-16 min-h-screen">
      <HubHero
        onChooseHost={() => scrollTo(hostRef)}
        onChooseSponsor={() => scrollTo(sponsorRef)}
      />

      <HubIntro />

      <div ref={hostRef}>
        <HostFlowSection />
      </div>

      <div ref={sponsorRef}>
        <SponsorFlowSection />
      </div>

      <OpportunityGrid events={sponsorableEvents} isLoading={isLoading} />

      <PackagePreview />

      <FinalCta />
    </div>
  );
};

export default SponsorshipHubPage;
