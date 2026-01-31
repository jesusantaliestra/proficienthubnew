import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import LanguageSelector from '../components/LanguageSelector';
import {
  Stethoscope,
  BookOpen,
  Headphones,
  FileText,
  Mic,
  Play,
  Clock,
  Target,
  Award,
  TrendingUp,
  Calendar,
  CheckCircle,
  Lock,
  ArrowRight,
  Home,
  LogOut,
  User,
  Settings,
  ChevronRight,
  Brain,
  MessageSquare,
  Star,
  Sparkles,
  GraduationCap,
  Heart,
  Activity,
  Eye,
  Pill,
  Syringe,
  Baby,
  Bone,
  TestTube,
  Radio,
  Ambulance
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// OET Professions configuration
const OET_PROFESSIONS = {
  nursing: {
    name: 'Nursing',
    nameEs: 'Enfermería',
    icon: Stethoscope,
    color: 'from-teal-500 to-emerald-500',
    bgColor: 'bg-teal-500/10',
    borderColor: 'border-teal-500/30',
    description: 'For registered nurses and nursing professionals'
  },
  medicine: {
    name: 'Medicine',
    nameEs: 'Medicina',
    icon: Activity,
    color: 'from-blue-500 to-indigo-500',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    description: 'For doctors and medical practitioners'
  },
  dentistry: {
    name: 'Dentistry',
    nameEs: 'Odontología',
    icon: Stethoscope,
    color: 'from-cyan-500 to-blue-500',
    bgColor: 'bg-cyan-500/10',
    borderColor: 'border-cyan-500/30',
    description: 'For dentists and dental professionals'
  },
  pharmacy: {
    name: 'Pharmacy',
    nameEs: 'Farmacia',
    icon: Pill,
    color: 'from-purple-500 to-violet-500',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30',
    description: 'For pharmacists'
  },
  physiotherapy: {
    name: 'Physiotherapy',
    nameEs: 'Fisioterapia',
    icon: Activity,
    color: 'from-orange-500 to-red-500',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/30',
    description: 'For physiotherapists'
  },
  radiography: {
    name: 'Radiography',
    nameEs: 'Radiografía',
    icon: Radio,
    color: 'from-slate-500 to-zinc-500',
    bgColor: 'bg-slate-500/10',
    borderColor: 'border-slate-500/30',
    description: 'For radiographers and imaging specialists'
  },
  optometry: {
    name: 'Optometry',
    nameEs: 'Optometría',
    icon: Eye,
    color: 'from-amber-500 to-yellow-500',
    bgColor: 'bg-amber-500/10',
    borderColor: 'border-amber-500/30',
    description: 'For optometrists'
  },
  dietetics: {
    name: 'Dietetics',
    nameEs: 'Dietética',
    icon: Heart,
    color: 'from-green-500 to-lime-500',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    description: 'For dietitians and nutritionists'
  },
  occupational_therapy: {
    name: 'Occupational Therapy',
    nameEs: 'Terapia Ocupacional',
    icon: Brain,
    color: 'from-pink-500 to-rose-500',
    bgColor: 'bg-pink-500/10',
    borderColor: 'border-pink-500/30',
    description: 'For occupational therapists'
  },
  speech_pathology: {
    name: 'Speech Pathology',
    nameEs: 'Logopedia',
    icon: MessageSquare,
    color: 'from-fuchsia-500 to-pink-500',
    bgColor: 'bg-fuchsia-500/10',
    borderColor: 'border-fuchsia-500/30',
    description: 'For speech pathologists'
  },
  veterinary_science: {
    name: 'Veterinary Science',
    nameEs: 'Veterinaria',
    icon: Heart,
    color: 'from-emerald-500 to-teal-500',
    bgColor: 'bg-emerald-500/10',
    borderColor: 'border-emerald-500/30',
    description: 'For veterinarians'
  },
  podiatry: {
    name: 'Podiatry',
    nameEs: 'Podología',
    icon: Bone,
    color: 'from-red-500 to-orange-500',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    description: 'For podiatrists'
  }
};

export default function OETProfessionDashboard() {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const { profession } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Get profession config
  const professionKey = profession || 'nursing';
  const professionConfig = OET_PROFESSIONS[professionKey] || OET_PROFESSIONS.nursing;
  const ProfessionIcon = professionConfig.icon;

  useEffect(() => {
    // Simulate loading
    setTimeout(() => setLoading(false), 500);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const startMockExam = (mockId, mode = 'full') => {
    toast.success('Iniciando examen...');
    navigate(`/oet/mock/${mockId}?mode=${mode}&profession=${professionKey}`);
  };

  // OET Exam Structure (same for all professions)
  const examSections = [
    {
      id: 'listening',
      name: 'Listening',
      nameEs: 'Comprensión Auditiva',
      icon: Headphones,
      duration: '50 min',
      questions: 42,
      parts: [
        { name: 'Part A', desc: 'Consultation Extracts', questions: 24 },
        { name: 'Part B', desc: 'Workplace Extracts', questions: 6 },
        { name: 'Part C', desc: 'Presentations/Interviews', questions: 12 }
      ],
      color: 'from-blue-500 to-cyan-500',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/30'
    },
    {
      id: 'reading',
      name: 'Reading',
      nameEs: 'Comprensión Lectora',
      icon: BookOpen,
      duration: '60 min',
      questions: 42,
      parts: [
        { name: 'Part A', desc: 'Expeditious Reading', questions: 20 },
        { name: 'Part B', desc: 'Short Workplace Texts', questions: 6 },
        { name: 'Part C', desc: 'Long Texts', questions: 16 }
      ],
      color: 'from-emerald-500 to-green-500',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/30'
    },
    {
      id: 'writing',
      name: 'Writing',
      nameEs: 'Expresión Escrita',
      icon: FileText,
      duration: '45 min',
      questions: 1,
      parts: [
        { name: 'Letter', desc: 'Professional Letter (180-200 words)', questions: 1 }
      ],
      color: 'from-purple-500 to-violet-500',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/30'
    },
    {
      id: 'speaking',
      name: 'Speaking',
      nameEs: 'Expresión Oral',
      icon: Mic,
      duration: '20 min',
      questions: 2,
      parts: [
        { name: 'Role-Play 1', desc: '3 min prep + 5 min', questions: 1 },
        { name: 'Role-Play 2', desc: '3 min prep + 5 min', questions: 1 }
      ],
      color: 'from-orange-500 to-amber-500',
      bgColor: 'bg-orange-500/10',
      borderColor: 'border-orange-500/30',
      dynamic: true
    }
  ];

  // Available mocks for this profession (in reality, would be fetched from API)
  const availableMocks = [
    {
      id: `${professionKey.toUpperCase().slice(0,3)}-001`,
      name: `OET ${professionConfig.name} Mock 001`,
      version: '1.0',
      status: 'available',
      difficulty: 'Standard',
      description: `Complete OET mock exam for ${professionConfig.name.toLowerCase()} professionals`
    },
    {
      id: `${professionKey.toUpperCase().slice(0,3)}-002`,
      name: `OET ${professionConfig.name} Mock 002`,
      version: '1.0',
      status: 'locked',
      difficulty: 'Standard',
      description: 'Additional practice exam'
    },
    {
      id: `${professionKey.toUpperCase().slice(0,3)}-003`,
      name: `OET ${professionConfig.name} Mock 003`,
      version: '1.0',
      status: 'locked',
      difficulty: 'Advanced',
      description: 'Challenging practice exam'
    }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className={`w-16 h-16 border-4 border-t-transparent rounded-full animate-spin mx-auto mb-4`} 
               style={{ borderColor: `var(--${professionConfig.color.split('-')[1]}-500)` }}></div>
          <p className="text-slate-400">Cargando dashboard OET {professionConfig.name}...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur-lg border-b border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo & Title */}
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 bg-gradient-to-br ${professionConfig.color} rounded-xl flex items-center justify-center`}>
                <ProfessionIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">OET {professionConfig.name}</h1>
                <p className="text-xs text-slate-400">{professionConfig.nameEs}</p>
              </div>
            </div>

            {/* User Menu */}
            <div className="flex items-center gap-4">
              <LanguageSelector variant="compact" />
              <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 rounded-lg">
                <User className="w-4 h-4 text-teal-400" />
                <span className="text-sm text-slate-300">{user?.name || user?.email}</span>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={handleLogout}
                className="text-slate-400 hover:text-white"
              >
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Banner */}
        <div className={`mb-8 bg-gradient-to-r ${professionConfig.bgColor} rounded-2xl p-6 border ${professionConfig.borderColor}`}>
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Badge className={`${professionConfig.bgColor} ${professionConfig.borderColor}`}>
                  <GraduationCap className="w-3 h-3 mr-1" />
                  OET {professionConfig.name}
                </Badge>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">
                ¡Bienvenido/a a tu preparación OET!
              </h2>
              <p className="text-slate-300 max-w-2xl">
                Prepárate para el OET (Occupational English Test) para {professionConfig.nameEs} con exámenes 
                simulados completos, práctica de speaking dinámico con IA, y retroalimentación instantánea.
              </p>
            </div>
            <div className="hidden md:block">
              <div className={`w-24 h-24 bg-gradient-to-br ${professionConfig.color} rounded-2xl flex items-center justify-center`}>
                <ProfessionIcon className="w-12 h-12 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Profession Selector */}
        <div className="mb-6">
          <p className="text-sm text-slate-400 mb-2">Seleccionar otra profesión:</p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(OET_PROFESSIONS).map(([key, config]) => {
              const Icon = config.icon;
              return (
                <Button
                  key={key}
                  variant={key === professionKey ? 'default' : 'outline'}
                  size="sm"
                  className={key === professionKey 
                    ? `bg-gradient-to-r ${config.color} text-white border-0`
                    : 'border-slate-700 text-slate-400 hover:text-white'}
                  onClick={() => navigate(`/oet/${key}`)}
                >
                  <Icon className="w-3 h-3 mr-1" />
                  {config.name}
                </Button>
              );
            })}
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-slate-900 border border-slate-800 p-1">
            <TabsTrigger value="overview" className={`data-[state=active]:bg-gradient-to-r data-[state=active]:${professionConfig.color} data-[state=active]:text-white`}>
              <Home className="w-4 h-4 mr-2" />
              Resumen
            </TabsTrigger>
            <TabsTrigger value="mocks" className={`data-[state=active]:bg-gradient-to-r data-[state=active]:${professionConfig.color} data-[state=active]:text-white`}>
              <Target className="w-4 h-4 mr-2" />
              Mock Exams
            </TabsTrigger>
            <TabsTrigger value="practice" className={`data-[state=active]:bg-gradient-to-r data-[state=active]:${professionConfig.color} data-[state=active]:text-white`}>
              <BookOpen className="w-4 h-4 mr-2" />
              Práctica
            </TabsTrigger>
            <TabsTrigger value="progress" className={`data-[state=active]:bg-gradient-to-r data-[state=active]:${professionConfig.color} data-[state=active]:text-white`}>
              <TrendingUp className="w-4 h-4 mr-2" />
              Progreso
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Exam Structure */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-slate-400" />
                Estructura del Examen OET
              </h3>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                {examSections.map((section) => (
                  <Card 
                    key={section.id} 
                    className={`bg-slate-900/50 border ${section.borderColor} hover:border-opacity-100 transition-all cursor-pointer group`}
                  >
                    <CardContent className="p-5">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${section.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                        <section.icon className="w-6 h-6 text-white" />
                      </div>
                      <h4 className="text-white font-semibold mb-1">{section.name}</h4>
                      <p className="text-sm text-slate-400 mb-3">{section.nameEs}</p>
                      
                      <div className="flex items-center gap-4 text-xs text-slate-500 mb-3">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {section.duration}
                        </span>
                        <span>{section.questions} preguntas</span>
                      </div>

                      {section.dynamic && (
                        <Badge className="bg-orange-500/20 text-orange-300 border-orange-500/30 text-xs">
                          <Sparkles className="w-3 h-3 mr-1" />
                          IA Dinámica
                        </Badge>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="grid md:grid-cols-3 gap-4">
              <Card className={`bg-gradient-to-br ${professionConfig.bgColor} ${professionConfig.borderColor} hover:border-opacity-100 transition-all cursor-pointer group`}
                    onClick={() => setActiveTab('mocks')}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-white font-semibold mb-1">Iniciar Mock Exam</h4>
                      <p className="text-sm text-slate-400">Examen completo simulado</p>
                    </div>
                    <div className={`w-12 h-12 bg-gradient-to-br ${professionConfig.color} rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform`}>
                      <Play className="w-6 h-6 text-white" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-orange-900/50 to-amber-900/50 border-orange-500/30 hover:border-orange-500/50 transition-all cursor-pointer group"
                    onClick={() => navigate('/oet/speaking-practice')}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-white font-semibold mb-1">Speaking Dinámico</h4>
                      <p className="text-sm text-slate-400">Práctica con avatar IA</p>
                    </div>
                    <div className="w-12 h-12 bg-orange-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Mic className="w-6 h-6 text-white" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-purple-900/50 to-violet-900/50 border-purple-500/30 hover:border-purple-500/50 transition-all cursor-pointer group"
                    onClick={() => navigate('/tutor/oet')}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-white font-semibold mb-1">AI Tutor</h4>
                      <p className="text-sm text-slate-400">Asistencia personalizada</p>
                    </div>
                    <div className="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Brain className="w-6 h-6 text-white" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Mock Exams Tab */}
          <TabsContent value="mocks" className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-slate-400" />
                Exámenes Mock Disponibles - {professionConfig.name}
              </h3>
            </div>

            <div className="grid gap-4">
              {availableMocks.map((mock) => (
                <Card 
                  key={mock.id}
                  className={`bg-slate-900/50 border ${
                    mock.status === 'available' 
                      ? `${professionConfig.borderColor} hover:border-opacity-100` 
                      : 'border-slate-700 opacity-60'
                  } transition-all`}
                >
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`w-14 h-14 rounded-xl flex items-center justify-center ${
                          mock.status === 'available'
                            ? `bg-gradient-to-br ${professionConfig.color}`
                            : 'bg-slate-700'
                        }`}>
                          {mock.status === 'available' ? (
                            <FileText className="w-7 h-7 text-white" />
                          ) : (
                            <Lock className="w-7 h-7 text-slate-500" />
                          )}
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="text-white font-semibold">{mock.name}</h4>
                            <Badge variant="outline" className="text-xs">v{mock.version}</Badge>
                          </div>
                          <p className="text-sm text-slate-400">{mock.description}</p>
                          <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              ~175 min total
                            </span>
                            <span>4 secciones</span>
                            <Badge className={mock.difficulty === 'Advanced' ? 'bg-orange-500/20 text-orange-300' : 'bg-slate-700 text-slate-300'}>
                              {mock.difficulty}
                            </Badge>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        {mock.status === 'available' ? (
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button className={`bg-gradient-to-r ${professionConfig.color} text-white`}>
                                <Play className="w-4 h-4 mr-2" />
                                Iniciar Examen
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="bg-slate-900 border-slate-700">
                              <DialogHeader>
                                <DialogTitle className="text-white">Iniciar {mock.name}</DialogTitle>
                                <DialogDescription className="text-slate-400">
                                  Elige cómo quieres realizar el examen
                                </DialogDescription>
                              </DialogHeader>
                              <div className="space-y-4 mt-4">
                                <Button 
                                  className={`w-full bg-gradient-to-r ${professionConfig.color} h-auto py-4`}
                                  onClick={() => startMockExam(mock.id, 'full')}
                                >
                                  <div className="text-left">
                                    <div className="font-semibold">Examen Completo</div>
                                    <div className="text-xs opacity-80">Las 4 secciones en orden (~175 min)</div>
                                  </div>
                                </Button>
                                <Button 
                                  variant="outline" 
                                  className="w-full h-auto py-4 border-slate-600 text-slate-300 hover:bg-slate-800"
                                  onClick={() => startMockExam(mock.id, 'section')}
                                >
                                  <div className="text-left">
                                    <div className="font-semibold">Por Secciones</div>
                                    <div className="text-xs opacity-80">Completa cada sección a tu ritmo</div>
                                  </div>
                                </Button>
                              </div>
                            </DialogContent>
                          </Dialog>
                        ) : (
                          <Button disabled variant="outline" className="border-slate-700 text-slate-500">
                            <Lock className="w-4 h-4 mr-2" />
                            Bloqueado
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Practice Tab */}
          <TabsContent value="practice" className="space-y-6">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-slate-400" />
              Práctica por Sección - {professionConfig.name}
            </h3>

            <div className="grid md:grid-cols-2 gap-4">
              {examSections.map((section) => (
                <Card 
                  key={section.id}
                  className={`bg-slate-900/50 border ${section.borderColor} hover:border-opacity-100 transition-all cursor-pointer`}
                  onClick={() => navigate(`/oet/practice/${section.id}?profession=${professionKey}`)}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${section.color} flex items-center justify-center flex-shrink-0`}>
                        <section.icon className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <h4 className="text-white font-semibold mb-1">{section.name}</h4>
                        <p className="text-sm text-slate-400 mb-3">{section.nameEs}</p>
                        
                        <div className="space-y-2">
                          {section.parts.map((part, idx) => (
                            <div 
                              key={idx} 
                              className="flex items-center justify-between p-2 rounded bg-slate-800/50 hover:bg-slate-800 transition-colors"
                            >
                              <div>
                                <span className="text-sm text-slate-300">{part.name}</span>
                                <span className="text-xs text-slate-500 ml-2">- {part.desc}</span>
                              </div>
                              <ChevronRight className="w-4 h-4 text-slate-500" />
                            </div>
                          ))}
                        </div>

                        {section.dynamic && (
                          <div className="mt-3 p-2 rounded bg-orange-500/10 border border-orange-500/20">
                            <div className="flex items-center gap-2 text-orange-300 text-xs">
                              <Sparkles className="w-3 h-3" />
                              Speaking dinámico con avatar IA
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Progress Tab */}
          <TabsContent value="progress" className="space-y-6">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-slate-400" />
              Tu Progreso - {professionConfig.name}
            </h3>

            {/* Overall Progress */}
            <Card className="bg-slate-900/50 border-slate-800">
              <CardContent className="p-6">
                <div className="grid md:grid-cols-4 gap-6">
                  <div className="text-center p-4 rounded-xl bg-slate-800/50">
                    <div className={`text-3xl font-bold mb-1`} style={{ color: `var(--${professionConfig.color.split('-')[1]}-400)` }}>0</div>
                    <div className="text-sm text-slate-400">Mocks Completados</div>
                  </div>
                  <div className="text-center p-4 rounded-xl bg-slate-800/50">
                    <div className="text-3xl font-bold text-emerald-400 mb-1">-</div>
                    <div className="text-sm text-slate-400">Banda Promedio</div>
                  </div>
                  <div className="text-center p-4 rounded-xl bg-slate-800/50">
                    <div className="text-3xl font-bold text-blue-400 mb-1">0h</div>
                    <div className="text-sm text-slate-400">Tiempo de Estudio</div>
                  </div>
                  <div className="text-center p-4 rounded-xl bg-slate-800/50">
                    <div className="text-3xl font-bold text-purple-400 mb-1">0</div>
                    <div className="text-sm text-slate-400">Prácticas Speaking</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Empty State */}
            <Card className="bg-slate-900/50 border-slate-800 border-dashed">
              <CardContent className="p-12 text-center">
                <div className={`w-16 h-16 bg-gradient-to-br ${professionConfig.color} rounded-full flex items-center justify-center mx-auto mb-4 opacity-50`}>
                  <Target className="w-8 h-8 text-white" />
                </div>
                <h4 className="text-white font-semibold mb-2">¡Comienza tu preparación!</h4>
                <p className="text-slate-400 text-sm mb-4 max-w-md mx-auto">
                  Completa tu primer mock exam de {professionConfig.name} para ver tu progreso y obtener recomendaciones personalizadas.
                </p>
                <Button 
                  className={`bg-gradient-to-r ${professionConfig.color}`}
                  onClick={() => setActiveTab('mocks')}
                >
                  <Play className="w-4 h-4 mr-2" />
                  Iniciar Mock Exam
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
