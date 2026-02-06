
export type VisibilityTier = 'LOW' | 'MEDIUM' | 'HIGH';
export type AudienceType = 'general_public' | 'students_earlycareer' | 'professionals' | 'founders_operators' | 'executives_investors';

export interface SponsorshipItem {
  id: string;
  name: string;
  description: string;
  category: 'Speaking' | 'Promotion' | 'Digital' | 'Access';
  base_price_usd: number;
  visibility_tier: VisibilityTier;
}

export interface EventSponsorshipSettings {
  allowed_item_ids: string[];
  expected_attendance: number;
  audience_type: AudienceType;
  allow_exclusivity: boolean;
}

export interface UserSponsorship {
  eventId: string;
  items: string[];
  exclusiveItems: string[];
  timestamp: number;
}

export interface LuminaEvent {
  id: string;
  title: string;
  description: string;
  date: string;
  time: string;
  location: string;
  type: 'online' | 'in-person' | 'hybrid';
  category: 'Tech' | 'Design' | 'Business' | 'Music' | 'Art';
  image: string;
  hostName: string;
  attendeesCount: number;
  sponsorshipOptIn?: boolean;
  sponsorshipSettings?: EventSponsorshipSettings;
  exclusiveItemsSponsored?: string[]; // IDs of items that are no longer available due to exclusivity
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  hostedEvents: string[];
  joinedEvents: string[];
}
