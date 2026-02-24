import React, { useState, useEffect, useRef, useContext, createContext } from 'react';
import { HashRouter, Routes, Route, Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { 
  Mic, Search, Calendar, MapPin, User as UserIcon, Plus, 
  Heart, Share2, ArrowRight, Video, MessageCircle, X,
  ChevronRight, Map as MapIcon, Mic2, Send, CreditCard, Check,
  Sparkles, Zap, RefreshCw, ShieldCheck, Clock, Users, DollarSign, Globe, Image as ImageIcon, Link as LinkIcon,
  Tag, Briefcase, FileText, Mail, Home, Compass
} from 'lucide-react';
import { EVENTS, SPONSORS, MOCK_USER } from './constants';
import { Event, Sponsor, TicketSelection, ChatMessage, EventFormat } from './types';

// --- Context Management ---

interface EventContextType {
  events: Event[];
  addEvent: (event: Event) => void;
  user: typeof MOCK_USER;
}

const EventContext = createContext<EventContextType>({
  events: [],
  addEvent: () => {},
  user: MOCK_USER
});

const useEvents = () => useContext(EventContext);

// --- Reusable Components ---

const Button = ({ children, variant = 'primary', className = '', onClick, icon: Icon, disabled = false, type = 'button' }: any) => {
  const base = "inline-flex items-center justify-center px-6 py-3 rounded-xl font-medium transition-all duration-300 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation";
  const variants = {
    primary: "bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-[0_0_20px_rgba(168,85,247,0.4)] hover:shadow-[0_0_30px_rgba(168,85,247,0.6)]",
    glass: "bg-white/10 backdrop-blur-md border border-white/10 text-white hover:bg-white/20 hover:border-white/30",
    ghost: "text-gray-400 hover:text-white hover:bg-white/5",
    outline: "border border-purple-500/50 text-purple-400 hover:bg-purple-500/10",
    success: "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.4)]"
  };
  
  return (
    <button type={type} disabled={disabled} onClick={onClick} className={`${base} ${variants[variant as keyof typeof variants]} ${className}`}>
      {Icon && <Icon className="w-5 h-5 mr-2" />}
      {children}
    </button>
  );
};

const Orb = ({ size = "lg", active = false }: { size?: 'sm'|'lg', active?: boolean }) => {
  const sizeClasses = size === 'lg' ? 'w-48 h-48 md:w-64 md:h-64' : 'w-16 h-16'; 
  
  return (
    <div className={`relative ${sizeClasses} flex items-center justify-center`}>
      {/* 1. Deep Ambient Glow */}
      <div className={`absolute inset-0 bg-purple-600/30 rounded-full blur-[80px] transition-all duration-1000 ${active ? 'scale-150 opacity-100' : 'scale-100 opacity-50'}`} />

      {/* 2. Outer Rotating Rings (Thin) */}
      <div className="absolute inset-[-4px] rounded-full border border-transparent border-t-purple-500/60 border-l-cyan-500/60 animate-spin-slow" />
      <div className="absolute inset-[-8px] rounded-full border border-transparent border-b-pink-500/40 border-r-purple-500/40 animate-spin-reverse-slower" />

      {/* 3. The Sphere Container */}
      <div 
        className="relative w-full h-full rounded-full overflow-hidden backdrop-blur-md border border-white/10 shadow-[inset_0_0_50px_rgba(255,255,255,0.15)] z-10 bg-black/20 isolate transform-gpu"
        style={{
          WebkitMaskImage: '-webkit-radial-gradient(white, black)',
        }}
      >
          {/* 4. Conic Gradient Background */}
          <div className={`absolute inset-[-50%] w-[200%] h-[200%] bg-[conic-gradient(from_0deg,#4c1d95,#ec4899,#06b6d4,#4c1d95)] animate-spin-slower blur-2xl opacity-60`} />
          
          {/* 5. Internal Fluid Blobs */}
          <div className={`absolute top-[20%] left-[20%] w-[60%] h-[60%] bg-purple-500 rounded-full mix-blend-overlay blur-xl animate-blob`} />
          <div className={`absolute top-[20%] right-[20%] w-[50%] h-[50%] bg-cyan-400 rounded-full mix-blend-overlay blur-xl animate-blob`} style={{ animationDelay: '2s' }} />
          <div className={`absolute bottom-[10%] left-[30%] w-[70%] h-[60%] bg-pink-500 rounded-full mix-blend-overlay blur-xl animate-blob`} style={{ animationDelay: '4s' }} />

          {/* 6. Active State Core */}
          <div className={`absolute inset-0 bg-white/10 transition-opacity duration-300 ${active ? 'opacity-100' : 'opacity-0'}`} />

          {/* 7. Surface Reflections */}
          <div className="absolute top-0 left-1/4 w-1/2 h-1/2 bg-gradient-to-b from-white/40 to-transparent rounded-full blur-md opacity-80" />
          <div className="absolute bottom-4 right-8 w-8 h-4 bg-white/30 rounded-full blur-sm -rotate-12" />
      </div>
      
      {/* 8. Center Pulse */}
      {active && (
         <div className="absolute inset-0 flex items-center justify-center z-20">
            <div className="w-1/3 h-1/3 bg-white rounded-full blur-xl animate-pulse" />
         </div>
      )}
    </div>
  );
};

const NavBar = () => {
  const location = useLocation();
  const { user } = useEvents();
  const isActive = (path: string) => location.pathname === path ? 'text-white' : 'text-gray-400 hover:text-gray-200';

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-panel border-b-0 rounded-b-2xl mx-4 mt-2 px-6 h-16 flex items-center justify-between">
      <Link to="/" className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/30">
          <div className="w-3 h-3 bg-white rounded-full"></div>
        </div>
        <span className="font-bold text-lg tracking-tight">Circle</span>
      </Link>

      <div className="hidden md:flex items-center gap-8">
        <Link to="/" className={`text-sm font-medium transition-colors ${isActive('/')}`}>Home</Link>
        <Link to="/explore" className={`text-sm font-medium transition-colors ${isActive('/explore')}`}>Explore</Link>
        <Link to="/host" className={`text-sm font-medium transition-colors ${isActive('/host')}`}>Host</Link>
        <Link to="/profile" className={`text-sm font-medium transition-colors ${isActive('/profile')}`}>Profile</Link>
      </div>

      <div className="flex items-center gap-4">
        <button className="p-2 rounded-full hover:bg-white/10 transition-colors hidden md:block">
          <Search className="w-5 h-5 text-gray-300" />
        </button>
        <Link to="/profile">
           <div className="w-8 h-8 rounded-full overflow-hidden border border-white/20">
             <img src={user.avatarUrl} alt="Profile" className="w-full h-full object-cover" />
           </div>
        </Link>
      </div>
    </nav>
  );
};

const MobileNav = ({ onOpenAI }: { onOpenAI: () => void }) => {
  const location = useLocation();
  const isActive = (path: string) => location.pathname === path;
  const baseClass = "flex flex-col items-center justify-center w-full h-full space-y-1 touch-manipulation";
  const activeClass = "text-purple-400";
  const inactiveClass = "text-gray-500 hover:text-gray-300";

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 h-20 bg-[#030014]/90 backdrop-blur-xl border-t border-white/10 px-4 pb-2 md:hidden flex items-center justify-between safe-area-bottom">
        <Link to="/" className={`${baseClass} ${isActive('/') ? activeClass : inactiveClass}`}>
            <Home className="w-6 h-6" />
            <span className="text-[10px] font-medium">Home</span>
        </Link>
        <Link to="/explore" className={`${baseClass} ${isActive('/explore') ? activeClass : inactiveClass}`}>
            <Compass className="w-6 h-6" />
            <span className="text-[10px] font-medium">Explore</span>
        </Link>

        {/* AI Button - Floating effect */}
        <div className="relative -top-6">
            <button
                onClick={onOpenAI}
                className="w-14 h-14 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/40 border-4 border-[#030014] active:scale-95 transition-transform"
                aria-label="Speak to AI"
            >
                <Mic className="w-6 h-6 text-white" />
            </button>
        </div>

        <Link to="/host" className={`${baseClass} ${isActive('/host') ? activeClass : inactiveClass}`}>
            <Plus className="w-6 h-6" />
            <span className="text-[10px] font-medium">Host</span>
        </Link>
        <Link to="/profile" className={`${baseClass} ${isActive('/profile') ? activeClass : inactiveClass}`}>
            <UserIcon className="w-6 h-6" />
            <span className="text-[10px] font-medium">Profile</span>
        </Link>
    </div>
  );
}

const EventCard: React.FC<{ event: Event; onClick: () => void }> = ({ event, onClick }) => {
  return (
    <div 
      onClick={onClick}
      className="group relative glass-card rounded-3xl overflow-hidden cursor-pointer transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl hover:shadow-purple-500/20"
    >
      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent z-10"></div>
      <img src={event.imageUrl} alt={event.title} className="w-full h-64 object-cover transition-transform duration-700 group-hover:scale-110" />
      
      <div className="absolute top-4 right-4 z-20">
        <span className="px-3 py-1 rounded-full text-xs font-bold bg-white/10 backdrop-blur-md border border-white/20 text-white">
          {event.format}
        </span>
      </div>
      
      {event.sponsorId && (
         <div className="absolute top-4 left-4 z-20">
           <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-[#1a1a2e]/80 backdrop-blur-md border border-yellow-500/30">
             <span className="text-[10px] font-bold text-yellow-400 uppercase tracking-wider">Sponsored</span>
           </div>
         </div>
      )}

      <div className="absolute bottom-0 left-0 right-0 p-6 z-20">
        <div className="text-purple-400 text-sm font-semibold mb-1 uppercase tracking-wider">
          {new Date(event.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} • {event.time}
        </div>
        <h3 className="text-xl font-bold text-white mb-2 leading-tight">{event.title}</h3>
        <div className="flex items-center gap-2 text-gray-400 text-sm">
          <MapPin className="w-4 h-4" />
          {event.location}
        </div>
      </div>
    </div>
  );
};

// --- Feature Components ---

const AIAssistantOverlay = ({ isOpen, onClose, initialQuery }: { isOpen: boolean; onClose: () => void; initialQuery?: string }) => {
  const { events } = useEvents();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (isOpen) {
      setMessages([{
        id: 'welcome',
        sender: 'ai',
        text: 'Circle is here. How can I help you plan your perfect event experience?',
        timestamp: Date.now()
      }]);
      if (initialQuery) {
        handleSend(initialQuery);
      }
    }
  }, [isOpen, initialQuery]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    
    // User Message
    const userMsg: ChatMessage = { id: Date.now().toString(), sender: 'user', text, timestamp: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setInputValue("");

    // Simulate AI Thinking
    setIsListening(true); 
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsListening(false);

    // AI Response Logic (Mock)
    let aiResponse: ChatMessage = {
      id: (Date.now() + 1).toString(),
      sender: 'ai',
      text: "I didn't quite catch that.",
      timestamp: Date.now()
    };

    const lowerText = text.toLowerCase();

    if (lowerText.includes('ufc') || lowerText.includes('fight') || lowerText.includes('vegas')) {
      aiResponse.text = "Great! I found 3 UFC events in Las Vegas coming up. Here they are.";
      aiResponse.action = 'show_events';
      aiResponse.data = events.filter(e => e.title.includes('UFC'));
    } else if (lowerText.includes('budget') || lowerText.includes('899')) {
      aiResponse.text = "Perfect. I found 57 available tickets within your $899 budget for UFC 308. I've opened the seat map for you.";
      aiResponse.action = 'show_map';
      aiResponse.data = { eventId: 'e1', budget: 899 };
    } else if (lowerText.includes('online') || lowerText.includes('tech')) {
       aiResponse.text = "Showing you some top online tech events.";
       aiResponse.action = 'show_events';
       aiResponse.data = events.filter(e => e.category === 'Tech');
    }

    setMessages(prev => [...prev, aiResponse]);

    // Handle Actions
    if (aiResponse.action === 'show_events') {
        // In a real app this might navigate or show a specialized view
        // For this demo, we assume the user is looking at the overlay
    } else if (aiResponse.action === 'show_map') {
        setTimeout(() => {
             onClose();
             navigate(`/event/${aiResponse.data.eventId}/tickets`);
        }, 2000);
    }
  };

  const toggleMic = () => {
    if (isListening) return;
    setIsListening(true);
    // Simulate speech to text
    setTimeout(() => {
      setIsListening(false);
      handleSend("Find a UFC fight in Vegas in November");
    }, 2000);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[60] bg-black/80 backdrop-blur-xl flex flex-col items-center justify-end md:justify-center p-4">
      <button onClick={onClose} className="absolute top-6 right-6 p-2 bg-white/10 rounded-full hover:bg-white/20 text-white z-50">
        <X className="w-6 h-6" />
      </button>

      <div className="w-full max-w-2xl flex flex-col items-center gap-8 mb-8 md:mb-0 h-full md:h-auto justify-center">
        <div className="relative shrink-0">
             <Orb size="lg" active={isListening} />
             {isListening && <p className="absolute -bottom-12 left-0 right-0 text-center text-purple-300 animate-pulse">Listening...</p>}
        </div>

        <div className="w-full flex-1 md:h-[300px] md:flex-none overflow-y-auto space-y-4 px-4 scrollbar-hide mask-gradient-b">
          {messages.map(msg => (
            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] p-4 rounded-2xl ${msg.sender === 'user' ? 'bg-white/10 border border-white/10' : 'bg-gradient-to-br from-purple-900/50 to-blue-900/50 border border-purple-500/20'} backdrop-blur-md`}>
                <p className="text-white text-lg leading-relaxed">{msg.text}</p>
                {msg.action === 'show_events' && (
                  <div className="mt-4 space-y-2">
                     {msg.data.map((e: Event) => (
                        <div key={e.id} onClick={() => { onClose(); navigate(`/event/${e.id}`); }} className="flex items-center gap-3 p-2 bg-black/40 rounded-lg cursor-pointer hover:bg-white/5">
                            <img src={e.imageUrl} className="w-12 h-12 rounded-lg object-cover" />
                            <div>
                                <p className="font-bold text-sm">{e.title}</p>
                                <p className="text-xs text-gray-400">{e.date}</p>
                            </div>
                            <Button variant="glass" className="ml-auto text-xs px-3 py-1">View</Button>
                        </div>
                     ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="w-full relative shrink-0">
            <input 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend(inputValue)}
              type="text" 
              placeholder="Ask Circle..." 
              className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-6 pr-14 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500/50 focus:bg-white/10 transition-all"
            />
            <div className="absolute right-2 top-2 flex items-center gap-1">
                 <button onClick={toggleMic} className={`p-2 rounded-xl transition-colors ${isListening ? 'text-red-400 bg-red-500/10' : 'text-gray-400 hover:text-white'}`}>
                    <Mic className="w-5 h-5" />
                 </button>
                 <button onClick={() => handleSend(inputValue)} className="p-2 text-purple-400 hover:text-white transition-colors">
                    <ArrowRight className="w-5 h-5" />
                 </button>
            </div>
        </div>
      </div>
    </div>
  );
};

// --- Pages ---

const LandingPage = ({ onOpenAI }: { onOpenAI: () => void }) => {
  const navigate = useNavigate();
  const { events } = useEvents();

  return (
    <div className="min-h-screen relative pt-20 pb-32 px-4">
      {/* Hero */}
      <div className="max-w-7xl mx-auto flex flex-col items-center justify-center text-center mt-8 md:mt-24 mb-24 md:mb-32 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] md:w-[600px] md:h-[600px] bg-purple-600/20 rounded-full blur-[80px] md:blur-[120px] -z-10 animate-pulse-slow"></div>
        
        <div onClick={onOpenAI} className="mb-8 md:mb-12 cursor-pointer transition-transform hover:scale-105 active:scale-95">
           <Orb active={false} />
        </div>

        <h1 className="text-4xl md:text-7xl font-bold mb-6 tracking-tight px-4">
          <span className="block text-white mb-2">Experience Events</span>
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 text-glow">
            Reimagined by AI
          </span>
        </h1>
        <p className="text-lg md:text-xl text-gray-400 max-w-2xl mb-10 leading-relaxed px-4">
          Discover, host, and attend immersive events with the power of voice-activated intelligence.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 w-full md:w-auto px-4">
          <Button onClick={onOpenAI} icon={Mic}>Speak to Circle</Button>
          <Button variant="glass" onClick={() => navigate('/explore')} icon={Search}>Explore Events</Button>
        </div>
        
        <div className="mt-8 md:mt-12 text-sm text-gray-500">
           Tap the orb or speak to start planning.
        </div>
      </div>

      {/* Featured Section */}
      <div className="max-w-7xl mx-auto pb-10">
        <div className="flex items-center justify-between mb-8 px-2">
          <h2 className="text-2xl font-bold text-white">Trending Now</h2>
          <Link to="/explore" className="text-purple-400 hover:text-purple-300 flex items-center text-sm">View all <ChevronRight className="w-4 h-4 ml-1" /></Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {events.slice(0, 3).map(event => (
            <EventCard key={event.id} event={event} onClick={() => navigate(`/event/${event.id}`)} />
          ))}
        </div>
      </div>
    </div>
  );
};

const ExplorePage = () => {
  const [filter, setFilter] = useState('All');
  const [search, setSearch] = useState('');
  const navigate = useNavigate();
  const { events } = useEvents();

  const filteredEvents = events.filter(e => {
      const matchesSearch = e.title.toLowerCase().includes(search.toLowerCase());
      const matchesFilter = filter === 'All' || e.category === filter || e.format === filter;
      return matchesSearch && matchesFilter;
  });

  return (
    <div className="min-h-screen pt-24 px-4 pb-32 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Explore Events</h1>
          <p className="text-gray-400">Find your next unforgettable experience.</p>
        </div>
        
        <div className="flex flex-col gap-4 w-full md:w-auto">
            <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input 
                  type="text" 
                  placeholder="Search events..." 
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-12 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white w-full md:w-64 focus:outline-none focus:border-purple-500/50"
                />
            </div>
            {/* Filter Tabs */}
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4 md:mx-0 md:px-0">
              {['All', 'Sports', 'Tech', 'Art', 'Online'].map(f => (
                <button 
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-colors ${filter === f ? 'bg-purple-600 text-white' : 'bg-white/5 text-gray-400 hover:text-white'}`}
                >
                  {f}
                </button>
              ))}
            </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredEvents.map(event => (
          <EventCard key={event.id} event={event} onClick={() => navigate(`/event/${event.id}`)} />
        ))}
      </div>
      
      {filteredEvents.length === 0 && (
          <div className="text-center py-20">
              <p className="text-gray-500 text-lg">No events found matching your criteria.</p>
          </div>
      )}
    </div>
  );
};

const SeatMapPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [selectedSeats, setSelectedSeats] = useState<TicketSelection[]>([]);
    
    // Simulate map interaction
    const handleSeatClick = (section: string, row: string, seat: string, price: number) => {
        const id = `${section}-${row}-${seat}`;
        if (selectedSeats.find(s => s.id === id)) {
            setSelectedSeats(prev => prev.filter(s => s.id !== id));
        } else {
            setSelectedSeats(prev => [...prev, { section, row, seat, price, id }]);
        }
    };

    const total = selectedSeats.reduce((acc, curr) => acc + curr.price, 0);

    return (
        <div className="min-h-screen pt-24 px-4 pb-32 max-w-7xl mx-auto flex flex-col md:flex-row gap-8">
            {/* Map Area */}
            <div className="flex-1 glass-card rounded-3xl p-4 md:p-6 relative min-h-[400px] md:min-h-[600px] flex items-center justify-center overflow-hidden">
                <div className="absolute top-4 left-4 z-10">
                    <Button variant="ghost" className="pl-0 text-sm" onClick={() => navigate(-1)}>← Back</Button>
                    <h2 className="text-xl md:text-2xl font-bold text-white mt-2">Select Seats</h2>
                </div>

                {/* Simulated CSS Radial Interactive Map */}
                <div className="relative w-[600px] h-[600px] scale-[0.55] sm:scale-75 md:scale-100 transition-transform origin-center">
                    {/* Arena Center */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 bg-gray-800 rounded-xl flex items-center justify-center border border-gray-700">
                        <span className="text-gray-500 font-bold tracking-widest">STAGE</span>
                    </div>
                    
                    {/* Sections Rings */}
                    {[1, 2, 3].map((ring) => (
                        <div key={ring} className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white/5`} style={{ width: `${ring * 200 + 100}px`, height: `${ring * 200 + 100}px` }}>
                            {/* Render Mock Sections */}
                            {Array.from({ length: 8 }).map((_, i) => {
                                const angle = (i * 45) * (Math.PI / 180);
                                const radius = (ring * 100 + 50);
                                const x = Math.cos(angle) * radius;
                                const y = Math.sin(angle) * radius;
                                const sectionId = `Sec ${ring}0${i}`;
                                const price = 200 + (3-ring)*100;
                                const isSelected = selectedSeats.some(s => s.section === sectionId);

                                return (
                                    <button
                                        key={i}
                                        onClick={() => handleSeatClick(sectionId, 'A', '1', price)}
                                        className={`absolute w-16 h-12 rounded-lg text-[10px] font-bold transition-all duration-300 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center justify-center touch-manipulation
                                            ${isSelected ? 'bg-purple-600 text-white shadow-[0_0_15px_rgba(168,85,247,0.5)] scale-110' : 'bg-white/10 text-gray-300 hover:bg-white/20'}`}
                                        style={{ 
                                            left: `calc(50% + ${x}px)`, 
                                            top: `calc(50% + ${y}px)`,
                                            transform: `translate(-50%, -50%) rotate(${i * 45 + 90}deg)`
                                        }}
                                    >
                                        <span>{sectionId}</span>
                                        <span className="text-xs opacity-70">${price}</span>
                                    </button>
                                );
                            })}
                        </div>
                    ))}
                </div>
            </div>

            {/* Selection Sidebar */}
            <div className="w-full md:w-96 flex flex-col gap-4">
                <div className="glass-card rounded-3xl p-6 flex-1">
                    <h3 className="text-xl font-bold text-white mb-6">Your Tickets</h3>
                    
                    {selectedSeats.length === 0 ? (
                        <div className="text-center py-10 text-gray-500">
                            Select seats on the map to proceed.
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {selectedSeats.map(seat => (
                                <div key={seat.id} className="flex justify-between items-center p-3 rounded-xl bg-white/5 border border-white/5">
                                    <div>
                                        <div className="text-white font-medium">{seat.section}</div>
                                        <div className="text-xs text-gray-400">Row {seat.row} • Seat {seat.seat}</div>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <span className="text-purple-400 font-bold">${seat.price}</span>
                                        <button onClick={() => handleSeatClick(seat.section, seat.row, seat.seat, seat.price)} className="text-gray-500 hover:text-red-400 p-2">
                                            <X className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                    
                    <div className="mt-8 pt-6 border-t border-white/10">
                        <div className="flex justify-between text-lg font-bold text-white mb-6">
                            <span>Total</span>
                            <span>${total}</span>
                        </div>
                        <Button className="w-full" disabled={selectedSeats.length === 0} onClick={() => alert("Purchase Flow Confirmed!")}>
                             Complete Purchase
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
};

const CreateEventPage = () => {
    const { addEvent, user } = useEvents();
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    
    // Expanded Form State
    const [formData, setFormData] = useState({
        title: '',
        category: 'Tech',
        format: 'In-Person' as EventFormat,
        date: '',
        time: '',
        location: '', // Address or URL
        capacity: 100,
        price: 0,
        imageUrl: '',
        description: '',
        sponsorId: '' as string | null,
    });

    // Sponsorship Sub-State
    const [optInSponsorship, setOptInSponsorship] = useState(false);
    const [sponsorStep, setSponsorStep] = useState<'requirements' | 'matching' | 'results' | 'outreach'>('requirements');
    const [sponsorNeeds, setSponsorNeeds] = useState({
        industries: [] as string[],
        tiers: [] as string[],
        perks: [] as string[],
        budget: '',
    });
    const [matchedSponsors, setMatchedSponsors] = useState<any[]>([]);
    const [selectedSponsorForOutreach, setSelectedSponsorForOutreach] = useState<Sponsor | null>(null);
    const [outreachMessage, setOutreachMessage] = useState('');
    
    const [isRecording, setIsRecording] = useState(false);
    
    const handleNext = () => setStep(step + 1);
    const handleBack = () => setStep(step - 1);

    const handlePublish = () => {
        const newEvent: Event = {
            id: `e${Date.now()}`,
            ...formData,
            hostId: user.id,
            attendees: 0,
            tags: [formData.category, formData.format],
            venueName: formData.format === 'In-Person' ? formData.location.split(',')[0] : 'Virtual',
        };
        addEvent(newEvent);
        navigate('/profile'); // Redirect to profile to see hosted event
    };

    const toggleRecord = () => {
        setIsRecording(!isRecording);
        if(!isRecording) {
            setTimeout(() => {
                setIsRecording(false);
                setFormData(prev => ({...prev, description: "Join us for an exclusive tech networking night where founders and VCs connect. Expect panel discussions on Series A funding and open mic pitches."}));
            }, 2000);
        }
    };

    // --- Sponsorship Logic ---

    const runSponsorshipMatch = () => {
        setSponsorStep('matching');
        setTimeout(() => {
            // Simulated AI Matching Logic
            let matches = SPONSORS.filter(s => {
                // Simple category matching simulation
                if (formData.category === 'Tech' && ['TechFlow', 'CryptoSecure', 'SoundWave'].includes(s.name)) return true;
                if (formData.category === 'Sports' && ['Nebula Drink', 'GreenEat'].includes(s.name)) return true;
                if (formData.category === 'Art' && ['Urban Threads', 'SoundWave'].includes(s.name)) return true;
                if (formData.category === 'Music' && ['SoundWave', 'Nebula Drink'].includes(s.name)) return true;
                return Math.random() > 0.7; // Random others
            }).map(s => ({
                ...s,
                matchScore: Math.floor(85 + Math.random() * 14),
                reason: `Strong alignment with your ${formData.category} audience.`,
                estBudget: s.tier === 'Platinum' ? '$10k - $25k' : s.tier === 'Gold' ? '$5k - $10k' : '$1k - $5k'
            }));

            // Ensure at least one match
            if (matches.length === 0) {
                 matches = [SPONSORS[0]].map(s => ({...s, matchScore: 92, reason: "Top rated sponsor for general events.", estBudget: '$5k+'}))
            }

            setMatchedSponsors(matches.sort((a,b) => b.matchScore - a.matchScore));
            setSponsorStep('results');
        }, 3000);
    };

    const startOutreach = (sponsor: Sponsor) => {
        setSelectedSponsorForOutreach(sponsor);
        setOutreachMessage(
`Dear ${sponsor.name} Team,

I am hosting "${formData.title}", a premier ${formData.category} event on ${formData.date}. We expect ${formData.capacity} attendees and believe your brand aligns perfectly with our audience.

We are looking for a ${sponsor.tier} partner and would love to discuss offering ${sponsor.perks.join(', ')} in exchange for your support.

Best,
${user.name}`
        );
        setSponsorStep('outreach');
    };

    const sendOutreach = () => {
        // Simulate sending
        if (selectedSponsorForOutreach) {
            setFormData(prev => ({ ...prev, sponsorId: selectedSponsorForOutreach.id }));
            // Reset flow to just show success or move next
            setSponsorStep('results'); // Or go to a "success" state
        }
    };

    const toggleNeed = (field: 'industries' | 'tiers' | 'perks', value: string) => {
        setSponsorNeeds(prev => {
            const current = prev[field];
            const updated = current.includes(value) 
                ? current.filter(i => i !== value)
                : [...current, value];
            return { ...prev, [field]: updated };
        });
    };

    return (
        <div className="min-h-screen pt-24 px-4 pb-32 max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-white mb-2">Host an Event</h1>
            <p className="text-gray-400 mb-8">Create an unforgettable experience.</p>
            
            {/* Steps Indicator */}
            <div className="flex items-center gap-2 mb-12 overflow-x-auto pb-2">
                {[1, 2, 3, 4, 5, 6].map(s => (
                    <div key={s} className={`flex-1 min-w-[30px] h-2 rounded-full transition-all ${s <= step ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-white/10'}`}></div>
                ))}
            </div>

            <div className="glass-card p-6 md:p-8 rounded-3xl animate-in fade-in slide-in-from-bottom-4 duration-500">
                
                {/* Step 1: Basics */}
                {step === 1 && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><Sparkles className="w-5 h-5 text-purple-400"/> Event Basics</h2>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Event Title</label>
                            <input 
                                type="text" 
                                className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white focus:border-purple-500/50 focus:outline-none"
                                placeholder="e.g. Neon Tech Summit"
                                value={formData.title}
                                onChange={(e) => setFormData({...formData, title: e.target.value})}
                            />
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">Category</label>
                                <select 
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white focus:border-purple-500/50 focus:outline-none appearance-none"
                                    value={formData.category}
                                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                                >
                                    <option className="bg-gray-900" value="Tech">Tech</option>
                                    <option className="bg-gray-900" value="Art">Art</option>
                                    <option className="bg-gray-900" value="Sports">Sports</option>
                                    <option className="bg-gray-900" value="Music">Music</option>
                                    <option className="bg-gray-900" value="Business">Business</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">Format</label>
                                <select 
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white focus:border-purple-500/50 focus:outline-none appearance-none"
                                    value={formData.format}
                                    onChange={(e) => setFormData({...formData, format: e.target.value as EventFormat})}
                                >
                                    <option className="bg-gray-900" value="In-Person">In-Person</option>
                                    <option className="bg-gray-900" value="Online">Online</option>
                                    <option className="bg-gray-900" value="Hybrid">Hybrid</option>
                                </select>
                            </div>
                        </div>
                    </div>
                )}

                {/* Step 2: Logistics */}
                {step === 2 && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><Clock className="w-5 h-5 text-purple-400"/> Logistics</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">Date</label>
                                <input 
                                    type="date" 
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white focus:border-purple-500/50 focus:outline-none"
                                    value={formData.date}
                                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">Time</label>
                                <input 
                                    type="time" 
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white focus:border-purple-500/50 focus:outline-none"
                                    value={formData.time}
                                    onChange={(e) => setFormData({...formData, time: e.target.value})}
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">
                                {formData.format === 'Online' ? 'Meeting URL' : 'Venue Address'}
                            </label>
                            <div className="relative">
                                {formData.format === 'Online' ? <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" /> : <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />}
                                <input 
                                    type="text" 
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-4 pl-12 text-white focus:border-purple-500/50 focus:outline-none"
                                    placeholder={formData.format === 'Online' ? "https://zoom.us/j/..." : "123 Event St, City, State"}
                                    value={formData.location}
                                    onChange={(e) => setFormData({...formData, location: e.target.value})}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {/* Step 3: Capacity & Details */}
                {step === 3 && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><Users className="w-5 h-5 text-purple-400"/> Capacity & Price</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                             <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">Max Capacity</label>
                                <div className="relative">
                                    <Users className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                    <input 
                                        type="number" 
                                        className="w-full bg-white/5 border border-white/10 rounded-xl p-4 pl-12 text-white focus:border-purple-500/50 focus:outline-none"
                                        value={formData.capacity}
                                        onChange={(e) => setFormData({...formData, capacity: parseInt(e.target.value)})}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">Ticket Price ($)</label>
                                <div className="relative">
                                    <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                    <input 
                                        type="number" 
                                        className="w-full bg-white/5 border border-white/10 rounded-xl p-4 pl-12 text-white focus:border-purple-500/50 focus:outline-none"
                                        placeholder="0 for free"
                                        value={formData.price}
                                        onChange={(e) => setFormData({...formData, price: parseInt(e.target.value)})}
                                    />
                                </div>
                            </div>
                        </div>
                        <div>
                             <label className="block text-sm font-medium text-gray-400 mb-2">Cover Image URL</label>
                             <div className="relative">
                                <ImageIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                <input 
                                    type="text" 
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-4 pl-12 text-white focus:border-purple-500/50 focus:outline-none"
                                    placeholder="https://..."
                                    value={formData.imageUrl}
                                    onChange={(e) => setFormData({...formData, imageUrl: e.target.value})}
                                />
                             </div>
                             {formData.imageUrl && (
                                 <img src={formData.imageUrl} alt="Preview" className="mt-4 w-full h-40 object-cover rounded-xl border border-white/10" />
                             )}
                        </div>
                    </div>
                )}

                {/* Step 4: Description (AI Voice) */}
                {step === 4 && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><Mic2 className="w-5 h-5 text-purple-400"/> Description</h2>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Event Details (Voice Enabled)</label>
                            <div className="relative">
                                <textarea 
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white focus:border-purple-500/50 focus:outline-none h-40 resize-none"
                                    placeholder="Type or tap the mic to dictate..."
                                    value={formData.description}
                                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                                />
                                <button 
                                    onClick={toggleRecord}
                                    className={`absolute bottom-4 right-4 p-2 rounded-full transition-all ${isRecording ? 'bg-red-500/20 text-red-500 animate-pulse' : 'bg-white/10 text-gray-400 hover:text-white'}`}
                                >
                                    {isRecording ? <Mic2 className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Step 5: Expanded Sponsorship Flow */}
                {step === 5 && (
                    <div className="space-y-8 min-h-[400px]">
                         <div className="text-center mb-6">
                            <Sparkles className="w-10 h-10 text-yellow-400 mx-auto mb-2" />
                            <h3 className="text-2xl font-bold text-white">Sponsorship Hub</h3>
                            <p className="text-gray-400 text-sm">Connect with brands that align with your vision.</p>
                         </div>

                         {!optInSponsorship ? (
                            <div className="p-8 rounded-2xl border border-white/10 bg-white/5 flex flex-col items-center text-center space-y-6">
                                <div className="p-4 bg-gradient-to-br from-yellow-500/20 to-orange-500/20 rounded-full border border-yellow-500/20">
                                    <Briefcase className="w-8 h-8 text-yellow-400" />
                                </div>
                                <div>
                                    <h4 className="text-xl font-bold text-white mb-2">Find a Sponsor?</h4>
                                    <p className="text-gray-400 max-w-sm mx-auto">Our AI can analyze your event details to find the perfect brand partners to fund your experience.</p>
                                </div>
                                <div className="flex gap-4 w-full max-w-xs">
                                    <Button variant="ghost" className="flex-1" onClick={() => setStep(6)}>Skip</Button>
                                    <Button className="flex-1" onClick={() => { setOptInSponsorship(true); setSponsorStep('requirements'); }}>Let's Start</Button>
                                </div>
                            </div>
                         ) : (
                             <>
                                {/* Sub-Step 1: Collect Requirements */}
                                {sponsorStep === 'requirements' && (
                                    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                                        <div>
                                            <label className="text-sm font-medium text-gray-300 mb-3 block">Preferred Industry</label>
                                            <div className="flex flex-wrap gap-2">
                                                {['Tech', 'Beverage', 'Crypto', 'Fashion', 'Wellness', 'Music'].map(i => (
                                                    <button 
                                                        key={i}
                                                        onClick={() => toggleNeed('industries', i)}
                                                        className={`px-4 py-2 rounded-xl text-sm font-medium border transition-all ${sponsorNeeds.industries.includes(i) ? 'bg-purple-600 border-purple-500 text-white' : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'}`}
                                                    >
                                                        {i}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>

                                        <div>
                                            <label className="text-sm font-medium text-gray-300 mb-3 block">Sponsorship Tiers Needed</label>
                                            <div className="flex flex-wrap gap-2">
                                                {['Title ($20k+)', 'Gold ($10k)', 'Silver ($5k)', 'In-Kind'].map(t => (
                                                    <button 
                                                        key={t}
                                                        onClick={() => toggleNeed('tiers', t)}
                                                        className={`px-4 py-2 rounded-xl text-sm font-medium border transition-all ${sponsorNeeds.tiers.includes(t) ? 'bg-purple-600 border-purple-500 text-white' : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'}`}
                                                    >
                                                        {t}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>

                                        <div>
                                            <label className="text-sm font-medium text-gray-300 mb-3 block">What can you offer?</label>
                                            <div className="flex flex-wrap gap-2">
                                                {['Logo Placement', 'Booth Space', 'Speaking Slot', 'Social Shoutout', 'VIP Tickets'].map(p => (
                                                    <button 
                                                        key={p}
                                                        onClick={() => toggleNeed('perks', p)}
                                                        className={`px-4 py-2 rounded-xl text-sm font-medium border transition-all ${sponsorNeeds.perks.includes(p) ? 'bg-purple-600 border-purple-500 text-white' : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'}`}
                                                    >
                                                        {p}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                        
                                        <Button className="w-full mt-4" onClick={runSponsorshipMatch} icon={Zap}>
                                            Analyze & Match
                                        </Button>
                                    </div>
                                )}

                                {/* Sub-Step 2: Matching Loading State */}
                                {sponsorStep === 'matching' && (
                                    <div className="flex flex-col items-center justify-center py-10">
                                        <div className="relative w-24 h-24 mb-6">
                                            <div className="absolute inset-0 rounded-full border-4 border-purple-500/30 border-t-purple-500 animate-spin"></div>
                                            <div className="absolute inset-4 rounded-full border-4 border-cyan-500/30 border-b-cyan-500 animate-spin-reverse-slow"></div>
                                        </div>
                                        <p className="text-lg font-medium text-white animate-pulse">AI is finding your perfect partners...</p>
                                        <p className="text-sm text-gray-500 mt-2">Analyzing industry fit and budget alignment.</p>
                                    </div>
                                )}

                                {/* Sub-Step 3: Results List */}
                                {sponsorStep === 'results' && (
                                    <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-300">
                                        <div className="flex justify-between items-center mb-2">
                                            <h4 className="text-white font-bold">Top Matches</h4>
                                            <button onClick={() => setSponsorStep('requirements')} className="text-xs text-purple-400 hover:text-purple-300">Edit Needs</button>
                                        </div>
                                        
                                        <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                                            {matchedSponsors.map((sponsor: any) => (
                                                <div key={sponsor.id} className={`p-4 rounded-xl border transition-all ${formData.sponsorId === sponsor.id ? 'bg-green-500/10 border-green-500/50' : 'bg-white/5 border-white/10 hover:border-white/20'}`}>
                                                    <div className="flex justify-between items-start mb-2">
                                                        <div className="flex items-center gap-3">
                                                            <img src={sponsor.logoUrl} className="w-10 h-10 rounded-lg bg-white p-1 object-contain" />
                                                            <div>
                                                                <h5 className="font-bold text-white text-sm">{sponsor.name}</h5>
                                                                <span className="text-xs text-gray-400">{sponsor.tier} Partner</span>
                                                            </div>
                                                        </div>
                                                        <span className="text-xs font-bold text-green-400 bg-green-500/10 px-2 py-1 rounded-full">{sponsor.matchScore}% Match</span>
                                                    </div>
                                                    
                                                    <div className="text-xs text-gray-300 mb-3 bg-black/20 p-2 rounded-lg">
                                                        <span className="font-bold text-purple-400">Why:</span> {sponsor.reason}
                                                    </div>
                                                    
                                                    <div className="flex justify-between items-center mt-3 pt-3 border-t border-white/5">
                                                        <span className="text-xs text-gray-500 font-mono">Est. {sponsor.estBudget}</span>
                                                        {formData.sponsorId === sponsor.id ? (
                                                            <span className="text-xs font-bold text-green-500 flex items-center gap-1"><Check className="w-3 h-3"/> Requested</span>
                                                        ) : (
                                                            <button onClick={() => startOutreach(sponsor)} className="text-xs font-bold text-white bg-purple-600 hover:bg-purple-500 px-3 py-1.5 rounded-lg transition-colors">
                                                                Send Request
                                                            </button>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                        <Button variant="ghost" className="w-full text-sm" onClick={() => setStep(6)}>Continue Matching Later</Button>
                                    </div>
                                )}

                                {/* Sub-Step 4: Outreach Composer */}
                                {sponsorStep === 'outreach' && selectedSponsorForOutreach && (
                                    <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-300">
                                        <div className="flex items-center gap-3 mb-2">
                                            <button onClick={() => setSponsorStep('results')} className="text-gray-400 hover:text-white"><ArrowRight className="w-4 h-4 rotate-180" /></button>
                                            <h4 className="font-bold text-white">Draft Request to {selectedSponsorForOutreach.name}</h4>
                                        </div>

                                        <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                                            <div className="flex items-center gap-2 mb-4 border-b border-white/10 pb-3">
                                                <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center">
                                                    <Mail className="w-4 h-4 text-purple-400" />
                                                </div>
                                                <div>
                                                    <p className="text-xs text-gray-400">To:</p>
                                                    <p className="text-sm text-white font-medium">sponsorships@{selectedSponsorForOutreach.name.toLowerCase().replace(' ', '')}.com</p>
                                                </div>
                                            </div>
                                            <textarea 
                                                value={outreachMessage}
                                                onChange={(e) => setOutreachMessage(e.target.value)}
                                                className="w-full bg-transparent text-gray-300 text-sm leading-relaxed focus:outline-none h-48 resize-none"
                                            />
                                        </div>
                                        
                                        <div className="flex gap-3">
                                            <Button variant="ghost" onClick={() => setSponsorStep('results')} className="flex-1">Cancel</Button>
                                            <Button onClick={sendOutreach} className="flex-1" icon={Send}>Send Proposal</Button>
                                        </div>
                                    </div>
                                )}
                             </>
                         )}
                    </div>
                )}

                {/* Step 6: Review & Publish */}
                {step === 6 && (
                    <div className="text-center py-8">
                        <div className="w-20 h-20 bg-green-500/20 text-green-500 rounded-full flex items-center justify-center mx-auto mb-6 border border-green-500/30">
                            <Check className="w-10 h-10" />
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">Ready to Publish?</h2>
                        <p className="text-gray-400 mb-8">Your event "{formData.title}" will be live for everyone to see.</p>
                        
                        <div className="text-left bg-white/5 p-4 rounded-xl mb-6">
                             <div className="flex justify-between mb-2">
                                 <span className="text-gray-400">Date</span>
                                 <span className="text-white">{formData.date} at {formData.time}</span>
                             </div>
                             <div className="flex justify-between mb-2">
                                 <span className="text-gray-400">Location</span>
                                 <span className="text-white">{formData.location}</span>
                             </div>
                             <div className="flex justify-between">
                                 <span className="text-gray-400">Format</span>
                                 <span className="text-white">{formData.format}</span>
                             </div>
                        </div>

                        {formData.sponsorId && (
                            <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-500/10 border border-yellow-500/30 rounded-full text-yellow-400 mb-8">
                                <Sparkles className="w-4 h-4" />
                                <span className="text-sm font-bold">Sponsored Pending</span>
                            </div>
                        )}
                    </div>
                )}

                <div className="flex justify-between mt-8 pt-8 border-t border-white/10">
                    {step > 1 ? (
                        <Button variant="ghost" onClick={handleBack}>Back</Button>
                    ) : <div></div>}
                    
                    {step < 6 ? (
                        <Button onClick={handleNext} disabled={step === 5 && optInSponsorship && sponsorStep !== 'results'}>
                            {step === 5 ? "Next Step" : "Next Step"}
                        </Button>
                    ) : (
                        <Button onClick={handlePublish}>Publish Event</Button>
                    )}
                </div>
            </div>
        </div>
    );
};

const EventDetailsPage = () => {
    const { id } = useParams();
    const { events } = useEvents();
    const event = events.find(e => e.id === id);
    const navigate = useNavigate();

    if (!event) return <div className="text-white pt-24 text-center">Event not found</div>;

    return (
        <div className="min-h-screen pt-0 pb-32">
             {/* Hero Image */}
             <div className="relative h-[40vh] md:h-[50vh] w-full">
                 <div className="absolute inset-0 bg-gradient-to-t from-[#030014] via-[#030014]/60 to-transparent z-10"></div>
                 {event.imageUrl ? (
                    <img src={event.imageUrl} className="w-full h-full object-cover" />
                 ) : (
                    <div className="w-full h-full bg-gray-900 flex items-center justify-center">
                        <ImageIcon className="w-20 h-20 text-gray-700" />
                    </div>
                 )}
                 <div className="absolute top-6 left-4 z-20">
                     <Button variant="glass" className="rounded-full w-10 h-10 p-0 flex items-center justify-center" onClick={() => navigate(-1)}>
                         <span className="text-lg pb-1">←</span>
                     </Button>
                 </div>
             </div>

             <div className="max-w-5xl mx-auto px-4 -mt-20 md:-mt-32 relative z-20">
                 <div className="glass-card p-6 md:p-8 rounded-3xl mb-8 flex flex-col md:flex-row gap-8 items-start justify-between">
                     <div className="flex-1">
                         <div className="flex flex-wrap gap-2 mb-4">
                             {event.tags.map(t => (
                                 <span key={t} className="px-3 py-1 rounded-full text-xs bg-purple-500/20 text-purple-300 border border-purple-500/30">
                                     #{t}
                                 </span>
                             ))}
                         </div>
                         <h1 className="text-3xl md:text-5xl font-bold text-white mb-4 leading-tight">{event.title}</h1>
                         <div className="flex flex-col gap-2 text-gray-300 text-sm md:text-base">
                             <div className="flex items-center gap-2"><Calendar className="w-5 h-5 text-purple-400" /> {new Date(event.date).toLocaleDateString()} at {event.time}</div>
                             <div className="flex items-center gap-2"><MapPin className="w-5 h-5 text-purple-400" /> {event.venueName ? `${event.venueName}, ` : ''}{event.location}</div>
                             <div className="flex items-center gap-2"><UserIcon className="w-5 h-5 text-purple-400" /> Hosted by {event.hostId === MOCK_USER.id ? 'You' : (event.hostId === 'h1' ? 'UFC Official' : 'Tech Giants')}</div>
                         </div>
                     </div>
                     
                     <div className="w-full md:w-auto flex flex-col gap-4 min-w-[200px]">
                         <Button onClick={() => navigate(`/event/${event.id}/tickets`)} className="w-full">
                            Get Tickets (${event.price})
                         </Button>
                         <div className="flex gap-4">
                             <Button variant="glass" className="flex-1" icon={Heart}>Save</Button>
                             <Button variant="glass" className="flex-1" icon={Share2}>Share</Button>
                         </div>
                     </div>
                 </div>

                 <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                     <div className="md:col-span-2 space-y-8">
                         <section>
                             <h2 className="text-2xl font-bold text-white mb-4">About Event</h2>
                             <p className="text-gray-400 leading-relaxed text-lg">{event.description}</p>
                         </section>

                         {event.sponsorId && (
                             <section className="p-6 rounded-2xl bg-gradient-to-r from-[#1a1a2e] to-black border border-white/10">
                                 <div className="flex items-center justify-between mb-4">
                                     <h3 className="text-yellow-500 text-sm font-bold uppercase tracking-widest">Official Sponsor</h3>
                                     <span className="text-xs text-gray-500">Sponsored</span>
                                 </div>
                                 <div className="flex items-center gap-4">
                                     <div className="w-16 h-16 bg-white rounded-xl flex items-center justify-center shrink-0">
                                         {/* Mock Logo */}
                                         <span className="text-black font-bold">LOGO</span>
                                     </div>
                                     <div>
                                         <h4 className="text-white font-bold text-xl">Nebula Drink</h4>
                                         <p className="text-sm text-gray-400">Fueling the future of events.</p>
                                     </div>
                                     <Button variant="outline" className="ml-auto hidden sm:flex">Learn More</Button>
                                 </div>
                                 <Button variant="outline" className="w-full mt-4 sm:hidden">Learn More</Button>
                             </section>
                         )}
                     </div>

                     <div className="space-y-6">
                         <div className="glass-panel p-6 rounded-2xl">
                             <h3 className="text-white font-bold mb-4">Location</h3>
                             <div className="h-48 bg-gray-800 rounded-xl mb-4 flex items-center justify-center border border-white/10">
                                 <MapIcon className="w-8 h-8 text-gray-600" />
                                 <span className="ml-2 text-gray-400 text-sm">Map Placeholder</span>
                             </div>
                             <p className="text-gray-400 text-sm">{event.location}</p>
                         </div>
                     </div>
                 </div>
             </div>
        </div>
    );
};

const ProfilePage = () => {
    const { user, events } = useEvents();
    const hostedEvents = events.filter(e => e.hostId === user.id);

    return (
        <div className="min-h-screen pt-24 px-4 pb-32 max-w-4xl mx-auto">
            <div className="flex flex-col md:flex-row items-center md:items-start gap-6 mb-12 text-center md:text-left">
                <img src={user.avatarUrl} className="w-24 h-24 rounded-full border-2 border-purple-500 p-1" />
                <div>
                    <h1 className="text-3xl font-bold text-white">{user.name}</h1>
                    <p className="text-gray-400">{user.email}</p>
                    <div className="flex justify-center md:justify-start gap-4 mt-4">
                        <div className="text-center">
                            <span className="block text-xl font-bold text-white">{events.length}</span>
                            <span className="text-xs text-gray-500">Platform Events</span>
                        </div>
                        <div className="text-center">
                            <span className="block text-xl font-bold text-white">{hostedEvents.length}</span>
                            <span className="text-xs text-gray-500">Hosted</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="space-y-8">
                <div>
                    <h2 className="text-xl font-bold text-white mb-4">Hosted Events</h2>
                    {hostedEvents.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {hostedEvents.map(event => (
                                <div key={event.id} className="glass-card p-4 rounded-2xl flex gap-4 hover:bg-white/5 transition-colors">
                                     <img src={event.imageUrl || 'https://picsum.photos/200'} className="w-20 h-20 rounded-xl object-cover shrink-0" />
                                     <div className="min-w-0">
                                         <h3 className="font-bold text-white line-clamp-1">{event.title}</h3>
                                         <p className="text-xs text-gray-400 mt-1">{new Date(event.date).toLocaleDateString()}</p>
                                         <div className="mt-2 flex gap-2">
                                             <span className="text-[10px] bg-purple-500/20 text-purple-300 px-2 py-1 rounded-md">{event.format}</span>
                                             {event.sponsorId && <span className="text-[10px] bg-yellow-500/20 text-yellow-300 px-2 py-1 rounded-md">Sponsored</span>}
                                         </div>
                                     </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-gray-500">You haven't hosted any events yet.</p>
                    )}
                </div>

                <div>
                    <h2 className="text-xl font-bold text-white mb-4">Your Tickets</h2>
                    <div className="glass-card p-6 rounded-2xl flex flex-col sm:flex-row items-center justify-between border-l-4 border-l-purple-500 gap-4 text-center sm:text-left">
                        <div>
                            <h3 className="text-lg font-bold text-white">UFC 308: Las Vegas Fight Night</h3>
                            <p className="text-sm text-gray-400">Nov 9, 2025 • 8:00 PM</p>
                            <p className="text-sm text-purple-400 mt-2">Sec 201, Row A, Seats 1-3</p>
                        </div>
                        <div className="w-full sm:w-auto">
                            <Button variant="glass" className="text-sm w-full sm:w-auto">View Ticket</Button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

// --- Main App Component ---

const App = () => {
  const [events, setEvents] = useState<Event[]>(EVENTS);
  const [showAI, setShowAI] = useState(false);

  const addEvent = (event: Event) => {
    setEvents(prev => [event, ...prev]);
  };

  return (
    <EventContext.Provider value={{ events, addEvent, user: MOCK_USER }}>
      <HashRouter>
        <div className="bg-background min-h-screen text-white font-sans selection:bg-purple-500/30 selection:text-white">
          <NavBar />
          <AIAssistantOverlay isOpen={showAI} onClose={() => setShowAI(false)} />
          
          <Routes>
            <Route path="/" element={<LandingPage onOpenAI={() => setShowAI(true)} />} />
            <Route path="/explore" element={<ExplorePage />} />
            <Route path="/event/:id" element={<EventDetailsPage />} />
            <Route path="/event/:id/tickets" element={<SeatMapPage />} />
            <Route path="/host" element={<CreateEventPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Routes>

          {/* Mobile Bottom Navigation */}
          <MobileNav onOpenAI={() => setShowAI(true)} />
        </div>
      </HashRouter>
    </EventContext.Provider>
  );
};

export default App;