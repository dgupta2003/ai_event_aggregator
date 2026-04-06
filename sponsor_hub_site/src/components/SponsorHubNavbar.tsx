import React, { useState, useEffect } from 'react';
import { Sparkles, Menu, X } from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Overview', sectionId: 'hub-hero' },
  { label: 'Hosts', sectionId: 'host-flow' },
  { label: 'Sponsors', sectionId: 'sponsor-flow' },
  { label: 'Opportunities', sectionId: 'opportunities' },
  { label: 'Estimator', sectionId: 'estimator' },
];

const scrollTo = (id: string) => {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

const SponsorHubNavbar: React.FC = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleNav = (id: string) => {
    scrollTo(id);
    setMobileOpen(false);
  };

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-[#030014]/90 backdrop-blur-xl border-b border-white/5'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <button
          onClick={() => handleNav('hub-hero')}
          className="flex items-center gap-2 text-white font-bold text-lg"
        >
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <span>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
              Sponsor
            </span>{' '}
            Hub
          </span>
        </button>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-1">
          {NAV_ITEMS.map(item => (
            <button
              key={item.sectionId}
              onClick={() => handleNav(item.sectionId)}
              className="px-4 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-all"
            >
              {item.label}
            </button>
          ))}
        </nav>

        {/* Desktop CTA */}
        <div className="hidden md:flex items-center gap-3">
          <button
            onClick={() => handleNav('sponsor-flow')}
            className="px-4 py-2 rounded-xl text-sm font-medium text-gray-300 border border-white/15 bg-white/5 hover:bg-white/10 transition-all"
          >
            For Sponsors
          </button>
          <button
            onClick={() => handleNav('host-flow')}
            className="px-4 py-2 rounded-xl text-sm font-bold text-white bg-purple-600 hover:bg-purple-500 transition-all shadow-lg shadow-purple-500/20"
          >
            For Hosts
          </button>
        </div>

        {/* Mobile toggle */}
        <button
          onClick={() => setMobileOpen(o => !o)}
          className="md:hidden w-9 h-9 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-gray-300"
        >
          {mobileOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden bg-[#030014]/95 backdrop-blur-xl border-b border-white/5 px-4 py-4 space-y-1">
          {NAV_ITEMS.map(item => (
            <button
              key={item.sectionId}
              onClick={() => handleNav(item.sectionId)}
              className="w-full text-left px-4 py-3 rounded-xl text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-all"
            >
              {item.label}
            </button>
          ))}
          <div className="pt-2 flex flex-col gap-2">
            <button
              onClick={() => handleNav('sponsor-flow')}
              className="w-full py-3 rounded-xl text-sm font-medium text-gray-300 border border-white/15 bg-white/5"
            >
              For Sponsors
            </button>
            <button
              onClick={() => handleNav('host-flow')}
              className="w-full py-3 rounded-xl text-sm font-bold text-white bg-purple-600"
            >
              For Hosts
            </button>
          </div>
        </div>
      )}
    </header>
  );
};

export default SponsorHubNavbar;
