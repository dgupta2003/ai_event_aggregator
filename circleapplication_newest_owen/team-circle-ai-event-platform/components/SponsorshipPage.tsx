import React, { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Check, ChevronRight, Info, ShoppingCart, 
  Zap, Users, Target, Shield, ArrowLeft,
  LayoutGrid, Mic2, Megaphone, Globe, Plus, Minus,
  Mail, Send, X
} from 'lucide-react';
import { SPONSORSHIP_MENU } from '../constants';
import { 
  SponsorshipItem, 
  EventSponsorshipSettings, 
  SponsorSelection, 
  AudienceType,
  Event,
  SponsorshipProposal
} from '../types';
import { calculateSponsorItemPrice, PricingBreakdown } from '../services/pricingService';
import { useEvents } from '../App';

// --- Components ---

const Badge = ({ children, variant = 'default' }: { children: React.ReactNode, variant?: 'default' | 'high' | 'medium' | 'low' }) => {
  const styles = {
    default: 'bg-gray-100 text-gray-600',
    high: 'bg-teal-50 text-teal-600 border border-teal-200',
    medium: 'bg-cyan-50 text-cyan-600 border border-cyan-200',
    low: 'bg-emerald-50 text-emerald-600 border border-emerald-200'
  };
  return (
    <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${styles[variant]}`}>
      {children}
    </span>
  );
};

const PricingBreakdownView = ({ breakdown }: { breakdown: PricingBreakdown }) => {
  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-2 text-xs">
      <div className="flex justify-between text-gray-500">
        <span>Base Price</span>
        <span>${breakdown.base}</span>
      </div>
      <div className="flex justify-between text-gray-500">
        <span>Size Multiplier (Attendance)</span>
        <span>x{breakdown.sizeMult}</span>
      </div>
      <div className="flex justify-between text-gray-500">
        <span>Audience Multiplier</span>
        <span>x{breakdown.audienceMult}</span>
      </div>
      <div className="flex justify-between text-gray-500">
        <span>Exposure Multiplier ({breakdown.exposureMult === 1.5 ? 'High' : breakdown.exposureMult === 1.2 ? 'Medium' : 'Low'})</span>
        <span>x{breakdown.exposureMult}</span>
      </div>
      {breakdown.exclusiveMult > 1 && (
        <div className="flex justify-between text-teal-500 font-medium">
          <span>Category Exclusivity</span>
          <span>x{breakdown.exclusiveMult}</span>
        </div>
      )}
      <div className="pt-2 border-t border-gray-200 flex justify-between text-gray-800 font-bold text-sm">
        <span>Final Price</span>
        <span className="text-glow">${breakdown.final}</span>
      </div>
    </div>
  );
};

export const SponsorshipPage = ({ 
  event, 
  mode = 'sponsor',
  onUpdateSettings
}: { 
  event: Event, 
  mode?: 'host' | 'sponsor',
  onUpdateSettings?: (settings: EventSponsorshipSettings) => void
}) => {
  const navigate = useNavigate();
  const { createProposal, user } = useEvents();
  
  // Host State
  const [hostSettings, setHostSettings] = useState<EventSponsorshipSettings>(
    event.sponsorshipSettings || {
      allowed_item_ids: SPONSORSHIP_MENU.map(i => i.id),
      expected_attendance: event.attendees || 100,
      audience_type: 'professionals',
      allow_exclusivity: true
    }
  );

  // Sponsor State
  const [selection, setSelection] = useState<SponsorSelection>({
    selected_item_ids: [],
    exclusivity_selected_item_ids: []
  });

  const [expandedItemId, setExpandedItemId] = useState<string | null>(null);
  const [showNegotiateComposer, setShowNegotiateComposer] = useState(false);
  const [negotiateMessage, setNegotiateMessage] = useState('');

  const handleNegotiate = () => {
    if (!user) {
      navigate('/auth');
      return;
    }

    const selectedItemsList = selection.selected_item_ids.map(id => {
      const item = SPONSORSHIP_MENU.find(i => i.id === id);
      if (!item) return '';
      const isExclusive = selection.exclusivity_selected_item_ids.includes(id);
      const breakdown = calculateSponsorItemPrice(item, hostSettings, isExclusive);
      return `- ${item.name}${isExclusive ? ' (Exclusive)' : ''}: $${breakdown.final}`;
    }).filter(Boolean).join('\n');

    const message = `Dear Event Host,

I'm writing to express our strong interest in sponsoring your upcoming event "${event.title}". 

We've reviewed your sponsorship menu and would like to move forward with the following selections:

${selectedItemsList}

Estimated Total Investment: $${cartTotal}

We believe our brand aligns perfectly with your ${hostSettings.audience_type.replace('_', ' ')} audience and we're excited about the potential partnership. 

Could we schedule a brief call to discuss the next steps and finalize the details?

Best regards,
[Your Name/Company]`;

    setNegotiateMessage(message);
    setShowNegotiateComposer(true);
  };

  const toggleItemSelection = (id: string) => {
    setSelection(prev => {
      const isSelected = prev.selected_item_ids.includes(id);
      if (isSelected) {
        return {
          selected_item_ids: prev.selected_item_ids.filter(i => i !== id),
          exclusivity_selected_item_ids: prev.exclusivity_selected_item_ids.filter(i => i !== id)
        };
      } else {
        return {
          ...prev,
          selected_item_ids: [...prev.selected_item_ids, id]
        };
      }
    });
  };

  const toggleExclusivity = (id: string) => {
    setSelection(prev => {
      const isExclusive = prev.exclusivity_selected_item_ids.includes(id);
      if (isExclusive) {
        return {
          ...prev,
          exclusivity_selected_item_ids: prev.exclusivity_selected_item_ids.filter(i => i !== id)
        };
      } else {
        return {
          ...prev,
          exclusivity_selected_item_ids: [...prev.exclusivity_selected_item_ids, id]
        };
      }
    });
  };

  const allowedItems = useMemo(() => {
    return SPONSORSHIP_MENU.filter(item => hostSettings.allowed_item_ids.includes(item.id));
  }, [hostSettings.allowed_item_ids]);

  const cartTotal = useMemo(() => {
    return selection.selected_item_ids.reduce((total, id) => {
      const item = SPONSORSHIP_MENU.find(i => i.id === id);
      if (!item) return total;
      const isExclusive = selection.exclusivity_selected_item_ids.includes(id);
      const breakdown = calculateSponsorItemPrice(item, hostSettings, isExclusive);
      return total + breakdown.final;
    }, 0);
  }, [selection, hostSettings]);

  const categories = Array.from(new Set(SPONSORSHIP_MENU.map(i => i.category)));

  if (mode === 'host') {
    return (
      <div className="max-w-4xl mx-auto p-6 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Sponsorship Settings</h1>
            <p className="text-gray-500 mt-1">Configure what sponsors can buy for your event.</p>
          </div>
          <button 
            onClick={() => onUpdateSettings?.(hostSettings)}
            className="px-6 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-teal-500/15"
          >
            Save Settings
          </button>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass-card p-6 rounded-2xl space-y-6 md:col-span-1">
            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              <Info className="w-5 h-5 text-teal-500" />
              Event Context
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Expected Attendance</label>
                <div className="flex items-center gap-3">
                  <button 
                    onClick={() => setHostSettings(s => ({ ...s, expected_attendance: Math.max(0, s.expected_attendance - 50) }))}
                    className="w-10 h-10 rounded-lg bg-gray-50 border border-gray-200 flex items-center justify-center hover:bg-gray-100"
                  >
                    <Minus className="w-4 h-4" />
                  </button>
                  <input 
                    type="number" 
                    value={hostSettings.expected_attendance}
                    onChange={(e) => setHostSettings(s => ({ ...s, expected_attendance: parseInt(e.target.value) || 0 }))}
                    className="flex-1 bg-transparent border-b border-gray-200 text-center text-xl font-bold focus:outline-none focus:border-teal-500"
                  />
                  <button 
                    onClick={() => setHostSettings(s => ({ ...s, expected_attendance: s.expected_attendance + 50 }))}
                    className="w-10 h-10 rounded-lg bg-gray-50 border border-gray-200 flex items-center justify-center hover:bg-gray-100"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Audience Type</label>
                <div className="relative">
                  <select 
                    value={hostSettings.audience_type}
                    onChange={(e) => setHostSettings(s => ({ ...s, audience_type: e.target.value as AudienceType }))}
                    className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 pr-10 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    <option className="bg-white text-gray-800" value="general_public">General Public</option>
                    <option className="bg-white text-gray-800" value="students_earlycareer">Students / Early Career</option>
                    <option className="bg-white text-gray-800" value="professionals">Professionals</option>
                    <option className="bg-white text-gray-800" value="founders_operators">Founders / Operators</option>
                    <option className="bg-white text-gray-800" value="executives_investors">Executives / Investors</option>
                  </select>
                  <ChevronRight className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 rotate-90" />
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-200">
                <div>
                  <p className="text-sm font-bold text-gray-800">Allow Exclusivity</p>
                  <p className="text-[10px] text-gray-500">Sponsors can pay 40% more to be the only one in a category.</p>
                </div>
                <button 
                  onClick={() => setHostSettings(s => ({ ...s, allow_exclusivity: !s.allow_exclusivity }))}
                  className={`w-12 h-6 rounded-full transition-colors relative ${hostSettings.allow_exclusivity ? 'bg-teal-600' : 'bg-gray-700'}`}
                >
                  <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${hostSettings.allow_exclusivity ? 'left-7' : 'left-1'}`} />
                </button>
              </div>
            </div>
          </div>

          <div className="md:col-span-2 space-y-6">
            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              <LayoutGrid className="w-5 h-5 text-teal-500" />
              Available Menu Items
            </h2>

            {categories.map(cat => (
              <div key={cat} className="space-y-3">
                <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">{cat}</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {SPONSORSHIP_MENU.filter(i => i.category === cat).map(item => {
                    const isAllowed = hostSettings.allowed_item_ids.includes(item.id);
                    return (
                      <div 
                        key={item.id}
                        onClick={() => setHostSettings(s => ({
                          ...s,
                          allowed_item_ids: isAllowed 
                            ? s.allowed_item_ids.filter(id => id !== item.id)
                            : [...s.allowed_item_ids, item.id]
                        }))}
                        className={`p-4 rounded-2xl border transition-all cursor-pointer flex items-center gap-3 ${
                          isAllowed 
                            ? 'bg-teal-500/10 border-teal-500/50' 
                            : 'bg-gray-50 border-gray-200 opacity-60 hover:opacity-100'
                        }`}
                      >
                        <div className={`w-5 h-5 rounded flex items-center justify-center border ${
                          isAllowed ? 'bg-teal-500 border-teal-500' : 'border-gray-300'
                        }`}>
                          {isAllowed && <Check className="w-3 h-3 text-gray-800" />}
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-bold text-gray-800 truncate">{item.name}</p>
                          <p className="text-[10px] text-gray-500">Base: ${item.base_price_usd}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Sponsor Mode
  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8 flex flex-col lg:flex-row gap-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex-1 space-y-8">
        <header>
          <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-500 hover:text-gray-900 mb-4 text-sm transition-colors">
            <ArrowLeft className="w-4 h-4" />
            Back to Event
          </button>
          <h1 className="text-4xl font-bold text-gray-800 leading-tight">
            Sponsor <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-500 to-cyan-500">{event.title}</span>
          </h1>
          <p className="text-gray-500 mt-2 max-w-2xl">
            Choose from the available sponsorship opportunities below. Prices are dynamically calculated based on event reach and audience quality.
          </p>
        </header>

        <div className="space-y-12">
          {categories.map(cat => {
            const itemsInCat = allowedItems.filter(i => i.category === cat);
            if (itemsInCat.length === 0) return null;

            return (
              <section key={cat} className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
                  <h2 className="text-xs font-bold text-gray-500 uppercase tracking-[0.2em]">{cat}</h2>
                  <div className="h-px flex-1 bg-gradient-to-l from-white/10 to-transparent" />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {itemsInCat.map(item => {
                    const isSelected = selection.selected_item_ids.includes(item.id);
                    const isExclusive = selection.exclusivity_selected_item_ids.includes(item.id);
                    const breakdown = calculateSponsorItemPrice(item, hostSettings, isExclusive);
                    const isExpanded = expandedItemId === item.id;

                    return (
                      <div 
                        key={item.id}
                        className={`group relative glass-card rounded-3xl p-6 transition-all duration-300 border ${
                          isSelected ? 'border-teal-500/50 ring-1 ring-teal-500/20' : 'border-gray-100 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex justify-between items-start mb-4">
                          <div className="space-y-1">
                            <Badge variant={item.visibility_tier.toLowerCase() as any}>{item.visibility_tier} Exposure</Badge>
                            <h3 className="text-xl font-bold text-gray-800 group-hover:text-teal-600 transition-colors">{item.name}</h3>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-gray-800">${breakdown.final}</div>
                            <button 
                              onClick={() => setExpandedItemId(isExpanded ? null : item.id)}
                              className="text-[10px] text-gray-500 hover:text-teal-500 flex items-center gap-1 ml-auto mt-1"
                            >
                              {isExpanded ? 'Hide' : 'View'} Breakdown
                              <ChevronRight className={`w-3 h-3 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
                            </button>
                          </div>
                        </div>

                        <p className="text-sm text-gray-500 mb-6 line-clamp-2">{item.description}</p>

                        {isExpanded && <PricingBreakdownView breakdown={breakdown} />}

                        <div className="flex items-center gap-4 mt-6">
                          <button 
                            onClick={() => toggleItemSelection(item.id)}
                            className={`flex-1 py-3 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 ${
                              isSelected 
                                ? 'bg-teal-600 text-white' 
                                : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
                            }`}
                          >
                            {isSelected ? <Check className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
                            {isSelected ? 'Selected' : 'Add to Selection'}
                          </button>

                          {isSelected && hostSettings.allow_exclusivity && (
                            <button 
                              onClick={() => toggleExclusivity(item.id)}
                              className={`px-4 py-3 rounded-xl font-bold text-xs transition-all border ${
                                isExclusive 
                                  ? 'bg-yellow-500/10 border-yellow-500/50 text-yellow-400' 
                                  : 'bg-gray-50 border-gray-200 text-gray-500 hover:bg-gray-100'
                              }`}
                              title="Become the exclusive sponsor in this category"
                            >
                              <Shield className={`w-4 h-4 ${isExclusive ? 'fill-yellow-400/20' : ''}`} />
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>
            );
          })}
        </div>
      </div>

      {/* Sidebar / Cart */}
      <div className="lg:w-96 shrink-0">
        <div className="sticky top-24 space-y-6">
          <div className="glass-card p-6 rounded-3xl border border-gray-200 overflow-hidden relative">
            {/* Background Glow */}
            <div className="absolute -top-24 -right-24 w-48 h-48 bg-teal-500/15 rounded-full blur-3xl" />
            
            <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <ShoppingCart className="w-5 h-5 text-teal-500" />
              Sponsorship Cart
            </h2>

            <div className="space-y-4 mb-8">
              {selection.selected_item_ids.length === 0 ? (
                <div className="py-12 text-center space-y-3">
                  <div className="w-12 h-12 rounded-full bg-gray-50 flex items-center justify-center mx-auto">
                    <Plus className="w-6 h-6 text-gray-600" />
                  </div>
                  <p className="text-gray-500 text-sm">No items selected yet.</p>
                </div>
              ) : (
                selection.selected_item_ids.map(id => {
                  const item = SPONSORSHIP_MENU.find(i => i.id === id);
                  if (!item) return null;
                  const isExclusive = selection.exclusivity_selected_item_ids.includes(id);
                  const breakdown = calculateSponsorItemPrice(item, hostSettings, isExclusive);
                  return (
                    <div key={id} className="flex justify-between items-start group">
                      <div className="min-w-0">
                        <p className="text-sm font-bold text-gray-800 truncate">{item.name}</p>
                        {isExclusive && <p className="text-[10px] text-yellow-500 font-bold uppercase tracking-wider">Exclusive</p>}
                      </div>
                      <div className="text-right ml-4">
                        <p className="text-sm font-bold text-gray-800">${breakdown.final}</p>
                        <button onClick={() => toggleItemSelection(id)} className="text-[10px] text-red-500 opacity-0 group-hover:opacity-100 transition-opacity">Remove</button>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            <div className="pt-6 border-t border-gray-200 space-y-4">
              <div className="flex justify-between items-end">
                <span className="text-gray-500 text-sm">Total Investment</span>
                <span className="text-3xl font-bold text-gray-800 text-glow">${cartTotal}</span>
              </div>
              
              <button 
                disabled={selection.selected_item_ids.length === 0}
                onClick={handleNegotiate}
                className="w-full py-4 bg-gradient-to-r from-teal-600 to-cyan-600 text-white rounded-2xl font-bold shadow-xl shadow-teal-500/15 hover:shadow-teal-500/20 transition-all disabled:opacity-50 disabled:grayscale active:scale-95"
              >
                Proceed to Negotiate
              </button>
              
              <p className="text-[10px] text-center text-gray-500 px-4">
                By proceeding, you agree to Circle's Sponsorship Terms and the host's event guidelines.
              </p>
            </div>
          </div>

          {/* Event Stats Card */}
          <div className="glass-card p-6 rounded-3xl border border-gray-200 space-y-4">
            <h3 className="text-sm font-bold text-gray-500 uppercase tracking-widest">Event Reach</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-teal-500">
                  <Users className="w-4 h-4" />
                  <span className="text-lg font-bold text-gray-800">{hostSettings.expected_attendance}</span>
                </div>
                <p className="text-[10px] text-gray-500">Expected Attendees</p>
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-cyan-400">
                  <Target className="w-4 h-4" />
                  <span className="text-lg font-bold text-gray-800">
                    {hostSettings.audience_type.split('_').map(w => w[0].toUpperCase() + w.slice(1)).join(' ')}
                  </span>
                </div>
                <p className="text-[10px] text-gray-500">Target Audience</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Negotiate Modal */}
      {showNegotiateComposer && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-gray-900/80 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="glass-card w-full max-w-2xl rounded-3xl border border-gray-200 overflow-hidden shadow-2xl animate-in zoom-in-95 duration-300">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center bg-gray-50">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-teal-500/20 flex items-center justify-center">
                  <Mail className="w-5 h-5 text-teal-500" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-800">Negotiate Sponsorship</h3>
                  <p className="text-xs text-gray-500">Send a proposal to the event host</p>
                </div>
              </div>
              <button 
                onClick={() => setShowNegotiateComposer(false)}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-500 hover:text-gray-900"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-3">
                <div className="flex items-center gap-2 text-xs text-gray-500 border-b border-gray-100 pb-2">
                  <span className="font-bold uppercase tracking-wider">To:</span>
                  <span className="text-gray-600">host@circle.ooo</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-500 border-b border-gray-100 pb-2">
                  <span className="font-bold uppercase tracking-wider">Subject:</span>
                  <span className="text-gray-600">Sponsorship Proposal: {event.title}</span>
                </div>
                <textarea 
                  value={negotiateMessage}
                  onChange={(e) => setNegotiateMessage(e.target.value)}
                  className="w-full bg-transparent text-gray-600 text-sm leading-relaxed focus:outline-none h-64 resize-none custom-scrollbar"
                />
              </div>

              <div className="flex gap-3">
                <button 
                  onClick={() => setShowNegotiateComposer(false)}
                  className="flex-1 py-3 rounded-xl font-bold text-sm bg-gray-50 text-gray-500 hover:bg-gray-100 transition-all"
                >
                  Cancel
                </button>
                <button 
                  onClick={async () => {
                    try {
                      await createProposal({
                        eventId: event.id,
                        eventTitle: event.title,
                        receiverId: event.hostId,
                        message: negotiateMessage,
                        estimatedInvestment: cartTotal,
                        proposalType: 'sponsorship'
                      });
                      alert('Sponsorship proposal sent! The host will be in touch soon.');
                      setShowNegotiateComposer(false);
                      setSelection({ selected_item_ids: [], exclusivity_selected_item_ids: [] });
                    } catch (error: any) {
                      alert(error?.message || 'Failed to send proposal. Please try again.');
                    }
                  }}
                  className="flex-1 py-3 bg-teal-600 hover:bg-teal-500 text-white rounded-xl font-bold transition-all flex items-center justify-center gap-2 shadow-lg shadow-teal-500/15"
                >
                  <Send className="w-4 h-4" />
                  Send Proposal
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
