import { Event } from '../types';

const BASE = '/api';

export const fetchEvents = async (): Promise<Event[]> => {
  const res = await fetch(`${BASE}/events`);
  if (!res.ok) throw new Error(`Failed to fetch events: ${res.status}`);
  const data = await res.json();
  // Backend returns { events: Event[] }
  return Array.isArray(data) ? data : (data.events ?? []);
};
