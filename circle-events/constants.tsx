
import { LuminaEvent, SponsorshipItem, AudienceType } from './types';

export const AUDIENCE_LABELS: Record<AudienceType, string> = {
  general_public: 'General Public',
  students_earlycareer: 'Students & Early Career',
  professionals: 'Industry Professionals',
  founders_operators: 'Founders & Operators',
  executives_investors: 'Executives & Investors'
};

export const SPONSORSHIP_MENU: SponsorshipItem[] = [
  // Speaking & Stage
  { id: 'sponsor_mention_1_2min', name: '1–2 min sponsor mention', description: 'Host mentions your brand during opening or closing.', category: 'Speaking', base_price_usd: 150, visibility_tier: 'HIGH' },
  { id: 'stage_talk_3_5min', name: '3–5 min on stage', description: 'A dedicated lightning talk slot for your representative.', category: 'Speaking', base_price_usd: 350, visibility_tier: 'HIGH' },
  { id: 'panel_seat', name: 'Panel seat', description: 'One seat on an official event discussion panel.', category: 'Speaking', base_price_usd: 500, visibility_tier: 'HIGH' },
  { id: 'opening_keynote', name: 'Opening keynote slot', description: 'Premium 15-min keynote slot at event kickoff.', category: 'Speaking', base_price_usd: 800, visibility_tier: 'HIGH' },
  
  // Physical / Digital Promotion
  { id: 'swag_distribution', name: 'Giveaways / swag distribution', description: 'Distribute branded items to all attendees.', category: 'Promotion', base_price_usd: 120, visibility_tier: 'MEDIUM' },
  { id: 'demo_table', name: 'Product demo table / booth', description: 'Standard exhibit space in the main networking area.', category: 'Promotion', base_price_usd: 250, visibility_tier: 'MEDIUM' },
  { id: 'premium_booth', name: 'Premium booth', description: 'Double-sized booth in a high-traffic entrance area.', category: 'Promotion', base_price_usd: 400, visibility_tier: 'MEDIUM' },
  { id: 'digital_goodie_link', name: 'Digital goodie (QR / link)', description: 'Placement in the digital attendee resource pack.', category: 'Promotion', base_price_usd: 90, visibility_tier: 'LOW' },

  // Digital & Content Exposure
  { id: 'logo_event_page', name: 'Logo on event page', description: 'Your brand logo featured in the partner section.', category: 'Digital', base_price_usd: 80, visibility_tier: 'LOW' },
  { id: 'logo_checkin_screen', name: 'Logo on check-in screen', description: 'First brand seen by attendees upon arrival.', category: 'Digital', base_price_usd: 120, visibility_tier: 'MEDIUM' },
  { id: 'email_mention_pre', name: 'Mention in email blast', description: 'Logo and 50 words in pre-event logistics email.', category: 'Digital', base_price_usd: 150, visibility_tier: 'LOW' },
  { id: 'post_event_recap', name: 'Mention in post-event recap', description: 'Thank you mention in the final event summary.', category: 'Digital', base_price_usd: 120, visibility_tier: 'LOW' },
  { id: 'social_post_by_host', name: 'Social post by host (1)', description: 'One dedicated shout-out on host social channels.', category: 'Digital', base_price_usd: 140, visibility_tier: 'LOW' },

  // Community / Access
  { id: 'lead_capture_optin', name: 'Lead capture opt-in', description: 'Access to opt-in attendee email list.', category: 'Access', base_price_usd: 300, visibility_tier: 'MEDIUM' },
  { id: 'networking_table', name: 'Hosted networking table', description: 'Branded table during lunch or networking hours.', category: 'Access', base_price_usd: 250, visibility_tier: 'MEDIUM' },
  { id: 'private_side_session', name: 'Private side session', description: 'Exclusive room for a private workshop or meeting.', category: 'Access', base_price_usd: 450, visibility_tier: 'HIGH' },
];

export const MOCK_EVENTS: LuminaEvent[] = [
  {
    id: '1',
    title: 'Future of AI Summit',
    description: 'Explore the next decade of artificial intelligence with industry leaders.',
    date: 'Oct 24, 2024',
    time: '10:00 AM PST',
    location: 'San Francisco, CA',
    type: 'hybrid',
    category: 'Tech',
    image: 'https://picsum.photos/seed/ai/800/600',
    hostName: 'Nexus Tech',
    attendeesCount: 1240,
    sponsorshipOptIn: true,
    sponsorshipSettings: {
      allowed_item_ids: ['opening_keynote', 'demo_table', 'logo_event_page', 'lead_capture_optin'],
      expected_attendance: 1200,
      audience_type: 'executives_investors',
      allow_exclusivity: true
    }
  },
  {
    id: '2',
    title: 'Design Systems 2024',
    description: 'Master the art of building scalable design systems for modern SaaS.',
    date: 'Nov 12, 2024',
    time: '02:00 PM EST',
    location: 'Online Only',
    type: 'online',
    category: 'Design',
    image: 'https://picsum.photos/seed/design/800/600',
    hostName: 'Studio Aura',
    attendeesCount: 850
  },
  {
    id: '3',
    title: 'Minimalist Architecture Expo',
    description: 'A deep dive into functional minimalism in modern residential architecture.',
    date: 'Dec 05, 2024',
    time: '11:00 AM CET',
    location: 'Berlin, DE',
    type: 'in-person',
    category: 'Art',
    image: 'https://picsum.photos/seed/arch/800/600',
    hostName: 'Bauhaus Modern',
    attendeesCount: 320,
    sponsorshipOptIn: true,
    sponsorshipSettings: {
      allowed_item_ids: ['logo_event_page', 'swag_distribution', 'panel_seat'],
      expected_attendance: 350,
      audience_type: 'professionals',
      allow_exclusivity: false
    }
  },
  {
    id: '4',
    title: 'Web3 Gaming Night',
    description: 'The intersection of blockchain and competitive gaming.',
    date: 'Oct 29, 2024',
    time: '07:00 PM PST',
    location: 'Online Only',
    type: 'online',
    category: 'Tech',
    image: 'https://picsum.photos/seed/gaming/800/600',
    hostName: 'Metaverse GRP',
    attendeesCount: 2100
  },
  {
    id: '5',
    title: 'Venture Capital 101',
    description: 'Learning the ropes of fundraising for early stage startups.',
    date: 'Nov 02, 2024',
    time: '09:00 AM PST',
    location: 'Palo Alto, CA',
    type: 'in-person',
    category: 'Business',
    image: 'https://picsum.photos/seed/biz/800/600',
    hostName: 'Sand Hill Academy',
    attendeesCount: 150
  }
];
