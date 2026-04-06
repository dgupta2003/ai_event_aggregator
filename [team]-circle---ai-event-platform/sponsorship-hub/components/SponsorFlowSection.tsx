import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Target, Search, TrendingUp, CheckCircle } from 'lucide-react';

const BENEFITS = [
  {
    icon: <Search className="w-5 h-5 text-cyan-400" />,
    text: 'Browse curated events matched to your brand audience and goals.',
  },
  {
    icon: <Target className="w-5 h-5 text-purple-400" />,
    text: 'Filter by audience type, event format, location, and budget range.',
  },
  {
    icon: <TrendingUp className="w-5 h-5 text-pink-400" />,
    text: 'See transparent, ROI-driven pricing upfront — no hidden fees.',
  },
  {
    icon: <CheckCircle className="w-5 h-5 text-emerald-400" />,
    text: 'Send sponsorship proposals directly to event hosts in seconds.',
  },
];

const SponsorFlowSection: React.FC = () => {
  return (
    <section
      id="sponsor-flow"
      className="py-24 px-4 bg-gradient-to-b from-transparent via-purple-950/10 to-transparent"
    >
      <div className="max-w-5xl mx-auto space-y-12">
        <div className="space-y-4 max-w-2xl">
          <span className="inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border border-cyan-500/40 bg-cyan-500/10 text-cyan-300">
            For Sponsors
          </span>
          <h2 className="text-3xl md:text-4xl font-bold text-white">
            Reach the exact audience
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">
              your brand needs
            </span>
          </h2>
          <p className="text-gray-400 text-base leading-relaxed">
            Browse live events with real audience data. Pick sponsorship items that match your
            goals and budget. Negotiate directly with hosts.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          {/* Benefit list */}
          <div className="space-y-3">
            {BENEFITS.map((b, i) => (
              <div
                key={i}
                className="flex items-start gap-4 p-4 glass-card rounded-xl border border-white/5 hover:border-white/10 transition-colors"
              >
                <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center shrink-0">
                  {b.icon}
                </div>
                <p className="text-gray-300 text-sm leading-relaxed pt-2.5">{b.text}</p>
              </div>
            ))}
          </div>

          {/* Mock profile card */}
          <div className="relative">
            <div className="absolute -inset-4 bg-gradient-to-br from-cyan-500/10 via-purple-500/10 to-pink-500/10 rounded-3xl blur-xl pointer-events-none" />
            <div className="relative glass-card rounded-2xl border border-white/10 p-6 space-y-5">
              <h3 className="text-white font-bold">Your Sponsorship Profile</h3>

              <div className="space-y-1">
                {[
                  { label: 'Target audience',  value: 'Founders & Operators'   },
                  { label: 'Preferred format',  value: 'In-Person / Hybrid'     },
                  { label: 'Budget range',      value: '$500 – $5,000'          },
                  { label: 'Geography',         value: 'US West Coast'          },
                ].map(row => (
                  <div
                    key={row.label}
                    className="flex justify-between items-center py-2.5 border-b border-white/5 last:border-0"
                  >
                    <span className="text-xs text-gray-500 uppercase tracking-wider">
                      {row.label}
                    </span>
                    <span className="text-sm text-white font-medium">{row.value}</span>
                  </div>
                ))}
              </div>

              <div className="p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/20">
                <p className="text-xs text-cyan-300 font-medium">
                  Based on your profile,{' '}
                  <span className="font-bold text-white">4 events</span> are a strong match right
                  now.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <Link
            to="/sponsors"
            className="flex-1 py-3 px-6 rounded-xl bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white text-sm font-bold text-center transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20"
          >
            Browse Opportunities
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/sponsor/signup"
            className="flex-1 py-3 px-6 rounded-xl border border-white/15 bg-white/5 hover:bg-white/10 text-white text-sm font-bold text-center transition-all flex items-center justify-center gap-2"
          >
            Create Sponsor Profile
          </Link>
        </div>
      </div>
    </section>
  );
};

export default SponsorFlowSection;
