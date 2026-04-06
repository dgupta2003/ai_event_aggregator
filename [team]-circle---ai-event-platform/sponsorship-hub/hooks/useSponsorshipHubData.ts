import { useEvents } from '../../App';
import { EVENTS, SPONSORSHIP_MENU } from '../../constants';
import { Event, SponsorshipItem } from '../../types';

export const useSponsorshipHubData = () => {
  const { events, isLoading } = useEvents();

  const liveEvents: Event[] = events.length > 0 ? events : EVENTS;

  const sponsorableEvents: Event[] = liveEvents
    .filter(e => e.visibility === 'public' && e.attendees > 50)
    .sort((a, b) => b.attendees - a.attendees)
    .slice(0, 6);

  const highlightedItems: SponsorshipItem[] = SPONSORSHIP_MENU.filter(
    i => i.visibility_tier === 'HIGH',
  );

  const sampleItems: SponsorshipItem[] = SPONSORSHIP_MENU.slice(0, 4);

  return { sponsorableEvents, highlightedItems, sampleItems, isLoading };
};
