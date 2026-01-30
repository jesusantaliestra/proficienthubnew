import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, Sparkles, ArrowRight } from 'lucide-react';
import { Button } from '../components/ui/button';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function LandingAgentWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [config, setConfig] = useState(null);
  const [remainingMessages, setRemainingMessages] = useState(5);
  const [limitReached, setLimitReached] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadConfig();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadConfig = async () => {
    try {
      const res = await fetch(`${API_URL}/api/landing-agent/config`);
      if (res.ok) {
        const data = await res.json();
        setConfig(data);
        setRemainingMessages(data.max_messages || 5);
        
        // Add greeting message
        if (data.greeting_message) {
          setMessages([{
            role: 'assistant',
            content: data.greeting_message
          }]);
        }
      }
    } catch (err) {
      console.error('Error loading landing agent config:', err);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading || limitReached) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/landing-agent/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId
        })
      });

      if (res.ok) {
        const data = await res.json();
        setSessionId(data.session_id);
        setRemainingMessages(data.remaining_messages);
        setLimitReached(data.limit_reached);
        
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.response,
          cta: data.cta
        }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Lo siento, hubo un error. Por favor intenta de nuevo.' 
      }]);
    }
    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!config?.enabled) return null;

  return (
    <>
      {/* Chat Widget Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 bg-gradient-to-r from-violet-600 to-indigo-600 text-white p-4 rounded-full shadow-2xl hover:shadow-violet-500/25 hover:scale-110 transition-all duration-300 group"
          data-testid="landing-agent-button"
        >
          <div className="relative">
            <MessageCircle className="w-6 h-6" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse" />
          </div>
          <span className="absolute right-full mr-3 top-1/2 -translate-y-1/2 bg-slate-900 text-white text-sm px-3 py-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
            ¿Tienes preguntas? ¡Chatea con nosotros!
          </span>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div 
          className="fixed bottom-6 right-6 z-50 w-96 max-w-[calc(100vw-3rem)] bg-white rounded-2xl shadow-2xl overflow-hidden border border-slate-200"
          data-testid="landing-agent-chat"
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-violet-600 to-indigo-600 text-white p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold">Asistente ProficientHub</h3>
                  <p className="text-xs text-white/80">Respuestas instantáneas con IA</p>
                </div>
              </div>
              <button 
                onClick={() => setIsOpen(false)}
                className="hover:bg-white/20 p-1 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="h-80 overflow-y-auto p-4 space-y-4 bg-slate-50">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-2xl ${
                  msg.role === 'user' 
                    ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-br-md' 
                    : 'bg-white text-slate-800 shadow-sm rounded-bl-md border border-slate-100'
                }`}>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  
                  {/* CTA Button */}
                  {msg.cta && (
                    <a 
                      href={msg.cta.url}
                      className="mt-3 inline-flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-sm px-4 py-2 rounded-full hover:shadow-lg transition-all"
                    >
                      {msg.cta.text}
                      <ArrowRight className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white text-slate-600 p-3 rounded-2xl rounded-bl-md shadow-sm border border-slate-100">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                    <span className="text-xs text-slate-400">Escribiendo...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Remaining Messages Indicator */}
          {!limitReached && remainingMessages <= 3 && (
            <div className="px-4 py-2 bg-amber-50 border-t border-amber-100">
              <p className="text-xs text-amber-700 text-center">
                {remainingMessages} mensaje{remainingMessages !== 1 ? 's' : ''} restante{remainingMessages !== 1 ? 's' : ''} en la demo
              </p>
            </div>
          )}

          {/* Input Area */}
          <div className="p-4 border-t border-slate-200 bg-white">
            {limitReached ? (
              <div className="text-center">
                <p className="text-sm text-slate-600 mb-3">
                  ¡Gracias por probar nuestro asistente!
                </p>
                <Button 
                  className="w-full bg-gradient-to-r from-violet-600 to-indigo-600"
                  onClick={() => window.location.href = '/register'}
                >
                  Registrarse para Acceso Completo
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            ) : (
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Escribe tu pregunta..."
                  className="flex-1 p-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent text-sm"
                  disabled={loading}
                  data-testid="landing-agent-input"
                />
                <Button 
                  onClick={sendMessage}
                  disabled={loading || !input.trim()}
                  className="bg-gradient-to-r from-violet-600 to-indigo-600 rounded-xl px-4"
                  data-testid="landing-agent-send"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
