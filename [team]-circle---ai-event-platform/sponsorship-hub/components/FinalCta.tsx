import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles, Users } from 'lucide-react';

const FinalCta: React.FC = () => {
  return (
    <section className="py-24 px-4 relative overflow-hidden">
      {/* Ambient glow */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[800px] h-[400px] bg-purple-600/10 rounded-full blur-[120px]" />
      </div>

      <div className="relative max-w-4xl mx-auto text-center space-y-10">
        <div className="space-y-4">
          <h2 className="text-4xl md:text-5xl font-bold text-white leading-tight">
            Ready to make it happen?
          </h2>
          <p className="text-gray-400 text-lg max-w-xl mx-auto">
            Host an event with built-in sponsorship. Or become a sponsor and reach the audience
            that matters.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/host"
            className="group flex items-center justify-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold text-base shadow-xl shadow-purple-500/25 hover:shadow-purple-500/40 hover:from-purple-500 hover:to-pink-500 transition-all duration-300"
          >
            <Users className="w-5 h-5" />
            Host an Event
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>

          <Link
            to="/sponsor/signup"
            className="group flex items-center justify-center gap-3 px-8 py-4 rounded-2xl border border-white/20 bg-white/5 backdrop-blur text-white font-bold text-base hover:bg-white/10 hover:border-white/30 transition-all duration-300"
          >
            <Sparkles className="w-5 h-5 text-cyan-400" />
            Become a Sponsor
            <ArrowRight className="w-5 h-5 opacity-70 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        <p className="text-gray-600 text-sm">
          Part of the <span className="text-gray-400">Circle</span> event platform
        </p>
      </div>
    </section>
  );
};

export default FinalCta;
