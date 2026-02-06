
import React, { useState, useEffect, useMemo } from 'react';
import { Search, Compass, PlusCircle, User, Bell, Filter, SlidersHorizontal, Sparkles, Layout, Ticket, ArrowRight, Edit3, Handshake, ShieldCheck, Briefcase, Loader2, Award } from 'lucide-react';
import { MOCK_EVENTS } from './constants';
import { LuminaEvent, UserSponsorship } from './types';
import EventCard from './components/EventCard';
import VoiceAssistant from './components/VoiceAssistant';
import CreateEventModal from './components/CreateEventModal';
import LiveEventView from './components/LiveEventView';
import SponsorMenu from './components/SponsorMenu';
import PortfolioPage from './components/PortfolioPage';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'explore' | 'hosted' | 'attending' | 'sponsors' | 'portfolio'>('explore');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEvent, setSelectedEvent] = useState<LuminaEvent | null>(null);
  const [editingEvent, setEditingEvent] = useState<LuminaEvent | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isLiveRoomOpen, setIsLiveRoomOpen] = useState(false);
  const [isProcessingSponsor, setIsProcessingSponsor] = useState(false);
  
  // Persistence logic for events
  const [events, setEvents] = useState<LuminaEvent[]>(() => {
    const saved = localStorage.getItem('circle_events');
    return saved ? JSON.parse(saved) : MOCK_EVENTS;
  });

  // Persistence logic for joined events
  const [joinedEventIds, setJoinedEventIds] = useState<Set<string>>(() => {
    const saved = localStorage.getItem('circle_joined_ids');
    return saved ? new Set(JSON.parse(saved)) : new Set();
  });

  // Detailed persistence logic for sponsored packages
  const [sponsoredPackages, setSponsoredPackages] = useState<UserSponsorship[]>(() => {
    const saved = localStorage.getItem('circle_sponsored_packages');
    return saved ? JSON.parse(saved) : [];
  });

  const [notification, setNotification] = useState<string | null>(null);

  // Sync with Local Storage
  useEffect(() => {
    localStorage.setItem('circle_events', JSON.stringify(events));
  }, [events]);

  useEffect(() => {
    localStorage.setItem('circle_joined_ids', JSON.stringify(Array.from(joinedEventIds)));
  }, [joinedEventIds]);

  useEffect(() => {
    localStorage.setItem('circle_sponsored_packages', JSON.stringify(sponsoredPackages));
  }, [sponsoredPackages]);

  const filteredEvents = useMemo(() => {
    if (activeTab === 'explore') {
      return events.filter(e => 
        e.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.category.toLowerCase().includes(searchQuery.toLowerCase())
      );
    } else if (activeTab === 'hosted') {
      return events.filter(e => e.hostName === 'Current User');
    } else if (activeTab === 'attending') {
      return events.filter(e => joinedEventIds.has(e.id));
    } else if (activeTab === 'sponsors') {
      return events.filter(e => e.sponsorshipOptIn === true);
    }
    return [];
  }, [events, searchQuery, activeTab, joinedEventIds]);

  const handleVoiceCommand = (result: any) => {
    if (result.message) {
      setNotification(result.message);
      setTimeout(() => setNotification(null), 4000);
    }

    if (result.action === 'search' && result.query) {
      setSearchQuery(result.query);
      setActiveTab('explore');
    } else if (result.action === 'navigate' && result.destination) {
      if (result.destination === 'host') setIsCreateModalOpen(true);
      else if (['explore', 'profile', 'attending', 'sponsors', 'portfolio'].includes(result.destination)) {
          setActiveTab(result.destination as any);
      }
    }
  };

  const handleSaveEvent = (data: any) => {
    if (data.id) {
      setEvents(prev => prev.map(e => e.id === data.id ? { ...e, ...data } : e));
      setNotification(data.sponsorshipOptIn ? "Event updated with sponsorship matching enabled!" : "Event updated successfully!");
    } else {
      const newEvent: LuminaEvent = {
        ...data,
        id: Math.random().toString(36).substr(2, 9),
        image: `https://picsum.photos/seed/${data.title}/800/600`,
        hostName: 'Current User',
        attendeesCount: 1,
      };
      setEvents([newEvent, ...events]);
      setNotification(data.sponsorshipOptIn ? "Event published with AI Sponsorship matching active!" : "Event published successfully!");
    }
    
    setIsCreateModalOpen(false);
    setEditingEvent(null);
    setActiveTab('hosted');
    setTimeout(() => setNotification(null), 3000);
  };

  const handleEventClick = (event: LuminaEvent) => {
    if (activeTab === 'hosted') {
      setEditingEvent(event);
      setIsCreateModalOpen(true);
    } else {
      setSelectedEvent(event);
    }
  };

  const joinEvent = (eventId: string) => {
    setJoinedEventIds(prev => new Set(prev).add(eventId));
    setSelectedEvent(null);
    setNotification("You've joined this event!");
    setActiveTab('attending');
    setTimeout(() => setNotification(null), 3000);
  };

  const handleSponsorCheckout = (items: string[], exclusive: string[]) => {
    if (!selectedEvent) return;
    setIsProcessingSponsor(true);
    
    setTimeout(() => {
      // 1. Update global event state to block exclusive items for others
      setEvents(prev => prev.map(e => {
        if (e.id === selectedEvent.id) {
          const currentExclusives = e.exclusiveItemsSponsored || [];
          return {
            ...e,
            exclusiveItemsSponsored: [...new Set([...currentExclusives, ...exclusive])]
          };
        }
        return e;
      }));

      // 2. Save user's detailed sponsorship package
      const newPackage: UserSponsorship = {
        eventId: selectedEvent.id,
        items,
        exclusiveItems: exclusive,
        timestamp: Date.now()
      };
      setSponsoredPackages(prev => [newPackage, ...prev]);

      setIsProcessingSponsor(false);
      setSelectedEvent(null);
      setActiveTab('portfolio');
      setNotification(exclusive.length > 0 
        ? "Exclusivity secured! Portfolio updated." 
        : "Sponsorship confirmed! Welcome to the Circle.");
      setTimeout(() => setNotification(null), 4000);
    }, 1500);
  };

  const isJoined = (eventId: string) => joinedEventIds.has(eventId);

  return (
    <div className="min-h-screen animated-mesh pb-20 md:pb-0">
      {/* Floating Header */}
      <nav className="fixed top-0 left-0 right-0 z-[80] p-4 flex justify-center">
        <div className="glass px-6 py-3 rounded-full flex items-center gap-8 glow w-full max-w-6xl justify-between">
          <div className="flex items-center gap-2 group cursor-pointer" onClick={() => setActiveTab('explore')}>
            <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center group-hover:rotate-12 transition-transform">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-extrabold tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-500">CIRCLE</span>
          </div>

          <div className="hidden md:flex items-center gap-6">
            <button 
              onClick={() => { setActiveTab('explore'); setEditingEvent(null); }}
              className={`text-sm font-semibold transition-all ${activeTab === 'explore' ? 'text-white underline underline-offset-8 decoration-indigo-500' : 'text-slate-500 hover:text-white'}`}
            >
              Explore
            </button>
            <button 
              onClick={() => { setActiveTab('hosted'); setEditingEvent(null); }}
              className={`text-sm font-semibold transition-all ${activeTab === 'hosted' ? 'text-white underline underline-offset-8 decoration-indigo-500' : 'text-slate-500 hover:text-white'}`}
            >
              Hosting
            </button>
            <button 
              onClick={() => { setActiveTab('attending'); setEditingEvent(null); }}
              className={`text-sm font-semibold transition-all ${activeTab === 'attending' ? 'text-white underline underline-offset-8 decoration-indigo-500' : 'text-slate-500 hover:text-white'}`}
            >
              Attending
            </button>
            <div className="w-[1px] h-4 bg-white/10" />
            <div className="flex items-center gap-6">
              <button 
                onClick={() => { setActiveTab('sponsors'); setEditingEvent(null); }}
                className={`text-sm font-bold flex items-center gap-1.5 transition-all ${activeTab === 'sponsors' ? 'text-emerald-400 underline underline-offset-8 decoration-emerald-500' : 'text-slate-500 hover:text-emerald-400'}`}
              >
                <Handshake className="w-4 h-4" />
                Opportunities
              </button>
              <button 
                onClick={() => { setActiveTab('portfolio'); setEditingEvent(null); }}
                className={`text-sm font-bold flex items-center gap-1.5 transition-all ${activeTab === 'portfolio' ? 'text-emerald-400 underline underline-offset-8 decoration-emerald-500' : 'text-slate-500 hover:text-emerald-400'}`}
              >
                <Award className="w-4 h-4" />
                Portfolio
              </button>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button className="p-2 text-slate-400 hover:text-white transition-colors relative">
              <Bell className="w-5 h-5" />
              <div className="absolute top-2 right-2 w-1.5 h-1.5 bg-indigo-500 rounded-full"></div>
            </button>
            <div className="w-10 h-10 rounded-full glass border border-white/10 p-0.5 cursor-pointer hover:scale-105 transition-transform">
              <img src="https://picsum.photos/seed/user1/40/40" alt="avatar" className="w-full h-full rounded-full object-cover" />
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto pt-32 px-6 pb-20">
        {activeTab === 'explore' && (
          <div className="space-y-12 animate-in fade-in slide-in-from-top-4 duration-700">
            <div className="max-w-3xl space-y-4">
              <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white">
                Events for the <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-violet-400 to-cyan-400">Next Frontier.</span>
              </h1>
              <p className="text-slate-400 text-lg md:text-xl font-medium max-w-xl">
                The world's first AI-powered hybrid event platform. Experience gatherings like never before.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 pt-6">
                <div className="relative flex-1 group">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-indigo-400 transition-colors" />
                  <input 
                    type="text" 
                    placeholder="Search by tech, music, city..."
                    className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:bg-white/10 transition-all text-lg"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                  />
                </div>
                <button 
                  onClick={() => { setEditingEvent(null); setIsCreateModalOpen(true); }}
                  className="bg-white text-slate-950 px-8 py-4 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-slate-200 transition-all active:scale-95 whitespace-nowrap"
                >
                  <PlusCircle className="w-5 h-5" />
                  Host Event
                </button>
              </div>
            </div>

            <div className="flex items-center gap-3 overflow-x-auto pb-4 no-scrollbar">
              <button className="flex items-center gap-2 glass px-4 py-2 rounded-xl text-sm font-medium hover:bg-white/10 transition-all">
                <SlidersHorizontal className="w-4 h-4" /> Filters
              </button>
              <div className="h-6 w-[1px] bg-white/10 mx-2" />
              {['All', 'Tech', 'Design', 'Business', 'Music', 'Art'].map(cat => (
                <button 
                  key={cat}
                  onClick={() => setSearchQuery(cat === 'All' ? '' : cat)}
                  className={`px-5 py-2 rounded-xl text-sm font-medium transition-all whitespace-nowrap ${searchQuery === cat ? 'bg-indigo-600 text-white' : 'glass text-slate-400 hover:text-white hover:bg-white/10'}`}
                >
                  {cat}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {filteredEvents.map(event => (
                <EventCard key={event.id} event={event} onClick={handleEventClick} />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'sponsors' && (
          <div className="space-y-12 animate-in fade-in slide-in-from-right-4 duration-500">
            <div className="max-w-3xl space-y-4">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold uppercase tracking-widest">
                <Briefcase className="w-3 h-3" /> Partnership Hub
              </div>
              <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white">
                Partner with <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400">Impactful Circles.</span>
              </h1>
              <p className="text-slate-400 text-lg md:text-xl font-medium max-w-xl">
                Browse premium events seeking sponsorship. Connect your brand with highly engaged audiences using AI-optimized pricing.
              </p>
            </div>

            {filteredEvents.length > 0 ? (
               <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {filteredEvents.map(event => (
                    <div key={event.id} className="relative group">
                      <EventCard event={event} onClick={handleEventClick} />
                      <div className="absolute top-4 right-4 z-10">
                        <div className="bg-emerald-500 px-3 py-1 rounded-full shadow-lg border border-white/20 flex items-center gap-1.5">
                          <Handshake className="w-3 h-3 text-white" />
                          <span className="text-[10px] font-black text-white uppercase">Partner Ready</span>
                        </div>
                      </div>
                    </div>
                  ))}
               </div>
            ) : (
              <div className="text-center py-20 bg-emerald-500/5 rounded-[3rem] border border-emerald-500/10">
                  <div className="w-20 h-20 bg-emerald-500/10 rounded-3xl flex items-center justify-center mx-auto mb-8">
                    <Handshake className="w-10 h-10 text-emerald-500" />
                  </div>
                  <h2 className="text-3xl font-bold text-white mb-2">No active seeking</h2>
                  <p className="text-slate-400 max-w-sm mx-auto">Currently, no events are seeking sponsors. Check back soon for new opportunities!</p>
               </div>
            )}
          </div>
        )}

        {activeTab === 'portfolio' && (
          <div className="space-y-12 animate-in fade-in slide-in-from-right-4 duration-500">
            <div className="max-w-3xl space-y-4">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold uppercase tracking-widest">
                <Award className="w-3 h-3" /> Brand Portfolio
              </div>
              <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white">
                Active <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400">Sponsorships.</span>
              </h1>
              <p className="text-slate-400 text-lg md:text-xl font-medium max-w-xl">
                Manage your active partnerships, view secured exclusivity slots, and track your brand's community impact.
              </p>
            </div>

            <PortfolioPage 
              packages={sponsoredPackages} 
              events={events} 
              onEventClick={(ev) => { setSelectedEvent(ev); setActiveTab('explore'); }} 
            />
          </div>
        )}

        {activeTab === 'attending' && (
          <div className="animate-in fade-in slide-in-from-right-4 duration-500 space-y-8">
             <div className="flex justify-between items-end">
                <div className="space-y-2">
                   <h2 className="text-4xl font-extrabold text-white">My Schedule</h2>
                   <p className="text-slate-400">Events you are attending and registered for.</p>
                </div>
                <button onClick={() => setActiveTab('explore')} className="text-indigo-400 hover:text-white transition-colors flex items-center gap-2 text-sm font-bold">
                   Find more <ArrowRight className="w-4 h-4" />
                </button>
             </div>
             
             {filteredEvents.length > 0 ? (
               <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {filteredEvents.map(event => (
                    <EventCard key={event.id} event={event} onClick={handleEventClick} />
                  ))}
               </div>
             ) : (
               <div className="text-center py-20 bg-white/5 rounded-[3rem] border border-white/5">
                  <div className="w-20 h-20 bg-indigo-500/10 rounded-3xl flex items-center justify-center mx-auto mb-8">
                    <Ticket className="w-10 h-10 text-indigo-500" />
                  </div>
                  <h2 className="text-3xl font-bold text-white mb-2">No tickets yet</h2>
                  <button onClick={() => setActiveTab('explore')} className="mt-8 px-10 py-4 bg-white text-slate-900 rounded-2xl font-bold hover:scale-105 transition-transform active:scale-95">Explore Events</button>
               </div>
             )}
          </div>
        )}

        {activeTab === 'hosted' && (
          <div className="animate-in fade-in slide-in-from-right-4 duration-500 space-y-8">
             <div className="flex justify-between items-end">
                <div className="space-y-2">
                   <h2 className="text-4xl font-extrabold text-white">Managed Events</h2>
                   <p className="text-slate-400">Click any card to edit your event details.</p>
                </div>
                <button onClick={() => { setEditingEvent(null); setIsCreateModalOpen(true); }} className="bg-indigo-600 text-white px-6 py-2.5 rounded-xl font-bold text-sm hover:scale-105 transition-all">Create New</button>
             </div>

             {filteredEvents.length > 0 ? (
               <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {filteredEvents.map(event => (
                    <div key={event.id} className="relative group">
                      <EventCard event={event} onClick={handleEventClick} />
                      <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                          <div className="bg-indigo-600 p-2 rounded-xl shadow-xl border border-white/20"><Edit3 className="w-4 h-4 text-white" /></div>
                        </div>
                        {event.sponsorshipOptIn && (
                          <div className="bg-emerald-500/20 backdrop-blur-md px-2 py-1 rounded-lg border border-emerald-500/30 flex items-center gap-1.5 shadow-lg">
                            <Handshake className="w-3 h-3 text-emerald-400" />
                            <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-tighter">Seeking</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
               </div>
             ) : (
               <div className="text-center py-20 bg-white/5 rounded-[3rem] border border-white/5">
                  <div className="w-20 h-20 bg-violet-500/10 rounded-3xl flex items-center justify-center mx-auto mb-8"><Layout className="w-10 h-10 text-violet-500" /></div>
                  <h2 className="text-3xl font-bold text-white mb-2">Ready to Host?</h2>
                  <button onClick={() => { setEditingEvent(null); setIsCreateModalOpen(true); }} className="mt-8 px-10 py-4 bg-indigo-600 text-white rounded-2xl font-bold hover:scale-105 transition-transform active:scale-95">Launch an Event</button>
               </div>
             )}
          </div>
        )}
      </main>

      {/* Event Details Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-md" onClick={() => setSelectedEvent(null)}></div>
          <div className="relative glass w-full max-w-5xl rounded-[2.5rem] overflow-hidden animate-in zoom-in-95 duration-300">
            <div className="flex flex-col md:flex-row max-h-[90vh]">
              <div className="md:w-1/3 aspect-video md:aspect-auto overflow-hidden border-r border-white/5">
                <img src={selectedEvent.image} alt={selectedEvent.title} className="w-full h-full object-cover" />
              </div>
              <div className="md:w-2/3 p-8 md:p-12 space-y-8 overflow-y-auto custom-scrollbar">
                {activeTab === 'sponsors' ? (
                  <SponsorMenu 
                    event={selectedEvent} 
                    onSponsor={handleSponsorCheckout} 
                    isProcessing={isProcessingSponsor}
                  />
                ) : (
                  <>
                    <div className="space-y-4">
                      <div className="flex items-center gap-2">
                        <span className="bg-indigo-500/20 text-indigo-400 text-xs font-bold px-3 py-1 rounded-full">{selectedEvent.category}</span>
                        <span className="text-slate-500 text-xs font-medium uppercase tracking-widest">{selectedEvent.type} EVENT</span>
                      </div>
                      <h2 className="text-4xl font-extrabold text-white leading-tight">{selectedEvent.title}</h2>
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-slate-800" />
                        <div className="text-sm">
                          <p className="text-slate-400">Hosted by</p>
                          <p className="text-white font-bold">{selectedEvent.hostName}</p>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4 text-slate-300">
                      <p className="leading-relaxed text-lg">{selectedEvent.description}</p>
                      <div className="grid grid-cols-2 gap-6 pt-4 border-t border-white/10">
                        <div>
                          <p className="text-xs font-bold text-slate-500 uppercase mb-1">When</p>
                          <p className="text-white">{selectedEvent.date}</p>
                          <p className="text-sm text-slate-400">{selectedEvent.time}</p>
                        </div>
                        <div>
                          <p className="text-xs font-bold text-slate-500 uppercase mb-1">Where</p>
                          <p className="text-white">{selectedEvent.location}</p>
                        </div>
                      </div>
                    </div>

                    <div className="pt-8 flex gap-4">
                       {isJoined(selectedEvent.id) ? (
                         <div className="flex-1 bg-white/5 border border-indigo-500/30 text-indigo-400 py-4 rounded-2xl font-bold flex items-center justify-center gap-2">
                            <Ticket className="w-5 h-5" /> Registered
                         </div>
                       ) : (
                         <button onClick={() => joinEvent(selectedEvent.id)} className="flex-1 bg-white text-slate-950 py-4 rounded-2xl font-bold hover:bg-slate-200 transition-all active:scale-95">Join Event</button>
                       )}
                       <button className="px-6 py-4 glass text-white rounded-2xl font-bold hover:bg-white/10 transition-all">Save</button>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {isCreateModalOpen && <CreateEventModal onClose={() => { setIsCreateModalOpen(false); setEditingEvent(null); }} onSubmit={handleSaveEvent} initialData={editingEvent} />}
      {isLiveRoomOpen && selectedEvent && <LiveEventView event={selectedEvent} onExit={() => setIsLiveRoomOpen(false)} />}
      {notification && <div className="fixed top-24 left-1/2 -translate-x-1/2 z-[200] glass px-6 py-3 rounded-full text-white font-medium shadow-2xl border-indigo-500/30 flex items-center gap-2 animate-in slide-in-from-top-4 duration-300"><Sparkles className="w-4 h-4 text-indigo-400" />{notification}</div>}
      <VoiceAssistant onCommand={handleVoiceCommand} />
    </div>
  );
};

export default App;
