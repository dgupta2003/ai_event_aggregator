
import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Search, Loader2, X, Command } from 'lucide-react';
import { gemini } from '../services/geminiService';

interface VoiceAssistantProps {
  onCommand: (result: { action: string; query?: string; destination?: string; message: string }) => void;
}

const VoiceAssistant: React.FC<VoiceAssistantProps> = ({ onCommand }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Basic Web Speech API for getting transcript
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;

      recognitionRef.current.onresult = (event: any) => {
        const current = event.resultIndex;
        const text = event.results[current][0].transcript;
        setTranscript(text);
        
        if (event.results[current].isFinal) {
          handleFinalTranscript(text);
        }
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  const startListening = () => {
    setTranscript('');
    setIsListening(true);
    setIsOpen(true);
    recognitionRef.current?.start();
  };

  const stopListening = () => {
    setIsListening(false);
    recognitionRef.current?.stop();
  };

  const handleFinalTranscript = async (text: string) => {
    setIsProcessing(true);
    const result = await gemini.processVoiceCommand(text);
    onCommand(result);
    setIsProcessing(false);
    
    // Auto close after small delay
    setTimeout(() => {
      setIsOpen(false);
    }, 3000);
  };

  return (
    <div className="fixed bottom-8 right-8 z-[100] flex flex-col items-end gap-4">
      {isOpen && (
        <div className="glass w-80 p-4 rounded-3xl glow animate-in fade-in slide-in-from-bottom-4 duration-300">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2 text-indigo-400 font-semibold">
              <Command className="w-4 h-4" />
              <span>Circle AI</span>
            </div>
            <button onClick={() => setIsOpen(false)} className="text-slate-500 hover:text-white transition-colors">
              <X className="w-4 h-4" />
            </button>
          </div>
          
          <div className="min-h-[80px] bg-white/5 rounded-2xl p-4 mb-4 flex items-center justify-center text-center">
            {isProcessing ? (
              <div className="flex flex-col items-center gap-2">
                <Loader2 className="w-6 h-6 animate-spin text-indigo-500" />
                <span className="text-xs text-slate-400">Processing request...</span>
              </div>
            ) : isListening ? (
              <p className="text-sm font-medium text-white">
                {transcript || "Listening..."}
              </p>
            ) : (
              <p className="text-sm text-slate-400 italic">
                Try "Find design events" or "Take me to hosting"
              </p>
            )}
          </div>

          <div className="flex justify-center gap-4">
            <div className={`p-0.5 rounded-full ${isListening ? 'bg-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.5)]' : 'bg-transparent'}`}>
              <button 
                onClick={isListening ? stopListening : startListening}
                className="w-12 h-12 rounded-full bg-slate-900 flex items-center justify-center hover:bg-slate-800 transition-colors"
              >
                {isListening ? (
                  <Mic className="w-6 h-6 text-indigo-400 animate-pulse" />
                ) : (
                  <Mic className="w-6 h-6 text-white" />
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {!isOpen && (
        <button 
          onClick={() => setIsOpen(true)}
          className="w-16 h-16 rounded-full glass glow flex items-center justify-center hover:scale-110 active:scale-90 transition-all group"
        >
          <div className="absolute inset-0 rounded-full bg-indigo-500/20 blur-xl group-hover:bg-indigo-500/30 transition-all"></div>
          <Mic className="w-7 h-7 text-white relative z-10" />
        </button>
      )}
    </div>
  );
};

export default VoiceAssistant;
