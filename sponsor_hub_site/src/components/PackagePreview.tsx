import React, { useState, useMemo } from 'react';
import { Sliders, DollarSign, ChevronRight } from 'lucide-react';
import { SPONSORSHIP_MENU } from '../constants/sponsorship';
import { AudienceType, EventSponsorshipSettings } from '../types';
import { calculateSponsorItemPrice } from '../services/pricingService';
import { AUDIENCE_LABELS, getVisibilityColor } from '../utils/hubHelpers';

const PREVIEW_ITEM_IDS = [
  'logo_event_page',
  'swag_distribution',
  'sponsor_mention_1_2min',
  'stage_talk_3_5min',
  'panel_seat',
  'lead_capture_optin',
];

const scrollTo = (id: string) => {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

const PackagePreview: React.FC = () => {
  const [attendance, setAttendance] = useState(500);
  const [audienceType, setAudienceType] = useState<AudienceType>('professionals');
  const [selectedIds, setSelectedIds] = useState<string[]>([
    'logo_event_page',
    'sponsor_mention_1_2min',
  ]);

  const settings: EventSponsorshipSettings = useMemo(
    () => ({
      allowed_item_ids: SPONSORSHIP_MENU.map(i => i.id),
      expected_attendance: attendance,
      audience_type: audienceType,
      allow_exclusivity: false,
    }),
    [attendance, audienceType],
  );

  const previewItems = useMemo(
    () => SPONSORSHIP_MENU.filter(i => PREVIEW_ITEM_IDS.includes(i.id)),
    [],
  );

  const total = useMemo(
    () =>
      selectedIds.reduce((sum, id) => {
        const item = SPONSORSHIP_MENU.find(i => i.id === id);
        if (!item) return sum;
        return sum + calculateSponsorItemPrice(item, settings, false).final;
      }, 0),
    [selectedIds, settings],
  );

  const toggleItem = (id: string) =>
    setSelectedIds(prev => (prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]));

  return (
    <section
      id="estimator"
      className="py-24 px-4 bg-gradient-to-b from-transparent via-slate-900/30 to-transparent"
    >
      <div className="max-w-5xl mx-auto space-y-10">
        <div className="text-center space-y-3">
          <h2 className="text-3xl md:text-4xl font-bold text-white">Package Estimator</h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            Adjust event context and pick sponsorship items to get a live cost estimate.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 items-start">
          {/* Controls */}
          <div className="lg:col-span-2 glass-card rounded-2xl border border-white/5 p-6 space-y-6">
            <h3 className="text-white font-bold flex items-center gap-2 text-sm">
              <Sliders className="w-4 h-4 text-purple-400" />
              Event Context
            </h3>

            <div className="space-y-3">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                Attendance
              </label>
              <input
                type="range"
                min={50}
                max={5000}
                step={50}
                value={attendance}
                onChange={e => setAttendance(Number(e.target.value))}
                className="w-full accent-purple-500"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>50</span>
                <span className="text-white font-bold">{attendance.toLocaleString()}</span>
                <span>5,000</span>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                Audience
              </label>
              {(Object.keys(AUDIENCE_LABELS) as AudienceType[]).map(type => (
                <button
                  key={type}
                  onClick={() => setAudienceType(type)}
                  className={`w-full px-3 py-2 rounded-lg text-xs font-medium text-left transition-all border ${
                    audienceType === type
                      ? 'bg-purple-500/15 border-purple-500/50 text-purple-200'
                      : 'bg-white/3 border-white/5 text-gray-500 hover:text-white hover:bg-white/5'
                  }`}
                >
                  {AUDIENCE_LABELS[type]}
                </button>
              ))}
            </div>
          </div>

          {/* Item selector + total */}
          <div className="lg:col-span-3 space-y-4">
            <h3 className="text-white font-bold text-sm flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-cyan-400" />
              Select Items
            </h3>

            <div className="space-y-2">
              {previewItems.map(item => {
                const isSelected = selectedIds.includes(item.id);
                const bd = calculateSponsorItemPrice(item, settings, false);
                const colorClass = getVisibilityColor(item.visibility_tier);
                return (
                  <div
                    key={item.id}
                    onClick={() => toggleItem(item.id)}
                    className={`flex items-center justify-between p-4 rounded-xl cursor-pointer transition-all border ${
                      isSelected
                        ? 'bg-purple-500/10 border-purple-500/40'
                        : 'bg-white/3 border-white/5 hover:border-white/15'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-5 h-5 rounded-md flex items-center justify-center border transition-colors shrink-0 ${
                          isSelected ? 'bg-purple-500 border-purple-500' : 'border-white/20'
                        }`}
                      >
                        {isSelected && (
                          <svg
                            className="w-3 h-3 text-white"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={3}
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                        )}
                      </div>
                      <div>
                        <p className="text-sm text-white font-medium">{item.name}</p>
                        <span
                          className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border ${colorClass}`}
                        >
                          {item.visibility_tier}
                        </span>
                      </div>
                    </div>
                    <span
                      className={`text-sm font-bold ml-4 shrink-0 ${
                        isSelected ? 'text-white' : 'text-gray-500'
                      }`}
                    >
                      ${bd.final.toLocaleString()}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Total */}
            <div className="glass-card rounded-xl border border-purple-500/20 bg-purple-500/5 p-5 flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">Estimated Total</p>
                <p className="text-3xl font-bold text-white text-glow">
                  ${total.toLocaleString()}
                </p>
              </div>
              <button
                onClick={() => scrollTo('opportunities')}
                className="px-5 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-bold transition-all flex items-center gap-2 shadow-lg shadow-purple-500/20"
              >
                Browse Events
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PackagePreview;
