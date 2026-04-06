import React, { useState, useEffect, useRef, useContext, createContext } from 'react';
import { HashRouter, Routes, Route, Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { SponsorshipPage } from './components/SponsorshipPage';
import { calculateSponsorItemPrice } from './services/pricingService';
import { SPONSORSHIP_MENU } from './constants';
import { 
  Mic, Search, Calendar, MapPin, User as UserIcon, Plus, 
  Heart, Share2, ArrowRight, Video, MessageCircle, X,
  ChevronRight, Map as MapIcon, Mic2, Send, CreditCard, Check,
  Sparkles, Zap, RefreshCw, ShieldCheck, Clock, Users, DollarSign, Globe, Image as ImageIcon, Link as LinkIcon,
  Tag, Briefcase, FileText, Mail, Home, Compass, Shield, Edit
} from 'lucide-react';
import { EVENTS, SPONSORS, MOCK_USER } from './constants';
import { Event, Sponsor, ChatMessage, EventFormat, EventSponsorshipSettings, SponsorshipItem, AudienceType, SponsorshipProposal, User, SponsorDirectoryItem, SponsorProfile, SponsorEventMatch } from './types';

// --- Context Management ---

interface EventContextType {
  events: Event[];
  addEvent: (event: Event) => void;
  updateEvent: (event: Event) => void;
  deleteEvent: (eventId: string) => Promise<void>;
  attendEvent: (eventId: string) => Promise<void>;
  refreshUser: () => Promise<void>;
  fetchProposals: () => Promise<void>;
  user: User | null;
  proposals: SponsorshipProposal[];
  createProposal: (proposal: Omit<SponsorshipProposal, 'id' | 'senderId' | 'senderName' | 'status' | 'timestamp'>) => Promise<void>;
  updateProposalStatus: (proposalId: string, status: 'accepted' | 'declined') => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  uploadAvatar: (file: File) => Promise<void>;
  isLoading: boolean;
}

const EventContext = createContext<EventContextType>({
  events: [],
  addEvent: () => {},
  updateEvent: () => {},
  deleteEvent: async () => {},
  attendEvent: async () => {},
  refreshUser: async () => {},
  fetchProposals: async () => {},
  user: null,
  proposals: [],
  createProposal: async () => {},
  updateProposalStatus: async () => {},
  login: async () => {},
  register: async () => {},
  logout: async () => {},
  updateProfile: async () => {},
  uploadAvatar: async () => {},
  isLoading: true
});

export const useEvents = () => useContext(EventContext);

// --- Reusable Components ---

const Button = ({ children, variant = 'primary', className = '', onClick, icon: Icon, disabled = false, type = 'button' }: any) => {
  const base = "inline-flex items-center justify-center px-6 py-3 rounded-xl font-medium transition-all duration-300 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation";
  const variants = {
    primary: "bg-gradient-to-r from-teal-600 to-cyan-500 text-white shadow-[0_0_20px_rgba(13,148,136,0.3)] hover:shadow-[0_0_30px_rgba(13,148,136,0.4)]",
    glass: "bg-gray-100 backdrop-blur-md border border-gray-200 text-gray-800 hover:bg-gray-200 hover:border-gray-300",
    ghost: "text-gray-500 hover:text-gray-900 hover:bg-gray-50",
    outline: "border border-teal-500/50 text-teal-500 hover:bg-teal-500/10",
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
      <div className={`absolute inset-0 bg-teal-500/20 rounded-full blur-[80px] transition-all duration-1000 ${active ? 'scale-150 opacity-100' : 'scale-100 opacity-50'}`} />

      {/* 2. Outer Rotating Rings (Thin) */}
      <div className="absolute inset-[-4px] rounded-full border border-transparent border-t-teal-500/60 border-l-cyan-500/60 animate-spin-slow" />
      <div className="absolute inset-[-8px] rounded-full border border-transparent border-b-cyan-500/40 border-r-teal-500/40 animate-spin-reverse-slower" />

      {/* 3. The Sphere Container */}
      <div 
        className="relative w-full h-full rounded-full overflow-hidden backdrop-blur-md border border-gray-200 shadow-[inset_0_0_50px_rgba(255,255,255,0.15)] z-10 bg-gray-50 isolate transform-gpu"
        style={{
          WebkitMaskImage: '-webkit-radial-gradient(white, black)',
        }}
      >
          {/* 4. Conic Gradient Background */}
          <div className={`absolute inset-[-50%] w-[200%] h-[200%] bg-[conic-gradient(from_0deg,#0D9488,#06B6D4,#0F4C75,#0D9488)] animate-spin-slower blur-2xl opacity-60`} />
          
          {/* 5. Internal Fluid Blobs */}
          <div className={`absolute top-[20%] left-[20%] w-[60%] h-[60%] bg-teal-500 rounded-full mix-blend-overlay blur-xl animate-blob`} />
          <div className={`absolute top-[20%] right-[20%] w-[50%] h-[50%] bg-cyan-400 rounded-full mix-blend-overlay blur-xl animate-blob`} style={{ animationDelay: '2s' }} />
          <div className={`absolute bottom-[10%] left-[30%] w-[70%] h-[60%] bg-cyan-500 rounded-full mix-blend-overlay blur-xl animate-blob`} style={{ animationDelay: '4s' }} />

          {/* 6. Active State Core */}
          <div className={`absolute inset-0 bg-gray-100 transition-opacity duration-300 ${active ? 'opacity-100' : 'opacity-0'}`} />

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
  const { user, logout } = useEvents();
  const isActive = (path: string) => location.pathname === path ? 'text-teal-600' : 'text-gray-500 hover:text-gray-700';

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-panel border-b-0 rounded-b-2xl mx-4 mt-2 px-6 h-16 flex items-center justify-between">
      <Link to="/" className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-teal-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-teal-500/15">
          <div className="w-3 h-3 bg-white rounded-full"></div>
        </div>
        <span className="font-bold text-lg tracking-tight">Circle</span>
      </Link>

      <div className="hidden md:flex items-center gap-8">
        <Link to="/" className={`text-sm font-medium transition-colors ${isActive('/')}`}>Home</Link>
        <Link to="/explore" className={`text-sm font-medium transition-colors ${isActive('/explore')}`}>Explore</Link>
        <Link to="/sponsors" className={`text-sm font-medium transition-colors ${isActive('/sponsors')}`}>Sponsors</Link>
        <Link to="/host" className={`text-sm font-medium transition-colors ${isActive('/host')}`}>Host</Link>
        {user && <Link to="/profile" className={`text-sm font-medium transition-colors ${isActive('/profile')}`}>Profile</Link>}
      </div>

      <div className="flex items-center gap-4">
        <button className="p-2 rounded-full hover:bg-gray-100 transition-colors hidden md:block">
          <Search className="w-5 h-5 text-gray-500" />
        </button>
        {user ? (
          <div className="flex items-center gap-3">
            <Link to="/profile">
               <div className="w-8 h-8 rounded-full overflow-hidden border border-gray-300">
                 <img src={user.avatarUrl || 'https://picsum.photos/seed/user/200'} alt="Profile" className="w-full h-full object-cover" />
               </div>
            </Link>
            <button onClick={logout} className="text-xs text-gray-500 hover:text-gray-900 transition-colors hidden md:block">Logout</button>
          </div>
        ) : (
          <Link to="/auth">
            <Button variant="outline" className="px-4 py-1.5 text-xs">Login</Button>
          </Link>
        )}
      </div>
    </nav>
  );
};

const MobileNav = ({ onOpenAI }: { onOpenAI: () => void }) => {
  const location = useLocation();
  const isActive = (path: string) => location.pathname === path;
  const baseClass = "flex flex-col items-center justify-center w-full h-full space-y-1 touch-manipulation";
  const activeClass = "text-teal-500";
  const inactiveClass = "text-gray-500 hover:text-gray-700";

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 h-20 bg-white/95 backdrop-blur-xl border-t border-gray-200 px-4 pb-2 md:hidden flex items-center justify-between safe-area-bottom">
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
                className="w-14 h-14 rounded-full bg-gradient-to-r from-teal-600 to-cyan-600 flex items-center justify-center shadow-lg shadow-teal-500/20 border-4 border-white active:scale-95 transition-transform"
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

const EventCard: React.FC<{ event: Event; onClick: () => void; onEdit?: (e: React.MouseEvent) => void }> = ({ event, onClick, onEdit }) => {
  return (
    <div 
      onClick={onClick}
      className="group relative glass-card rounded-3xl overflow-hidden cursor-pointer transition-all duration-300 hover:scale-[1.02] hover:shadow-xl hover:shadow-teal-500/10"
    >
      <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/50 to-transparent z-10"></div>
      <img src={event.imageUrl || 'https://picsum.photos/seed/event/800/400'} alt={event.title} className="w-full h-64 object-cover transition-transform duration-700 group-hover:scale-110" />
      
      <div className="absolute top-4 right-4 z-20 flex gap-2">
        {onEdit && (
          <button 
            onClick={onEdit}
            className="p-2 rounded-full bg-white/20 backdrop-blur-md border border-white/30 text-white hover:bg-white/30 transition-colors"
          >
            <Edit className="w-4 h-4" />
          </button>
        )}
        <span className="px-3 py-1 rounded-full text-xs font-bold bg-white/20 backdrop-blur-md border border-white/30 text-white">
          {event.format}
        </span>
      </div>
      
      {event.sponsorId && (
         <div className="absolute top-4 left-4 z-20">
           <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 backdrop-blur-md border border-yellow-400/40">
             <span className="text-[10px] font-bold text-yellow-300 uppercase tracking-wider">Sponsored</span>
           </div>
         </div>
      )}

      <div className="absolute bottom-0 left-0 right-0 p-6 z-20">
        <div className="text-teal-300 text-sm font-semibold mb-1 uppercase tracking-wider">
          {new Date(event.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} • {event.time}
        </div>
        <h3 className="text-xl font-bold text-white mb-2 leading-tight">{event.title}</h3>
        <div className="flex items-center gap-2 text-gray-300 text-sm">
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
      aiResponse.text = "Perfect. I found 57 available spots within your $899 budget for UFC 308. I've opened the event details for you.";
      aiResponse.action = 'show_event';
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
    } else if (aiResponse.action === 'show_event') {
        setTimeout(() => {
             onClose();
             navigate(`/event/${aiResponse.data.eventId}`);
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
    <div className="fixed inset-0 z-[60] bg-gray-900/80 backdrop-blur-xl text-white flex flex-col items-center justify-end md:justify-center p-4">
      <button onClick={onClose} className="absolute top-6 right-6 p-2 bg-white/10 rounded-full hover:bg-white/20 text-white z-50">
        <X className="w-6 h-6" />
      </button>

      <div className="w-full max-w-2xl flex flex-col items-center gap-8 mb-8 md:mb-0 h-full md:h-auto justify-center">
        <div className="relative shrink-0">
             <Orb size="lg" active={isListening} />
             {isListening && <p className="absolute -bottom-12 left-0 right-0 text-center text-teal-300 animate-pulse">Listening...</p>}
        </div>

        <div className="w-full flex-1 md:h-[300px] md:flex-none overflow-y-auto space-y-4 px-4 scrollbar-hide mask-gradient-b">
          {messages.map(msg => (
            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] p-4 rounded-2xl ${msg.sender === 'user' ? 'bg-white/10 border border-white/10' : 'bg-gradient-to-br from-teal-900/50 to-blue-900/50 border border-teal-500/20'} backdrop-blur-md`}>
                <p className="text-white text-lg leading-relaxed">{msg.text}</p>
                {msg.action === 'show_events' && (
                  <div className="mt-4 space-y-2">
                     {msg.data.map((e: Event) => (
                        <div key={e.id} onClick={() => { onClose(); navigate(`/event/${e.id}`); }} className="flex items-center gap-3 p-2 bg-gray-900/40 rounded-lg cursor-pointer hover:bg-gray-50">
                            <img src={e.imageUrl || 'https://picsum.photos/seed/event/100'} className="w-12 h-12 rounded-lg object-cover" />
                            <div>
                                <p className="font-bold text-sm">{e.title}</p>
                                <p className="text-xs text-gray-500">{e.date}</p>
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
              className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-6 pr-14 text-white placeholder-gray-400 focus:outline-none focus:border-teal-500 focus:bg-white/10 transition-all"
            />
            <div className="absolute right-2 top-2 flex items-center gap-1">
                 <button onClick={toggleMic} className={`p-2 rounded-xl transition-colors ${isListening ? 'text-red-400 bg-red-500/10' : 'text-gray-500 hover:text-gray-900'}`}>
                    <Mic className="w-5 h-5" />
                 </button>
                 <button onClick={() => handleSend(inputValue)} className="p-2 text-teal-500 hover:text-gray-900 transition-colors">
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
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] md:w-[600px] md:h-[600px] bg-teal-500/15 rounded-full blur-[80px] md:blur-[120px] -z-10 animate-pulse-slow"></div>
        
        <div onClick={onOpenAI} className="mb-8 md:mb-12 cursor-pointer transition-transform hover:scale-105 active:scale-95">
           <Orb active={false} />
        </div>

        <h1 className="text-4xl md:text-7xl font-bold mb-6 tracking-tight px-4">
          <span className="block text-gray-800 mb-2">Experience Events</span>
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-teal-500 via-cyan-500 to-cyan-400 text-glow">
            Reimagined by AI
          </span>
        </h1>
        <p className="text-lg md:text-xl text-gray-500 max-w-2xl mb-10 leading-relaxed px-4">
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
          <h2 className="text-2xl font-bold text-gray-800">Trending Now</h2>
          <Link to="/explore" className="text-teal-500 hover:text-teal-600 flex items-center text-sm">View all <ChevronRight className="w-4 h-4 ml-1" /></Link>
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
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Explore Events</h1>
          <p className="text-gray-500">Find your next unforgettable experience.</p>
        </div>
        
        <div className="flex flex-col gap-4 w-full md:w-auto">
            <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input 
                  type="text" 
                  placeholder="Search events..." 
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-12 pr-4 py-3 rounded-xl bg-gray-50 border border-gray-200 text-gray-800 w-full md:w-64 focus:outline-none focus:border-teal-500"
                />
            </div>
            {/* Filter Tabs */}
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4 md:mx-0 md:px-0">
              {['All', 'Sports', 'Tech', 'Art', 'Online'].map(f => (
                <button 
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-colors ${filter === f ? 'bg-teal-600 text-white' : 'bg-gray-50 text-gray-500 hover:text-gray-900'}`}
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

const SponsorsPage = () => {
  const navigate = useNavigate();
  const { user, events, createProposal } = useEvents();
  const [sponsors, setSponsors] = useState<SponsorDirectoryItem[]>([]);
  const [isMatchedMode, setIsMatchedMode] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [matchEventId, setMatchEventId] = useState('');
  const [proposalEventId, setProposalEventId] = useState('');
  const [selectedSponsor, setSelectedSponsor] = useState<SponsorDirectoryItem | null>(null);
  const [expandedSponsorId, setExpandedSponsorId] = useState<string | null>(null);
  const [proposalMessage, setProposalMessage] = useState('');
  const [proposalBudget, setProposalBudget] = useState('1000');
  const hostedEvents = events.filter(e => e.hostId === user?.id);

  const fetchSponsors = async (eventId?: string) => {
    setIsLoading(true);
    setError('');
    try {
      const query = eventId ? `?eventId=${encodeURIComponent(eventId)}` : '';
      const response = await fetch(`/api/sponsors${query}`, { credentials: 'include' });
      if (!response.ok) throw new Error('Failed to load sponsors');
      const data = await response.json();
      setSponsors(data);
      setIsMatchedMode(!!eventId);
    } catch (err: any) {
      setError(err.message || 'Failed to load sponsors');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSponsors();
  }, []);

  const filteredSponsors = sponsors.filter((s) => {
    const searchValue = search.toLowerCase();
    return (
      s.companyName.toLowerCase().includes(searchValue) ||
      s.name.toLowerCase().includes(searchValue) ||
      s.industries.some((industry) => industry.toLowerCase().includes(searchValue))
    );
  });

  const getOutreachMessage = (sponsor: SponsorDirectoryItem, event: Event) => {
    const audienceType = event.sponsorshipSettings?.audience_type
      ? event.sponsorshipSettings.audience_type.replace(/_/g, ' ')
      : 'general public';
    const offerings = event.sponsorshipSettings?.allowed_item_ids?.length
      ? SPONSORSHIP_MENU
          .filter(item => event.sponsorshipSettings?.allowed_item_ids.includes(item.id))
          .slice(0, 4)
          .map(item => item.name)
          .join(', ')
      : 'custom sponsor visibility options, community engagement, and content placement';
    const hostContext = [user?.name, user?.location, user?.bio]
      .filter(Boolean)
      .join(' • ');
    const fitLine = sponsor.matchReason
      ? `Based on our sponsor matching, we believe there is a strong fit: ${sponsor.matchReason}.`
      : `Your focus on ${sponsor.industries.slice(0, 2).join(' and ')} aligns with our audience and event goals.`;

    return `Hi ${sponsor.companyName} team,\n\nI’m reaching out about a partnership for our event \"${event.title}\" (${event.format}) on ${event.date} at ${event.location}.\n\nEvent highlights:\n- Category: ${event.category}\n- Expected attendance: ${event.capacity}\n- Audience: ${audienceType}\n- Sponsor opportunities: ${offerings}\n\n${fitLine}\n\nWe’re looking for a sponsor who can help us elevate attendee experience while getting meaningful brand exposure. Our current sponsorship estimate is around $${proposalBudget || '1000'}, and we’re open to tailoring a package around your goals.\n\nHost context: ${hostContext || 'Circle event host'}\n\nWould you be open to a quick call this week to discuss a partnership package?\n\nBest,\n${user?.name || 'Event Host'}`;
  };

  const handleRunMatch = async () => {
    if (!user) {
      navigate('/auth');
      return;
    }
    if (!hostedEvents.length) {
      alert('Host an event first to run sponsor matching.');
      return;
    }

    const eventId = matchEventId || hostedEvents[0].id;
    setMatchEventId(eventId);
    await fetchSponsors(eventId);
  };

  const handleClearMatch = async () => {
    setMatchEventId('');
    await fetchSponsors();
  };

  const startProposal = (sponsor: SponsorDirectoryItem) => {
    if (!user) {
      navigate('/auth');
      return;
    }
    if (!hostedEvents.length) {
      alert('Host an event first to send sponsor partnership requests.');
      return;
    }

    const defaultEvent = (matchEventId ? events.find(e => e.id === matchEventId) : hostedEvents[0]) || hostedEvents[0];
    const budgetGuess = sponsor.budgetMin && sponsor.budgetMax
      ? Math.round((sponsor.budgetMin + sponsor.budgetMax) / 2)
      : 1000;

    setSelectedSponsor(sponsor);
    setProposalEventId(defaultEvent.id);
    setProposalBudget(String(budgetGuess));
    setProposalMessage(getOutreachMessage(sponsor, defaultEvent));
  };

  useEffect(() => {
    if (!selectedSponsor || !proposalEventId) return;
    const selectedEvent = events.find(e => e.id === proposalEventId);
    if (!selectedEvent) return;
    setProposalMessage(getOutreachMessage(selectedSponsor, selectedEvent));
  }, [proposalEventId, proposalBudget]);

  const sendPartnershipRequest = async () => {
    if (!selectedSponsor || !user) return;
    const event = events.find(e => e.id === proposalEventId) || hostedEvents[0];
    if (!event) {
      alert('Select one of your hosted events first.');
      return;
    }

    try {
      await createProposal({
        eventId: event.id,
        eventTitle: event.title,
        receiverId: selectedSponsor.userId,
        message: proposalMessage,
        estimatedInvestment: Number(proposalBudget) || 0,
        proposalType: 'partnership'
      });
      alert('Partnership request sent successfully.');
      setSelectedSponsor(null);
    } catch (err: any) {
      alert(err.message || 'Failed to send partnership request');
    }
  };

  return (
    <div className="min-h-screen pt-24 px-4 pb-32 max-w-7xl mx-auto">
      {selectedSponsor && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-gray-900/80 backdrop-blur-sm" onClick={() => setSelectedSponsor(null)}></div>
          <div className="relative z-10 w-full max-w-2xl glass-card border border-gray-200 rounded-3xl p-6 md:p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-2">Request Partnership</h3>
            <p className="text-gray-500 text-sm mb-6">Sending to {selectedSponsor.companyName}</p>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Event</label>
                <div className="relative">
                  <select
                    value={proposalEventId || hostedEvents[0]?.id || ''}
                    onChange={(e) => setProposalEventId(e.target.value)}
                    className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 pr-10 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    {hostedEvents.map((event) => (
                      <option key={event.id} value={event.id} className="bg-white text-gray-800">{event.title}</option>
                    ))}
                  </select>
                  <ChevronRight className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 rotate-90" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Estimated Budget ($)</label>
                <input
                  type="number"
                  value={proposalBudget}
                  onChange={(e) => setProposalBudget(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Message</label>
                <textarea
                  value={proposalMessage}
                  onChange={(e) => setProposalMessage(e.target.value)}
                  rows={8}
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <Button variant="glass" className="flex-1" onClick={() => setSelectedSponsor(null)}>Cancel</Button>
              <Button className="flex-1" onClick={sendPartnershipRequest}>Send Request</Button>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Sponsors</h1>
          <p className="text-gray-500">Explore sponsor partners and send direct partnership requests.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => navigate('/sponsor/signup')}>Become a Sponsor</Button>
          <Button variant="glass" onClick={() => navigate('/sponsor/dashboard')}>Sponsor Dashboard</Button>
        </div>
      </div>

      <div className="glass-card rounded-2xl p-4 md:p-6 mb-8 flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search sponsors by company, industry, or founder"
            className="w-full bg-gray-50 border border-gray-200 rounded-xl py-3 pl-12 pr-4 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
          />
        </div>
        <div className="md:w-80">
          <div className="relative">
            <select
              value={matchEventId}
              onChange={(e) => setMatchEventId(e.target.value)}
              className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 pr-10 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="" className="bg-white text-gray-800">Select Event to Match</option>
              {hostedEvents.map((event) => (
                <option key={event.id} value={event.id} className="bg-white text-gray-800">{event.title}</option>
              ))}
            </select>
            <ChevronRight className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 rotate-90" />
          </div>
        </div>
        <div className="md:w-auto flex gap-2">
          <Button className="whitespace-nowrap" onClick={handleRunMatch} icon={Sparkles}>Match Sponsors</Button>
          <Button variant="glass" className="whitespace-nowrap" onClick={handleClearMatch} disabled={!isMatchedMode}>Clear</Button>
        </div>
      </div>

      {isMatchedMode && (
        <div className="mb-6 p-3 rounded-xl bg-teal-500/10 border border-teal-500/30 text-sm text-purple-200">
          Showing matched recommendations for your selected event. Partnership messages are auto-generated with event-specific value points.
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-16 text-gray-500">Loading sponsors...</div>
      ) : error ? (
        <div className="text-center py-16 text-red-400">{error}</div>
      ) : filteredSponsors.length === 0 ? (
        <div className="text-center py-16 text-gray-500">No sponsors found.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredSponsors.map((sponsor) => (
            <div
              key={sponsor.userId}
              onClick={() => setExpandedSponsorId(expandedSponsorId === sponsor.userId ? null : sponsor.userId)}
              className={`glass-card rounded-3xl p-6 border cursor-pointer transition-all duration-300 ${
                expandedSponsorId === sponsor.userId
                  ? 'border-teal-500/40 shadow-lg shadow-teal-500/5'
                  : 'border-gray-200 hover:border-teal-500/30'
              }`}
            >
              <div className="flex items-center gap-3 mb-4">
                <img src={sponsor.avatarUrl || 'https://picsum.photos/seed/sponsor/80'} className="w-12 h-12 rounded-xl object-cover border border-gray-300" />
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-bold text-gray-800 leading-tight">{sponsor.companyName}</h3>
                  <p className="text-xs text-gray-500">Contact: {sponsor.name}</p>
                </div>
                <ChevronRight className={`w-5 h-5 text-gray-400 transition-transform duration-300 shrink-0 ${expandedSponsorId === sponsor.userId ? 'rotate-90' : ''}`} />
              </div>
              <p className={`text-sm text-gray-500 mb-4 ${expandedSponsorId === sponsor.userId ? '' : 'line-clamp-2'}`}>{sponsor.bio || 'No sponsor bio provided yet.'}</p>
              <div className="flex flex-wrap gap-2 mb-4">
                {sponsor.industries.slice(0, 3).map((industry) => (
                  <span key={industry} className="px-2 py-1 bg-gray-50 border border-gray-200 rounded-full text-[10px] text-gray-500">{industry}</span>
                ))}
              </div>
              <div className="flex items-center justify-between mb-4 text-xs">
                <span className="text-gray-500">Budget</span>
                <span className="text-gray-800">${sponsor.budgetMin} - ${sponsor.budgetMax}</span>
              </div>
              {typeof sponsor.matchScore === 'number' && (
                <div className="mb-4 p-3 bg-teal-50 border border-teal-200 rounded-xl">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] text-teal-600 uppercase tracking-wider font-bold">Match Score</span>
                    <span className="text-sm text-gray-800 font-bold">{sponsor.matchScore}%</span>
                  </div>
                  <p className="text-[11px] text-gray-500">{sponsor.matchReason}</p>
                </div>
              )}
              {expandedSponsorId === sponsor.userId && (
                <div className="flex gap-2 pt-2 border-t border-gray-100 mt-2" onClick={(e) => e.stopPropagation()}>
                  {sponsor.website ? (
                    <Button variant="glass" className="flex-1 py-2 text-xs" onClick={() => window.open(sponsor.website, '_blank')}>Website</Button>
                  ) : <div className="flex-1" />}
                  <Button className="flex-1 py-2 text-xs" onClick={() => startProposal(sponsor)}>Request Partnership</Button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const SponsorSignupPage = () => {
  const { user } = useEvents();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    companyName: '',
    website: '',
    bio: '',
    industries: '',
    budgetMin: '500',
    budgetMax: '5000',
    preferredFormats: [] as EventFormat[],
    preferredGeographies: '',
    preferredAudienceTypes: [] as AudienceType[]
  });
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (!user) navigate('/auth');
  }, [user]);

  const toggleFormat = (format: EventFormat) => {
    setFormData(prev => ({
      ...prev,
      preferredFormats: prev.preferredFormats.includes(format)
        ? prev.preferredFormats.filter(f => f !== format)
        : [...prev.preferredFormats, format]
    }));
  };

  const toggleAudience = (audience: AudienceType) => {
    setFormData(prev => ({
      ...prev,
      preferredAudienceTypes: prev.preferredAudienceTypes.includes(audience)
        ? prev.preferredAudienceTypes.filter(a => a !== audience)
        : [...prev.preferredAudienceTypes, audience]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const response = await fetch('/api/sponsors/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          companyName: formData.companyName,
          website: formData.website,
          bio: formData.bio,
          industries: formData.industries.split(',').map(v => v.trim()).filter(Boolean),
          budgetMin: Number(formData.budgetMin) || 0,
          budgetMax: Number(formData.budgetMax) || 0,
          preferredFormats: formData.preferredFormats,
          preferredGeographies: formData.preferredGeographies.split(',').map(v => v.trim()).filter(Boolean),
          preferredAudienceTypes: formData.preferredAudienceTypes
        })
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ error: 'Failed to save sponsor profile' }));
        throw new Error(err.error || 'Failed to save sponsor profile');
      }
      navigate('/sponsor/dashboard');
    } catch (error: any) {
      alert(error.message || 'Failed to save sponsor profile');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen pt-24 px-4 pb-32 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-2">Become a Sponsor</h1>
      <p className="text-gray-500 mb-8">Create your sponsor profile to discover and sponsor relevant events.</p>

      <form onSubmit={handleSubmit} className="glass-card rounded-3xl p-6 md:p-8 space-y-6 border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Company Name</label>
            <input value={formData.companyName} onChange={(e) => setFormData(s => ({ ...s, companyName: e.target.value }))} required className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500" />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Website</label>
            <input value={formData.website} onChange={(e) => setFormData(s => ({ ...s, website: e.target.value }))} placeholder="https://company.com" className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500" />
          </div>
        </div>

        <div>
          <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Bio</label>
          <textarea value={formData.bio} onChange={(e) => setFormData(s => ({ ...s, bio: e.target.value }))} rows={4} className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none" />
        </div>

        <div>
          <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Industries (comma separated)</label>
          <input value={formData.industries} onChange={(e) => setFormData(s => ({ ...s, industries: e.target.value }))} required placeholder="Tech, AI, Consumer" className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Budget Min ($)</label>
            <input type="number" value={formData.budgetMin} onChange={(e) => setFormData(s => ({ ...s, budgetMin: e.target.value }))} className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500" />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Budget Max ($)</label>
            <input type="number" value={formData.budgetMax} onChange={(e) => setFormData(s => ({ ...s, budgetMax: e.target.value }))} className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500" />
          </div>
        </div>

        <div>
          <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Preferred Formats</label>
          <div className="flex gap-2 flex-wrap">
            {(['Online', 'In-Person', 'Hybrid'] as EventFormat[]).map((format) => (
              <button
                key={format}
                type="button"
                onClick={() => toggleFormat(format)}
                className={`px-3 py-2 rounded-xl text-xs border ${formData.preferredFormats.includes(format) ? 'bg-teal-600 border-teal-500 text-gray-800' : 'bg-gray-50 border-gray-200 text-gray-500'}`}
              >
                {format}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Preferred Audience Types</label>
          <div className="flex gap-2 flex-wrap">
            {([
              'general_public',
              'students_earlycareer',
              'professionals',
              'founders_operators',
              'executives_investors'
            ] as AudienceType[]).map((audience) => (
              <button
                key={audience}
                type="button"
                onClick={() => toggleAudience(audience)}
                className={`px-3 py-2 rounded-xl text-xs border ${formData.preferredAudienceTypes.includes(audience) ? 'bg-teal-600 border-teal-500 text-gray-800' : 'bg-gray-50 border-gray-200 text-gray-500'}`}
              >
                {audience.replace(/_/g, ' ')}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Preferred Geographies (comma separated)</label>
          <input value={formData.preferredGeographies} onChange={(e) => setFormData(s => ({ ...s, preferredGeographies: e.target.value }))} placeholder="San Francisco, New York, Remote" className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500" />
        </div>

        <div className="flex gap-3">
          <Button type="button" variant="glass" className="flex-1" onClick={() => navigate('/sponsors')}>Cancel</Button>
          <Button type="submit" className="flex-1" disabled={isSaving}>{isSaving ? 'Saving...' : 'Create Sponsor Profile'}</Button>
        </div>
      </form>
    </div>
  );
};

const SponsorDashboardPage = () => {
  const { user } = useEvents();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<SponsorProfile | null>(null);
  const [matches, setMatches] = useState<SponsorEventMatch[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadDashboard = async () => {
    setIsLoading(true);
    try {
      const [profileRes, matchesRes] = await Promise.all([
        fetch('/api/sponsors/me', { credentials: 'include' }),
        fetch('/api/sponsors/matches', { credentials: 'include' })
      ]);

      if (profileRes.status === 404) {
        navigate('/sponsor/signup');
        return;
      }
      if (!profileRes.ok) throw new Error('Failed to load sponsor profile');
      if (!matchesRes.ok) throw new Error('Failed to load matched events');

      const profileData = await profileRes.json();
      const matchData = await matchesRes.json();
      setProfile(profileData);
      setMatches(matchData);
    } catch (error: any) {
      alert(error.message || 'Failed to load sponsor dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }
    loadDashboard();
  }, [user?.id]);

  if (isLoading) {
    return <div className="min-h-screen pt-32 text-center text-gray-500">Loading sponsor dashboard...</div>;
  }

  return (
    <div className="min-h-screen pt-24 px-4 pb-32 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Sponsor Dashboard</h1>
          <p className="text-gray-500">Discover event opportunities matched to your sponsor profile.</p>
        </div>
        <Button variant="outline" onClick={() => navigate('/sponsor/signup')}>Edit Sponsor Profile</Button>
      </div>

      {profile && (
        <div className="glass-card rounded-2xl p-6 border border-gray-200 mb-8">
          <h3 className="text-xl font-bold text-gray-800 mb-2">{profile.companyName}</h3>
          <p className="text-sm text-gray-500 mb-3">{profile.bio || 'No bio yet.'}</p>
          <div className="flex flex-wrap gap-2">
            {profile.industries.map((industry) => (
              <span key={industry} className="px-2 py-1 bg-gray-50 border border-gray-200 rounded-full text-[10px] text-gray-500">{industry}</span>
            ))}
          </div>
        </div>
      )}

      {matches.length === 0 ? (
        <div className="text-center py-16 text-gray-500">No event matches found yet.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {matches.map((event) => (
            <div key={event.id} className="glass-card rounded-3xl p-5 border border-gray-200 hover:border-teal-500/30 transition-all">
              <img src={event.imageUrl || 'https://picsum.photos/seed/event/600/300'} className="w-full h-36 object-cover rounded-xl mb-4" />
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-gray-800 font-bold line-clamp-1">{event.title}</h3>
                <span className="text-xs text-teal-300 font-bold">{event.matchScore}%</span>
              </div>
              <p className="text-xs text-gray-500 mb-3 line-clamp-2">{event.matchReason}</p>
              <p className="text-[11px] text-gray-500 mb-4">{event.date} • {event.location}</p>
              <div className="flex gap-2">
                <Button variant="glass" className="flex-1 py-2 text-xs" onClick={() => navigate(`/event/${event.id}`)}>View Event</Button>
                <Button className="flex-1 py-2 text-xs" onClick={() => navigate(`/event/${event.id}/sponsor`)}>Sponsor</Button>
              </div>
              {event.pitchDeckUrl && (
                  <Button variant="outline" className="w-full mt-2 py-2 text-xs border-teal-500/30 text-teal-600 hover:bg-teal-50" onClick={() => window.open(event.pitchDeckUrl, '_blank')}>View Pitchdeck</Button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const EditEventPage = () => {
    const { id } = useParams();
    const { events, updateEvent, user } = useEvents();
    const navigate = useNavigate();
    const eventToEdit = events.find(e => e.id === id);
    
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState<any>(null);
    const [isRecording, setIsRecording] = useState(false);

    useEffect(() => {
        if (eventToEdit) {
            setFormData({
                title: eventToEdit.title,
                category: eventToEdit.category,
                format: eventToEdit.format,
                date: eventToEdit.date,
                time: eventToEdit.time,
                location: eventToEdit.location,
                capacity: eventToEdit.capacity || 100,
                price: eventToEdit.price,
                imageUrl: eventToEdit.imageUrl || '',
                description: eventToEdit.description,
                pitchDeckUrl: eventToEdit.pitchDeckUrl || '',
                sponsorId: eventToEdit.sponsorId || '',
                sponsorshipSettings: eventToEdit.sponsorshipSettings || {
                    allowed_item_ids: SPONSORSHIP_MENU.map(i => i.id),
                    expected_attendance: 100,
                    audience_type: 'professionals',
                    allow_exclusivity: true
                }
            });
        }
    }, [eventToEdit]);

    if (!eventToEdit || !formData) return <div className="pt-24 text-center">Loading event...</div>;

    const handleNext = () => setStep(step + 1);
    const handleBack = () => setStep(step - 1);

    const handleSave = () => {
        const updatedEvent: Event = {
            ...eventToEdit,
            ...formData,
            tags: [formData.category, formData.format],
            venueName: formData.format === 'In-Person' ? formData.location.split(',')[0] : 'Virtual',
        };
        updateEvent(updatedEvent);
        navigate('/profile');
    };

    const toggleRecord = () => {
        setIsRecording(!isRecording);
        if(!isRecording) {
            setTimeout(() => {
                setIsRecording(false);
                setFormData((prev: any) => ({...prev, description: "Join us for an exclusive tech networking night where founders and VCs connect. Expect panel discussions on Series A funding and open mic pitches."}));
            }, 2000);
        }
    };

    const handlePitchDeckUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      const fd = new FormData();
      fd.append('pitchdeck', file);

      try {
        const res = await fetch('/api/events/pitchdeck', {
          method: 'POST',
          body: fd,
          credentials: 'include'
        });

        if (!res.ok) throw new Error('Upload failed');
        const data = await res.json();
        setFormData({ ...formData, pitchDeckUrl: data.pitchDeckUrl });
      } catch (err: any) {
        alert(err.message || 'Failed to upload pitch deck');
      }
    };

    return (
        <div className="min-h-screen pt-24 px-4 pb-32 max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Edit Event</h1>
            <p className="text-gray-500 mb-8">Update your event details.</p>
            
            <div className="flex items-center gap-2 mb-12 overflow-x-auto pb-2">
                {[1, 2, 3, 4, 5, 6].map(s => (
                    <div key={s} className={`flex-1 min-w-[30px] h-2 rounded-full transition-all ${s <= step ? 'bg-gradient-to-r from-blue-500 to-teal-500' : 'bg-gray-100'}`}></div>
                ))}
            </div>

            <div className="glass-card p-6 md:p-8 rounded-3xl">
                {step === 1 && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2"><Sparkles className="w-5 h-5 text-teal-500"/> Event Basics</h2>
                        <div>
                            <label className="block text-sm font-medium text-gray-500 mb-2">Event Title</label>
                            <input 
                                type="text" 
                                className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 text-gray-800 focus:border-teal-500 focus:outline-none"
                                value={formData.title}
                                onChange={(e) => setFormData({...formData, title: e.target.value})}
                            />
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-500 mb-2">Category</label>
                              <div className="relative">
                                <select 
                                  className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-xl p-4 pr-10 text-gray-800 focus:border-teal-500 focus:outline-none"
                                  value={formData.category}
                                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                                >
                                  <option className="bg-white text-gray-800" value="Tech">Tech</option>
                                  <option className="bg-white text-gray-800" value="Art">Art</option>
                                  <option className="bg-white text-gray-800" value="Sports">Sports</option>
                                  <option className="bg-white text-gray-800" value="Music">Music</option>
                                  <option className="bg-white text-gray-800" value="Business">Business</option>
                                </select>
                                <ChevronRight className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 rotate-90" />
                              </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-500 mb-2">Format</label>
                              <div className="relative">
                                <select 
                                  className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-xl p-4 pr-10 text-gray-800 focus:border-teal-500 focus:outline-none"
                                  value={formData.format}
                                  onChange={(e) => setFormData({...formData, format: e.target.value as EventFormat})}
                                >
                                  <option className="bg-white text-gray-800" value="In-Person">In-Person</option>
                                  <option className="bg-white text-gray-800" value="Online">Online</option>
                                  <option className="bg-white text-gray-800" value="Hybrid">Hybrid</option>
                                </select>
                                <ChevronRight className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 rotate-90" />
                              </div>
                            </div>
                        </div>
                    </div>
                )}

                {step === 2 && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2"><Clock className="w-5 h-5 text-teal-500"/> Logistics</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-500 mb-2">Date</label>
                                <input 
                                    type="date" 
                                    className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 text-gray-800 focus:border-teal-500 focus:outline-none"
                                    value={formData.date}
                                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-500 mb-2">Time</label>
                                <input 
                                    type="time" 
                                    className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 text-gray-800 focus:border-teal-500 focus:outline-none"
                                    value={formData.time}
                                    onChange={(e) => setFormData({...formData, time: e.target.value})}
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-500 mb-2">
                                {formData.format === 'Online' ? 'Meeting URL' : 'Venue Address'}
                            </label>
                            <div className="relative">
                                {formData.format === 'Online' ? <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" /> : <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />}
                                <input 
                                    type="text" 
                                    className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 pl-12 text-gray-800 focus:border-teal-500 focus:outline-none"
                                    value={formData.location}
                                    onChange={(e) => setFormData({...formData, location: e.target.value})}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {step === 3 && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2"><Users className="w-5 h-5 text-teal-500"/> Capacity & Price</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-500 mb-2">Max Capacity</label>
                                <div className="relative">
                                    <Users className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                    <input 
                                        type="number" 
                                        className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 pl-12 text-gray-800 focus:border-teal-500 focus:outline-none"
                                        value={formData.capacity}
                                        onChange={(e) => setFormData({...formData, capacity: parseInt(e.target.value) || 0})}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-500 mb-2">Ticket Price ($)</label>
                                <div className="relative">
                                    <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                    <input 
                                        type="number" 
                                        className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 pl-12 text-gray-800 focus:border-teal-500 focus:outline-none"
                                        value={formData.price}
                                        onChange={(e) => setFormData({...formData, price: parseInt(e.target.value) || 0})}
                                    />
                                </div>
                            </div>
                        </div>
                        <div>
                             <label className="block text-sm font-medium text-gray-500 mb-2">Cover Image URL</label>
                             <div className="relative">
                                <ImageIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                <input 
                                    type="text" 
                                    className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 pl-12 text-gray-800 focus:border-teal-500 focus:outline-none"
                                    value={formData.imageUrl}
                                    onChange={(e) => setFormData({...formData, imageUrl: e.target.value})}
                                />
                             </div>
                        </div>
                    </div>
                )}

                {step === 4 && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2"><Mic2 className="w-5 h-5 text-teal-500"/> Description</h2>
                        <div>
                            <label className="block text-sm font-medium text-gray-500 mb-2">Event Details</label>
                            <div className="relative">
                                <textarea 
                                    className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 text-gray-800 focus:border-teal-500 focus:outline-none h-40 resize-none"
                                    value={formData.description}
                                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                                />
                                <button 
                                    onClick={toggleRecord}
                                    className={`absolute bottom-4 right-4 p-2 rounded-full transition-all ${isRecording ? 'bg-red-500/20 text-red-500 animate-pulse' : 'bg-gray-100 text-gray-500 hover:text-gray-900'}`}
                                >
                                    {isRecording ? <Mic2 className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {step === 5 && (
                    <div className="space-y-6">
                         <h3 className="text-xl font-bold text-gray-800">Sponsorship Settings</h3>
                         <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                             <div className="space-y-4">
                                 <div>
                                    <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Target Audience</label>
                                  <div className="relative">
                                    <select 
                                      value={formData.sponsorshipSettings?.audience_type}
                                      onChange={(e) => setFormData({
                                        ...formData, 
                                        sponsorshipSettings: { 
                                          ...formData.sponsorshipSettings!, 
                                          audience_type: e.target.value as any 
                                        }
                                      })}
                                      className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 pr-10 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
                                    >
                                      <option className="bg-white text-gray-800" value="general_public">General Public</option>
                                      <option className="bg-white text-gray-800" value="students_earlycareer">Students / Early Career</option>
                                      <option className="bg-white text-gray-800" value="professionals">Professionals</option>
                                      <option className="bg-white text-gray-800" value="founders_operators">Founders / Operators</option>
                                      <option className="bg-white text-gray-800" value="executives_investors">Executives / Investors</option>
                                    </select>
                                    <ChevronRight className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 rotate-90" />
                                  </div>
                                 </div>
                                 <div className="mt-4">
                                    <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Pitch Deck (PDF)</label>
                                    {formData.pitchDeckUrl ? (
                                        <div className="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-xl">
                                            <span className="text-sm text-teal-600 font-medium truncate pr-2">Pitch Deck Uploaded</span>
                                            <div className="flex items-center gap-2">
                                                <button className="text-xs px-2 py-1 h-auto text-gray-500 hover:text-red-500 rounded bg-gray-100 hover:bg-red-50 transition-colors" onClick={() => setFormData({ ...formData, pitchDeckUrl: '' })}>Remove</button>
                                                <button className="text-xs px-2 py-1 h-auto text-teal-700 hover:bg-teal-50 border border-teal-200 rounded transition-colors" onClick={() => window.open(formData.pitchDeckUrl, '_blank')}>View</button>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="relative">
                                            <input 
                                                type="file" 
                                                accept=".pdf,.ppt,.pptx"
                                                onChange={handlePitchDeckUpload}
                                                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-bold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100 p-2 border border-gray-200 rounded-xl"
                                            />
                                        </div>
                                    )}
                                 </div>
                             </div>
                             <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                                 {SPONSORSHIP_MENU.map(item => {
                                     const isAllowed = formData.sponsorshipSettings?.allowed_item_ids.includes(item.id);
                                     return (
                                         <div 
                                            key={item.id}
                                            onClick={() => {
                                                const current = formData.sponsorshipSettings?.allowed_item_ids || [];
                                                const next = isAllowed ? current.filter(id => id !== item.id) : [...current, item.id];
                                                setFormData({
                                                    ...formData,
                                                    sponsorshipSettings: {
                                                        ...formData.sponsorshipSettings!,
                                                        allowed_item_ids: next
                                                    }
                                                });
                                            }}
                                            className={`p-3 rounded-xl border transition-all cursor-pointer flex items-center gap-3 ${
                                                isAllowed ? 'bg-teal-500/10 border-teal-500/50' : 'bg-gray-50 border-gray-200 opacity-60'
                                            }`}
                                         >
                                             <div className={`w-4 h-4 rounded flex items-center justify-center border ${isAllowed ? 'bg-teal-500 border-teal-500' : 'border-gray-300'}`}>
                                                 {isAllowed && <Check className="w-2 h-2 text-gray-800" />}
                                             </div>
                                             <div className="min-w-0">
                                                 <p className="text-xs font-bold text-gray-800 truncate">{item.name}</p>
                                                 <p className="text-[10px] text-gray-500">{item.category}</p>
                                             </div>
                                         </div>
                                     );
                                 })}
                             </div>
                         </div>
                    </div>
                )}

                {step === 6 && (
                    <div className="text-center py-8">
                        <h2 className="text-2xl font-bold text-gray-800 mb-2">Review Changes</h2>
                        <p className="text-gray-500 mb-8">Confirm the updates for "{formData.title}".</p>
                        <div className="text-left bg-gray-50 p-4 rounded-xl mb-6">
                             <div className="flex justify-between mb-2">
                                 <span className="text-gray-500">Date</span>
                                 <span className="text-gray-800">{formData.date} at {formData.time}</span>
                             </div>
                             <div className="flex justify-between mb-2">
                                 <span className="text-gray-500">Location</span>
                                 <span className="text-gray-800">{formData.location}</span>
                             </div>
                        </div>
                    </div>
                )}

                <div className="flex justify-between mt-8 pt-8 border-t border-gray-200">
                    {step > 1 ? (
                        <Button variant="ghost" onClick={handleBack}>Back</Button>
                    ) : <div></div>}
                    
                    {step < 6 ? (
                        <Button onClick={handleNext}>Next Step</Button>
                    ) : (
                        <Button onClick={handleSave}>Save Changes</Button>
                    )}
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
        pitchDeckUrl: '',
        sponsorId: '' as string | null,
        sponsorshipSettings: {
            allowed_item_ids: SPONSORSHIP_MENU.map(i => i.id),
            expected_attendance: 100,
            audience_type: 'professionals' as AudienceType,
            allow_exclusivity: true
        }
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

    const handlePublish = async () => {
        const newEvent = {
            id: `e${Date.now()}`,
            ...formData,
            hostId: user?.id || 'm1',
            attendees: 0,
            tags: [formData.category, formData.format],
            venueName: formData.format === 'In-Person' ? formData.location.split(',')[0] : 'Virtual',
            visibility: formData.visibility || 'public',
        } as Event;
        await addEvent(newEvent);
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

    const handlePitchDeckUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      const fd = new FormData();
      fd.append('pitchdeck', file);

      try {
        const res = await fetch('/api/events/pitchdeck', {
          method: 'POST',
          body: fd,
          credentials: 'include'
        });

        if (!res.ok) throw new Error('Upload failed');
        const data = await res.json();
        setFormData({ ...formData, pitchDeckUrl: data.pitchDeckUrl });
      } catch (err: any) {
        alert(err.message || 'Failed to upload pitch deck');
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
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Host an Event</h1>
            <p className="text-gray-500 mb-8">Create an unforgettable experience.</p>
            
            {/* Steps Indicator */}
            <div className="flex items-center gap-2 mb-12 overflow-x-auto pb-2">
                {[1, 2, 3, 4, 5, 6].map(s => (
                    <div key={s} className={`flex-1 min-w-[30px] h-2 rounded-full transition-all ${s <= step ? 'bg-gradient-to-r from-teal-500 to-cyan-500' : 'bg-gray-100'}`}></div>
                ))}
            </div>

            <div className="glass-card p-6 md:p-8 rounded-3xl animate-in fade-in slide-in-from-bottom-4 duration-500">
                
                {/* Step 1: Basics */}
                {step === 1 && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2"><Sparkles className="w-5 h-5 text-teal-500"/> Event Basics</h2>
                        <div>
                            <label className="block text-sm font-medium text-gray-500 mb-2">Event Title</label>
                            <input 
                                type="text" 
                                className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 text-gray-800 focus:border-teal-500 focus:outline-none"
                                placeholder="e.g. Neon Tech Summit"
                                value={formData.title}
                                onChange={(e) => setFormData({...formData, title: e.target.value})}
                            />
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-500 mb-2">Category</label>
                              <div className="relative">
                                <select 
                                  className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-xl p-4 pr-10 text-gray-800 focus:border-teal-500 focus:outline-none"
                                  value={formData.category}
                                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                                >
                                  <option className="bg-white text-gray-800" value="Tech">Tech</option>
                                  <option className="bg-white text-gray-800" value="Art">Art</option>
                                  <option className="bg-white text-gray-800" value="Sports">Sports</option>
                                  <option className="bg-white text-gray-800" value="Music">Music</option>
                                  <option className="bg-white text-gray-800" value="Business">Business</option>
                                </select>
                                <ChevronRight className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 rotate-90" />
                              </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-500 mb-2">Format</label>
                              <div className="relative">
                                <select 
                                  className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-xl p-4 pr-10 text-gray-800 focus:border-teal-500 focus:outline-none"
                                  value={formData.format}
                                  onChange={(e) => setFormData({...formData, format: e.target.value as EventFormat})}
                                >
                                  <option className="bg-white text-gray-800" value="In-Person">In-Person</option>
                                  <option className="bg-white text-gray-800" value="Online">Online</option>
                                  <option className="bg-white text-gray-800" value="Hybrid">Hybrid</option>
                                </select>
                                <ChevronRight className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 rotate-90" />
                              </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Step 2: Logistics */}
                {step === 2 && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2"><Clock className="w-5 h-5 text-teal-500"/> Logistics</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-500 mb-2">Date</label>
                                <input 
                                    type="date" 
                                    className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 text-gray-800 focus:border-teal-500 focus:outline-none"
                                    value={formData.date}
                                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-500 mb-2">Time</label>
                                <input 
                                    type="time" 
                                    className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 text-gray-800 focus:border-teal-500 focus:outline-none"
                                    value={formData.time}
                                    onChange={(e) => setFormData({...formData, time: e.target.value})}
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-500 mb-2">
                                {formData.format === 'Online' ? 'Meeting URL' : 'Venue Address'}
                            </label>
                            <div className="relative">
                                {formData.format === 'Online' ? <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" /> : <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />}
                                <input 
                                    type="text" 
                                    className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 pl-12 text-gray-800 focus:border-teal-500 focus:outline-none"
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
                        <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2"><Users className="w-5 h-5 text-teal-500"/> Capacity & Price</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-500 mb-2">Max Capacity</label>
                                <div className="relative">
                                    <Users className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                    <input 
                                        type="number" 
                                        className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 pl-12 text-gray-800 focus:border-teal-500 focus:outline-none"
                                        value={formData.capacity}
                                        onChange={(e) => {
                                            const val = parseInt(e.target.value) || 0;
                                            setFormData({
                                                ...formData, 
                                                capacity: val,
                                                sponsorshipSettings: {
                                                    ...formData.sponsorshipSettings!,
                                                    expected_attendance: val
                                                }
                                            });
                                        }}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-500 mb-2">Ticket Price ($)</label>
                                <div className="relative">
                                    <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                    <input 
                                        type="number" 
                                        className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 pl-12 text-gray-800 focus:border-teal-500 focus:outline-none"
                                        placeholder="0 for free"
                                        value={formData.price}
                                        onChange={(e) => setFormData({...formData, price: parseInt(e.target.value)})}
                                    />
                                </div>
                            </div>
                        </div>
                        <div>
                             <label className="block text-sm font-medium text-gray-500 mb-2">Cover Image URL</label>
                             <div className="relative">
                                <ImageIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                <input 
                                    type="text" 
                                    className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 pl-12 text-gray-800 focus:border-teal-500 focus:outline-none"
                                    placeholder="https://..."
                                    value={formData.imageUrl}
                                    onChange={(e) => setFormData({...formData, imageUrl: e.target.value})}
                                />
                             </div>
                             {formData.imageUrl && (
                                 <img src={formData.imageUrl || 'https://picsum.photos/seed/preview/800/400'} alt="Preview" className="mt-4 w-full h-40 object-cover rounded-xl border border-gray-200" />
                             )}
                        </div>
                    </div>
                )}

                {/* Step 4: Description (AI Voice) */}
                {step === 4 && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2"><Mic2 className="w-5 h-5 text-teal-500"/> Description</h2>
                        <div>
                            <label className="block text-sm font-medium text-gray-500 mb-2">Event Details (Voice Enabled)</label>
                            <div className="relative">
                                <textarea 
                                    className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 text-gray-800 focus:border-teal-500 focus:outline-none h-40 resize-none"
                                    placeholder="Type or tap the mic to dictate..."
                                    value={formData.description}
                                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                                />
                                <button 
                                    onClick={toggleRecord}
                                    className={`absolute bottom-4 right-4 p-2 rounded-full transition-all ${isRecording ? 'bg-red-500/20 text-red-500 animate-pulse' : 'bg-gray-100 text-gray-500 hover:text-gray-900'}`}
                                >
                                    {isRecording ? <Mic2 className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Step 5: Sponsorship Menu */}
                {step === 5 && (
                    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                         <div className="text-center mb-6">
                            <Sparkles className="w-10 h-10 text-yellow-400 mx-auto mb-2" />
                            <h3 className="text-2xl font-bold text-gray-800">Sponsorship Menu</h3>
                            <p className="text-gray-500 text-sm">Select which items sponsors can purchase for your event.</p>
                         </div>

                         <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                             <div className="space-y-4">
                                 <div>
                                    <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Target Audience</label>
                                  <div className="relative">
                                    <select 
                                      value={formData.sponsorshipSettings?.audience_type}
                                      onChange={(e) => setFormData({
                                        ...formData, 
                                        sponsorshipSettings: { 
                                          ...formData.sponsorshipSettings!, 
                                          audience_type: e.target.value as any 
                                        }
                                      })}
                                      className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 pr-10 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
                                    >
                                      <option className="bg-white text-gray-800" value="general_public">General Public</option>
                                      <option className="bg-white text-gray-800" value="students_earlycareer">Students / Early Career</option>
                                      <option className="bg-white text-gray-800" value="professionals">Professionals</option>
                                      <option className="bg-white text-gray-800" value="founders_operators">Founders / Operators</option>
                                      <option className="bg-white text-gray-800" value="executives_investors">Executives / Investors</option>
                                    </select>
                                    <ChevronRight className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 rotate-90" />
                                  </div>
                                 </div>
                                 <div className="mt-4">
                                    <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Pitch Deck (PDF)</label>
                                    {formData.pitchDeckUrl ? (
                                        <div className="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-xl">
                                            <span className="text-sm text-teal-600 font-medium truncate pr-2">Pitch Deck Uploaded</span>
                                            <div className="flex items-center gap-2">
                                                <button className="text-xs px-2 py-1 h-auto text-gray-500 hover:text-red-500 rounded bg-gray-100 hover:bg-red-50 transition-colors" onClick={() => setFormData({ ...formData, pitchDeckUrl: '' })}>Remove</button>
                                                <button className="text-xs px-2 py-1 h-auto text-teal-700 hover:bg-teal-50 border border-teal-200 rounded transition-colors" onClick={() => window.open(formData.pitchDeckUrl, '_blank')}>View</button>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="relative">
                                            <input 
                                                type="file" 
                                                accept=".pdf,.ppt,.pptx"
                                                onChange={handlePitchDeckUpload}
                                                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-bold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100 p-2 border border-gray-200 rounded-xl cursor-pointer"
                                            />
                                        </div>
                                    )}
                                 </div>
                                 <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-200">
                                    <div>
                                        <p className="text-sm font-bold text-gray-800">Allow Exclusivity</p>
                                        <p className="text-[10px] text-gray-500">Sponsors can pay more for exclusive rights.</p>
                                    </div>
                                    <button 
                                        onClick={() => setFormData({
                                            ...formData,
                                            sponsorshipSettings: {
                                                ...formData.sponsorshipSettings!,
                                                allow_exclusivity: !formData.sponsorshipSettings?.allow_exclusivity
                                            }
                                        })}
                                        className={`w-12 h-6 rounded-full transition-colors relative ${formData.sponsorshipSettings?.allow_exclusivity ? 'bg-teal-600' : 'bg-gray-700'}`}
                                    >
                                        <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${formData.sponsorshipSettings?.allow_exclusivity ? 'left-7' : 'left-1'}`} />
                                    </button>
                                 </div>
                             </div>

                             <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                                 {SPONSORSHIP_MENU.map(item => {
                                     const isAllowed = formData.sponsorshipSettings?.allowed_item_ids.includes(item.id);
                                     return (
                                         <div 
                                            key={item.id}
                                            onClick={() => {
                                                const current = formData.sponsorshipSettings?.allowed_item_ids || [];
                                                const next = isAllowed ? current.filter(id => id !== item.id) : [...current, item.id];
                                                setFormData({
                                                    ...formData,
                                                    sponsorshipSettings: {
                                                        ...formData.sponsorshipSettings!,
                                                        allowed_item_ids: next
                                                    }
                                                });
                                            }}
                                            className={`p-3 rounded-xl border transition-all cursor-pointer flex items-center gap-3 ${
                                                isAllowed ? 'bg-teal-500/10 border-teal-500/50' : 'bg-gray-50 border-gray-200 opacity-60'
                                            }`}
                                         >
                                             <div className={`w-4 h-4 rounded flex items-center justify-center border ${isAllowed ? 'bg-teal-500 border-teal-500' : 'border-gray-300'}`}>
                                                 {isAllowed && <Check className="w-2 h-2 text-gray-800" />}
                                             </div>
                                             <div className="min-w-0">
                                                 <p className="text-xs font-bold text-gray-800 truncate">{item.name}</p>
                                                 <p className="text-[10px] text-gray-500">{item.category}</p>
                                             </div>
                                         </div>
                                     );
                                 })}
                             </div>
                         </div>
                    </div>
                )}

                {/* Step 6: Review & Publish */}
                {step === 6 && (
                    <div className="text-center py-8">
                        <div className="w-20 h-20 bg-green-500/20 text-green-500 rounded-full flex items-center justify-center mx-auto mb-6 border border-green-500/30">
                            <Check className="w-10 h-10" />
                        </div>
                        <h2 className="text-2xl font-bold text-gray-800 mb-2">Ready to Publish?</h2>
                        <p className="text-gray-500 mb-8">Your event "{formData.title}" will be live for everyone to see.</p>
                        
                        <div className="text-left bg-gray-50 p-4 rounded-xl mb-6">
                             <div className="flex justify-between mb-2">
                                 <span className="text-gray-500">Date</span>
                                 <span className="text-gray-800">{formData.date} at {formData.time}</span>
                             </div>
                             <div className="flex justify-between mb-2">
                                 <span className="text-gray-500">Location</span>
                                 <span className="text-gray-800">{formData.location}</span>
                             </div>
                             <div className="flex justify-between mb-2">
                                 <span className="text-gray-500">Format</span>
                                 <span className="text-gray-800">{formData.format}</span>
                             </div>
                             <div className="flex justify-between items-center border-t border-gray-200 pt-4 mt-2">
                                 <span className="text-gray-500">Visibility</span>
                               <div className="relative">
                                <select 
                                  value={formData.visibility || 'public'}
                                  onChange={(e) => setFormData({...formData, visibility: e.target.value as 'public' | 'private'})}
                                  className="appearance-none bg-gray-100 border border-gray-300 rounded-lg px-3 py-1.5 pr-8 text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
                                 >
                                  <option className="bg-white text-gray-800" value="public">Public (Discoverable)</option>
                                  <option className="bg-white text-gray-800" value="private">Private (Invite Only)</option>
                                </select>
                                <ChevronRight className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500 rotate-90" />
                               </div>
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

                <div className="flex justify-between mt-8 pt-8 border-t border-gray-200">
                    {step > 1 ? (
                        <Button variant="ghost" onClick={handleBack}>Back</Button>
                    ) : <div></div>}
                    
                    {step < 6 ? (
                        <Button onClick={handleNext}>
                            Next Step
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
    const { events, attendEvent, deleteEvent, user } = useEvents();
    const event = events.find(e => e.id === id);
    const navigate = useNavigate();
    const [showConfirm, setShowConfirm] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [showSuccess, setShowSuccess] = useState(false);
    const [attendees, setAttendees] = useState<any[]>([]);

    const isHosting = event?.hostId === user?.id;

    useEffect(() => {
        const fetchAttendees = async () => {
            if (isHosting && event) {
                try {
                    const res = await fetch(`/api/events/${event.id}/attendees`, { credentials: 'include' });
                    if (res.ok) {
                        const data = await res.json();
                        setAttendees(data);
                    }
                } catch (err) {
                    console.error("Failed to fetch attendees", err);
                }
            }
        };
        fetchAttendees();
    }, [isHosting, event?.id]);

    if (!event) return <div className="text-gray-800 pt-24 text-center">Event not found</div>;

    const isAttending = user?.attendedEventIds?.includes(event.id) || false;

    const handleConfirmPurchase = async () => {
        if (!user) {
            navigate('/auth');
            return;
        }
        setIsProcessing(true);
        await attendEvent(event.id);
        setIsProcessing(false);
        setShowConfirm(false);
        setShowSuccess(true);
        setTimeout(() => {
            setShowSuccess(false);
            navigate('/profile'); // Redirect to profile to see the new registered event
        }, 1500);
    };

    const handleRegisterClick = () => {
        if (!user) {
            navigate('/auth');
            return;
        }
        if (event.price === 0) {
            // One-click register for free events
            handleConfirmPurchase();
        } else {
            // Show payment confirmation modal
            setShowConfirm(true);
        }
    };

    return (
        <div className="min-h-screen pt-0 pb-32">
             {/* Confirmation Modal */}
             {showConfirm && (
                 <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                     <div className="absolute inset-0 bg-gray-900/80 backdrop-blur-sm" onClick={() => !isProcessing && setShowConfirm(false)}></div>
                     <div className="glass-card p-8 rounded-3xl max-w-md w-full relative z-10 border border-gray-300 shadow-2xl animate-in fade-in zoom-in duration-300">
                         <h3 className="text-2xl font-bold text-gray-800 mb-4">{event.price === 0 ? 'Confirm Registration' : 'Confirm Purchase'}</h3>
                         <p className="text-gray-500 mb-6">
                             {event.price === 0 
                                ? `You are about to register for "${event.title}" for Free.`
                                : `You are about to purchase a ticket for "${event.title}" for $${event.price}.`
                             }
                         </p>
                         
                         <div className="space-y-4">
                             <Button 
                                className="w-full" 
                                onClick={handleConfirmPurchase}
                                disabled={isProcessing}
                             >
                                 {isProcessing ? 'Processing...' : (event.price === 0 ? 'Complete Registration' : 'Confirm Purchase')}
                             </Button>
                             <Button 
                                variant="glass" 
                                className="w-full" 
                                onClick={() => setShowConfirm(false)}
                                disabled={isProcessing}
                             >
                                 Cancel
                             </Button>
                         </div>
                     </div>
                 </div>
             )}

             {/* Success Notification */}
             {showSuccess && (
                 <div className="fixed top-24 left-1/2 -translate-x-1/2 z-[100] animate-in slide-in-from-top-4 duration-300">
                     <div className="bg-emerald-500/90 backdrop-blur-md text-white px-6 py-3 rounded-full shadow-2xl flex items-center gap-3 border border-emerald-400/30">
                         <Check className="w-5 h-5" />
                         <span className="font-bold">{event.price === 0 ? 'Registration Complete!' : 'Tickets Purchased!'}</span>
                     </div>
                 </div>
             )}

             {/* Hero Image */}
             <div className="relative h-[40vh] md:h-[50vh] w-full">
                 <div className="absolute inset-0 bg-gradient-to-t from-[#FFFFFF] via-[#FFFFFF]/60 to-transparent z-10"></div>
                 {event.imageUrl ? (
                    <img src={event.imageUrl || 'https://picsum.photos/seed/event/800/400'} className="w-full h-full object-cover" />
                 ) : (
                    <div className="w-full h-full bg-gray-900 flex items-center justify-center">
                        <ImageIcon className="w-20 h-20 text-gray-700" />
                    </div>
                 )}
                 <div className="absolute top-6 left-4 z-20 flex gap-3 items-center">
                     <Button variant="glass" className="rounded-full w-10 h-10 p-0 flex items-center justify-center" onClick={() => navigate(-1)}>
                         <span className="text-lg pb-1">←</span>
                     </Button>
                     {event.visibility === 'private' && (
                         <span className="px-3 py-1 bg-black/50 backdrop-blur border border-white/20 rounded-full text-xs font-bold text-white flex items-center gap-1">
                            <Shield className="w-3 h-3" /> Private Event
                         </span>
                     )}
                 </div>
             </div>

             <div className="max-w-5xl mx-auto px-4 -mt-20 md:-mt-32 relative z-20">
                 <div className="glass-card p-6 md:p-8 rounded-3xl mb-8 flex flex-col md:flex-row gap-8 items-start justify-between">
                     <div className="flex-1">
                         <div className="flex flex-wrap gap-2 mb-4">
                             {event.tags.map(t => (
                                 <span key={t} className="px-3 py-1 rounded-full text-xs bg-teal-50 text-teal-600 border border-teal-200">
                                     #{t}
                                 </span>
                             ))}
                         </div>
                         <h1 className="text-3xl md:text-5xl font-bold text-gray-800 mb-4 leading-tight">{event.title}</h1>
                         <div className="flex flex-col gap-2 text-gray-600 text-sm md:text-base">
                             <div className="flex items-center gap-2"><Calendar className="w-5 h-5 text-teal-500" /> {new Date(event.date).toLocaleDateString()} at {event.time}</div>
                             <div className="flex items-center gap-2"><MapPin className="w-5 h-5 text-teal-500" /> {event.venueName ? `${event.venueName}, ` : ''}{event.location}</div>
                             <div className="flex items-center gap-2"><UserIcon className="w-5 h-5 text-teal-500" /> Hosted by {event.hostId === MOCK_USER.id || event.hostId === user?.id ? 'You' : (event.hostName || (event.hostId === 'h1' ? 'UFC Official' : 'Tech Giants'))}</div>
                         </div>
                     </div>
                     
                     <div className="w-full md:w-auto flex flex-col gap-4 min-w-[200px]">
                         <Button 
                            onClick={() => !isAttending && handleRegisterClick()} 
                            className="w-full"
                            disabled={isAttending || event.hostId === user?.id || isProcessing}
                         >
                            {event.hostId === user?.id 
                                ? 'You are Hosting'
                                : (isAttending ? 'Attending' : (event.price === 0 ? 'Register (Free)' : `Get Tickets ($${event.price})`))
                            }
                         </Button>
                         {event.hostId === user?.id && (
                             <div className="flex gap-2">
                                 <Button variant="outline" className="flex-1" onClick={() => navigate(`/event/${event.id}/edit`)}>Edit Event</Button>
                                 <Button variant="glass" className="w-12 !px-0 bg-red-500/10 border-red-500/30 text-red-400 hover:bg-red-500/20" onClick={async () => {
                                     if(confirm('Are you sure you want to delete this event?')) {
                                         await deleteEvent(event.id);
                                         navigate('/explore');
                                     }
                                 }}>🗑</Button>
                             </div>
                         )}
                         <Button variant="outline" onClick={() => navigate(`/event/${event.id}/sponsor`)} className="w-full" icon={Shield}>
                            Sponsor Event
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
                             <h2 className="text-2xl font-bold text-gray-800 mb-4">About Event</h2>
                             <p className="text-gray-500 leading-relaxed text-lg">{event.description}</p>
                         </section>

                         {event.sponsorId && (
                             <section className="p-6 rounded-2xl bg-gradient-to-r from-gray-50 to-black border border-gray-200">
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
                                         <h4 className="text-gray-800 font-bold text-xl">Nebula Drink</h4>
                                         <p className="text-sm text-gray-500">Fueling the future of events.</p>
                                     </div>
                                     <Button variant="outline" className="ml-auto hidden sm:flex">Learn More</Button>
                                 </div>
                                 <Button variant="outline" className="w-full mt-4 sm:hidden">Learn More</Button>
                             </section>
                         )}
                     </div>

                     <div className="space-y-6">
                         <div className="glass-panel p-6 rounded-2xl">
                             <h3 className="text-gray-800 font-bold mb-4">Location</h3>
                             <div className="h-48 bg-gray-800 rounded-xl mb-4 flex items-center justify-center border border-gray-200">
                                 <MapIcon className="w-8 h-8 text-gray-600" />
                                 <span className="ml-2 text-gray-500 text-sm">Map Placeholder</span>
                             </div>
                             <p className="text-gray-500 text-sm">{event.location}</p>
                         </div>

                         {isHosting && (
                             <div className="glass-panel p-6 rounded-2xl">
                                 <div className="flex justify-between items-center mb-4">
                                     <h3 className="text-gray-800 font-bold">Attendees</h3>
                                     <span className="bg-teal-500/20 text-teal-500 px-2 py-0.5 rounded-full text-xs font-bold">{attendees.length}</span>
                                 </div>
                                 <div className="space-y-3 max-h-60 overflow-y-auto pr-2 no-scrollbar">
                                     {attendees.length === 0 ? (
                                         <p className="text-sm text-gray-500">No attendees yet.</p>
                                     ) : (
                                         attendees.map(a => (
                                             <div key={a.id} className="flex items-center gap-3 p-2 rounded-xl hover:bg-gray-50 transition-colors">
                                                 <img src={a.avatarUrl || 'https://picsum.photos/seed/user/200'} className="w-8 h-8 rounded-full border border-teal-500/30 object-cover" />
                                                 <div>
                                                     <p className="text-sm text-gray-800 font-medium leading-none mb-1">{a.name}</p>
                                                     {a.username && <p className="text-xs text-gray-500 leading-none">@{a.username}</p>}
                                                 </div>
                                             </div>
                                         ))
                                     )}
                                 </div>
                             </div>
                         )}
                     </div>
                 </div>
             </div>
        </div>
    );
};

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register, user, isLoading } = useEvents();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && user) {
      if (!user.onboardingCompleted) {
        navigate('/onboarding');
      } else {
        navigate('/explore');
      }
    }
  }, [user, isLoading, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    console.log(`[AuthPage] Attempting ${isLogin ? 'login' : 'registration'} for ${email}`);

    try {
      if (isLogin) {
        await login(email, password);
        console.log('[AuthPage] Login call completed');
      } else {
        if (password !== confirmPassword) {
          throw new Error("Passwords do not match");
        }
        await register(name, email, password);
        console.log('[AuthPage] Registration call completed');
      }
    } catch (err: any) {
      console.error('[AuthPage] Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen pt-32 px-4 flex items-center justify-center">
      <div className="glass-panel p-8 w-full max-w-md space-y-8 animate-in fade-in zoom-in-95 duration-500">
        <div className="text-center">
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-teal-500 to-cyan-500">
            {isLogin ? 'Welcome Back' : 'Join Circle'}
          </h1>
          <p className="text-gray-500 mt-2">
            {isLogin ? 'Sign in to your account' : 'Create your account to get started'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div className="space-y-1">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Full Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 transition-all"
                placeholder="Alex Rivera"
              />
            </div>
          )}
          <div className="space-y-1">
            <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 transition-all"
              placeholder="alex@example.com"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 transition-all"
              placeholder="••••••••"
            />
          </div>
          {!isLogin && (
            <div className="space-y-1">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Confirm Password</label>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 transition-all"
                placeholder="••••••••"
              />
            </div>
          )}

          {error && <p className="text-red-400 text-xs text-center">{error}</p>}

          <Button type="submit" disabled={loading} className="w-full py-4">
            {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
          </Button>
        </form>

        <div className="text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-sm text-gray-500 hover:text-teal-500 transition-colors"
          >
            {isLogin ? "Don't have an account? Sign Up" : "Already have an account? Sign In"}
          </button>
        </div>
      </div>
    </div>
  );
};

const OnboardingPage = () => {
  const { user, updateProfile, isLoading } = useEvents();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    username: '',
    bio: '',
    location: '',
    interests: [] as string[]
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isLoading) {
      if (!user) navigate('/auth');
      else if (user.onboardingCompleted) navigate('/explore');
    }
  }, [user, isLoading, navigate]);

  if (isLoading) {
    return (
      <div className="min-h-screen pt-48 text-center">
        <div className="animate-spin w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  const handleNext = () => setStep(s => s + 1);
  const handlePrev = () => setStep(s => s - 1);

  const handleSubmit = async () => {
    if (formData.interests.length === 0) {
      setError("Please select at least one interest to continue.");
      return;
    }
    setLoading(true);
    setError('');
    try {
      console.log('Starting profile update...', { ...formData, onboardingCompleted: true });
      await updateProfile({ ...formData, onboardingCompleted: true });
      console.log('Profile update successful, navigating...');
      navigate('/explore');
    } catch (err: any) {
      console.error('Onboarding error:', err);
      setError(err.message || "Failed to save profile. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const toggleInterest = (interest: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const interestOptions = ['Tech', 'Music', 'Art', 'Sports', 'Networking', 'Gaming', 'Food', 'Business'];

  return (
    <div className="min-h-screen pt-32 px-4 flex items-center justify-center">
      <div className="glass-panel p-8 w-full max-w-xl space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <div className="flex justify-between items-center mb-8">
          {[1, 2, 3].map(i => (
            <div key={i} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-colors ${step >= i ? 'bg-teal-600 text-white' : 'bg-gray-50 text-gray-500'}`}>
                {i}
              </div>
              {i < 3 && <div className={`w-12 h-0.5 mx-2 ${step > i ? 'bg-teal-600' : 'bg-gray-50'}`} />}
            </div>
          ))}
        </div>

        {step === 1 && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-800">Choose a Username</h2>
              <p className="text-gray-500 text-sm mt-1">How should others see you on Circle?</p>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Username</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData(s => ({ ...s, username: e.target.value }))}
                className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="alex_rivera"
              />
              {formData.username && formData.username.length < 3 && (
                <p className="text-red-400 text-[10px] mt-1 ml-1">Username must be at least 3 characters</p>
              )}
            </div>
            <Button onClick={handleNext} disabled={!formData.username || formData.username.length < 3} className="w-full">Continue</Button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-800">Tell us about yourself</h2>
              <p className="text-gray-500 text-sm mt-1">Add a bio and your location.</p>
            </div>
            <div className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Bio</label>
                <textarea
                  value={formData.bio}
                  onChange={(e) => setFormData(s => ({ ...s, bio: e.target.value }))}
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 h-32 resize-none"
                  placeholder="I love attending tech events and meeting new people..."
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Location</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData(s => ({ ...s, location: e.target.value }))}
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="San Francisco, CA"
                />
              </div>
            </div>
            <div className="flex gap-4">
              <Button onClick={handlePrev} variant="glass" className="flex-1">Back</Button>
              <Button onClick={handleNext} className="flex-1">Continue</Button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-800">What are you into?</h2>
              <p className="text-gray-500 text-sm mt-1">Select your interests to get better recommendations.</p>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {interestOptions.map(interest => (
                <button
                  key={interest}
                  onClick={() => toggleInterest(interest)}
                  className={`p-3 rounded-xl border text-sm font-medium transition-all ${
                    formData.interests.includes(interest)
                      ? 'bg-teal-600 border-teal-500 text-gray-800 shadow-lg shadow-teal-500/15'
                      : 'bg-gray-50 border-gray-200 text-gray-500 hover:bg-gray-100 hover:border-gray-300'
                  }`}
                >
                  {interest}
                </button>
              ))}
            </div>
            {error && <p className="text-red-400 text-xs text-center">{error}</p>}
            <div className="flex gap-4">
              <Button onClick={handlePrev} variant="glass" className="flex-1">Back</Button>
              <Button onClick={handleSubmit} disabled={loading} className="flex-1">
                {loading ? 'Saving...' : 'Finish Setup'}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const ProfilePage = () => {
  const { user, events, proposals, isLoading, uploadAvatar, updateProfile, refreshUser, updateProposalStatus } = useEvents();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<'hosted' | 'attending' | 'proposals'>('attending');
    const [isEditing, setIsEditing] = useState(false);
  const [selectedProposal, setSelectedProposal] = useState<SponsorshipProposal | null>(null);
  const [proposalToast, setProposalToast] = useState<{ visible: boolean; message: string }>({ visible: false, message: '' });
    const [editForm, setEditForm] = useState({
        name: '',
        username: '',
        bio: '',
        location: ''
    });
    const fileInputRef = useRef<HTMLInputElement>(null);
    
    useEffect(() => {
        refreshUser();
    }, []);

    useEffect(() => {
        if (user) {
            setEditForm({
                name: user.name || '',
                username: user.username || '',
                bio: user.bio || '',
                location: user.location || ''
            });
        }
    }, [user]);

    if (isLoading) {
        return (
            <div className="min-h-screen pt-48 text-center">
                <div className="animate-spin w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                <p className="text-gray-500">Loading your profile...</p>
            </div>
        );
    }

    if (!user) {
        return (
            <div className="min-h-screen pt-48 text-center px-4">
                <div className="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-6">
                    <UserIcon className="w-10 h-10 text-gray-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Sign in to view your profile</h2>
                <p className="text-gray-500 mb-8 max-w-md mx-auto">Track your events, manage sponsorships, and connect with the community.</p>
                <Button onClick={() => navigate('/auth')}>Sign In / Register</Button>
            </div>
        );
    }

    if (isEditing) {
        return (
            <div className="min-h-screen pt-24 px-4 pb-32 max-w-2xl mx-auto">
                <div className="flex items-center gap-4 mb-8">
                    <Button variant="glass" onClick={() => setIsEditing(false)}>
                        <X className="w-4 h-4" />
                    </Button>
                    <h1 className="text-3xl font-bold text-gray-800">Edit Profile</h1>
                </div>
                
                <div className="glass-card p-8 rounded-3xl border border-gray-200 space-y-6">
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Full Name</label>
                        <input 
                            type="text" 
                            value={editForm.name}
                            onChange={(e) => setEditForm(s => ({ ...s, name: e.target.value }))}
                            className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-gray-800 focus:outline-none focus:border-teal-500 transition-all"
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Username</label>
                        <input 
                            type="text" 
                            value={editForm.username}
                            onChange={(e) => setEditForm(s => ({ ...s, username: e.target.value }))}
                            className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-gray-800 focus:outline-none focus:border-teal-500 transition-all"
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Bio</label>
                        <textarea 
                            value={editForm.bio}
                            onChange={(e) => setEditForm(s => ({ ...s, bio: e.target.value }))}
                            rows={4}
                            className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-gray-800 focus:outline-none focus:border-teal-500 transition-all resize-none"
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Location</label>
                        <input 
                            type="text" 
                            value={editForm.location}
                            onChange={(e) => setEditForm(s => ({ ...s, location: e.target.value }))}
                            className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-gray-800 focus:outline-none focus:border-teal-500 transition-all"
                        />
                    </div>
                    
                    <div className="pt-4 flex gap-4">
                        <Button variant="primary" className="flex-1" onClick={async () => {
                            try {
                                await updateProfile(editForm);
                                setIsEditing(false);
                            } catch (err) {
                                alert("Failed to update profile");
                            }
                        }}>Save Changes</Button>
                        <Button variant="glass" className="flex-1" onClick={() => setIsEditing(false)}>Cancel</Button>
                    </div>
                </div>
            </div>
        );
    }

    const hostedEvents = events.filter(e => e.hostId === user.id);
    const attendingEvents = events.filter(e => user.attendedEventIds?.includes(e.id));
    const receivedProposals = proposals.filter(p => p.receiverId === user.id);
    const sentProposals = proposals.filter(p => p.senderId === user.id);

    const statusBadgeClass = (status: SponsorshipProposal['status']) => {
      if (status === 'accepted') return 'bg-emerald-500/20 text-emerald-400';
      if (status === 'declined') return 'bg-red-500/20 text-red-400';
      return 'bg-yellow-500/20 text-yellow-500';
    };

    const selectedProposalEvent = selectedProposal
      ? events.find(e => e.id === selectedProposal.eventId)
      : null;

    const isSelectedProposalReceiver = !!selectedProposal && selectedProposal.receiverId === user.id;

    const handleProposalDecision = async (proposalId: string, status: 'accepted' | 'declined') => {
      await updateProposalStatus(proposalId, status);
      setSelectedProposal(null);
      setProposalToast({
        visible: true,
        message: status === 'accepted' ? 'Proposal accepted successfully.' : 'Proposal declined successfully.'
      });
      setTimeout(() => {
        setProposalToast({ visible: false, message: '' });
      }, 2200);
    };

    const handleAvatarClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            try {
                await uploadAvatar(file);
            } catch (err) {
                alert("Failed to upload avatar");
            }
        }
    };

    return (
        <div className="min-h-screen pt-24 px-4 pb-32 max-w-4xl mx-auto">
        {proposalToast.visible && (
          <div className="fixed top-24 left-1/2 -translate-x-1/2 z-[110] animate-in slide-in-from-top-4 duration-300">
            <div className="bg-emerald-500/90 backdrop-blur-md text-white px-6 py-3 rounded-full shadow-2xl flex items-center gap-3 border border-emerald-400/30">
              <Check className="w-5 h-5" />
              <span className="font-bold text-sm">{proposalToast.message}</span>
            </div>
          </div>
        )}

        {selectedProposal && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <div
              className="absolute inset-0 bg-gray-900/80 backdrop-blur-sm"
              onClick={() => setSelectedProposal(null)}
            ></div>
            <div className="relative z-10 w-full max-w-2xl glass-card border border-gray-200 rounded-3xl p-6 md:p-8 animate-in fade-in zoom-in-95 duration-300">
              <div className="flex items-start justify-between gap-4 mb-6">
                <div>
                  <p className="text-xs font-bold text-gray-500 uppercase tracking-[0.2em] mb-2">Proposal Details</p>
                  <h3 className="text-2xl font-bold text-gray-800">{selectedProposal.eventTitle}</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {isSelectedProposalReceiver ? `From: ${selectedProposal.senderName}` : 'To: Event Host'}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedProposal(null)}
                  className="p-2 rounded-full hover:bg-gray-100 transition-colors text-gray-500 hover:text-gray-900"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-gray-50 border border-gray-200 rounded-xl p-3">
                    <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Status</p>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${statusBadgeClass(selectedProposal.status)}`}>
                      {selectedProposal.status}
                    </span>
                  </div>
                  <div className="bg-gray-50 border border-gray-200 rounded-xl p-3">
                    <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Investment</p>
                    <p className="text-gray-800 font-bold text-lg">${selectedProposal.estimatedInvestment}</p>
                  </div>
                </div>

                <div className="bg-gray-100 p-4 rounded-2xl border border-gray-100">
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Message</p>
                  <p className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">{selectedProposal.message}</p>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Sent {new Date(selectedProposal.timestamp).toLocaleString()}</span>
                  {selectedProposalEvent && (
                    <button
                      onClick={() => {
                        setSelectedProposal(null);
                        navigate(`/event/${selectedProposal.eventId}`);
                      }}
                      className="text-teal-500 hover:text-teal-600"
                    >
                      View Event
                    </button>
                  )}
                </div>
              </div>

              <div className="pt-6 mt-6 border-t border-gray-200 flex flex-col sm:flex-row gap-3">
                {isSelectedProposalReceiver && selectedProposal.status === 'pending' ? (
                  <>
                    <Button
                      variant="primary"
                      className="flex-1"
                      onClick={() => handleProposalDecision(selectedProposal.id, 'accepted')}
                    >
                      Accept Proposal
                    </Button>
                    <Button
                      variant="glass"
                      className="flex-1"
                      onClick={() => handleProposalDecision(selectedProposal.id, 'declined')}
                    >
                      Decline Proposal
                    </Button>
                  </>
                ) : (
                  <Button variant="glass" className="w-full" onClick={() => setSelectedProposal(null)}>
                    Close
                  </Button>
                )}
              </div>
            </div>
          </div>
        )}

            <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange} 
                className="hidden" 
                accept="image/*" 
            />
            <div className="flex flex-col md:flex-row items-center md:items-start gap-8 mb-12 text-center md:text-left animate-in fade-in slide-in-from-top-4 duration-500">
                <div className="relative group cursor-pointer" onClick={handleAvatarClick}>
                    <img 
                        src={user.avatarUrl || 'https://picsum.photos/seed/user/200'} 
                        className="w-32 h-32 rounded-3xl object-cover border-2 border-teal-500/30 p-1 group-hover:border-teal-500 transition-all" 
                    />
                    <div className="absolute inset-0 bg-gray-900/40 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                        <ImageIcon className="w-8 h-8 text-gray-800" />
                    </div>
                </div>
                <div className="flex-1 space-y-4">
                    <div>
                        <div className="flex flex-col md:flex-row items-center md:items-end gap-3 mb-1">
                            <h1 className="text-4xl font-bold text-gray-800">{user.name}</h1>
                            {user.username && <span className="text-teal-500 font-medium text-sm mb-1">@{user.username}</span>}
                        </div>
                        <p className="text-gray-500 flex items-center justify-center md:justify-start gap-2">
                            <Mail className="w-4 h-4" />
                            {user.email}
                        </p>
                    </div>
                    
                    {user.bio && <p className="text-gray-500 text-sm leading-relaxed max-w-xl">{user.bio}</p>}
                    
                    <div className="flex flex-wrap justify-center md:justify-start gap-4 text-xs font-bold text-gray-500 uppercase tracking-widest">
                        {user.location && (
                            <div className="flex items-center gap-1.5">
                                <MapPin className="w-3.5 h-3.5 text-teal-500" />
                                {user.location}
                            </div>
                        )}
                        <div className="flex items-center gap-1.5">
                            <Clock className="w-3.5 h-3.5 text-teal-500" />
                            Joined {new Date(user.createdAt || '').toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                        </div>
                    </div>

                    <div className="flex flex-wrap justify-center md:justify-start gap-2">
                        {Array.isArray(user.interests) && user.interests.map(interest => (
                            <span key={interest} className="px-3 py-1 bg-gray-50 border border-gray-200 rounded-full text-[10px] text-gray-500">
                                {interest}
                            </span>
                        ))}
                    </div>
                </div>
                <div className="flex flex-col gap-3">
                    <Button variant="primary" onClick={() => navigate('/host')}>Host New Event</Button>
                    <Button variant="glass" onClick={() => setIsEditing(true)}>Edit Profile</Button>
                </div>
            </div>

            <div className="flex gap-8 border-b border-gray-200 mb-8 overflow-x-auto no-scrollbar">
                {[
                    { id: 'attending', label: 'Attending', count: attendingEvents.length },
                    { id: 'hosted', label: 'My Events', count: hostedEvents.length },
                    { id: 'proposals', label: 'Sponsorships', count: receivedProposals.length + sentProposals.length }
                ].map(tab => (
                    <button 
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        className={`pb-4 px-2 text-sm font-bold transition-all relative whitespace-nowrap flex items-center gap-2 ${activeTab === tab.id ? 'text-teal-600' : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        {tab.label}
                        {tab.count > 0 && <span className="text-[10px] bg-gray-100 px-1.5 py-0.5 rounded-md">{tab.count}</span>}
                        {activeTab === tab.id && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-teal-500 shadow-[0_0_10px_rgba(13,148,136,0.4)]" />}
                    </button>
                ))}
            </div>

            {activeTab === 'attending' && (
                <div className="space-y-6 animate-in fade-in duration-500">
                    {attendingEvents.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {attendingEvents.map(event => (
                                <EventCard key={event.id} event={event} onClick={() => navigate(`/event/${event.id}`)} />
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-20 bg-gray-50 rounded-3xl border border-dashed border-gray-200">
                            <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Calendar className="w-8 h-8 text-gray-600" />
                            </div>
                            <h3 className="text-xl font-bold text-gray-800 mb-2">No registrations yet</h3>
                            <p className="text-gray-500 mb-6">Explore upcoming events and find your next experience.</p>
                            <Button onClick={() => navigate('/explore')}>Explore Events</Button>
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'hosted' && (
                <div className="space-y-6 animate-in fade-in duration-500">
                    {hostedEvents.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {hostedEvents.map(event => (
                                <EventCard 
                                    key={event.id} 
                                    event={event} 
                                    onClick={() => navigate(`/event/${event.id}`)}
                                    onEdit={(e) => {
                                        e.stopPropagation();
                                        navigate(`/event/${event.id}/edit`);
                                    }}
                                />
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-20 bg-gray-50 rounded-3xl border border-dashed border-gray-200">
                            <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Plus className="w-8 h-8 text-gray-600" />
                            </div>
                            <h3 className="text-xl font-bold text-gray-800 mb-2">No hosted events</h3>
                            <p className="text-gray-500 mb-6">Start your own event and build a community.</p>
                            <Button onClick={() => navigate('/host')}>Create Event</Button>
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'proposals' && (
                <div className="space-y-12 animate-in fade-in duration-500">
                    <div className="space-y-6">
                        <h3 className="text-xs font-bold text-gray-500 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
                            <ShieldCheck className="w-4 h-4" />
                            Received Proposals
                        </h3>
                        {receivedProposals.length > 0 ? (
                            <div className="grid grid-cols-1 gap-6">
                                {receivedProposals.map(proposal => (
                                    <div key={proposal.id} className="glass-card p-6 rounded-3xl border border-gray-200 hover:border-teal-500/30 transition-all">
                                        <div className="flex justify-between items-start mb-4">
                                            <div>
                                                <h4 className="text-lg font-bold text-gray-800">{proposal.eventTitle}</h4>
                                                <p className="text-sm text-teal-500 font-medium">From: {proposal.senderName}</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-2xl font-bold text-gray-800">${proposal.estimatedInvestment}</p>
                                                <p className="text-[10px] text-gray-500 uppercase tracking-widest">{new Date(proposal.timestamp).toLocaleDateString()}</p>
                                            </div>
                                        </div>
                                        <div className="bg-gray-100 p-4 rounded-2xl border border-gray-100 mb-6">
                                            <p className="text-sm text-gray-500 italic leading-relaxed">"{proposal.message}"</p>
                                        </div>
                                        <div className="flex gap-3">
                                          <Button
                                            variant="primary"
                                            className="flex-1 py-2.5 text-xs"
                                            disabled={proposal.status !== 'pending'}
                                            onClick={() => updateProposalStatus(proposal.id, 'accepted')}
                                          >
                                            {proposal.status === 'accepted' ? 'Accepted' : 'Accept'}
                                          </Button>
                                          <Button
                                            variant="glass"
                                            className="flex-1 py-2.5 text-xs"
                                            disabled={proposal.status !== 'pending'}
                                            onClick={() => updateProposalStatus(proposal.id, 'declined')}
                                          >
                                            {proposal.status === 'declined' ? 'Declined' : 'Decline'}
                                          </Button>
                                          <Button
                                            variant="ghost"
                                            className="flex-1 py-2.5 text-xs"
                                            onClick={() => setSelectedProposal(proposal)}
                                          >
                                            View Details
                                          </Button>
                                        </div>
                                        <div className="mt-3 text-right">
                                          <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${statusBadgeClass(proposal.status)}`}>
                                            {proposal.status}
                                          </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-12 bg-gray-50 rounded-3xl border border-dashed border-gray-200">
                                <p className="text-gray-500 text-sm">No sponsorship proposals received yet.</p>
                            </div>
                        )}
                    </div>

                    <div className="space-y-6">
                        <h3 className="text-xs font-bold text-gray-500 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
                            <Send className="w-4 h-4" />
                            Sent Proposals
                        </h3>
                        {sentProposals.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {sentProposals.map(proposal => (
                                    <div key={proposal.id} className="glass-card p-5 rounded-2xl border border-gray-200 opacity-80 hover:opacity-100 transition-all">
                                        <div className="flex justify-between items-start mb-2">
                                            <h4 className="font-bold text-gray-800 truncate pr-4">{proposal.eventTitle}</h4>
                                        <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${statusBadgeClass(proposal.status)}`}>{proposal.status}</span>
                                        </div>
                                        <div className="flex justify-between items-end">
                                            <p className="text-sm font-bold text-gray-800">${proposal.estimatedInvestment}</p>
                                          <div className="flex items-center gap-3">
                                            <button
                                              onClick={() => setSelectedProposal(proposal)}
                                              className="text-[10px] text-teal-500 hover:text-teal-600 uppercase tracking-wider font-bold"
                                            >
                                              View Details
                                            </button>
                                            <p className="text-[10px] text-gray-500">{new Date(proposal.timestamp).toLocaleDateString()}</p>
                                          </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-12 bg-gray-50 rounded-3xl border border-dashed border-gray-200">
                                <p className="text-gray-500 text-sm">You haven't sent any sponsorship proposals yet.</p>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

// --- Main App Component ---

const SponsorViewWrapper = () => {
    const { id } = useParams();
    const { events } = useEvents();
    const event = events.find(e => e.id === id);
    if (!event) return <div className="pt-24 text-center">Event not found</div>;
    return <SponsorshipPage event={event} mode="sponsor" />;
};

const HostSponsorSettingsWrapper = () => {
    const { id } = useParams();
    const { events, addEvent } = useEvents(); // In a real app we'd have an updateEvent
    const event = events.find(e => e.id === id);
    const navigate = useNavigate();

    if (!event) return <div className="pt-24 text-center">Event not found</div>;

    const handleUpdate = (settings: any) => {
        // Mock update
        event.sponsorshipSettings = settings;
        navigate(`/event/${event.id}`);
    };

    return <SponsorshipPage event={event} mode="host" onUpdateSettings={handleUpdate} />;
};

const EventProvider = ({ children }: { children: React.ReactNode }) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [proposals, setProposals] = useState<SponsorshipProposal[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const checkAuth = async () => {
    try {
      console.log('[Auth] Checking authentication status...');
      const res = await fetch('/api/auth/me', { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        console.log('[Auth] User authenticated:', data.email);
        setUser(data);
      } else {
        console.log('[Auth] User not authenticated (status:', res.status, ')');
        setUser(null);
      }
    } catch (error) {
      console.error("[Auth] Check failed:", error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchEvents = async () => {
    try {
      const response = await fetch('/api/events', { credentials: 'include' });
      if (response.ok) {
        const data = await response.json();
        setEvents(data);
      }
    } catch (error) {
      console.error("Failed to fetch events:", error);
    }
  };

  useEffect(() => {
    fetchEvents();
    checkAuth();
  }, []);

  const fetchProposals = async () => {
    try {
      const response = await fetch('/api/proposals', { credentials: 'include' });
      if (response.ok) {
        const data = await response.json();
        setProposals(data);
      } else if (response.status === 401) {
        setProposals([]);
      }
    } catch (error) {
      console.error('Failed to fetch proposals:', error);
    }
  };

  useEffect(() => {
    if (user) {
      fetchProposals();
    } else {
      setProposals([]);
    }
  }, [user?.id]);

  const login = async (email: string, password: string) => {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
      credentials: 'include'
    });
    if (res.ok) {
      const data = await res.json();
      setUser(data.user);
    } else {
      let errMessage = "Login failed";
      try {
        const err = await res.json();
        if (err.error) {
          try {
            const parsed = JSON.parse(err.error);
            if (Array.isArray(parsed) && parsed[0]?.message) {
              errMessage = parsed[0].message;
            } else errMessage = err.error;
          } catch {
            errMessage = err.error;
          }
        }
      } catch (e) {
        // Fallback for empty or non-JSON responses
      }
      throw new Error(errMessage);
    }
  };

  const register = async (name: string, email: string, password: string) => {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
      credentials: 'include'
    });
    if (res.ok) {
      const data = await res.json();
      setUser(data.user);
      return { success: true };
    } else {
      let errMessage = "Registration failed";
      try {
        const err = await res.json();
        if (err.error) {
          try {
            const parsed = JSON.parse(err.error);
            if (Array.isArray(parsed) && parsed[0]?.message) {
              errMessage = parsed[0].message;
            } else errMessage = err.error;
          } catch {
            errMessage = err.error;
          }
        }
      } catch (e) {
        // Fallback for empty or non-JSON responses
      }
      throw new Error(errMessage);
    }
  };

  const logout = async () => {
    await fetch('/api/auth/logout', { 
      method: 'POST',
      credentials: 'include'
    });
    setUser(null);
    setProposals([]);
  };

  const updateProfile = async (data: Partial<User>) => {
    const res = await fetch('/api/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'include'
    });
    if (res.ok) {
      setUser(prev => prev ? { ...prev, ...data } : null);
    } else {
      let errMessage = "Update failed";
      try {
        const err = await res.json();
        errMessage = err.error || errMessage;
      } catch (e) {
        // Fallback
      }
      throw new Error(errMessage);
    }
  };

  const uploadAvatar = async (file: File) => {
    const formData = new FormData();
    formData.append('avatar', file);
    const res = await fetch('/api/profile/avatar', {
      method: 'POST',
      body: formData,
      credentials: 'include'
    });
    if (res.ok) {
      const data = await res.json();
      setUser(prev => prev ? { ...prev, avatarUrl: data.avatarUrl } : null);
    } else {
      let errMessage = "Upload failed";
      try {
        const err = await res.json();
        errMessage = err.error || errMessage;
      } catch (e) {
        // Fallback
      }
      throw new Error(errMessage);
    }
  };

  const addEvent = async (event: Event) => {
    try {
      const response = await fetch('/api/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event),
        credentials: 'include'
      });
      if (response.ok) {
        setEvents(prev => [event, ...prev]);
      }
    } catch (error) {
      console.error("Failed to add event:", error);
    }
  };

  const updateEvent = async (event: Event) => {
    try {
      const response = await fetch(`/api/events/${event.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event),
        credentials: 'include'
      });
      if (response.ok) {
        setEvents(prev => prev.map(e => e.id === event.id ? event : e));
      }
    } catch (error) {
      console.error("Failed to update event:", error);
    }
  };

  const deleteEvent = async (eventId: string) => {
    try {
      const response = await fetch(`/api/events/${eventId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (response.ok) {
        setEvents(prev => prev.filter(e => e.id !== eventId));
      } else {
        const err = await response.json();
        throw new Error(err.error || "Failed to delete event");
      }
    } catch (error) {
      console.error("Failed to delete event:", error);
      throw error;
    }
  };

  const attendEvent = async (eventId: string) => {
    try {
      const response = await fetch('/api/users/attend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: user?.id, eventId }),
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setUser(prev => prev ? { ...prev, attendedEventIds: data.attendedEventIds } : null);
        // Re-fetch events to update attendee counts
        fetchEvents();
      }
    } catch (error) {
      console.error("Failed to attend event:", error);
    }
  };

  const refreshUser = async () => {
    await checkAuth();
  };

  const createProposal = async (proposal: Omit<SponsorshipProposal, 'id' | 'senderId' | 'senderName' | 'status' | 'timestamp'>) => {
    const response = await fetch('/api/proposals', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(proposal),
      credentials: 'include'
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ error: 'Failed to create proposal' }));
      throw new Error(err.error || 'Failed to create proposal');
    }

    const created = await response.json();
    setProposals(prev => [created, ...prev]);
  };

  const updateProposalStatus = async (proposalId: string, status: 'accepted' | 'declined') => {
    const response = await fetch(`/api/proposals/${proposalId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
      credentials: 'include'
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ error: 'Failed to update proposal' }));
      throw new Error(err.error || 'Failed to update proposal');
    }

    const updated = await response.json();
    setProposals(prev => prev.map(p => p.id === updated.id ? updated : p));
  };

  return (
    <EventContext.Provider value={{ 
      events, addEvent, updateEvent, deleteEvent, attendEvent, refreshUser, fetchProposals, user, proposals, createProposal, updateProposalStatus,
      login, register, logout, updateProfile, uploadAvatar, isLoading
    }}>
      {children}
    </EventContext.Provider>
  );
};

const App = () => {
  const [showAI, setShowAI] = useState(false);

  return (
    <EventProvider>
      <HashRouter>
        <div className="bg-background min-h-screen text-gray-800 font-sans selection:bg-teal-500/20 selection:text-white">
          <NavBar />
          <AIAssistantOverlay isOpen={showAI} onClose={() => setShowAI(false)} />
          
          <Routes>
            <Route path="/" element={<LandingPage onOpenAI={() => setShowAI(true)} />} />
            <Route path="/explore" element={<ExplorePage />} />
            <Route path="/sponsors" element={<SponsorsPage />} />
            <Route path="/sponsor/signup" element={<SponsorSignupPage />} />
            <Route path="/sponsor/dashboard" element={<SponsorDashboardPage />} />
            <Route path="/event/:id" element={<EventDetailsPage />} />
            <Route path="/event/:id/edit" element={<EditEventPage />} />
            <Route path="/event/:id/sponsor" element={<SponsorViewWrapper />} />
            <Route path="/event/:id/sponsor/settings" element={<HostSponsorSettingsWrapper />} />
            <Route path="/host" element={<CreateEventPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/auth" element={<AuthPage />} />
            <Route path="/onboarding" element={<OnboardingPage />} />
          </Routes>

          {/* Mobile Bottom Navigation */}
          <MobileNav onOpenAI={() => setShowAI(true)} />
        </div>
      </HashRouter>
    </EventProvider>
  );
};

export default App;
