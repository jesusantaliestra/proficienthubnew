import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import {
  Mic,
  MicOff,
  Play,
  Pause,
  Square,
  PhoneOff,
  Volume2,
  VolumeX,
  Clock,
  User,
  Stethoscope,
  MessageSquare,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  ChevronRight,
  FileText,
  Brain,
  Sparkles,
  Video,
  VideoOff
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function OETSpeakingMock() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { rolePlayId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  // Session state
  const [sessionId, setSessionId] = useState(null);
  const [sessionStatus, setSessionStatus] = useState('idle'); // idle, preparing, active, paused, completed
  const [isConnected, setIsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  
  // Role-play data
  const [rolePlay, setRolePlay] = useState(null);
  const [prepTime, setPrepTime] = useState(180); // 3 minutes prep
  const [examTime, setExamTime] = useState(300); // 5 minutes exam
  const [currentPhase, setCurrentPhase] = useState('prep'); // prep, exam, review
  
  // Conversation state
  const [conversationHistory, setConversationHistory] = useState([]);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [avatarSpeaking, setAvatarSpeaking] = useState(false);
  const [lastAvatarResponse, setLastAvatarResponse] = useState('');
  
  // Media refs
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const wsRef = useRef(null);
  
  // Timer effect for prep phase
  useEffect(() => {
    if (currentPhase === 'prep' && prepTime > 0 && sessionStatus === 'preparing') {
      const timer = setInterval(() => {
        setPrepTime(prev => {
          if (prev <= 1) {
            setCurrentPhase('exam');
            startExamPhase();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [currentPhase, prepTime, sessionStatus]);

  // Timer effect for exam phase
  useEffect(() => {
    if (currentPhase === 'exam' && examTime > 0 && sessionStatus === 'active') {
      const timer = setInterval(() => {
        setExamTime(prev => {
          if (prev <= 1) {
            endSession();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [currentPhase, examTime, sessionStatus]);

  // Fetch role-play data
  useEffect(() => {
    fetchRolePlayData();
  }, [rolePlayId]);

  const fetchRolePlayData = async () => {
    try {
      const token = localStorage.getItem('token');
      const rpId = rolePlayId || 'S-012-B'; // Default to first role-play
      
      const response = await fetch(`${API_URL}/api/oet-speaking/role-play/${rpId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setRolePlay(data);
      } else {
        // Use mock data if API not ready
        setRolePlay({
          id: 'S-012-B',
          topic: 'Medication Change - Treatment Fatigue',
          setting: 'Diabetes Outpatient Clinic',
          patient_name: 'Mr Graham Webb',
          patient_gender: 'male',
          patient_age: 58,
          prep_time: 3,
          roleplay_time: 5,
          task: [
            'Explain why the additional medication (empagliflozin) is being recommended',
            'Explore the patient\'s feelings about his current diabetes management',
            'Address any concerns about side effects',
            'Negotiate a plan that the patient is willing to accept'
          ],
          patient_context: {
            diagnosis: 'Type 2 diabetes - 12 years',
            current_medications: 'Metformin 1g BD, Gliclazide 80mg BD',
            recent_hba1c: '72 mmol/mol (target <58)',
            bmi: 31
          },
          opening_line: "Oh, hello nurse. I suppose you're here to talk about these new tablets they want me to take. *sighs* I've just about had enough of all this, to be honest."
        });
      }
    } catch (error) {
      console.error('Error fetching role-play:', error);
      toast.error('Error al cargar el role-play');
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const startSession = async () => {
    try {
      setSessionStatus('preparing');
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/oet-speaking/session/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          role_play_id: rolePlay?.id || 'S-012-B',
          patient_gender: rolePlay?.patient_gender || 'male'
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        toast.success('Sesión iniciada. Tienes 3 minutos para prepararte.');
      } else {
        // Continue with local session for demo
        setSessionId(`local-${Date.now()}`);
        toast.success('Sesión de práctica iniciada. Tienes 3 minutos para prepararte.');
      }
    } catch (error) {
      console.error('Error starting session:', error);
      setSessionId(`local-${Date.now()}`);
      toast.info('Modo de práctica local activado');
    }
  };

  const startExamPhase = async () => {
    setSessionStatus('active');
    setCurrentPhase('exam');
    
    // Request microphone access
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorderRef.current.onstop = () => {
        processAudioChunks();
      };
      
      // Start listening automatically
      setIsListening(true);
      mediaRecorderRef.current.start(1000); // Capture in 1-second chunks
      
      // Play opening line
      if (rolePlay?.opening_line) {
        setLastAvatarResponse(rolePlay.opening_line);
        setAvatarSpeaking(true);
        setConversationHistory([{
          role: 'avatar',
          text: rolePlay.opening_line,
          timestamp: new Date().toISOString()
        }]);
        
        // Simulate avatar speaking duration
        setTimeout(() => {
          setAvatarSpeaking(false);
        }, 5000);
      }
      
      toast.success('¡El examen ha comenzado! El paciente te saluda.');
    } catch (error) {
      console.error('Microphone access error:', error);
      toast.error('No se pudo acceder al micrófono');
    }
  };

  const processAudioChunks = async () => {
    if (audioChunksRef.current.length === 0) return;
    
    const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
    audioChunksRef.current = [];
    
    // Send to backend for transcription and response
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('audio', audioBlob);
      formData.append('session_id', sessionId);
      
      const response = await fetch(`${API_URL}/api/oet-speaking/process-audio`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Add user message to history
        if (data.user_text) {
          setConversationHistory(prev => [...prev, {
            role: 'user',
            text: data.user_text,
            timestamp: new Date().toISOString()
          }]);
          setCurrentTranscript('');
        }
        
        // Add avatar response
        if (data.avatar_response) {
          setAvatarSpeaking(true);
          setLastAvatarResponse(data.avatar_response);
          setConversationHistory(prev => [...prev, {
            role: 'avatar',
            text: data.avatar_response,
            timestamp: new Date().toISOString()
          }]);
          
          // Simulate speaking duration based on text length
          const speakDuration = Math.max(3000, data.avatar_response.length * 50);
          setTimeout(() => {
            setAvatarSpeaking(false);
          }, speakDuration);
        }
      }
    } catch (error) {
      console.error('Error processing audio:', error);
    }
  };

  const toggleListening = () => {
    if (isListening) {
      mediaRecorderRef.current?.stop();
      setIsListening(false);
    } else {
      audioChunksRef.current = [];
      mediaRecorderRef.current?.start(1000);
      setIsListening(true);
    }
  };

  const endSession = async () => {
    setSessionStatus('completed');
    setCurrentPhase('review');
    
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
    
    setIsListening(false);
    
    // Save session to backend
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API_URL}/api/oet-speaking/session/${sessionId}/end`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          conversation_history: conversationHistory
        })
      });
    } catch (error) {
      console.error('Error ending session:', error);
    }
    
    toast.success('Sesión de speaking completada');
  };

  const skipPrep = () => {
    setPrepTime(0);
    setCurrentPhase('exam');
    startExamPhase();
  };

  // Render different phases
  if (!rolePlay) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400">Cargando role-play...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <header className="bg-slate-900/95 backdrop-blur-lg border-b border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-orange-500 to-amber-500 flex items-center justify-center">
                <Mic className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-sm font-bold text-white">OET Speaking Mock</h1>
                <p className="text-xs text-slate-400">{rolePlay.setting}</p>
              </div>
            </div>

            {/* Timer */}
            <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              (currentPhase === 'prep' && prepTime < 30) || (currentPhase === 'exam' && examTime < 60)
                ? 'bg-red-500/20 text-red-400' 
                : 'bg-slate-800 text-slate-300'
            }`}>
              <Clock className="w-4 h-4" />
              <span className="font-mono text-lg font-bold">
                {currentPhase === 'prep' ? formatTime(prepTime) : formatTime(examTime)}
              </span>
              <Badge className={`ml-2 ${
                currentPhase === 'prep' ? 'bg-blue-500/20 text-blue-300' :
                currentPhase === 'exam' ? 'bg-orange-500/20 text-orange-300' :
                'bg-emerald-500/20 text-emerald-300'
              }`}>
                {currentPhase === 'prep' ? 'Preparación' : currentPhase === 'exam' ? 'Examen' : 'Revisión'}
              </Badge>
            </div>

            {/* Actions */}
            <Button
              variant="ghost"
              size="sm"
              className="text-slate-400 hover:text-white"
              onClick={() => navigate('/oet/nurse')}
            >
              Salir
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Idle State - Start Session */}
        {sessionStatus === 'idle' && (
          <div className="max-w-3xl mx-auto">
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-orange-500 to-amber-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Mic className="w-10 h-10 text-white" />
                </div>
                <CardTitle className="text-white text-2xl">OET Speaking Role-Play</CardTitle>
                <CardDescription className="text-lg">{rolePlay.topic}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Patient Info */}
                <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                  <div className="flex items-center gap-3 mb-3">
                    <User className="w-5 h-5 text-orange-400" />
                    <span className="text-white font-medium">Paciente: {rolePlay.patient_name}</span>
                    <Badge className="bg-slate-700">{rolePlay.patient_age} años</Badge>
                  </div>
                  <p className="text-sm text-slate-400">Escenario: {rolePlay.setting}</p>
                </div>

                {/* Task Card */}
                <div className="p-4 bg-orange-500/10 rounded-xl border border-orange-500/30">
                  <h4 className="text-orange-300 font-semibold mb-3 flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    Tu Tarea (Candidate Card)
                  </h4>
                  <ul className="space-y-2">
                    {(rolePlay.task || []).map((item, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-slate-300">
                        <ChevronRight className="w-4 h-4 text-orange-400 mt-0.5 flex-shrink-0" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Patient Context */}
                {rolePlay.patient_context && (
                  <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                    <h4 className="text-slate-300 font-semibold mb-3 flex items-center gap-2">
                      <Stethoscope className="w-4 h-4" />
                      Notas del Paciente
                    </h4>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      {Object.entries(rolePlay.patient_context).map(([key, value]) => (
                        <div key={key}>
                          <span className="text-slate-500 capitalize">{key.replace(/_/g, ' ')}:</span>
                          <span className="text-slate-300 ml-2">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Instructions */}
                <Alert className="bg-blue-500/10 border-blue-500/30">
                  <Sparkles className="h-4 w-4 text-blue-400" />
                  <AlertTitle className="text-blue-300">Speaking Dinámico con IA</AlertTitle>
                  <AlertDescription className="text-blue-200/80">
                    El avatar actuará como el paciente. Tendrás 3 minutos de preparación y luego 5 minutos 
                    de conversación fluida. El micrófono escuchará continuamente - solo habla naturalmente.
                  </AlertDescription>
                </Alert>

                <Button 
                  size="lg" 
                  className="w-full bg-orange-500 hover:bg-orange-600 h-14 text-lg"
                  onClick={startSession}
                  data-testid="start-speaking-session"
                >
                  <Play className="w-5 h-5 mr-2" />
                  Iniciar Sesión de Speaking
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Preparation Phase */}
        {sessionStatus === 'preparing' && currentPhase === 'prep' && (
          <div className="max-w-3xl mx-auto">
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader className="text-center">
                <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30 mb-4 mx-auto">
                  <Clock className="w-3 h-3 mr-1" />
                  Tiempo de Preparación
                </Badge>
                <CardTitle className="text-white text-4xl font-mono">{formatTime(prepTime)}</CardTitle>
                <CardDescription>Lee tu tarjeta de candidato y prepara tu estrategia</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Task Card - Full View */}
                <div className="p-6 bg-orange-500/10 rounded-xl border border-orange-500/30">
                  <h4 className="text-orange-300 font-semibold mb-4 text-lg flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Candidate Card - {rolePlay.patient_name}
                  </h4>
                  <p className="text-sm text-slate-400 mb-4">Setting: {rolePlay.setting}</p>
                  <h5 className="text-white font-medium mb-2">Your Tasks:</h5>
                  <ul className="space-y-3">
                    {rolePlay.task.map((item, idx) => (
                      <li key={idx} className="flex items-start gap-3 text-slate-300">
                        <span className="w-6 h-6 bg-orange-500 rounded-full flex items-center justify-center text-white text-sm flex-shrink-0">
                          {idx + 1}
                        </span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Patient Context */}
                {rolePlay.patient_context && (
                  <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                    <h4 className="text-slate-300 font-semibold mb-3">Patient Notes:</h4>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      {Object.entries(rolePlay.patient_context).map(([key, value]) => (
                        <div key={key} className="p-2 bg-slate-800 rounded">
                          <span className="text-slate-500 capitalize block text-xs">{key.replace(/_/g, ' ')}</span>
                          <span className="text-slate-300">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex gap-3">
                  <Button 
                    variant="outline" 
                    className="flex-1 border-slate-700 text-slate-300"
                    onClick={skipPrep}
                  >
                    Saltar Preparación
                  </Button>
                  <Button 
                    className="flex-1 bg-orange-500 hover:bg-orange-600"
                    onClick={skipPrep}
                  >
                    Estoy Listo
                    <ChevronRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Active Exam Phase */}
        {sessionStatus === 'active' && currentPhase === 'exam' && (
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Avatar/Video Area */}
            <div className="lg:col-span-2">
              <Card className="bg-slate-900/50 border-slate-800">
                <CardContent className="p-0">
                  {/* Avatar Display */}
                  <div className="relative bg-gradient-to-br from-slate-800 to-slate-900 aspect-video rounded-t-xl overflow-hidden">
                    {/* Placeholder for HeyGen avatar */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <div className={`w-32 h-32 rounded-full bg-gradient-to-br ${
                          rolePlay.patient_gender === 'female' 
                            ? 'from-pink-500 to-rose-500' 
                            : 'from-blue-500 to-indigo-500'
                        } flex items-center justify-center mx-auto mb-4 ${
                          avatarSpeaking ? 'animate-pulse ring-4 ring-orange-500/50' : ''
                        }`}>
                          <User className="w-16 h-16 text-white" />
                        </div>
                        <p className="text-white font-medium">{rolePlay.patient_name}</p>
                        <p className="text-slate-400 text-sm">{rolePlay.patient_age} años • {rolePlay.setting}</p>
                        {avatarSpeaking && (
                          <Badge className="mt-2 bg-orange-500/20 text-orange-300 animate-pulse">
                            <Volume2 className="w-3 h-3 mr-1" />
                            Hablando...
                          </Badge>
                        )}
                      </div>
                    </div>
                    
                    {/* Video element for HeyGen (hidden for now) */}
                    <video 
                      ref={videoRef} 
                      autoPlay 
                      playsInline 
                      className="absolute inset-0 w-full h-full object-cover hidden"
                    />
                    
                    {/* Current response overlay */}
                    {lastAvatarResponse && (
                      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
                        <p className="text-white text-sm italic">"{lastAvatarResponse}"</p>
                      </div>
                    )}
                  </div>

                  {/* Controls */}
                  <div className="p-4 border-t border-slate-800">
                    <div className="flex items-center justify-center gap-4">
                      <Button
                        size="lg"
                        className={`w-16 h-16 rounded-full ${
                          isListening 
                            ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                            : 'bg-emerald-500 hover:bg-emerald-600'
                        }`}
                        onClick={toggleListening}
                        data-testid="mic-toggle"
                      >
                        {isListening ? (
                          <MicOff className="w-8 h-8" />
                        ) : (
                          <Mic className="w-8 h-8" />
                        )}
                      </Button>
                      
                      <Button
                        size="lg"
                        variant="destructive"
                        className="px-8"
                        onClick={endSession}
                      >
                        <Square className="w-5 h-5 mr-2" />
                        Terminar
                      </Button>
                    </div>
                    
                    <p className="text-center text-sm text-slate-400 mt-3">
                      {isListening 
                        ? '🔴 Micrófono activo - Habla con el paciente' 
                        : 'Presiona el micrófono para hablar'}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Conversation Panel */}
            <div className="lg:col-span-1">
              <Card className="bg-slate-900/50 border-slate-800 h-full">
                <CardHeader className="pb-3">
                  <CardTitle className="text-white text-sm flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-orange-400" />
                    Conversación
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 max-h-[500px] overflow-y-auto">
                  {conversationHistory.map((turn, idx) => (
                    <div 
                      key={idx}
                      className={`p-3 rounded-lg ${
                        turn.role === 'user'
                          ? 'bg-teal-500/10 border border-teal-500/30 ml-4'
                          : 'bg-orange-500/10 border border-orange-500/30 mr-4'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        {turn.role === 'user' ? (
                          <>
                            <Stethoscope className="w-3 h-3 text-teal-400" />
                            <span className="text-xs text-teal-400">Tú (Enfermero/a)</span>
                          </>
                        ) : (
                          <>
                            <User className="w-3 h-3 text-orange-400" />
                            <span className="text-xs text-orange-400">Paciente</span>
                          </>
                        )}
                      </div>
                      <p className="text-sm text-slate-300">{turn.text}</p>
                    </div>
                  ))}
                  
                  {currentTranscript && (
                    <div className="p-3 rounded-lg bg-slate-800/50 border border-slate-700 ml-4">
                      <div className="flex items-center gap-2 mb-1">
                        <Stethoscope className="w-3 h-3 text-slate-400" />
                        <span className="text-xs text-slate-400">Transcribiendo...</span>
                      </div>
                      <p className="text-sm text-slate-400 italic">{currentTranscript}</p>
                    </div>
                  )}
                  
                  {conversationHistory.length === 0 && !currentTranscript && (
                    <div className="text-center py-8 text-slate-500">
                      <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">La conversación aparecerá aquí</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Review/Completed Phase */}
        {sessionStatus === 'completed' && (
          <div className="max-w-3xl mx-auto">
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-emerald-500 to-green-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-10 h-10 text-white" />
                </div>
                <CardTitle className="text-white text-2xl">¡Sesión Completada!</CardTitle>
                <CardDescription>Has completado el role-play de speaking</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Summary Stats */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-slate-800/50 rounded-xl">
                    <div className="text-2xl font-bold text-teal-400">{conversationHistory.filter(t => t.role === 'user').length}</div>
                    <div className="text-xs text-slate-400">Tus turnos</div>
                  </div>
                  <div className="text-center p-4 bg-slate-800/50 rounded-xl">
                    <div className="text-2xl font-bold text-orange-400">{conversationHistory.filter(t => t.role === 'avatar').length}</div>
                    <div className="text-xs text-slate-400">Respuestas paciente</div>
                  </div>
                  <div className="text-center p-4 bg-slate-800/50 rounded-xl">
                    <div className="text-2xl font-bold text-purple-400">{300 - examTime}s</div>
                    <div className="text-xs text-slate-400">Duración</div>
                  </div>
                </div>

                {/* Conversation Review */}
                <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700 max-h-[300px] overflow-y-auto">
                  <h4 className="text-slate-300 font-semibold mb-3">Transcripción de la Conversación</h4>
                  {conversationHistory.map((turn, idx) => (
                    <div key={idx} className="mb-3 pb-3 border-b border-slate-700 last:border-0">
                      <span className={`text-xs font-medium ${turn.role === 'user' ? 'text-teal-400' : 'text-orange-400'}`}>
                        {turn.role === 'user' ? 'Enfermero/a:' : 'Paciente:'}
                      </span>
                      <p className="text-sm text-slate-300 mt-1">{turn.text}</p>
                    </div>
                  ))}
                </div>

                <div className="flex gap-3">
                  <Button 
                    variant="outline" 
                    className="flex-1 border-slate-700 text-slate-300"
                    onClick={() => navigate('/oet/nurse')}
                  >
                    Volver al Dashboard
                  </Button>
                  <Button 
                    className="flex-1 bg-orange-500 hover:bg-orange-600"
                    onClick={() => {
                      setSessionStatus('idle');
                      setConversationHistory([]);
                      setPrepTime(180);
                      setExamTime(300);
                      setCurrentPhase('prep');
                    }}
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Practicar de Nuevo
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}
