
import React, { useState, useMemo } from 'react';
import { LuminaEvent, SponsorshipItem } from '../types';
import { SPONSORSHIP_MENU } from '../constants';
import { calculateSponsorItemPrice } from '../services/pricingService';
import { ShoppingCart, ShieldCheck, Briefcase, ChevronRight, Info, Plus, Check, Handshake, InfoIcon, X, Loader2, Sparkles, Trash2 } from 'lucide-react';

interface SponsorMenuProps {
  event: LuminaEvent;
  onSponsor: (items: string[], exclusiveIds: string[]) => void;
  isProcessing: boolean;
}

const SponsorMenu: React.FC<SponsorMenuProps> = ({ event, onSponsor, isProcessing }) => {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [exclusiveIds, setExclusiveIds] = useState<string[]>([]);
  const [showBreakdown, setShowBreakdown] = useState<string | null>(null);

  const allowedItems = useMemo(() => {
    const ids = event.sponsorshipSettings?.allowed_item_ids || [];
    const exclusiveBlocked = event.exclusiveItemsSponsored || [];
    
    // Filter out items that are either not allowed by host OR have been exclusively claimed already
    return SPONSORSHIP_MENU.filter(item => 
      ids.includes(item.id) && !exclusiveBlocked.includes(item.id)
    );
  }, [event]);

  const toggleItem = (id: string) => {
    setSelectedIds(prev => {
      const isSelected = prev.includes(id);
      if (isSelected) {
        setExclusiveIds(ex => ex.filter(i => i !== id));
        return prev.filter(i => i !== id);
      }
      return [...prev, id];
    });
  };

  const toggleExclusive = (id: string) => {
    if (!event.sponsorshipSettings?.allow_exclusivity) return;
    setExclusiveIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const cartItems = useMemo(() => {
    return selectedIds.map(id => {
      const item = SPONSORSHIP_MENU.find(i => i.id === id)!;
      const isExclusive = exclusiveIds.includes(id);
      const calculation = calculateSponsorItemPrice(
        item, 
        event.sponsorshipSettings!, 
        isExclusive
      );
      return { ...item, ...calculation, isExclusive };
    });
  }, [selectedIds, exclusiveIds, event.sponsorshipSettings]);

  const total = useMemo(() => cartItems.reduce((acc, curr) => acc + curr.total, 0), [cartItems]);

  if (!event.sponsorshipSettings) return null;

  return (
    <div className="space-y-6 animate-in fade-in duration-500 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-emerald-400" />
            Partnership Marketplace
          </h3>
          <p className="text-xs text-slate-500">AI-optimized rates for {event.title}</p>
        </div>
        <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest bg-white/5 px-2 py-1 rounded">
          {allowedItems.length} Options Available
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 overflow-y-auto pr-2 custom-scrollbar flex-1 max-h-[350px]">
        {allowedItems.length > 0 ? (
          allowedItems.map(item => {
            const isSelected = selectedIds.includes(item.id);
            const isExclusive = exclusiveIds.includes(item.id);
            const pricing = calculateSponsorItemPrice(item, event.sponsorshipSettings!, isExclusive);
            
            return (
              <div 
                key={item.id}
                className={`p-4 rounded-2xl border transition-all ${isSelected ? 'bg-emerald-500/10 border-emerald-500/30 ring-1 ring-emerald-500/20' : 'bg-slate-900/40 border-white/5 hover:border-white/10'}`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-bold text-white">{item.name}</h4>
                      <span className={`text-[9px] px-1.5 py-0.5 rounded font-black uppercase tracking-tighter ${item.visibility_tier === 'HIGH' ? 'bg-amber-500/20 text-amber-500' : item.visibility_tier === 'MEDIUM' ? 'bg-indigo-500/20 text-indigo-400' : 'bg-slate-700 text-slate-400'}`}>
                        {item.visibility_tier} IMPACT
                      </span>
                      {isExclusive && (
                        <span className="bg-emerald-500/20 text-emerald-400 text-[9px] px-1.5 py-0.5 rounded font-black uppercase flex items-center gap-1">
                          <ShieldCheck className="w-2 h-2" /> Exclusive
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 line-clamp-2">{item.description}</p>
                  </div>
                  
                  <div className="flex flex-col items-end gap-2 shrink-0">
                    <div className="text-right">
                      <span className={`text-lg font-black transition-colors ${isExclusive ? 'text-emerald-400' : 'text-white'}`}>
                        ${pricing.total}
                      </span>
                      <button 
                        onClick={() => setShowBreakdown(showBreakdown === item.id ? null : item.id)}
                        className="ml-2 p-1 text-slate-500 hover:text-white transition-colors"
                      >
                        <InfoIcon className="w-3 h-3" />
                      </button>
                    </div>
                    <button 
                      onClick={() => toggleItem(item.id)}
                      className={`px-4 py-1.5 rounded-lg font-bold text-xs transition-all ${isSelected ? 'bg-emerald-500 text-white' : 'bg-white/10 text-white hover:bg-white/20'}`}
                    >
                      {isSelected ? 'Remove' : 'Select'}
                    </button>
                  </div>
                </div>

                {isSelected && event.sponsorshipSettings?.allow_exclusivity && (
                  <div className="mt-4 pt-3 border-t border-emerald-500/10 flex items-center justify-between bg-emerald-500/5 -mx-4 px-4 -mb-4 rounded-b-2xl py-3">
                    <div className="flex items-center gap-2">
                      <ShieldCheck className={`w-4 h-4 ${isExclusive ? 'text-emerald-400' : 'text-slate-600'}`} />
                      <div>
                        <span className="text-xs font-bold text-slate-200 block">Category Exclusivity</span>
                        <span className="text-[10px] text-slate-500">Block competitors for +40% premium</span>
                      </div>
                    </div>
                    <button 
                      onClick={() => toggleExclusive(item.id)}
                      className={`w-10 h-5 rounded-full relative transition-colors ${isExclusive ? 'bg-emerald-500' : 'bg-slate-800'}`}
                    >
                      <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${isExclusive ? 'left-[22px]' : 'left-0.5'}`} />
                    </button>
                  </div>
                )}

                {showBreakdown === item.id && (
                  <div className="mt-3 p-3 bg-black/40 rounded-xl border border-white/5 animate-in slide-in-from-top-1 duration-200">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-[10px] font-bold text-slate-500 uppercase">Dynamic Pricing Breakdown</span>
                      <X className="w-3 h-3 text-slate-500 cursor-pointer" onClick={() => setShowBreakdown(null)} />
                    </div>
                    <div className="grid grid-cols-2 gap-y-1.5 gap-x-4">
                      <div className="flex justify-between text-[11px]"><span className="text-slate-400">Base Price:</span> <span className="text-white">${pricing.breakdown.base}</span></div>
                      <div className="flex justify-between text-[11px]"><span className="text-slate-400">Scale Factor:</span> <span className="text-white">{pricing.breakdown.multipliers.size}x</span></div>
                      <div className="flex justify-between text-[11px]"><span className="text-slate-400">Audience Tier:</span> <span className="text-white">{pricing.breakdown.multipliers.audience}x</span></div>
                      <div className="flex justify-between text-[11px]"><span className="text-slate-400">Exposure:</span> <span className="text-white">{pricing.breakdown.multipliers.exposure}x</span></div>
                      {isExclusive && (
                        <div className="flex justify-between text-[11px] col-span-2 text-emerald-400 pt-1 border-t border-emerald-500/10"><span className="font-bold">Exclusivity Premium:</span> <span className="font-bold">1.4x</span></div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-center bg-slate-900/40 rounded-3xl border border-white/5">
            <ShieldCheck className="w-12 h-12 text-slate-700 mb-4" />
            <h4 className="text-white font-bold mb-1">Categories Locked</h4>
            <p className="text-xs text-slate-500 max-w-[200px]">All available packages for this event have been exclusively claimed.</p>
          </div>
        )}
      </div>

      {selectedIds.length > 0 && (
        <div className="mt-4 glass p-6 rounded-[2rem] border-emerald-500/30 bg-emerald-500/5 animate-in slide-in-from-bottom-4 duration-300">
          <div className="space-y-4 mb-6">
            <h4 className="text-xs font-black text-emerald-500 uppercase tracking-[0.2em]">Sponsorship Summary</h4>
            <div className="space-y-2 max-h-[120px] overflow-y-auto pr-2 custom-scrollbar">
              {cartItems.map(item => (
                <div key={item.id} className="flex items-center justify-between text-sm py-1 border-b border-white/5 last:border-0">
                  <div className="flex flex-col">
                    <span className="text-white font-medium">{item.name}</span>
                    {item.isExclusive && (
                      <span className="text-[10px] text-emerald-400 font-bold flex items-center gap-1">
                        <ShieldCheck className="w-2 h-2" /> Exclusive Partnership
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`font-bold ${item.isExclusive ? 'text-emerald-400' : 'text-slate-300'}`}>${item.total}</span>
                    <button onClick={() => toggleItem(item.id)} className="text-slate-600 hover:text-rose-500 transition-colors">
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-between items-end mb-6 pt-4 border-t border-white/10">
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Total Investment</p>
              <h4 className="text-4xl font-black text-white flex items-center gap-2">
                ${total.toLocaleString()}
                <Sparkles className="w-5 h-5 text-emerald-400 animate-pulse" />
              </h4>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-400">{selectedIds.length} Packages</p>
              <p className="text-[9px] text-slate-600 uppercase font-bold tracking-tighter">AI Estimated Pricing</p>
            </div>
          </div>
          
          <button 
            disabled={isProcessing}
            onClick={() => onSponsor(selectedIds, exclusiveIds)}
            className="w-full py-4 bg-emerald-500 text-white rounded-2xl font-black text-lg hover:bg-emerald-600 shadow-xl shadow-emerald-500/20 active:scale-95 transition-all flex items-center justify-center gap-2 group"
          >
            {isProcessing ? (
              <Loader2 className="w-6 h-6 animate-spin" />
            ) : (
              <>
                <ShoppingCart className="w-5 h-5 group-hover:rotate-12 transition-transform" />
                Confirm & Secure Sponsorship
              </>
            )}
          </button>
          
          <p className="text-[10px] text-center text-slate-500 mt-4 px-8">
            By confirming, you agree to Circle's partnership terms. Secure checkout via Stripe.
          </p>
        </div>
      )}
    </div>
  );
};

export default SponsorMenu;
