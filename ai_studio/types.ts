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