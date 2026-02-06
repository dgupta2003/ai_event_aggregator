
import { SponsorshipItem, EventSponsorshipSettings, AudienceType, VisibilityTier } from '../types';

export const getSizeMultiplier = (attendance: number): number => {
  if (attendance < 30) return 0.8;
  if (attendance <= 75) return 1.0;
  if (attendance <= 150) return 1.25;
  if (attendance <= 300) return 1.5;
  if (attendance <= 800) return 2.0;
  return 2.5;
};

export const getAudienceMultiplier = (type: AudienceType): number => {
  const multipliers: Record<AudienceType, number> = {
    general_public: 1.0,
    students_earlycareer: 1.1,
    professionals: 1.25,
    founders_operators: 1.4,
    executives_investors: 1.6
  };
  return multipliers[type];
};

export const getExposureMultiplier = (tier: VisibilityTier): number => {
  const multipliers: Record<VisibilityTier, number> = {
    LOW: 1.0,
    MEDIUM: 1.2,
    HIGH: 1.5
  };
  return multipliers[tier];
};

export const calculateSponsorItemPrice = (
  item: SponsorshipItem,
  eventSettings: EventSponsorshipSettings,
  isExclusive: boolean
): { total: number; breakdown: any } => {
  const mSize = getSizeMultiplier(eventSettings.expected_attendance);
  const mAudience = getAudienceMultiplier(eventSettings.audience_type);
  const mExposure = getExposureMultiplier(item.visibility_tier);
  const mExclusive = isExclusive ? 1.4 : 1.0;

  const rawPrice = item.base_price_usd * mSize * mAudience * mExposure * mExclusive;
  
  // Round to nearest $10
  const finalPrice = Math.round(rawPrice / 10) * 10;

  return {
    total: finalPrice,
    breakdown: {
      base: item.base_price_usd,
      multipliers: {
        size: mSize,
        audience: mAudience,
        exposure: mExposure,
        exclusive: mExclusive
      }
    }
  };
};
