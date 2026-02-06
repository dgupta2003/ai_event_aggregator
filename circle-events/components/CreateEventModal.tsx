
import React, { useState, useEffect } from 'react';
import { X, Mic, Plus, Calendar, MapPin, Clock, Layout, Loader2, Save, Handshake, Sparkles, Users, UserCheck, ChevronDown, Check } from 'lucide-react';
import { gemini } from '../services/geminiService';
import { LuminaEvent, EventSponsorshipSettings, AudienceType } from '../types';
import { SPONSORSHIP_MENU, AUDIENCE_LABELS } from '../constants';
import { calculateSponsorItemPrice } from '../services/pricingService';

interface CreateEventModalProps {
  onClose: () => void;
  onSubmit: (data: any) => void;
  initialData?: LuminaEvent | null;
}

const CreateEventModal: React.FC<CreateEventModalProps> = ({ onClose, onSubmit, initialData }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    date: '',
    time: '',
    location: '',
    type: 'online' as const,
    category: 'Tech' as const,
    sponsorshipOptIn: false,
    sponsorshipSettings: {
      allowed_item_ids: [] as string[],
      expected_attendance: 50,
      audience_type: 'general_public' as AudienceType,
      allow_exclusivity: false
    }
  });
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({
        title: initialData.title,
        description: initialData.description,
        date: initialData.date,
        time: initialData.time,
        location: initialData.location,
        type: initialData.type,
        category: initialData.category,
        sponsorshipOptIn: initialData.sponsorshipOptIn || false,
        sponsorshipSettings: initialData.sponsorshipSettings || {
          allowed_item_ids: [],
          expected_attendance: 50,
          audience_type: 'general_public',
          allow_exclusivity: false
        }
      });
    }
  }, [initialData]);

  const handleVoiceDescription = async () => {
    const prompt = window.prompt("Speak your event ideas (Type for now, imagine it's voice):");
    if (!prompt) return;

    setIsGenerating(true);
    const enrichedDescription = await gemini.generateEventDescription(prompt);
    setFormData(prev => ({ ...prev, description: enrichedDescription }));
    setIsGenerating(false);
  };

  const toggleSponsorshipItem = (id: string) => {
    setFormData(prev => {
      const current = prev.sponsorshipSettings.allowed_item_ids;
      const next = current.includes(id) 
        ? current.filter(i => i !== id) 
        : [...current, id];
      return {
        ...prev,
        sponsorshipSettings: { ...prev.sponsorshipSettings, allowed_item_ids: next }
      };
    });
  };

  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" onClick={onClose}></div>
      
      <div className="relative glass w-full max-w-2xl rounded-3xl overflow-hidden animate-in zoom-in-95 duration-300 flex flex-col max-h-[90vh]">
        <div className="p-8 border-b border-white/5 flex justify-between items-center bg-slate-950/20 backdrop-blur-md">
            <h2 className="text-3xl font-extrabold text-white">
              {initialData ? 'Edit Event' : 'Host an Event'}
            </h2>
            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors">
              <X className="w-6 h-6 text-slate-400" />
            </button>
        </div>

        <div className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
          <div className="space-y-6">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Event Title</label>
              <input 
                type="text" 
                placeholder="What are we hosting?"
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                value={formData.title}
                onChange={e => setFormData({...formData, title: e.target.value})}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-widest flex items-center gap-1">
                  <Calendar className="w-3 h-3" /> Date
                </label>
                <input 
                  type="text" 
                  placeholder="e.g. Oct 24, 2024"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                  value={formData.date}
                  onChange={e => setFormData({...formData, date: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-widest flex items-center gap-1">
                  <Clock className="w-3 h-3" /> Time
                </label>
                <input 
                  type="text" 
                  placeholder="e.g. 10:00 AM PST"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                  value={formData.time}
                  onChange={e => setFormData({...formData, time: e.target.value})}
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-widest flex items-center gap-1">
                <MapPin className="w-3 h-3" /> Location
              </label>
              <input 
                type="text" 
                placeholder="San Francisco or Online URL"
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                value={formData.location}
                onChange={e => setFormData({...formData, location: e.target.value})}
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Description</label>
                <button 
                  onClick={handleVoiceDescription}
                  disabled={isGenerating}
                  className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
                >
                  {isGenerating ? <Loader2 className="w-3 h-3 animate-spin" /> : <Mic className="w-3 h-3" />}
                  AI Generate
                </button>
              </div>
              <textarea 
                rows={3}
                placeholder="Tell the world about your event..."
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 resize-none text-sm"
                value={formData.description}
                onChange={e => setFormData({...formData, description: e.target.value})}
              ></textarea>
            </div>
          </div>

          {/* Sponsorship Matching Toggle */}
          <div className="pt-4 mt-4 border-t border-white/10">
            <div 
              className={`p-4 rounded-2xl border transition-all cursor-pointer flex items-center justify-between gap-4 ${formData.sponsorshipOptIn ? 'bg-indigo-500/10 border-indigo-500/30 ring-1 ring-indigo-500/50' : 'bg-white/5 border-white/5 hover:bg-white/10'}`}
              onClick={() => setFormData(prev => ({ ...prev, sponsorshipOptIn: !prev.sponsorshipOptIn }))}
            >
              <div className="flex gap-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${formData.sponsorshipOptIn ? 'bg-indigo-500 text-white' : 'bg-white/10 text-slate-400'}`}>
                  <Handshake className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                     <h4 className="text-white font-bold">Seek Sponsorship</h4>
                     {formData.sponsorshipOptIn && <Sparkles className="w-3 h-3 text-indigo-400 animate-pulse" />}
                  </div>
                  <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed max-w-sm">Open your event to premium brands and automated partnership matching.</p>
                </div>
              </div>
              <div className={`w-10 h-5 rounded-full relative transition-colors ${formData.sponsorshipOptIn ? 'bg-indigo-500' : 'bg-slate-800'}`}>
                 <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${formData.sponsorshipOptIn ? 'left-[22px]' : 'left-0.5'}`} />
              </div>
            </div>

            {formData.sponsorshipOptIn && (
              <div className="mt-4 animate-in fade-in slide-in-from-top-2 duration-300 space-y-6 p-4 glass rounded-2xl border-indigo-500/20">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest flex items-center gap-1">
                      <Users className="w-3 h-3" /> Attendance
                    </label>
                    <input 
                      type="number" 
                      className="w-full bg-slate-900 border border-white/10 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500"
                      value={formData.sponsorshipSettings.expected_attendance}
                      onChange={e => setFormData({...formData, sponsorshipSettings: {...formData.sponsorshipSettings, expected_attendance: parseInt(e.target.value) || 0}})}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest flex items-center gap-1">
                      <UserCheck className="w-3 h-3" /> Audience Type
                    </label>
                    <select 
                      className="w-full bg-slate-900 border border-white/10 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500 appearance-none"
                      value={formData.sponsorshipSettings.audience_type}
                      onChange={e => setFormData({...formData, sponsorshipSettings: {...formData.sponsorshipSettings, audience_type: e.target.value as AudienceType}})}
                    >
                      {Object.entries(AUDIENCE_LABELS).map(([val, label]) => (
                        <option key={val} value={val}>{label}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between items-end">
                    <label className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Allowed Sponsorship Items</label>
                    <span className="text-[9px] text-slate-500 italic">Est. Sponsor Pricing shown</span>
                  </div>
                  <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto pr-2 custom-scrollbar">
                    {SPONSORSHIP_MENU.map(item => {
                      const isSelected = formData.sponsorshipSettings.allowed_item_ids.includes(item.id);
                      // Calculate dynamic price based on current attendance and audience type
                      const { total } = calculateSponsorItemPrice(
                        item, 
                        formData.sponsorshipSettings, 
                        false // Base preview assumes non-exclusive
                      );

                      return (
                        <div 
                          key={item.id}
                          onClick={() => toggleSponsorshipItem(item.id)}
                          className={`flex items-center justify-between p-3 rounded-xl border transition-all cursor-pointer ${isSelected ? 'bg-indigo-500/10 border-indigo-500/30' : 'bg-slate-900/50 border-white/5 hover:border-white/20'}`}
                        >
                          <div className="flex flex-col">
                            <span className="text-sm font-semibold text-white">{item.name}</span>
                            <span className="text-[10px] text-slate-500">{item.category} • Base ${item.base_price_usd}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className={`text-xs font-bold ${isSelected ? 'text-indigo-400' : 'text-slate-400'}`}>
                              ${total}
                            </span>
                            {isSelected && <Check className="w-4 h-4 text-indigo-400" />}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div 
                  className="flex items-center justify-between p-3 rounded-xl bg-slate-900/50 border border-white/5 cursor-pointer hover:bg-slate-900"
                  onClick={() => setFormData(prev => ({ ...prev, sponsorshipSettings: { ...prev.sponsorshipSettings, allow_exclusivity: !prev.sponsorshipSettings.allow_exclusivity }}))}
                >
                  <div className="flex flex-col">
                    <span className="text-sm font-semibold text-white">Allow Category Exclusivity</span>
                    <span className="text-[10px] text-slate-500">Sponsors can pay +40% to block competitors.</span>
                  </div>
                  <div className={`w-8 h-4 rounded-full relative transition-colors ${formData.sponsorshipSettings.allow_exclusivity ? 'bg-indigo-500' : 'bg-slate-700'}`}>
                    <div className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-all ${formData.sponsorshipSettings.allow_exclusivity ? 'left-[18px]' : 'left-0.5'}`} />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="p-8 border-t border-white/5 bg-slate-950/20 backdrop-blur-md">
          <button 
            onClick={() => onSubmit({...formData, id: initialData?.id})}
            className="w-full py-4 bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl text-white font-bold text-lg hover:shadow-[0_0_30px_rgba(99,102,241,0.4)] transition-all hover:scale-[1.01] active:scale-95 flex items-center justify-center gap-2"
          >
            {initialData ? (
              <><Save className="w-5 h-5" /> Save Changes</>
            ) : (
              <><Plus className="w-5 h-5" /> Launch Event</>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateEventModal;
