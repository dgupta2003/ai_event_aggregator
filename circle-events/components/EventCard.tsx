
import React from 'react';
import { LuminaEvent } from '../types';
import { MapPin, Calendar, Users, ArrowUpRight } from 'lucide-react';

interface EventCardProps {
  event: LuminaEvent;
  onClick: (event: LuminaEvent) => void;
}

const EventCard: React.FC<EventCardProps> = ({ event, onClick }) => {
  return (
    <div 
      onClick={() => onClick(event)}
      className="group relative cursor-pointer glass rounded-2xl overflow-hidden transition-all duration-500 hover:scale-[1.02] hover:glow active:scale-95"
    >
      <div className="aspect-video overflow-hidden">
        <img 
          src={event.image} 
          alt={event.title} 
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110 opacity-80 group-hover:opacity-100"
        />
        <div className="absolute top-4 left-4 bg-white/10 backdrop-blur-md px-3 py-1 rounded-full border border-white/10 text-xs font-medium uppercase tracking-wider">
          {event.category}
        </div>
      </div>
      
      <div className="p-5 space-y-4">
        <div className="flex justify-between items-start">
          <h3 className="text-xl font-bold text-white group-hover:text-indigo-400 transition-colors">
            {event.title}
          </h3>
          <ArrowUpRight className="w-5 h-5 text-slate-500 group-hover:text-white transition-all opacity-0 group-hover:opacity-100 -translate-x-2 group-hover:translate-x-0" />
        </div>
        
        <div className="grid grid-cols-2 gap-3 text-sm text-slate-400">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-indigo-500" />
            <span>{event.date}</span>
          </div>
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-violet-500" />
            <span className="truncate">{event.location}</span>
          </div>
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-cyan-500" />
            <span>{event.attendeesCount}+ attending</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${event.type === 'online' ? 'bg-emerald-500' : event.type === 'hybrid' ? 'bg-amber-500' : 'bg-rose-500'}`} />
            <span className="capitalize">{event.type}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EventCard;
