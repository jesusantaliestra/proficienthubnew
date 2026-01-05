import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { ScrollArea } from '../components/ui/scroll-area';
import { 
  Brain, Send, ArrowLeft, Sparkles, BookOpen, 
  Lightbulb, Target, MessageSquare, Loader2
} from 'lucide-react';
import axios from 'axios';
import { toast, Toaster } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AITutor() {
  const { examType } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const scrollRef = useRef(null);

  const examNames = {
    toefl: 'TOEFL',
    ielts: 'IELTS',
    cambridge: 'Cambridge',
    pte: 'PTE',
    oet: 'OET'
  };

  const suggestedQuestions = [
    `What are the key strategies for the ${examNames[examType]} reading section?`,
    `How can I improve my ${examNames[examType]} speaking score?`,
    `What common mistakes should I avoid in ${examNames[examType]} writing?`,
    `Can you explain the ${examNames[examType]} scoring system?`
  ];

  useEffect(() => {
    fetchHistory();
    // Add welcome message
    setMessages([{
      role: 'assistant',
      content: `Hello! I'm your ${examNames[examType]} exam expert. I can help you with strategies, practice tips, and answer any questions about the exam. What would you like to learn today?`
    }]);
  }, [examType]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/ai-tutor/history/${examType}`);
      setHistory(response.data.conversations || []);
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  };

  const sendMessage = async (messageText = input) => {
    if (!messageText.trim()) return;
    
    const userMessage = { role: 'user', content: messageText };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/ai-tutor/chat`, {
        message: messageText,
        exam_type: examType,
        context: null
      });

      const assistantMessage = { role: 'assistant', content: response.data.response };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Failed to get response. Please try again.');
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'I apologize, but I encountered an issue. Please try again.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col" data-testid="ai-tutor-page">
      <Toaster position="top-right" richColors />
      
      {/* Header */}
      <header className="bg-slate-900/50 border-b border-slate-800 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              onClick={() => navigate(-1)}
              className="text-slate-400 hover:text-white"
              data-testid="back-btn"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center`}>
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-white font-outfit">
                  {examNames[examType]} AI Tutor
                </h1>
                <p className="text-xs text-slate-500">Powered by Advanced AI</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>Premium AI Tutor</span>
          </div>
        </div>
      </header>

      {/* Main Chat Area */}
      <div className="flex-1 max-w-5xl mx-auto w-full p-6 flex gap-6">
        {/* Chat */}
        <div className="flex-1 flex flex-col">
          <Card className="flex-1 bg-slate-900/30 border-slate-800 flex flex-col">
            <ScrollArea className="flex-1 p-6" ref={scrollRef}>
              <div className="space-y-6">
                {messages.map((message, index) => (
                  <div 
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    data-testid={`message-${index}`}
                  >
                    <div className={`max-w-[80%] ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                      <div className={`flex items-start gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                          message.role === 'user' 
                            ? 'bg-blue-500' 
                            : 'bg-gradient-to-br from-purple-500 to-purple-700'
                        }`}>
                          {message.role === 'user' 
                            ? <span className="text-xs font-bold text-white">{user?.name?.charAt(0) || 'U'}</span>
                            : <Brain className="w-4 h-4 text-white" />
                          }
                        </div>
                        <div className={`rounded-2xl px-4 py-3 ${
                          message.role === 'user'
                            ? 'bg-blue-500 text-white'
                            : 'bg-slate-800 text-slate-200'
                        }`}>
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {loading && (
                  <div className="flex justify-start">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center">
                        <Brain className="w-4 h-4 text-white" />
                      </div>
                      <div className="bg-slate-800 rounded-2xl px-4 py-3">
                        <Loader2 className="w-5 h-5 text-slate-400 animate-spin" />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* Suggested Questions */}
            {messages.length <= 1 && (
              <div className="px-6 pb-4">
                <p className="text-xs text-slate-500 mb-3">Suggested questions:</p>
                <div className="flex flex-wrap gap-2">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => sendMessage(question)}
                      className="px-3 py-2 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-full transition-colors"
                      data-testid={`suggested-question-${index}`}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Input */}
            <div className="p-4 border-t border-slate-800">
              <div className="flex gap-3">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={`Ask anything about ${examNames[examType]}...`}
                  className="flex-1 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
                  disabled={loading}
                  data-testid="chat-input"
                />
                <Button 
                  onClick={() => sendMessage()}
                  disabled={loading || !input.trim()}
                  className="bg-blue-500 hover:bg-blue-600 px-6"
                  data-testid="send-btn"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="w-72 space-y-4 hidden lg:block">
          <Card className="bg-slate-900/30 border-slate-800">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-white flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-amber-400" />
                Quick Tips
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="p-3 bg-slate-800/50 rounded-lg">
                <p className="text-xs text-slate-400">Ask about specific sections like reading, writing, listening, or speaking</p>
              </div>
              <div className="p-3 bg-slate-800/50 rounded-lg">
                <p className="text-xs text-slate-400">Request practice questions or sample answers</p>
              </div>
              <div className="p-3 bg-slate-800/50 rounded-lg">
                <p className="text-xs text-slate-400">Get feedback on your written responses</p>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900/30 border-slate-800">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-white flex items-center gap-2">
                <Target className="w-4 h-4 text-emerald-400" />
                Exam Focus Areas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {['Reading', 'Listening', 'Speaking', 'Writing'].map((section) => (
                  <button
                    key={section}
                    onClick={() => sendMessage(`What are the best strategies for the ${examNames[examType]} ${section} section?`)}
                    className="w-full text-left px-3 py-2 text-sm bg-slate-800/50 hover:bg-slate-800 text-slate-300 rounded-lg transition-colors"
                  >
                    {section} Strategies
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {history.length > 0 && (
            <Card className="bg-slate-900/30 border-slate-800">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-white flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-blue-400" />
                  Recent Chats
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-40 overflow-auto">
                  {history.slice(0, 5).map((chat, index) => (
                    <div key={index} className="p-2 bg-slate-800/30 rounded text-xs text-slate-400 truncate">
                      {chat.user_message}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
