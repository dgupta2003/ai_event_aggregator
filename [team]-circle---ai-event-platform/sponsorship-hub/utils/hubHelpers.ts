import { AudienceType, SponsorshipItem, EventSponsorshipSettings } from '../../types';
import { calculateSponsorItemPrice } from '../../services/pricingService';

export const AUDIENCE_LABELS: Record<AudienceType, string> = {
  general_public: 'General Public',
  students_earlycareer: 'Students / Early Career',
  professionals: 'Professionals',
  founders_operators: 'Founders & Operators',
  executives_investors: 'Executives & Investors',
};

export const formatAudienceLabel = (type: AudienceType): string =>
  AUDIENCE_LABELS[type] ?? type;

export const estimatePackageTotal = (
  items: SponsorshipItem[],
  settings: EventSponsorshipSettings,
): number =>
  items.reduce((sum, item) => {
    const bd = calculateSponsorItemPrice(item, settings, false);
    return sum + bd.final;
  }, 0);

export const getVisibilityColor = (tier: string): string => {
  switch (tier) {
    case 'HIGH':   return 'text-purple-300 border-purple-500/30 bg-purple-500/10';
    case 'MEDIUM': return 'text-cyan-300 border-cyan-500/30 bg-cyan-500/10';
    default:       return 'text-emerald-300 border-emerald-500/30 bg-emerald-500/10';
  }
};
