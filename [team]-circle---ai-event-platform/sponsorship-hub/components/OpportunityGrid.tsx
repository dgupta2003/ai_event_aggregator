import React from 'react';
import { Loader2, Search } from 'lucide-react';
import { Event } from '../../types';
import OpportunityCard from './OpportunityCard';

interface OpportunityGridProps {
  events: Event[];
  isLoading: boolean;
}

const OpportunityGrid: React.FC<OpportunityGridProps> = ({ events, isLoading }) => {
  return (
    <section className="py-24 px-4">
      <div className="max-w-5xl mx-auto space-y-10">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-white">Open Opportunities</h2>
            <p className="text-gray-400 mt-2">
              Events currently seeking sponsors. Prices are live and audience-adjusted.
            </p>
          </div>
          {events.length > 0 && (
            <span className="text-sm text-gray-500 shrink-0">
              {events.length} event{events.length !== 1 ? 's' : ''} available
            </span>
          )}
        </div>

        {/* States */}
        {isLoading ? (
          <div className="py-24 flex flex-col items-center gap-4 text-gray-500">
            <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
            <p className="text-sm">Loading opportunities…</p>
          </div>
        ) : events.length === 0 ? (
          <div className="py-24 flex flex-col items-center gap-4 text-center">
            <div className="w-16 h-16 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
              <Search className="w-7 h-7 text-gray-500" />
            </div>
            <div>
              <p className="text-white font-bold text-lg">No opportunities yet</p>
              <p className="text-gray-500 text-sm mt-1 max-w-sm">
                Be the first to configure sponsorship settings on your event and appear here.
              </p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {events.map(event => (
              <OpportunityCard key={event.id} event={event} />
            ))}
          </div>
        )}
      </div>
    </section>
  );
};

export default OpportunityGrid;
