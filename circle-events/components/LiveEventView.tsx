
import React, { useState } from 'react';
import { LuminaEvent } from '../types';
import { X, Mic, MicOff, Video, VideoOff, MessageSquare, Users, Settings, LogOut } from 'lucide-react';

interface LiveEventViewProps {
  event: LuminaEvent;
  onExit: () => void;
}

const LiveEventView: React.FC<LiveEventViewProps> = ({ event, onExit }) => {
  const [isMicOn, setIsMicOn] = useState(false);
  const [isCamOn, setIsCamOn] = useState(true);
  const [activeTab, setActiveTab] = useState<'chat' | 'people'>('chat');

  return (
    <div className="fixed inset-0 z-[150] bg-slate-950 flex flex-col md:flex-row animate-in fade-in duration-500">
      {/* Main Content (Stage) */}
      <div className="flex-1 relative flex flex-col">
        <div className="absolute top-6 left-6 z-10 flex items-center gap-4">
          <div className="bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-tighter">Live</div>
          <h2 className="text-white font-semibold text-lg drop-shadow-lg">{event.title}</h2>
        </div>

        <div className="flex-1 flex items-center justify-center bg-black/40 overflow-hidden m-4 rounded-3xl relative">
          <img 
            src={event.image} 
            className="absolute inset-0 w-full h-full object-cover blur-2xl opacity-20"
            alt="bg"
          />
          <div className="relative z-10 w-full max-w-4xl aspect-video rounded-2xl overflow-hidden border border-white/10 glow bg-slate-900 group">
             {/* Mock Video Stream */}
             <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center space-y-4">
                  <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-tr from-indigo-500 to-cyan-500 flex items-center justify-center text-3xl font-bold">
                    {event.hostName[0]}
                  </div>
                  <p className="text-slate-400 font-medium">{event.hostName} is presenting...</p>
                </div>
             </div>
             
             {/* Self View (Mini) */}
             {isCamOn && (
               <div className="absolute bottom-4 right-4 w-40 aspect-video rounded-xl bg-slate-800 border border-white/20 overflow-hidden shadow-2xl">
                  <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/60"></div>
                  <div className="absolute bottom-2 left-2 text-[10px] font-medium text-white">You</div>
                  <img src="https://picsum.photos/seed/you/200/150" alt="me" className="w-full h-full object-cover" />
               </div>
             )}
          </div>
        </div>

        {/* Controls Overlay */}
        <div className="h-24 px-8 flex items-center justify-between border-t border-white/5 bg-slate-950/80 backdrop-blur-xl">
           <div className="flex items-center gap-3">
             <button 
              onClick={() => setIsMicOn(!isMicOn)}
              className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all ${isMicOn ? 'bg-indigo-500 text-white' : 'bg-white/5 text-slate-400 hover:bg-white/10'}`}
             >
               {isMicOn ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
             </button>
             <button 
              onClick={() => setIsCamOn(!isCamOn)}
              className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all ${isCamOn ? 'bg-indigo-500 text-white' : 'bg-white/5 text-slate-400 hover:bg-white/10'}`}
             >
               {isCamOn ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
             </button>
           </div>

           <div className="flex items-center gap-4">
             <button className="px-6 py-2.5 rounded-xl bg-white/5 text-slate-200 hover:bg-white/10 transition-all font-medium flex items-center gap-2">
               <Settings className="w-4 h-4" />
               Audio Settings
             </button>
             <button 
              onClick={onExit}
              className="px-6 py-2.5 rounded-xl bg-rose-500/10 text-rose-500 hover:bg-rose-500 hover:text-white transition-all font-bold flex items-center gap-2"
             >
               <LogOut className="w-4 h-4" />
               Leave Room
             </button>
           </div>
        </div>
      </div>

      {/* Sidebar (Chat & People) */}
      <div className="w-full md:w-80 border-l border-white/5 flex flex-col bg-slate-950/50 backdrop-blur-sm">
        <div className="p-4 flex gap-1 bg-white/5 mx-4 mt-4 rounded-xl">
          <button 
            onClick={() => setActiveTab('chat')}
            className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${activeTab === 'chat' ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'}`}
          >
            Chat
          </button>
          <button 
            onClick={() => setActiveTab('people')}
            className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${activeTab === 'people' ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'}`}
          >
            People ({event.attendeesCount})
          </button>
        </div>

        <div className="flex-1 p-4 overflow-y-auto">
          {activeTab === 'chat' ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="flex gap-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-800 shrink-0" />
                  <div className="space-y-1">
                    <div className="flex items-baseline gap-2">
                      <span className="text-xs font-bold text-white">User_{i}</span>
                      <span className="text-[10px] text-slate-500">2:4{i} PM</span>
                    </div>
                    <p className="text-sm text-slate-400">Loving this presentation! Really great insights.</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
                <div key={i} className="flex items-center justify-between p-2 rounded-xl hover:bg-white/5">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500/50 to-purple-500/50" />
                    <span className="text-sm font-medium text-slate-300">Attendee {i}</span>
                  </div>
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-4 border-t border-white/5">
           <div className="relative">
             <input 
              type="text" 
              placeholder="Send a message..."
              className="w-full bg-white/5 rounded-xl py-3 pl-4 pr-12 text-sm text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
             />
             <button className="absolute right-2 top-1.5 p-1.5 rounded-lg bg-indigo-500 text-white hover:bg-indigo-600">
               <MessageSquare className="w-4 h-4" />
             </button>
           </div>
        </div>
      </div>
    </div>
  );
};

export default LiveEventView;
