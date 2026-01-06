import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { 
  Bot, Send, Mic, MicOff, Volume2, VolumeX, Loader2,
  MessageSquare, ChevronLeft, Settings, Play, Pause,
  BookOpen, Lightbulb, Target, CheckCircle
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AITutor() {
  const navigate = useNavigate();
  const { examType = 'ielts' } = useParams();
  const { user } = useAuth();
  
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [voiceMode, setVoiceMode] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState('nova');
  const [availableVoices, setAvailableVoices] = useState([]);
  
  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);

  const examInfo = {
    toefl: { name: 'TOEFL', color: 'bg-blue-500', description: 'Academic English for US universities' },
    ielts: { name: 'IELTS', color: 'bg-red-500', description: 'International English testing' },
    cambridge: { name: 'Cambridge', color: 'bg-purple-500', description: 'Comprehensive English qualifications' },
    pte: { name: 'PTE', color: 'bg-orange-500', description: 'Computer-based testing' },
    oet: { name: 'OET', color: 'bg-green-500', description: 'Healthcare professionals' }
  };

  useEffect(() => {
    fetchVoices();
    loadHistory();
    // Add welcome message
    setMessages([{
      role: 'assistant',
      content: `¡Hola! I'm your ${examInfo[examType]?.name || 'English'} AI tutor. I can help you with:

• **Test strategies** - Tips for each section
• **Practice questions** - Get instant feedback
• **Grammar & vocabulary** - Improve your skills
• **Speaking practice** - Use voice mode for conversation

How can I help you prepare today?`,
      timestamp: new Date()
    }]);
  }, [examType]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchVoices = async () => {
    try {
      const response = await axios.get(`${API_URL}/voice/available-voices`);
      setAvailableVoices(response.data.voices);
    } catch (error) {
      console.error('Error fetching voices:', error);
    }
  };

  const loadHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/ai-tutor/history/${examType}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Could load previous conversations here
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const sendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const token = localStorage.getItem('token');
      
      if (voiceMode) {
        // Use voice chat endpoint
        const response = await axios.post(
          `${API_URL}/ai-tutor/voice-chat`,
          {
            message: messageText,
            exam_type: examType,
            voice: selectedVoice
          },
          { headers: { Authorization: `Bearer ${token}` } }
        );

        const assistantMessage = {
          role: 'assistant',
          content: response.data.text_response,
          audio: response.data.audio_base64,
          timestamp: new Date()
        };

        setMessages(prev => [...prev, assistantMessage]);

        // Auto-play audio
        if (response.data.audio_base64) {
          playAudio(response.data.audio_base64);
        }
      } else {
        // Text-only chat
        const response = await axios.post(
          `${API_URL}/ai-tutor/chat`,
          {
            message: messageText,
            exam_type: examType
          },
          { headers: { Authorization: `Bearer ${token}` } }
        );

        const assistantMessage = {
          role: 'assistant',
          content: response.data.response,
          timestamp: new Date()
        };

        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Error communicating with tutor');
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date(),
        error: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const playAudio = (base64Audio) => {
    try {
      const audio = new Audio(`data:audio/mp3;base64,${base64Audio}`);
      audioRef.current = audio;
      
      audio.onplay = () => setIsPlaying(true);
      audio.onended = () => setIsPlaying(false);
      audio.onerror = () => {
        setIsPlaying(false);
        toast.error('Error playing audio');
      };
      
      audio.play();
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach(track => track.stop());
        await transcribeAndSend(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      toast.error('Could not access microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAndSend = async (audioBlob) => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');
      
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'voice_message.webm');
      formData.append('language', 'en');
      
      const transcribeResponse = await axios.post(
        `${API_URL}/voice/speech-to-text`,
        formData,
        { 
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          } 
        }
      );

      const transcribedText = transcribeResponse.data.text;
      
      if (transcribedText) {
        await sendMessage(transcribedText);
      } else {
        toast.error('Could not transcribe audio');
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error transcribing:', error);
      toast.error('Error processing voice message');
      setIsLoading(false);
    }
  };

  const quickPrompts = [
    { icon: Target, text: "What's the best strategy for the reading section?", label: "Reading Tips" },
    { icon: Lightbulb, text: "Give me a practice question for writing task 2", label: "Writing Practice" },
    { icon: BookOpen, text: "What vocabulary should I focus on?", label: "Vocabulary" },
    { icon: CheckCircle, text: "How can I improve my speaking score?", label: "Speaking Help" }
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => navigate(-1)}
              >
                <ChevronLeft className="w-4 h-4 mr-1" />
                Back
              </Button>
              
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl ${examInfo[examType]?.color || 'bg-gray-500'} flex items-center justify-center`}>
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="font-bold text-gray-900">
                    {examInfo[examType]?.name} AI Tutor
                  </h1>
                  <p className="text-xs text-gray-500">
                    {examInfo[examType]?.description}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Voice Mode Toggle */}
              <Button
                variant={voiceMode ? 'default' : 'outline'}
                size="sm"
                onClick={() => setVoiceMode(!voiceMode)}
                className={voiceMode ? 'bg-[#58CC02] hover:bg-[#46A302]' : ''}
              >
                {voiceMode ? <Volume2 className="w-4 h-4 mr-2" /> : <VolumeX className="w-4 h-4 mr-2" />}
                {voiceMode ? 'Voice On' : 'Voice Off'}
              </Button>

              {/* Voice Selection */}
              {voiceMode && (
                <select
                  value={selectedVoice}
                  onChange={(e) => setSelectedVoice(e.target.value)}
                  className="text-sm border rounded-lg px-2 py-1"
                >
                  {availableVoices.map(voice => (
                    <option key={voice.id} value={voice.id}>
                      {voice.name}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-6 py-6 space-y-4">
          {messages.map((message, idx) => (
            <div
              key={idx}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-[#58CC02] text-white'
                    : message.error
                      ? 'bg-red-100 text-red-800'
                      : 'bg-white border border-gray-200 text-gray-800'
                }`}
              >
                <div className="prose prose-sm max-w-none">
                  {message.content.split('\n').map((line, i) => (
                    <p key={i} className="mb-1 last:mb-0">
                      {line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .split(/(<strong>.*?<\/strong>)/)
                        .map((part, j) => 
                          part.startsWith('<strong>') 
                            ? <strong key={j}>{part.replace(/<\/?strong>/g, '')}</strong>
                            : part
                        )}
                    </p>
                  ))}
                </div>
                
                {/* Audio playback button */}
                {message.audio && message.role === 'assistant' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="mt-2 text-gray-500"
                    onClick={() => isPlaying ? stopAudio() : playAudio(message.audio)}
                  >
                    {isPlaying ? <Pause className="w-4 h-4 mr-1" /> : <Play className="w-4 h-4 mr-1" />}
                    {isPlaying ? 'Stop' : 'Play Audio'}
                  </Button>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
                <div className="flex items-center gap-2 text-gray-500">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Quick Prompts */}
      {messages.length <= 2 && (
        <div className="max-w-4xl mx-auto px-6 pb-4">
          <p className="text-sm text-gray-500 mb-3">Quick questions:</p>
          <div className="flex flex-wrap gap-2">
            {quickPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => sendMessage(prompt.text)}
                className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-full text-sm hover:border-[#58CC02] hover:bg-green-50 transition-all"
              >
                <prompt.icon className="w-4 h-4 text-[#58CC02]" />
                {prompt.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 sticky bottom-0">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            {voiceMode && (
              <Button
                variant={isRecording ? 'destructive' : 'outline'}
                size="icon"
                className={isRecording ? 'animate-pulse' : ''}
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isLoading}
              >
                {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </Button>
            )}
            
            <Input
              placeholder={isRecording ? "Recording..." : "Ask me anything about the exam..."}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              disabled={isLoading || isRecording}
              className="flex-1"
            />
            
            <Button
              className="bg-[#58CC02] hover:bg-[#46A302]"
              onClick={() => sendMessage()}
              disabled={!inputMessage.trim() || isLoading}
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          
          {isRecording && (
            <p className="text-center text-sm text-red-500 mt-2 animate-pulse">
              🎤 Recording... Click the microphone to stop
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
