import React, { useState, useMemo } from 'react';
import { ArrowRight, Users, Sliders, Plus, Minus } from 'lucide-react';
import { SPONSORSHIP_MENU } from '../constants/sponsorship';
import { AudienceType, EventSponsorshipSettings } from '../types';
import { calculateSponsorItemPrice } from '../services/pricingService';
import { AUDIENCE_LABELS } from '../utils/hubHelpers';

const SAMPLE_ITEM_IDS = [
  'sponsor_mention_1_2min',
  'panel_seat',
  'demo_table',
  'logo_event_page',
];

const scrollTo = (id: string) => {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

const HostFlowSection: React.FC = () => {
  const [attendance, setAttendance] = useState(300);
  const [audienceType, setAudienceType] = useState<AudienceType>('professionals');

  const settings: EventSponsorshipSettings = useMemo(
    () => ({
      allowed_item_ids: SPONSORSHIP_MENU.map(i => i.id),
      expected_attendance: attendance,
      audience_type: audienceType,
      allow_exclusivity: true,
    }),
    [attendance, audienceType],
  );

  const sampleItems = useMemo(
    () => SPONSORSHIP_MENU.filter(i => SAMPLE_ITEM_IDS.includes(i.id)),
    [],
  );

  const totalRevenue = useMemo(
    () =>
      sampleItems.reduce((sum, item) => {
        const bd = calculateSponsorItemPrice(item, settings, false);
        return sum + bd.final;
      }, 0),
    [sampleItems, settings],
  );

  return (
    <section id="host-flow" className="py-24 px-4">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* Header */}
        <div className="space-y-4 max-w-2xl">
          <span className="inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border border-purple-500/40 bg-purple-500/10 text-purple-300">
            For Hosts
          </span>
          <h2 className="text-3xl md:text-4xl font-bold text-white">
            Turn your event into a
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
              sponsorship opportunity
            </span>
          </h2>
          <p className="text-gray-400 text-base leading-relaxed">
            Set your audience profile and attendance. Circle automatically prices every sponsorship
            slot. Sponsors see real value — you earn real revenue.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Controls */}
          <div className="glass-card rounded-2xl border border-white/5 p-6 space-y-6">
            <h3 className="text-white font-bold flex items-center gap-2">
              <Sliders className="w-4 h-4 text-purple-400" />
              Event Profile
            </h3>

            <div className="space-y-2">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                Expected Attendance
              </label>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setAttendance(a => Math.max(50, a - 50))}
                  className="w-9 h-9 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center hover:bg-white/10 text-gray-300 transition-colors"
                >
                  <Minus className="w-4 h-4" />
                </button>
                <div className="flex-1 text-center">
                  <span className="text-3xl font-bold text-white">{attendance}</span>
                  <span className="text-gray-500 ml-2 text-sm">attendees</span>
                </div>
                <button
                  onClick={() => setAttendance(a => a + 50)}
                  className="w-9 h-9 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center hover:bg-white/10 text-gray-300 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                Audience Type
              </label>
              <div className="grid grid-cols-1 gap-2">
                {(Object.keys(AUDIENCE_LABELS) as AudienceType[]).map(type => (
                  <button
                    key={type}
                    onClick={() => setAudienceType(type)}
                    className={`px-4 py-2.5 rounded-xl text-sm font-medium text-left transition-all border ${
                      audienceType === type
                        ? 'bg-purple-500/15 border-purple-500/50 text-purple-200'
                        : 'bg-white/3 border-white/10 text-gray-400 hover:bg-white/5 hover:text-white'
                    }`}
                  >
                    {AUDIENCE_LABELS[type]}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Live Pricing Preview */}
          <div className="space-y-4 flex flex-col">
            <div className="glass-card rounded-2xl border border-purple-500/20 bg-purple-500/5 p-6 space-y-4 flex-1">
              <div className="flex justify-between items-center">
                <h3 className="text-white font-bold flex items-center gap-2">
                  <Users className="w-4 h-4 text-purple-400" />
                  Sample Package Value
                </h3>
                <div className="text-right">
                  <div className="text-2xl font-bold text-white text-glow">
                    ${totalRevenue.toLocaleString()}
                  </div>
                  <div className="text-xs text-gray-500">estimated total</div>
                </div>
              </div>

              <div className="space-y-1">
                {sampleItems.map(item => {
                  const bd = calculateSponsorItemPrice(item, settings, false);
                  return (
                    <div
                      key={item.id}
                      className="flex justify-between items-center py-2.5 border-b border-white/5 last:border-0"
                    >
                      <div>
                        <p className="text-sm text-white font-medium">{item.name}</p>
                        <p className="text-xs text-gray-500">{item.category}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-bold text-white">${bd.final}</p>
                        <p className="text-[10px] text-gray-600">base ${bd.base}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <p className="text-xs text-gray-600 text-center px-4">
              Prices adjust automatically based on audience quality and event size. Sponsors pay
              market rates — you keep the revenue.
            </p>

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={() => scrollTo('opportunities')}
                className="flex-1 py-3 px-6 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-bold text-center transition-all flex items-center justify-center gap-2 shadow-lg shadow-purple-500/20"
              >
                View Opportunities
                <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => scrollTo('estimator')}
                className="flex-1 py-3 px-6 rounded-xl border border-white/15 bg-white/5 hover:bg-white/10 text-white text-sm font-bold text-center transition-all flex items-center justify-center gap-2"
              >
                Configure Package
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HostFlowSection;
