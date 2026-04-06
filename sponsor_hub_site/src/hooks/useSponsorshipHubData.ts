import { useState, useEffect } from 'react';
import { fetchEvents } from '../services/api';
import { SPONSORSHIP_MENU, FALLBACK_EVENTS } from '../constants/sponsorship';
import { Event, SponsorshipItem } from '../types';

export const useSponsorshipHubData = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchEvents()
      .then(data => setEvents(data))
      .catch(() => setEvents(FALLBACK_EVENTS))
      .finally(() => setIsLoading(false));
  }, []);

  const liveEvents: Event[] = events.length > 0 ? events : FALLBACK_EVENTS;

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
