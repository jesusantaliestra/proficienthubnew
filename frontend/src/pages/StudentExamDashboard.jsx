import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import {
  Play, Clock, Target, Award, ChevronRight, BookOpen, Mic, PenTool,
  Brain, Download, ShoppingCart, Plus, CheckCircle, Lock, Crown, Flame,
  TrendingUp, Calendar, Star, Zap, FileText, BarChart3
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Unified exam dashboard - Academy + ProficientHub mocks as ONE premium experience
export default function StudentExamDashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [loading, setLoading] = useState(true);
  const [credits, setCredits] = useState(null);
  const [examHistory, setExamHistory] = useState([]);
  const [upsellOptions, setUpsellOptions] = useState(null);
  const [academyContent, setAcademyContent] = useState(null);
  const [showUpsell, setShowUpsell] = useState(false);
  const [startingExam, setStartingExam] = useState(false);
  const [purchasingPlan, setPurchasingPlan] = useState(null);

  const examType = user?.current_exam || 'oet';
  
  // Exam configurations
  const EXAM_CONFIG = {
    oet: { name: 'OET', color: 'emerald', icon: '⚕️', gradient: 'from-emerald-500 to-teal-600' },
    ielts: { name: 'IELTS', color: 'red', icon: '🌍', gradient: 'from-red-500 to-rose-600' },
    toefl: { name: 'TOEFL', color: 'blue', icon: '🎓', gradient: 'from-blue-500 to-indigo-600' },
    pte: { name: 'PTE', color: 'amber', icon: '💻', gradient: 'from-amber-500 to-orange-600' },
    cambridge: { name: 'Cambridge', color: 'purple', icon: '🏛️', gradient: 'from-purple-500 to-violet-600' }
  };

  const config = EXAM_CONFIG[examType] || EXAM_CONFIG.oet;

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      const [creditsRes, historyRes, upsellRes, contentRes] = await Promise.all([
        axios.get(`${API_URL}/api/exam-plans/my-credits`, { headers }).catch(() => ({ data: null })),
        axios.get(`${API_URL}/api/exam-plans/my-history?exam_type=${examType}&limit=10`, { headers }).catch(() => ({ data: { attempts: [] } })),
        axios.get(`${API_URL}/api/exam-plans/upsell-options`, { headers }).catch(() => ({ data: null })),
        axios.get(`${API_URL}/api/institution/content/${examType}`, { headers }).catch(() => ({ data: null }))
      ]);

      setCredits(creditsRes.data);
      setExamHistory(historyRes.data.attempts || []);
      setUpsellOptions(upsellRes.data);
      setAcademyContent(contentRes.data);
    } catch (err) {
      console.error('Error loading dashboard:', err);
    }
    setLoading(false);
  };

  const startMockExam = async (section = null) => {
    if (credits?.credits?.mocks?.remaining <= 0 && !section) {
      setShowUpsell(true);
      return;
    }

    setStartingExam(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/api/exam-plans/start-mock`,
        { exam_type: examType, section, timed: true },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Navigate to exam page with attempt data
      navigate(`/exam/${examType}/take`, { 
        state: { 
          attemptId: response.data.attempt_id,
          questions: response.data.questions,
          timeLimit: response.data.time_limit_seconds
        } 
      });
    } catch (err) {
      if (err.response?.status === 402) {
        setShowUpsell(true);
        toast.error('No te quedan mocks disponibles');
      } else {
        toast.error('Error al iniciar el examen');
      }
    }
    setStartingExam(false);
  };

  const downloadPDF = async (attemptId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/api/exam-plans/attempt/${attemptId}/pdf`,
        { 
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `exam_report_${attemptId.slice(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Reporte descargado');
    } catch (err) {
      toast.error('Error al descargar el reporte');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Cargando tu dashboard...</p>
        </div>
      </div>
    );
  }

  const sections = [
    { id: 'reading', name: 'Reading', icon: BookOpen, color: 'text-blue-400' },
    { id: 'writing', name: 'Writing', icon: PenTool, color: 'text-purple-400' },
    { id: 'listening', name: 'Listening', icon: '🎧', color: 'text-green-400' },
    { id: 'speaking', name: 'Speaking', icon: Mic, color: 'text-orange-400' }
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-white" data-testid="student-exam-dashboard">
      {/* Header with Credits */}
      <header className={`bg-gradient-to-r ${config.gradient} p-6`}>
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-5xl">{config.icon}</span>
              <div>
                <h1 className="text-3xl font-bold">{config.name} Preparation</h1>
                <p className="text-white/80">Tu camino hacia el éxito</p>
              </div>
            </div>
            
            {/* Credits Display */}
            <div className="flex items-center gap-4">
              <div className="bg-white/20 backdrop-blur rounded-xl p-4 text-center">
                <p className="text-white/80 text-sm">Mocks Disponibles</p>
                <p className="text-4xl font-bold">{credits?.credits?.mocks?.remaining || 0}</p>
              </div>
              <div className="bg-white/20 backdrop-blur rounded-xl p-4 text-center">
                <p className="text-white/80 text-sm">Speaking</p>
                <p className="text-4xl font-bold">{credits?.credits?.speaking?.remaining || 0}</p>
              </div>
              <div className="bg-white/20 backdrop-blur rounded-xl p-4 text-center">
                <p className="text-white/80 text-sm">Writing</p>
                <p className="text-4xl font-bold">{credits?.credits?.writing?.remaining || 0}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 space-y-8">
        {/* Main Action Card - Start Full Mock */}
        <Card className={`bg-gradient-to-br ${config.gradient} border-0 overflow-hidden`}>
          <CardContent className="p-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold mb-2">Examen Completo {config.name}</h2>
                <p className="text-white/80 mb-4">
                  Simulación real • Timer activo • Feedback instantáneo
                </p>
                <div className="flex items-center gap-4 mb-6">
                  <div className="flex items-center gap-2 text-white/90">
                    <Clock className="w-5 h-5" />
                    <span>~3 horas</span>
                  </div>
                  <div className="flex items-center gap-2 text-white/90">
                    <FileText className="w-5 h-5" />
                    <span>4 secciones</span>
                  </div>
                  <div className="flex items-center gap-2 text-white/90">
                    <Award className="w-5 h-5" />
                    <span>Reporte PDF</span>
                  </div>
                </div>
                
                <Button 
                  size="lg"
                  onClick={() => startMockExam()}
                  disabled={startingExam}
                  className="bg-white text-slate-900 hover:bg-gray-100 font-semibold px-8"
                  data-testid="start-full-mock"
                >
                  {startingExam ? (
                    <span className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-slate-900 border-t-transparent rounded-full animate-spin" />
                      Iniciando...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <Play className="w-5 h-5" />
                      Comenzar Examen Completo
                      {credits?.credits?.mocks?.remaining > 0 && (
                        <Badge className="bg-slate-900 text-white ml-2">
                          -1 Mock
                        </Badge>
                      )}
                    </span>
                  )}
                </Button>

                {credits?.credits?.mocks?.remaining <= 2 && credits?.credits?.mocks?.remaining > 0 && (
                  <p className="text-yellow-200 text-sm mt-3 flex items-center gap-2">
                    <Zap className="w-4 h-4" />
                    Te quedan solo {credits.credits.mocks.remaining} mocks
                  </p>
                )}
              </div>
              
              <div className="hidden lg:block">
                <div className="w-48 h-48 bg-white/10 rounded-full flex items-center justify-center backdrop-blur">
                  <span className="text-8xl">{config.icon}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Section Practice - FREE */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-white">Práctica por Sección</h3>
            <Badge variant="outline" className="border-green-500 text-green-400">
              <CheckCircle className="w-3 h-3 mr-1" /> Práctica Gratuita
            </Badge>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {sections.map((section) => (
              <Card 
                key={section.id}
                className="bg-slate-900/80 border-slate-800 hover:border-slate-600 cursor-pointer transition-all hover:scale-[1.02]"
                onClick={() => startMockExam(section.id)}
              >
                <CardContent className="p-6">
                  <div className="flex items-center gap-4">
                    <div className={`w-14 h-14 rounded-xl bg-slate-800 flex items-center justify-center text-2xl`}>
                      {typeof section.icon === 'string' ? section.icon : <section.icon className={`w-7 h-7 ${section.color}`} />}
                    </div>
                    <div>
                      <h4 className="font-bold text-white text-lg">{section.name}</h4>
                      <p className="text-slate-400 text-sm">Practica sin límite</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* AI Tutor & Resources */}
        <div className="grid lg:grid-cols-2 gap-6">
          <Card className="bg-gradient-to-br from-violet-900/50 to-purple-900/50 border-violet-700/50">
            <CardContent className="p-6">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-14 h-14 rounded-xl bg-violet-600/30 flex items-center justify-center">
                  <Brain className="w-8 h-8 text-violet-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">AI Tutor Personal</h3>
                  <p className="text-violet-300">Resuelve tus dudas 24/7</p>
                </div>
              </div>
              <p className="text-slate-300 mb-4">
                Tu tutor especializado en {config.name} te ayuda con cualquier pregunta, 
                explica conceptos y te da feedback personalizado.
              </p>
              <Button 
                className="w-full bg-violet-600 hover:bg-violet-700"
                onClick={() => navigate(`/tutor?exam=${examType}`)}
              >
                <Brain className="w-4 h-4 mr-2" />
                Hablar con AI Tutor
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-900/50 to-cyan-900/50 border-blue-700/50">
            <CardContent className="p-6">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-14 h-14 rounded-xl bg-blue-600/30 flex items-center justify-center">
                  <BookOpen className="w-8 h-8 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Material de Estudio</h3>
                  <p className="text-blue-300">Recursos exclusivos</p>
                </div>
              </div>
              <p className="text-slate-300 mb-4">
                Accede a guías, videos, flashcards y material de preparación 
                específico para tu examen.
              </p>
              <Button 
                className="w-full bg-blue-600 hover:bg-blue-700"
                onClick={() => navigate(`/resources/${examType}`)}
              >
                <BookOpen className="w-4 h-4 mr-2" />
                Ver Material
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Exam History with PDF Downloads */}
        <Card className="bg-slate-900/80 border-slate-800">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-white flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-emerald-400" />
                Historial de Exámenes
              </CardTitle>
              <Button variant="ghost" size="sm" onClick={() => navigate('/exam-history')}>
                Ver todo <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {examHistory.length === 0 ? (
              <div className="text-center py-8">
                <Target className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">Aún no has completado ningún examen</p>
                <Button 
                  className="mt-4"
                  onClick={() => startMockExam()}
                >
                  Comenzar tu primer mock
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {examHistory.map((attempt) => (
                  <div 
                    key={attempt.id}
                    className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${config.gradient} flex items-center justify-center`}>
                        <span className="text-2xl">{config.icon}</span>
                      </div>
                      <div>
                        <p className="font-medium text-white">
                          {attempt.is_full_mock ? 'Examen Completo' : `Práctica: ${attempt.section}`}
                        </p>
                        <p className="text-sm text-slate-400">
                          {new Date(attempt.completed_at).toLocaleDateString('es', { 
                            day: 'numeric', 
                            month: 'short', 
                            year: 'numeric' 
                          })}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className={`text-2xl font-bold ${
                          attempt.score >= 70 ? 'text-green-400' : 
                          attempt.score >= 50 ? 'text-yellow-400' : 'text-red-400'
                        }`}>
                          {attempt.score}%
                        </p>
                        <p className="text-xs text-slate-500">
                          {Math.floor(attempt.time_taken_seconds / 60)} min
                        </p>
                      </div>
                      
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => downloadPDF(attempt.id)}
                        className="text-emerald-400 hover:text-emerald-300"
                        data-testid={`download-pdf-${attempt.id}`}
                      >
                        <Download className="w-4 h-4 mr-1" />
                        PDF
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Performance Chart */}
        {examHistory.length >= 2 && (
          <Card className="bg-slate-900/80 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-emerald-400" />
                Tu Progreso
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={examHistory.slice().reverse()}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis 
                      dataKey="completed_at" 
                      stroke="#64748b"
                      tickFormatter={(value) => new Date(value).toLocaleDateString('es', { day: 'numeric', month: 'short' })}
                    />
                    <YAxis stroke="#64748b" domain={[0, 100]} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                      labelStyle={{ color: '#94a3b8' }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="score" 
                      name="Puntuación"
                      stroke="#10b981" 
                      strokeWidth={3}
                      dot={{ fill: '#10b981', strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}
      </main>

      {/* Upsell Modal */}
      <Dialog open={showUpsell} onOpenChange={setShowUpsell}>
        <DialogContent className="bg-slate-900 border-slate-700 text-white max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-2xl flex items-center gap-3">
              <ShoppingCart className="w-6 h-6 text-emerald-400" />
              Necesitas más mocks
            </DialogTitle>
          </DialogHeader>
          
          <div className="py-4">
            <p className="text-slate-300 mb-6">
              Has utilizado todos tus exámenes de práctica. ¡Adquiere más para seguir preparándote!
            </p>
            
            <div className="grid gap-4">
              {upsellOptions?.available_plans?.slice(0, 3).map((plan) => (
                <div 
                  key={plan.id}
                  className="flex items-center justify-between p-4 bg-slate-800 rounded-lg border border-slate-700 hover:border-emerald-500/50 transition-colors cursor-pointer"
                >
                  <div>
                    <h4 className="font-bold text-white">{plan.name}</h4>
                    <p className="text-sm text-slate-400">
                      {plan.mock_count} mocks
                      {plan.speaking_sessions > 0 && ` + ${plan.speaking_sessions} speaking`}
                      {plan.writing_evaluations > 0 && ` + ${plan.writing_evaluations} writing`}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-emerald-400">${plan.price}</p>
                    <Button size="sm" className="mt-2 bg-emerald-600 hover:bg-emerald-700">
                      Comprar
                    </Button>
                  </div>
                </div>
              ))}
              
              {/* Quick buy options */}
              <div className="border-t border-slate-700 pt-4 mt-2">
                <p className="text-sm text-slate-400 mb-3">Compra rápida:</p>
                <div className="flex gap-3">
                  {upsellOptions?.quick_buys?.map((item) => (
                    <Button 
                      key={item.type}
                      variant="outline" 
                      className="border-slate-600 text-slate-300 hover:bg-slate-800"
                    >
                      <Plus className="w-4 h-4 mr-1" />
                      {item.name} - ${item.price}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
