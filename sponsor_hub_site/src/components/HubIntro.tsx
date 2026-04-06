import React from 'react';
import { Zap, Shield, TrendingUp } from 'lucide-react';

const PILLARS = [
  {
    icon: <Zap className="w-5 h-5 text-purple-400" />,
    title: 'Dynamic Pricing',
    description:
      'Sponsorship rates calculated in real-time based on audience quality, attendance, and visibility tier.',
  },
  {
    icon: <Shield className="w-5 h-5 text-cyan-400" />,
    title: 'Transparent Value',
    description:
      'Every item shows exactly what you get and why it costs what it costs. No black boxes, no guesswork.',
  },
  {
    icon: <TrendingUp className="w-5 h-5 text-pink-400" />,
    title: 'Direct Match',
    description:
      'Sponsors discover events that fit their goals. Hosts attract brands that actually convert.',
  },
];

const HubIntro: React.FC = () => {
  return (
    <section className="py-24 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white">Sponsorship, simplified</h2>
          <p className="text-gray-400 max-w-2xl mx-auto text-lg">
            Circle's Sponsorship Hub connects event hosts with brand sponsors through a structured,
            pricing-transparent marketplace.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {PILLARS.map(p => (
            <div
              key={p.title}
              className="glass-card p-6 rounded-2xl border border-white/5 space-y-3 hover:border-white/10 transition-colors"
            >
              <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center">
                {p.icon}
              </div>
              <h3 className="text-white font-bold text-lg">{p.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{p.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HubIntro;
