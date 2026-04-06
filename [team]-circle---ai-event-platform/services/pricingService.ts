import { SponsorshipItem, EventSponsorshipSettings, AudienceType } from '../types';

export interface PricingBreakdown {
  base: number;
  sizeMult: number;
  audienceMult: number;
  exposureMult: number;
  exclusiveMult: number;
  final: number;
}

const AUDIENCE_MULTIPLIERS: Record<AudienceType, number> = {
  'general_public': 1.0,
  'students_earlycareer': 1.2,
  'professionals': 1.5,
  'founders_operators': 2.0,
  'executives_investors': 3.0
};

export const calculateSponsorItemPrice = (
  item: SponsorshipItem,
  settings: EventSponsorshipSettings,
  isExclusive: boolean
): PricingBreakdown => {
  const base = item.base_price_usd;
  
  // Size Multiplier: 1.0 for 100, 2.0 for 1000, etc. (Logarithmic or linear?)
  // Let's go with a simple linear scale for now: 1 + (attendance / 1000)
  const sizeMult = Number((1 + (settings.expected_attendance / 1000)).toFixed(2));
  
  const audienceMult = AUDIENCE_MULTIPLIERS[settings.audience_type] || 1.0;
  
  const exposureMult = item.visibility_tier === 'HIGH' ? 1.5 : item.visibility_tier === 'MEDIUM' ? 1.2 : 1.0;
  
  const exclusiveMult = isExclusive ? 2.5 : 1.0;
  
  const final = Math.round(base * sizeMult * audienceMult * exposureMult * exclusiveMult);
  
  return {
    base,
    sizeMult,
    audienceMult,
    exposureMult,
    exclusiveMult,
    final
  };
};
