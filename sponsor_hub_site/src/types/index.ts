export type EventFormat = 'Online' | 'In-Person' | 'Hybrid';
export type VisibilityTier = 'LOW' | 'MEDIUM' | 'HIGH';
export type AudienceType =
  | 'general_public'
  | 'students_earlycareer'
  | 'professionals'
  | 'founders_operators'
  | 'executives_investors';

export interface SponsorshipItem {
  id: string;
  name: string;
  description: string;
  category:
    | 'Speaking & Stage'
    | 'Physical / Digital Promotion'
    | 'Digital & Content Exposure'
    | 'Community / Access';
  base_price_usd: number;
  visibility_tier: VisibilityTier;
}

export interface EventSponsorshipSettings {
  allowed_item_ids: string[];
  expected_attendance: number;
  audience_type: AudienceType;
  allow_exclusivity: boolean;
}

export interface Event {
  id: string;
  title: string;
  description: string;
  date: string;
  time: string;
  location: string;
  venueName?: string;
  format: EventFormat;
  imageUrl: string;
  price: number;
  category: string;
  hostId: string;
  sponsorId?: string;
  attendees: number;
  capacity: number;
  tags: string[];
  isFeatured?: boolean;
  sponsorshipSettings?: EventSponsorshipSettings;
  visibility: 'public' | 'private';
  createdAt?: string;
  updatedAt?: string;
  hostName?: string;
}
