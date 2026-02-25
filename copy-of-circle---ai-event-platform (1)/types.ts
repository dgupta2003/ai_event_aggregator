export type EventFormat = 'Online' | 'In-Person' | 'Hybrid';
export type SponsorTier = 'Platinum' | 'Gold' | 'Silver' | 'Bronze';

export interface Sponsor {
  id: string;
  name: string;
  logoUrl: string;
  tier: SponsorTier;
  website: string;
  perks: string[];
}

export type VisibilityTier = 'LOW' | 'MEDIUM' | 'HIGH';
export type AudienceType = 'general_public' | 'students_earlycareer' | 'professionals' | 'founders_operators' | 'executives_investors';

export interface SponsorshipItem {
  id: string;
  name: string;
  description: string;
  category: 'Speaking & Stage' | 'Physical / Digital Promotion' | 'Digital & Content Exposure' | 'Community / Access';
  base_price_usd: number;
  visibility_tier: VisibilityTier;
}

export interface EventSponsorshipSettings {
  allowed_item_ids: string[];
  expected_attendance: number;
  audience_type: AudienceType;
  allow_exclusivity: boolean;
}

export interface SponsorSelection {
  selected_item_ids: string[];
  exclusivity_selected_item_ids: string[];
}

export interface Event {
  id: string;
  title: string;
  description: string;
  date: string; // ISO String
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
}

export interface SponsorshipProposal {
  id: string;
  eventId: string;
  eventTitle: string;
  senderId: string;
  senderName: string;
  receiverId: string;
  message: string;
  status: 'pending' | 'accepted' | 'declined';
  timestamp: number;
  estimatedInvestment: number;
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatarUrl: string;
  savedEventIds: string[];
  attendedEventIds: string[];
  hostedEventIds: string[];
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: number;
  action?: 'show_events' | 'show_map' | 'confirm_ticket';
  data?: any;
}

export interface TicketSelection {
  section: string;
  row: string;
  seat: string;
  price: number;
  id: string;
}