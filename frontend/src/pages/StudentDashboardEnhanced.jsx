import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  BookOpen,
  Clock,
  Award,
  TrendingUp,
  Calendar,
  Target,
  Mic,
  PenTool,
  Sparkles,
  Package,
  Play,
  ChevronRight,
  BarChart3,
  CheckCircle2,
  AlertCircle,
  Loader2,
  GraduationCap,
  Brain,
  FileText,
  ClipboardList
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function StudentDashboardEnhanced() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [packAccess, setPackAccess] = useState([]);
  const [studyPlans, setStudyPlans] = useState([]);
  const [placementResults, setPlacementResults] = useState([]);
  const [stats, setStats] = useState({
    mocksCompleted: 0,
    mocksRemaining: 0,
    speakingSessions: 0,
    aiTutorMinutes: 0,
    averageScore: 0
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };

      // Fetch all data in parallel
      const [accessRes, plansRes, placementRes] = await Promise.all([
        fetch(`${API_URL}/api/institution-packs/student-access`, { headers }),
        fetch(`${API_URL}/api/agent-planner/my-plans`, { headers }),
        fetch(`${API_URL}/api/placement-test/my-results`, { headers })
      ]);

      if (accessRes.ok) {
        const data = await accessRes.json();
        setPackAccess(data.access || []);
        
        // Calculate stats from pack access
        const totalMocks = data.access?.reduce((sum, a) => sum + (a.mocks_total || 0), 0) || 0;
        const remainingMocks = data.access?.reduce((sum, a) => sum + (a.mocks_remaining || 0), 0) || 0;
        const speakingSessions = data.access?.reduce((sum, a) => sum + (a.speaking_sessions_remaining || 0), 0) || 0;
        const aiMinutes = data.access?.reduce((sum, a) => sum + (a.ai_tutor_minutes_remaining || 0), 0) || 0;
        
        setStats(prev => ({
          ...prev,
          mocksCompleted: totalMocks - remainingMocks,
          mocksRemaining: remainingMocks,
          speakingSessions,
          aiTutorMinutes: aiMinutes
        }));
      }

      if (plansRes.ok) {
        const data = await plansRes.json();
        setStudyPlans(data.plans || []);
      }

      if (placementRes.ok) {
        const data = await placementRes.json();
        setPlacementResults(data.results || []);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getExpiryStatus = (expiresAt) => {
    const now = new Date();
    const expiry = new Date(expiresAt);
    const daysLeft = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));
    
    if (daysLeft <= 0) return { status: 'expired', text: 'Expirado', color: 'text-red-400' };
    if (daysLeft <= 7) return { status: 'warning', text: `${daysLeft} días`, color: 'text-orange-400' };
    return { status: 'ok', text: `${daysLeft} días`, color: 'text-green-400' };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-teal-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white mb-2">
            ¡Hola, {user?.name || 'Estudiante'}! 👋
          </h1>
          <p className="text-slate-400">
            Aquí tienes un resumen de tu progreso y recursos disponibles
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard
            icon={BookOpen}
            label="Mocks Disponibles"
            value={stats.mocksRemaining}
            color="text-blue-400"
            bgColor="bg-blue-500/20"
          />
          <StatCard
            icon={Mic}
            label="Sesiones Speaking"
            value={stats.speakingSessions === -1 ? '∞' : stats.speakingSessions}
            color="text-green-400"
            bgColor="bg-green-500/20"
          />
          <StatCard
            icon={Sparkles}
            label="Minutos AI Tutor"
            value={stats.aiTutorMinutes === -1 ? '∞' : stats.aiTutorMinutes}
            color="text-purple-400"
            bgColor="bg-purple-500/20"
          />
          <StatCard
            icon={Award}
            label="Mocks Completados"
            value={stats.mocksCompleted}
            color="text-orange-400"
            bgColor="bg-orange-500/20"
          />
        </div>

        {/* Main Content */}
        <Tabs defaultValue="packs" className="space-y-6">
          <TabsList className="bg-slate-800/50 border border-slate-700">
            <TabsTrigger value="packs" className="data-[state=active]:bg-teal-500">
              <Package className="w-4 h-4 mr-2" />
              Mis Packs
            </TabsTrigger>
            <TabsTrigger value="plans" className="data-[state=active]:bg-teal-500">
              <Calendar className="w-4 h-4 mr-2" />
              Plan de Estudio
            </TabsTrigger>
            <TabsTrigger value="placement" className="data-[state=active]:bg-teal-500">
              <ClipboardList className="w-4 h-4 mr-2" />
              Test de Nivel
            </TabsTrigger>
          </TabsList>

          {/* My Packs Tab */}
          <TabsContent value="packs" className="space-y-4">
            {packAccess.length === 0 ? (
              <Card className="bg-slate-900/50 border-slate-800">
                <CardContent className="py-12 text-center">
                  <Package className="w-16 h-16 mx-auto mb-4 text-slate-600" />
                  <h3 className="text-xl font-semibold text-white mb-2">
                    No tienes packs activos
                  </h3>
                  <p className="text-slate-400 mb-6 max-w-md mx-auto">
                    Explora nuestra tienda para encontrar el pack perfecto para tu preparación.
                  </p>
                  <Button 
                    onClick={() => navigate('/store')}
                    className="bg-teal-500 hover:bg-teal-600"
                  >
                    Ver Tienda de Packs
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid md:grid-cols-2 gap-4">
                {packAccess.map((access) => (
                  <PackAccessCard 
                    key={access.id} 
                    access={access}
                    onStartExam={() => navigate(`/oet/${access.profession || 'nurse'}`)}
                    onStartSpeaking={() => navigate('/oet/speaking-practice')}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          {/* Study Plans Tab */}
          <TabsContent value="plans" className="space-y-4">
            {studyPlans.length === 0 ? (
              <Card className="bg-slate-900/50 border-slate-800">
                <CardContent className="py-12 text-center">
                  <Calendar className="w-16 h-16 mx-auto mb-4 text-slate-600" />
                  <h3 className="text-xl font-semibold text-white mb-2">
                    Sin plan de estudio
                  </h3>
                  <p className="text-slate-400 mb-6 max-w-md mx-auto">
                    Crea un plan personalizado basado en tu fecha de examen y nivel actual.
                  </p>
                  <Button 
                    onClick={() => navigate('/student/create-plan')}
                    className="bg-teal-500 hover:bg-teal-600"
                  >
                    <Brain className="w-4 h-4 mr-2" />
                    Crear Plan con IA
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {studyPlans.map((plan) => (
                  <StudyPlanCard key={plan.id} plan={plan} />
                ))}
              </div>
            )}
          </TabsContent>

          {/* Placement Test Tab */}
          <TabsContent value="placement" className="space-y-4">
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <ClipboardList className="w-5 h-5 text-teal-400" />
                  Test de Nivel
                </CardTitle>
                <CardDescription>
                  Evalúa tu nivel actual de inglés para personalizar tu preparación
                </CardDescription>
              </CardHeader>
              <CardContent>
                {placementResults.length === 0 ? (
                  <div className="text-center py-6">
                    <p className="text-slate-400 mb-4">
                      Aún no has realizado el test de nivel
                    </p>
                    <Button 
                      onClick={() => navigate('/student/placement-test')}
                      className="bg-teal-500 hover:bg-teal-600"
                    >
                      <Play className="w-4 h-4 mr-2" />
                      Comenzar Test
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {placementResults.map((result) => (
                      <div 
                        key={result.id}
                        className="p-4 bg-slate-800/50 rounded-lg"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-white font-medium">{result.exam_type}</span>
                          <Badge className="bg-teal-500/20 text-teal-300">
                            Nivel: {result.results?.estimated_level || 'N/A'}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-slate-400">
                          <span>Puntuación: {result.results?.score}%</span>
                          <span>•</span>
                          <span>{new Date(result.completed_at).toLocaleDateString()}</span>
                        </div>
                        {result.results?.weak_areas?.length > 0 && (
                          <div className="mt-2">
                            <span className="text-xs text-slate-500">Áreas a mejorar: </span>
                            <span className="text-xs text-orange-400">
                              {result.results.weak_areas.join(', ')}
                            </span>
                          </div>
                        )}
                      </div>
                    ))}
                    <Button 
                      variant="outline" 
                      onClick={() => navigate('/student/placement-test')}
                      className="w-full border-slate-700"
                    >
                      Repetir Test
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Quick Actions */}
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-white mb-4">Acciones Rápidas</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <QuickActionCard
              icon={BookOpen}
              label="Hacer Mock Exam"
              onClick={() => navigate('/oet/nurse')}
              color="bg-blue-500"
            />
            <QuickActionCard
              icon={Mic}
              label="Practicar Speaking"
              onClick={() => navigate('/oet/speaking-practice')}
              color="bg-green-500"
            />
            <QuickActionCard
              icon={Sparkles}
              label="AI Tutor"
              onClick={() => navigate('/student/ai-tutor')}
              color="bg-purple-500"
            />
            <QuickActionCard
              icon={Package}
              label="Ver Tienda"
              onClick={() => navigate('/store')}
              color="bg-orange-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// Stat Card Component
function StatCard({ icon: Icon, label, value, color, bgColor }) {
  return (
    <Card className="bg-slate-900/50 border-slate-800">
      <CardContent className="p-4">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg ${bgColor} flex items-center justify-center`}>
            <Icon className={`w-5 h-5 ${color}`} />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{value}</p>
            <p className="text-xs text-slate-400">{label}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Pack Access Card Component
function PackAccessCard({ access, onStartExam, onStartSpeaking }) {
  const expiry = access.expires_at ? new Date(access.expires_at) : null;
  const daysLeft = expiry ? Math.ceil((expiry - new Date()) / (1000 * 60 * 60 * 24)) : 0;
  const isExpired = daysLeft <= 0;
  
  return (
    <Card className={`bg-slate-900/50 border-slate-800 ${isExpired ? 'opacity-60' : ''}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <Badge className="mb-2 bg-blue-500/20 text-blue-300 text-xs">
              {access.exam_type}
            </Badge>
            <CardTitle className="text-white text-lg">{access.pack_name}</CardTitle>
          </div>
          <Badge className={daysLeft <= 7 ? 'bg-orange-500/20 text-orange-300' : 'bg-green-500/20 text-green-300'}>
            {isExpired ? 'Expirado' : `${daysLeft} días`}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Resources */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex items-center gap-2 text-slate-300">
            <BookOpen className="w-4 h-4 text-blue-400" />
            <span>{access.mocks_remaining}/{access.mocks_total} Mocks</span>
          </div>
          {access.include_ai_tutor && (
            <div className="flex items-center gap-2 text-slate-300">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <span>AI Tutor {access.ai_tutor_minutes_remaining === -1 ? '∞' : access.ai_tutor_minutes_remaining}m</span>
            </div>
          )}
          {access.include_speaking && (
            <div className="flex items-center gap-2 text-slate-300">
              <Mic className="w-4 h-4 text-green-400" />
              <span>Speaking {access.speaking_sessions_remaining === -1 ? '∞' : access.speaking_sessions_remaining}</span>
            </div>
          )}
          {access.include_writing_evaluation && (
            <div className="flex items-center gap-2 text-slate-300">
              <PenTool className="w-4 h-4 text-orange-400" />
              <span>Writing {access.writing_evaluations_remaining === -1 ? '∞' : access.writing_evaluations_remaining}</span>
            </div>
          )}
        </div>

        {/* Progress */}
        {access.mocks_total > 0 && (
          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Progreso</span>
              <span>{Math.round((1 - access.mocks_remaining / access.mocks_total) * 100)}%</span>
            </div>
            <Progress 
              value={(1 - access.mocks_remaining / access.mocks_total) * 100} 
              className="h-1.5"
            />
          </div>
        )}

        {/* Actions */}
        {!isExpired && (
          <div className="flex gap-2 pt-2">
            {access.mocks_remaining > 0 && (
              <Button 
                size="sm" 
                onClick={onStartExam}
                className="flex-1 bg-teal-500 hover:bg-teal-600"
              >
                <Play className="w-4 h-4 mr-1" />
                Mock Exam
              </Button>
            )}
            {access.include_speaking && access.speaking_sessions_remaining !== 0 && (
              <Button 
                size="sm" 
                variant="outline"
                onClick={onStartSpeaking}
                className="flex-1 border-slate-700"
              >
                <Mic className="w-4 h-4 mr-1" />
                Speaking
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Study Plan Card Component
function StudyPlanCard({ plan }) {
  const navigate = useNavigate();
  const weeksCompleted = plan.progress?.length || 0;
  const progress = (weeksCompleted / plan.total_weeks) * 100;
  
  return (
    <Card className="bg-slate-900/50 border-slate-800">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-white font-medium">{plan.exam_type}</h3>
            <p className="text-sm text-slate-400">
              {plan.total_weeks} semanas • {plan.hours_per_week}h/semana
            </p>
          </div>
          <Badge className="bg-purple-500/20 text-purple-300">
            {plan.target_level}
          </Badge>
        </div>
        
        <div className="mb-3">
          <div className="flex justify-between text-xs text-slate-400 mb-1">
            <span>Semana {weeksCompleted + 1} de {plan.total_weeks}</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <Progress value={progress} className="h-1.5" />
        </div>
        
        <div className="flex items-center justify-between">
          <div className="text-xs text-slate-500">
            Meta: {new Date(plan.target_date).toLocaleDateString()}
          </div>
          <Button 
            size="sm" 
            variant="ghost"
            onClick={() => navigate(`/student/plan/${plan.id}`)}
            className="text-teal-400 hover:text-teal-300"
          >
            Ver Plan
            <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// Quick Action Card Component
function QuickActionCard({ icon: Icon, label, onClick, color }) {
  return (
    <Card 
      className="bg-slate-900/50 border-slate-800 hover:border-slate-700 cursor-pointer transition-all"
      onClick={onClick}
    >
      <CardContent className="p-4 flex flex-col items-center text-center">
        <div className={`w-12 h-12 rounded-xl ${color} flex items-center justify-center mb-3`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        <span className="text-sm text-white font-medium">{label}</span>
      </CardContent>
    </Card>
  );
}
