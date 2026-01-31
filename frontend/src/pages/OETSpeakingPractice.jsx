import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Mic,
  MicOff,
  Video,
  VideoOff,
  Play,
  Square,
  Volume2,
  VolumeX,
  Clock,
  User,
  MessageSquare,
  Sparkles,
  Zap,
  ArrowLeft,
  Settings,
  Info,
  CheckCircle2,
  AlertCircle,
  Crown,
  Coins
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Avatar tiers
const AVATAR_TIERS = {
  premium: {
    name: 'Premium (HeyGen)',
    icon: Crown,
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/20',
    description: 'Avatar con video streaming en tiempo real, lip-sync perfecto y emociones'
  },
  economic: {
    name: 'Básico',
    icon: Coins,
    color: 'text-green-400',
    bgColor: 'bg-green-500/20',
    description: 'Avatar con imagen estática y voz TTS del navegador'
  }
};

export default function OETSpeakingPractice() {
  const { t } = useTranslation();
  const { scenarioId } = useParams();
  const navigate = useNavigate();
  
  // State
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [session, setSession] = useState(null);
  const [phase, setPhase] = useState('selection'); // selection | prep | speaking | review
  const [prepTimeLeft, setPrepTimeLeft] = useState(180);
  const [speakingTimeLeft, setSpeakingTimeLeft] = useState(300);
  const [conversation, setConversation] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [selectedTier, setSelectedTier] = useState('economic');
  const [loading, setLoading] = useState(false);
  const [showTierSelector, setShowTierSelector] = useState(false);
  
  // Refs
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const speechSynthRef = useRef(null);
  
  // Load scenarios on mount
  useEffect(() => {
    fetchScenarios();
  }, []);
  
  // Handle scenario from URL param
  useEffect(() => {
    if (scenarioId && scenarios.length > 0) {
      const scenario = scenarios.find(s => s.id === scenarioId);
      if (scenario) {
        setSelectedScenario(scenario);
        setShowTierSelector(true);
      }
    }
  }, [scenarioId, scenarios]);
  
  // Prep timer
  useEffect(() => {
    if (phase === 'prep' && prepTimeLeft > 0) {
      timerRef.current = setInterval(() => {
        setPrepTimeLeft(prev => {
          if (prev <= 1) {
            clearInterval(timerRef.current);
            setPhase('speaking');
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timerRef.current);
    }
  }, [phase]);
  
  // Speaking timer
  useEffect(() => {
    if (phase === 'speaking' && speakingTimeLeft > 0) {
      timerRef.current = setInterval(() => {
        setSpeakingTimeLeft(prev => {
          if (prev <= 1) {
            clearInterval(timerRef.current);
            endSession();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timerRef.current);
    }
  }, [phase]);
  
  const fetchScenarios = async () => {
    try {
      const response = await fetch(`${API_URL}/api/avatar-service/oet/scenarios`);
      if (response.ok) {
        const data = await response.json();
        setScenarios(data.scenarios || []);
      }
    } catch (error) {
      console.error('Error fetching scenarios:', error);
    }
  };
  
  const startRoleplay = async () => {
    if (!selectedScenario) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/avatar-service/oet/start-roleplay?scenario_id=${selectedScenario.id}&provider=${selectedTier}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        setSession(data.session);
        setConversation([{
          role: 'avatar',
          content: data.initial_greeting
        }]);
        setShowTierSelector(false);
        setPhase('prep');
        
        // Speak initial greeting
        speakText(data.initial_greeting);
      } else {
        toast.error('Error al iniciar la práctica');
      }
    } catch (error) {
      toast.error('Error de conexión');
    } finally {
      setLoading(false);
    }
  };
  
  const speakText = (text) => {
    if (session?.connection_type === 'tts' || session?.use_web_speech) {
      // Use Web Speech API for economic tier
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 0.9;
        utterance.onstart = () => setIsSpeaking(true);
        utterance.onend = () => setIsSpeaking(false);
        speechSynthRef.current = utterance;
        window.speechSynthesis.speak(utterance);
      }
    }
    // For HeyGen premium, frontend SDK handles this
  };
  
  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };
  
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: { echoCancellation: true, noiseSuppression: true } 
      });
      
      const mediaRecorder = new MediaRecorder(stream);
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await processAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
    } catch (error) {
      toast.error('Por favor, permite el acceso al micrófono');
    }
  };
  
  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };
  
  const processAudio = async (audioBlob) => {
    // Send to Whisper API for transcription
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.webm');
      formData.append('language', 'en');
      formData.append('prompt', `OET speaking practice. Patient: ${selectedScenario?.patient_name}. Healthcare professional responding.`);
      if (session?.id) {
        formData.append('session_id', session.id);
      }
      
      const response = await fetch(`${API_URL}/api/speech/transcribe`, {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        const transcribedText = data.text;
        
        if (transcribedText && transcribedText.trim()) {
          await sendUserMessage(transcribedText);
        } else {
          toast.error('No se detectó ningún discurso. Intenta de nuevo.');
        }
      } else {
        const error = await response.json();
        console.error('Transcription error:', error);
        toast.error('Error al transcribir. Intenta de nuevo.');
      }
    } catch (error) {
      console.error('Transcription failed:', error);
      toast.error('Error de conexión. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };
    }
  };
  
  const sendUserMessage = async (text) => {
    if (!session || !text.trim()) return;
    
    // Add user message to conversation
    const userMessage = { role: 'user', content: text };
    setConversation(prev => [...prev, userMessage]);
    
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/avatar-service/session/${session.id}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: session.id,
          user_message: text,
          conversation_history: conversation
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        const avatarMessage = { role: 'avatar', content: data.avatar_response };
        setConversation(prev => [...prev, avatarMessage]);
        
        // Avatar speaks the response
        speakText(data.avatar_response);
      }
    } catch (error) {
      toast.error('Error al obtener respuesta');
    } finally {
      setLoading(false);
    }
  };
  
  const skipPrep = () => {
    clearInterval(timerRef.current);
    setPhase('speaking');
  };
  
  const endSession = async () => {
    clearInterval(timerRef.current);
    stopSpeaking();
    
    if (session) {
      try {
        await fetch(`${API_URL}/api/avatar-service/session/${session.id}`, {
          method: 'DELETE'
        });
      } catch (error) {
        console.error('Error ending session:', error);
      }
    }
    
    setPhase('review');
  };
  
  const resetPractice = () => {
    setSession(null);
    setSelectedScenario(null);
    setPhase('selection');
    setPrepTimeLeft(180);
    setSpeakingTimeLeft(300);
    setConversation([]);
  };
  
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Render scenario selection
  if (phase === 'selection') {
    return (
      <div className="min-h-screen bg-slate-950 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center gap-4 mb-8">
            <Button variant="ghost" onClick={() => navigate(-1)} className="text-slate-400">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                <Mic className="w-7 h-7 text-green-400" />
                OET Speaking Practice
              </h1>
              <p className="text-slate-400">Practica con pacientes simulados por IA</p>
            </div>
          </div>
          
          {/* Tier Info */}
          <div className="grid md:grid-cols-2 gap-4 mb-8">
            {Object.entries(AVATAR_TIERS).map(([tier, info]) => (
              <Card 
                key={tier}
                className={`bg-slate-900/50 border-slate-800 cursor-pointer transition-all ${
                  selectedTier === tier ? 'ring-2 ring-teal-500' : ''
                }`}
                onClick={() => setSelectedTier(tier)}
              >
                <CardContent className="p-4 flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-xl ${info.bgColor} flex items-center justify-center`}>
                    <info.icon className={`w-6 h-6 ${info.color}`} />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-white font-medium">{info.name}</h3>
                    <p className="text-slate-400 text-sm">{info.description}</p>
                  </div>
                  {selectedTier === tier && (
                    <CheckCircle2 className="w-5 h-5 text-teal-400" />
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
          
          {/* Scenarios */}
          <h2 className="text-xl font-semibold text-white mb-4">Selecciona un Escenario</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {scenarios.map((scenario) => (
              <Card 
                key={scenario.id}
                className="bg-slate-900/50 border-slate-800 hover:border-slate-700 transition-all cursor-pointer"
                onClick={() => { setSelectedScenario(scenario); setShowTierSelector(true); }}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <Badge className={`mb-2 ${
                      scenario.difficulty === 'beginner' ? 'bg-green-500/20 text-green-300' :
                      scenario.difficulty === 'intermediate' ? 'bg-yellow-500/20 text-yellow-300' :
                      'bg-red-500/20 text-red-300'
                    }`}>
                      {scenario.difficulty}
                    </Badge>
                    <User className="w-5 h-5 text-slate-500" />
                  </div>
                  <CardTitle className="text-white text-lg">{scenario.title}</CardTitle>
                  <CardDescription className="text-slate-400">
                    {scenario.patient_name}, {scenario.patient_age} años
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-500 text-sm mb-3">{scenario.setting}</p>
                  <p className="text-slate-400 text-sm line-clamp-2">{scenario.situation}</p>
                </CardContent>
              </Card>
            ))}
          </div>
          
          {/* Tier Selection Dialog */}
          <Dialog open={showTierSelector} onOpenChange={setShowTierSelector}>
            <DialogContent className="bg-slate-900 border-slate-700 max-w-lg">
              <DialogHeader>
                <DialogTitle className="text-white">Selecciona Tipo de Avatar</DialogTitle>
                <DialogDescription>
                  Elige entre avatar premium (video en tiempo real) o básico (voz TTS)
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-3 mt-4">
                {Object.entries(AVATAR_TIERS).map(([tier, info]) => (
                  <div 
                    key={tier}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      selectedTier === tier 
                        ? 'border-teal-500 bg-teal-500/10' 
                        : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                    }`}
                    onClick={() => setSelectedTier(tier)}
                  >
                    <div className="flex items-center gap-3">
                      <info.icon className={`w-5 h-5 ${info.color}`} />
                      <span className="text-white font-medium">{info.name}</span>
                      {selectedTier === tier && (
                        <CheckCircle2 className="w-4 h-4 text-teal-400 ml-auto" />
                      )}
                    </div>
                    <p className="text-slate-400 text-sm mt-1 ml-8">{info.description}</p>
                  </div>
                ))}
              </div>
              
              {selectedScenario && (
                <div className="mt-4 p-3 bg-slate-800/50 rounded-lg">
                  <p className="text-sm text-slate-400">Escenario seleccionado:</p>
                  <p className="text-white font-medium">{selectedScenario.title}</p>
                </div>
              )}
              
              <Button 
                onClick={startRoleplay}
                disabled={loading}
                className="w-full mt-4 bg-teal-500 hover:bg-teal-600"
              >
                {loading ? 'Iniciando...' : 'Comenzar Práctica'}
              </Button>
            </DialogContent>
          </Dialog>
        </div>
      </div>
    );
  }
  
  // Render preparation phase
  if (phase === 'prep') {
    return (
      <div className="min-h-screen bg-slate-950 p-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-xl font-bold text-white">Tiempo de Preparación</h1>
              <p className="text-slate-400">Lee la información del paciente y prepara tu respuesta</p>
            </div>
            <div className="text-center">
              <div className="text-4xl font-mono font-bold text-yellow-400">
                {formatTime(prepTimeLeft)}
              </div>
              <p className="text-sm text-slate-500">restantes</p>
            </div>
          </div>
          
          <Progress value={(prepTimeLeft / 180) * 100} className="mb-6 h-2" />
          
          {/* Patient Info */}
          <Card className="bg-slate-900/50 border-slate-800 mb-6">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <User className="w-5 h-5 text-blue-400" />
                Información del Paciente
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-slate-500 text-sm">Nombre</p>
                  <p className="text-white font-medium">{selectedScenario?.patient_name}</p>
                </div>
                <div>
                  <p className="text-slate-500 text-sm">Edad</p>
                  <p className="text-white font-medium">{selectedScenario?.patient_age} años</p>
                </div>
                <div>
                  <p className="text-slate-500 text-sm">Lugar</p>
                  <p className="text-white font-medium">{selectedScenario?.setting}</p>
                </div>
              </div>
              
              <div>
                <p className="text-slate-500 text-sm mb-2">Situación</p>
                <p className="text-slate-300">{selectedScenario?.situation}</p>
              </div>
            </CardContent>
          </Card>
          
          {/* Tasks */}
          <Card className="bg-slate-900/50 border-slate-800 mb-6">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                Tareas a Realizar
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {selectedScenario?.tasks?.map((task, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-slate-300">
                    <span className="text-teal-400 font-bold">{idx + 1}.</span>
                    {task}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
          
          <div className="flex gap-4">
            <Button 
              variant="outline" 
              onClick={resetPractice}
              className="border-slate-700"
            >
              Cancelar
            </Button>
            <Button 
              onClick={skipPrep}
              className="flex-1 bg-teal-500 hover:bg-teal-600"
            >
              Estoy Listo - Comenzar Speaking
            </Button>
          </div>
        </div>
      </div>
    );
  }
  
  // Render speaking phase
  if (phase === 'speaking') {
    return (
      <div className="min-h-screen bg-slate-950 p-6">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Badge className={selectedTier === 'premium' ? 'bg-yellow-500/20 text-yellow-300' : 'bg-green-500/20 text-green-300'}>
                {AVATAR_TIERS[selectedTier]?.name}
              </Badge>
              <span className="text-slate-400">{selectedScenario?.title}</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-center">
                <div className="text-2xl font-mono font-bold text-white">
                  {formatTime(speakingTimeLeft)}
                </div>
                <p className="text-xs text-slate-500">tiempo restante</p>
              </div>
              <Button variant="destructive" size="sm" onClick={endSession}>
                <Square className="w-4 h-4 mr-1" />
                Terminar
              </Button>
            </div>
          </div>
          
          <Progress value={(speakingTimeLeft / 300) * 100} className="mb-6 h-1" />
          
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Avatar Display */}
            <Card className="bg-slate-900/50 border-slate-800">
              <CardContent className="p-0">
                <div className="aspect-video bg-slate-800 rounded-t-lg flex items-center justify-center relative overflow-hidden">
                  {session?.avatar_image ? (
                    <img 
                      src={session.avatar_image} 
                      alt="Avatar"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-center">
                      <User className="w-20 h-20 text-slate-600 mx-auto mb-2" />
                      <p className="text-slate-500">{selectedScenario?.patient_name}</p>
                    </div>
                  )}
                  
                  {/* Speaking indicator */}
                  {isSpeaking && (
                    <div className="absolute bottom-4 left-4 flex items-center gap-2 bg-black/60 px-3 py-1.5 rounded-full">
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                      <span className="text-sm text-white">Hablando...</span>
                    </div>
                  )}
                </div>
                
                <div className="p-4">
                  <p className="text-white font-medium">{selectedScenario?.patient_name}</p>
                  <p className="text-slate-400 text-sm">{selectedScenario?.patient_age} años - {selectedScenario?.setting}</p>
                </div>
              </CardContent>
            </Card>
            
            {/* Conversation & Controls */}
            <div className="space-y-4">
              {/* Conversation History */}
              <Card className="bg-slate-900/50 border-slate-800 h-64 overflow-hidden">
                <CardHeader className="py-3">
                  <CardTitle className="text-white text-sm flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-blue-400" />
                    Conversación
                  </CardTitle>
                </CardHeader>
                <CardContent className="overflow-y-auto h-48 space-y-3">
                  {conversation.map((msg, idx) => (
                    <div 
                      key={idx}
                      className={`p-2 rounded-lg text-sm ${
                        msg.role === 'user' 
                          ? 'bg-teal-500/20 text-teal-100 ml-8' 
                          : 'bg-slate-800 text-slate-300 mr-8'
                      }`}
                    >
                      <p className="text-xs text-slate-500 mb-1">
                        {msg.role === 'user' ? 'Tú' : selectedScenario?.patient_name}
                      </p>
                      {msg.content}
                    </div>
                  ))}
                </CardContent>
              </Card>
              
              {/* Recording Controls */}
              <Card className="bg-slate-900/50 border-slate-800">
                <CardContent className="p-4">
                  <div className="flex items-center justify-center gap-4">
                    <Button
                      size="lg"
                      onClick={isRecording ? stopRecording : startRecording}
                      className={isRecording ? 'bg-red-500 hover:bg-red-600' : 'bg-teal-500 hover:bg-teal-600'}
                      disabled={isSpeaking || loading}
                    >
                      {isRecording ? (
                        <>
                          <MicOff className="w-5 h-5 mr-2" />
                          Detener
                        </>
                      ) : (
                        <>
                          <Mic className="w-5 h-5 mr-2" />
                          Hablar
                        </>
                      )}
                    </Button>
                    
                    {isSpeaking && (
                      <Button variant="outline" onClick={stopSpeaking}>
                        <VolumeX className="w-4 h-4 mr-2" />
                        Silenciar
                      </Button>
                    )}
                  </div>
                  
                  {isRecording && (
                    <div className="text-center mt-3">
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                        <span className="text-red-400 text-sm">Grabando...</span>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
              
              {/* Tasks Reference */}
              <Card className="bg-slate-900/50 border-slate-800">
                <CardContent className="p-4">
                  <p className="text-xs text-slate-500 mb-2">Tareas:</p>
                  <ul className="text-xs text-slate-400 space-y-1">
                    {selectedScenario?.tasks?.map((task, idx) => (
                      <li key={idx}>{idx + 1}. {task}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  // Render review phase
  if (phase === 'review') {
    return (
      <div className="min-h-screen bg-slate-950 p-6">
        <div className="max-w-3xl mx-auto text-center">
          <CheckCircle2 className="w-16 h-16 text-green-400 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-white mb-2">¡Práctica Completada!</h1>
          <p className="text-slate-400 mb-8">Has completado el roleplay de speaking</p>
          
          <Card className="bg-slate-900/50 border-slate-800 mb-6 text-left">
            <CardHeader>
              <CardTitle className="text-white">Resumen de la Conversación</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 max-h-64 overflow-y-auto">
              {conversation.map((msg, idx) => (
                <div 
                  key={idx}
                  className={`p-3 rounded-lg ${
                    msg.role === 'user' 
                      ? 'bg-teal-500/20 text-teal-100 ml-8' 
                      : 'bg-slate-800 text-slate-300 mr-8'
                  }`}
                >
                  <p className="text-xs text-slate-500 mb-1">
                    {msg.role === 'user' ? 'Tú' : 'Paciente'}
                  </p>
                  {msg.content}
                </div>
              ))}
            </CardContent>
          </Card>
          
          <div className="flex gap-4 justify-center">
            <Button variant="outline" onClick={resetPractice} className="border-slate-700">
              Nueva Práctica
            </Button>
            <Button onClick={() => navigate('/oet/nurse')} className="bg-teal-500 hover:bg-teal-600">
              Volver al Dashboard
            </Button>
          </div>
        </div>
      </div>
    );
  }
  
  return null;
}
