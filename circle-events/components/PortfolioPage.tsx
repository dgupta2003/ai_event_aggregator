
import React from 'react';
import { UserSponsorship, LuminaEvent } from '../types';
import { SPONSORSHIP_MENU } from '../constants';
import { calculateSponsorItemPrice } from '../services/pricingService';
import { ShieldCheck, Briefcase, Calendar, MapPin, ExternalLink, Award, Sparkles } from 'lucide-react';

interface PortfolioPageProps {
  packages: UserSponsorship[];
  events: LuminaEvent[];
  onEventClick: (event: LuminaEvent) => void;
}

const PortfolioPage: React.FC<PortfolioPageProps> = ({ packages, events, onEventClick }) => {
  if (packages.length === 0) {
    return (
      <div className="text-center py-24 bg-emerald-500/5 rounded-[3rem] border border-emerald-500/10 animate-in fade-in zoom-in-95 duration-500">
        <div className="w-24 h-24 bg-emerald-500/10 rounded-3xl flex items-center justify-center mx-auto mb-8">
          <Award className="w-12 h-12 text-emerald-500" />
        </div>
        <h2 className="text-4xl font-black text-white mb-4">No Active Partnerships</h2>
        <p className="text-slate-400 max-w-md mx-auto mb-10 font-medium">
          Start building your brand's presence by partnering with high-impact community events.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="grid grid-cols-1 gap-8">
        {packages.map((pkg) => {
          const event = events.find((e) => e.id === pkg.eventId);
          if (!event) return null;

          return (
            <div 
              key={`${pkg.eventId}-${pkg.timestamp}`}
              className="glass rounded-[2.5rem] overflow-hidden border-white/5 hover:border-emerald-500/30 transition-all group"
            >
              <div className="flex flex-col lg:flex-row">
                {/* Event Image & Core Info */}
                <div className="lg:w-1/3 relative h-64 lg:h-auto overflow-hidden">
                  <img 
                    src={event.image} 
                    alt={event.title} 
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent" />
                  <div className="absolute bottom-6 left-6 right-6">
                    <div className="flex items-center gap-2 mb-2">
                       <span className="bg-emerald-500 text-white text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-widest">Active Partner</span>
                    </div>
                    <h3 className="text-2xl font-black text-white mb-2">{event.title}</h3>
                    <div className="flex flex-col gap-1 text-slate-300 text-xs font-semibold">
                      <div className="flex items-center gap-2"><Calendar className="w-3 h-3 text-emerald-400" /> {event.date}</div>
                      <div className="flex items-center gap-2"><MapPin className="w-3 h-3 text-emerald-400" /> {event.location}</div>
                    </div>
                  </div>
                </div>

                {/* Sponsorship Breakdown */}
                <div className="flex-1 p-8 lg:p-10 bg-slate-900/40">
                  <div className="flex justify-between items-start mb-8">
                    <div>
                      <h4 className="text-xs font-black text-emerald-500 uppercase tracking-[0.2em] mb-1">Your Sponsorship Package</h4>
                      <p className="text-slate-500 text-sm">Secured on {new Date(pkg.timestamp).toLocaleDateString()}</p>
                    </div>
                    <button 
                      onClick={() => onEventClick(event)}
                      className="p-3 bg-white/5 rounded-2xl text-white hover:bg-white/10 transition-colors"
                    >
                      <ExternalLink className="w-5 h-5" />
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {pkg.items.map((itemId) => {
                      const item = SPONSORSHIP_MENU.find((i) => i.id === itemId);
                      if (!item) return null;
                      
                      const isExclusive = pkg.exclusiveItems.includes(itemId);
                      const pricing = calculateSponsorItemPrice(item, event.sponsorshipSettings!, isExclusive);

                      return (
                        <div key={itemId} className={`p-5 rounded-2xl border transition-all ${isExclusive ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-white/5 border-white/5'}`}>
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-sm font-bold text-white">{item.name}</span>
                                {isExclusive && <ShieldCheck className="w-3 h-3 text-emerald-400" />}
                              </div>
                              <span className="text-[10px] font-black text-slate-500 uppercase tracking-tighter bg-white/5 px-1.5 py-0.5 rounded">{item.category}</span>
                            </div>
                            <span className={`text-sm font-black ${isExclusive ? 'text-emerald-400' : 'text-slate-300'}`}>${pricing.total}</span>
                          </div>
                          <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">{item.description}</p>
                          {isExclusive && (
                            <div className="mt-3 flex items-center gap-1 text-[9px] font-black text-emerald-500 uppercase tracking-widest">
                              <Sparkles className="w-2.5 h-2.5" /> Category Exclusivity Locked
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  <div className="mt-8 pt-8 border-t border-white/5 flex flex-col sm:flex-row justify-between items-center gap-6">
                    <div className="flex items-center gap-6">
                      <div className="text-center sm:text-left">
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Total Investment</p>
                        <p className="text-2xl font-black text-white">${pkg.items.reduce((acc, id) => {
                           const itm = SPONSORSHIP_MENU.find(i => i.id === id)!;
                           return acc + calculateSponsorItemPrice(itm, event.sponsorshipSettings!, pkg.exclusiveItems.includes(id)).total;
                        }, 0).toLocaleString()}</p>
                      </div>
                      <div className="w-[1px] h-8 bg-white/10 hidden sm:block" />
                      <div className="text-center sm:text-left">
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Impact Tier</p>
                        <p className="text-2xl font-black text-indigo-400">Premium</p>
                      </div>
                    </div>
                    <button 
                      onClick={() => alert("Digital assets coming soon! Contact support for custom banners.")}
                      className="px-8 py-3 bg-emerald-500 text-white rounded-xl font-bold text-sm hover:bg-emerald-600 transition-all shadow-xl shadow-emerald-500/20 active:scale-95 flex items-center gap-2"
                    >
                      <Briefcase className="w-4 h-4" /> Download Assets
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PortfolioPage;
