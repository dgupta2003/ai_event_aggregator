import React from 'react';
import { Users, MapPin, ArrowRight, TrendingUp } from 'lucide-react';
import { Event } from '../types';
import { SPONSORSHIP_MENU } from '../constants/sponsorship';
import { calculateSponsorItemPrice } from '../services/pricingService';

interface OpportunityCardProps {
  event: Event;
  onViewPackages: () => void;
}

const OpportunityCard: React.FC<OpportunityCardProps> = ({ event, onViewPackages }) => {
  const settings = event.sponsorshipSettings ?? {
    allowed_item_ids: SPONSORSHIP_MENU.map(i => i.id),
    expected_attendance: event.attendees,
    audience_type: 'professionals' as const,
    allow_exclusivity: true,
  };

  const cheapestItem = SPONSORSHIP_MENU.find(i => i.visibility_tier === 'LOW');
  const premiumItem = SPONSORSHIP_MENU.find(i => i.visibility_tier === 'HIGH');

  const minPrice = cheapestItem
    ? calculateSponsorItemPrice(cheapestItem, settings, false).final
    : 0;
  const maxPrice = premiumItem
    ? calculateSponsorItemPrice(premiumItem, settings, false).final
    : 0;

  const fillPct = Math.min(100, Math.round((event.attendees / event.capacity) * 100));

  return (
    <div className="glass-card rounded-2xl border border-white/5 overflow-hidden group hover:border-purple-500/30 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/10 flex flex-col">
      {/* Image */}
      <div className="relative h-40 overflow-hidden shrink-0">
        <img
          src={event.imageUrl}
          alt={event.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
        <div className="absolute top-3 left-3 px-2 py-1 rounded-md bg-black/60 backdrop-blur text-[10px] font-bold uppercase tracking-wider text-purple-300 border border-purple-500/30">
          {event.format}
        </div>
        <div className="absolute top-3 right-3 px-2 py-1 rounded-md bg-black/60 backdrop-blur text-[10px] font-bold text-white">
          {event.category}
        </div>
      </div>

      {/* Content */}
      <div className="p-5 space-y-4 flex flex-col flex-1">
        <div>
          <h3 className="text-white font-bold text-base leading-tight mb-1 line-clamp-2">
            {event.title}
          </h3>
          <div className="flex items-center gap-1 text-gray-500 text-xs">
            <MapPin className="w-3 h-3 shrink-0" />
            {event.location} ·{' '}
            {new Date(event.date).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
            })}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 rounded-xl bg-white/3 border border-white/5">
            <div className="flex items-center gap-1.5 text-purple-400 mb-1">
              <Users className="w-3.5 h-3.5" />
              <span className="text-white font-bold text-sm">
                {event.attendees.toLocaleString()}
              </span>
            </div>
            <p className="text-[10px] text-gray-600">Attendees</p>
          </div>
          <div className="p-3 rounded-xl bg-white/3 border border-white/5">
            <div className="flex items-center gap-1.5 text-cyan-400 mb-1">
              <TrendingUp className="w-3.5 h-3.5" />
              <span className="text-white font-bold text-sm">{fillPct}%</span>
            </div>
            <p className="text-[10px] text-gray-600">Venue fill</p>
          </div>
        </div>

        {/* Pricing + CTA */}
        <div className="flex items-center justify-between pt-1 border-t border-white/5 mt-auto">
          <div>
            <p className="text-[10px] text-gray-600 uppercase tracking-wider">Sponsor from</p>
            <p className="text-white font-bold text-sm">
              ${minPrice.toLocaleString()}{' '}
              <span className="text-gray-500 font-normal text-xs">
                – ${maxPrice.toLocaleString()}
              </span>
            </p>
          </div>
          <button
            onClick={onViewPackages}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-purple-600/20 hover:bg-purple-600/40 text-purple-300 text-xs font-bold transition-colors border border-purple-500/20"
          >
            View Packages
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default OpportunityCard;
