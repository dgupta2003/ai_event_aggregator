import { Event, Sponsor, User, SponsorshipItem } from './types';

export const MOCK_USER: User = {
  id: 'u1',
  name: 'Alex Rivera',
  email: 'alex@example.com',
  avatarUrl: 'https://picsum.photos/id/64/200/200',
  savedEventIds: ['e2'],
  attendedEventIds: [],
  hostedEventIds: [],
};

export const SPONSORS: Sponsor[] = [
  {
    id: 's1',
    name: 'TechFlow',
    logoUrl: 'https://picsum.photos/id/30/100/100',
    tier: 'Platinum',
    website: 'https://example.com',
    perks: ['VIP Lounge Access', 'Logo on Lanyards'],
  },
  {
    id: 's2',
    name: 'Nebula Drink',
    logoUrl: 'https://picsum.photos/id/88/100/100',
    tier: 'Gold',
    website: 'https://example.com',
    perks: ['Free Samples', 'Branded Bar'],
  },
  {
    id: 's3',
    name: 'CryptoSecure',
    logoUrl: 'https://picsum.photos/id/106/100/100',
    tier: 'Silver',
    website: 'https://example.com',
    perks: ['Booth Space'],
  },
  {
    id: 's4',
    name: 'GreenEat',
    logoUrl: 'https://picsum.photos/id/292/100/100',
    tier: 'Silver',
    website: 'https://example.com',
    perks: ['Catering', 'Sustainability Badge'],
  },
  {
    id: 's5',
    name: 'SoundWave',
    logoUrl: 'https://picsum.photos/id/145/100/100',
    tier: 'Gold',
    website: 'https://example.com',
    perks: ['Audio Equipment', 'DJ Booth'],
  },
  {
    id: 's6',
    name: 'Urban Threads',
    logoUrl: 'https://picsum.photos/id/177/100/100',
    tier: 'Platinum',
    website: 'https://example.com',
    perks: ['Merch Stand', 'Fashion Show Segment'],
  }
];

export const SPONSORSHIP_MENU: SponsorshipItem[] = [
  // A) Speaking & Stage
  {
    id: "sponsor_mention_1_2min",
    name: "1–2 min sponsor mention",
    description: "A brief mention of your brand by the host during the event.",
    category: "Speaking & Stage",
    base_price_usd: 150,
    visibility_tier: "HIGH"
  },
  {
    id: "stage_talk_3_5min",
    name: "3–5 min on stage",
    description: "A dedicated time slot for your representative to speak on stage.",
    category: "Speaking & Stage",
    base_price_usd: 350,
    visibility_tier: "HIGH"
  },
  {
    id: "panel_seat",
    name: "Panel seat",
    description: "A seat on one of the event's discussion panels.",
    category: "Speaking & Stage",
    base_price_usd: 500,
    visibility_tier: "HIGH"
  },
  {
    id: "opening_keynote",
    name: "Opening keynote slot",
    description: "The prestigious opening keynote slot to set the tone for the event.",
    category: "Speaking & Stage",
    base_price_usd: 800,
    visibility_tier: "HIGH"
  },

  // B) Physical / Digital Promotion
  {
    id: "swag_distribution",
    name: "Giveaways / swag distribution",
    description: "Distribution of your branded merchandise to attendees.",
    category: "Physical / Digital Promotion",
    base_price_usd: 120,
    visibility_tier: "MEDIUM"
  },
  {
    id: "demo_table",
    name: "Product demo table / booth",
    description: "A dedicated space for you to demonstrate your products.",
    category: "Physical / Digital Promotion",
    base_price_usd: 250,
    visibility_tier: "MEDIUM"
  },
  {
    id: "premium_booth",
    name: "Premium booth",
    description: "A larger, more prominent booth space in a high-traffic area.",
    category: "Physical / Digital Promotion",
    base_price_usd: 400,
    visibility_tier: "MEDIUM"
  },
  {
    id: "digital_goodie_link",
    name: "Digital goodie (QR / link)",
    description: "A digital offer or resource shared via QR code or link.",
    category: "Physical / Digital Promotion",
    base_price_usd: 90,
    visibility_tier: "LOW"
  },

  // C) Digital & Content Exposure
  {
    id: "logo_event_page",
    name: "Logo on event page",
    description: "Your logo featured prominently on the official event page.",
    category: "Digital & Content Exposure",
    base_price_usd: 80,
    visibility_tier: "LOW"
  },
  {
    id: "logo_checkin_screen",
    name: "Logo on check-in screen",
    description: "Your logo displayed on the screens at the event check-in.",
    category: "Digital & Content Exposure",
    base_price_usd: 120,
    visibility_tier: "MEDIUM"
  },
  {
    id: "email_mention_pre",
    name: "Mention in email blast",
    description: "Your brand mentioned in the pre-event email sent to all attendees.",
    category: "Digital & Content Exposure",
    base_price_usd: 150,
    visibility_tier: "LOW"
  },
  {
    id: "post_event_recap",
    name: "Mention in post-event recap",
    description: "Your brand mentioned in the post-event summary email.",
    category: "Digital & Content Exposure",
    base_price_usd: 120,
    visibility_tier: "LOW"
  },
  {
    id: "social_post_by_host",
    name: "Social post by host (1)",
    description: "A dedicated social media post about your brand by the event host.",
    category: "Digital & Content Exposure",
    base_price_usd: 140,
    visibility_tier: "LOW"
  },

  // D) Community / Access
  {
    id: "lead_capture_optin",
    name: "Lead capture opt-in",
    description: "Ability to collect contact information from interested attendees.",
    category: "Community / Access",
    base_price_usd: 300,
    visibility_tier: "MEDIUM"
  },
  {
    id: "networking_table",
    name: "Hosted networking table",
    description: "A branded table during networking sessions.",
    category: "Community / Access",
    base_price_usd: 250,
    visibility_tier: "MEDIUM"
  },
  {
    id: "private_side_session",
    name: "Private side session",
    description: "A private room or session for you to host specific guests.",
    category: "Community / Access",
    base_price_usd: 450,
    visibility_tier: "HIGH"
  }
];

export const EVENTS: Event[] = [
  {
    id: 'e1',
    title: 'UFC 308: Las Vegas Fight Night',
    description: 'The biggest fight night of the year returns to the T-Mobile Arena. Experience the thrill live.',
    date: '2025-11-09',
    time: '20:00',
    location: 'Las Vegas, NV',
    venueName: 'T-Mobile Arena',
    format: 'In-Person',
    imageUrl: 'https://picsum.photos/id/147/800/400',
    price: 214,
    category: 'Sports',
    hostId: 'h1',
    sponsorId: 's2',
    attendees: 14500,
    capacity: 20000,
    tags: ['MMA', 'Sports', 'Live'],
    isFeatured: true,
  },
  {
    id: 'e2',
    title: 'Future of AI Summit',
    description: 'Join industry leaders to discuss the next generation of generative models.',
    date: '2025-11-15',
    time: '09:00',
    location: 'San Francisco, CA',
    format: 'Hybrid',
    imageUrl: 'https://picsum.photos/id/20/800/400',
    price: 499,
    category: 'Tech',
    hostId: 'h2',
    sponsorId: 's1',
    attendees: 1200,
    capacity: 2000,
    tags: ['AI', 'Tech', 'Networking'],
  },
  {
    id: 'e3',
    title: 'Neon Art Exhibition',
    description: 'An immersive journey through light and sound.',
    date: '2025-11-20',
    time: '18:00',
    location: 'New York, NY',
    format: 'In-Person',
    imageUrl: 'https://picsum.photos/id/56/800/400',
    price: 45,
    category: 'Art',
    hostId: 'h3',
    attendees: 300,
    capacity: 500,
    tags: ['Art', 'Culture'],
  },
  {
    id: 'e4',
    title: 'Global Dev Conference',
    description: 'Streaming live to developers worldwide.',
    date: '2025-12-01',
    time: '10:00',
    location: 'Online',
    format: 'Online',
    imageUrl: 'https://picsum.photos/id/2/800/400',
    price: 0,
    category: 'Tech',
    hostId: 'h2',
    attendees: 5000,
    capacity: 10000,
    tags: ['Code', 'Web3', 'Cloud'],
  },
  {
    id: 'e5',
    title: 'UFC 309: Championship Bout',
    description: 'The championship belt is on the line.',
    date: '2025-11-16',
    time: '19:00',
    location: 'Las Vegas, NV',
    venueName: 'MGM Grand Arena',
    format: 'In-Person',
    imageUrl: 'https://picsum.photos/id/158/800/400',
    price: 350,
    category: 'Sports',
    hostId: 'h1',
    attendees: 8000,
    capacity: 16000,
    tags: ['MMA', 'Championship'],
  },
];