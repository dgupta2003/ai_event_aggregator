import React from 'react';
import { Sparkles, Users, ArrowRight } from 'lucide-react';

interface HubHeroProps {
  onChooseHost: () => void;
  onChooseSponsor: () => void;
}

const HubHero: React.FC<HubHeroProps> = ({ onChooseHost, onChooseSponsor }) => {
  return (
    <section
      id="hub-hero"
      className="relative min-h-screen flex flex-col items-center justify-center px-4 py-24 overflow-hidden"
    >
      {/* Ambient glows */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-purple-600/10 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/4 w-[400px] h-[400px] bg-pink-600/8 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute top-1/2 right-1/4 w-[300px] h-[300px] bg-cyan-600/6 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative z-10 max-w-4xl mx-auto text-center space-y-8">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-purple-500/30 bg-purple-500/10 text-purple-300 text-sm font-medium">
          <Sparkles className="w-4 h-4" />
          Circle Sponsorship Hub
        </div>

        <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-[1.05]">
          <span className="text-white">Where Events</span>
          <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
            Meet Sponsors
          </span>
        </h1>

        <p className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed">
          Turn any event into a revenue engine. Browse live opportunities or configure your
          sponsorship package in minutes.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-2">
          <button
            onClick={onChooseHost}
            className="group relative px-8 py-5 rounded-2xl bg-gradient-to-br from-purple-600 to-purple-700 text-white font-bold text-lg shadow-xl shadow-purple-500/25 hover:shadow-purple-500/40 hover:from-purple-500 hover:to-purple-600 transition-all duration-300 flex items-center justify-center gap-3"
          >
            <Users className="w-5 h-5" />
            I'm a Host
            <ArrowRight className="w-5 h-5 opacity-70 group-hover:translate-x-1 transition-transform" />
          </button>

          <button
            onClick={onChooseSponsor}
            className="group px-8 py-5 rounded-2xl border border-white/20 bg-white/5 backdrop-blur text-white font-bold text-lg hover:bg-white/10 hover:border-white/30 transition-all duration-300 flex items-center justify-center gap-3"
          >
            <Sparkles className="w-5 h-5 text-cyan-400" />
            I'm a Sponsor
            <ArrowRight className="w-5 h-5 opacity-70 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>

        <p className="text-gray-600 text-sm">
          Real events · Dynamic pricing · Direct connection
        </p>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-gray-600 text-xs animate-bounce">
        <span>Scroll to explore</span>
        <div className="w-px h-8 bg-gradient-to-b from-gray-600 to-transparent" />
      </div>
    </section>
  );
};

export default HubHero;
