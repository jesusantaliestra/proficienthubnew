import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Checkbox } from '../components/ui/checkbox';
import { Badge } from '../components/ui/badge';
import {
  Brain,
  Calendar,
  Clock,
  Target,
  Sparkles,
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Loader2,
  BookOpen,
  Mic,
  PenTool,
  Headphones
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const EXAM_TYPES = [
  { id: 'OET', name: 'OET - Occupational English Test' },
  { id: 'IELTS_ACADEMIC', name: 'IELTS Academic' },
  { id: 'IELTS_GENERAL', name: 'IELTS General Training' },
  { id: 'TOEFL', name: 'TOEFL iBT' },
  { id: 'PTE', name: 'PTE Academic' },
  { id: 'CAMBRIDGE_FCE', name: 'Cambridge B2 First (FCE)' },
  { id: 'CAMBRIDGE_CAE', name: 'Cambridge C1 Advanced (CAE)' },
];

const OET_PROFESSIONS = [
  { id: 'nursing', name: 'Enfermería' },
  { id: 'medicine', name: 'Medicina' },
  { id: 'dentistry', name: 'Odontología' },
  { id: 'pharmacy', name: 'Farmacia' },
  { id: 'physiotherapy', name: 'Fisioterapia' },
];

const SKILL_ICONS = {
  listening: Headphones,
  reading: BookOpen,
  writing: PenTool,
  speaking: Mic
};

const CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

export default function CreateStudyPlanPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState(null);
  
  const [formData, setFormData] = useState({
    exam_type: 'OET',
    profession: 'nursing',
    target_date: '',
    hours_per_week: 10,
    current_level: 'B1',
    focus_areas: ['listening', 'reading', 'writing', 'speaking']
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const toggleFocusArea = (skill) => {
    setFormData(prev => ({
      ...prev,
      focus_areas: prev.focus_areas.includes(skill)
        ? prev.focus_areas.filter(s => s !== skill)
        : [...prev.focus_areas, skill]
    }));
  };

  const generatePlan = async () => {
    if (!formData.target_date) {
      toast.error('Selecciona una fecha de examen');
      return;
    }
    
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/agent-planner/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        const data = await response.json();
        setPlan(data.plan);
        setStep(3);
        toast.success('¡Plan de estudio generado!');
      } else {
        toast.error('Error al generar el plan');
      }
    } catch (error) {
      toast.error('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  // Step 1: Exam Details
  const renderStep1 = () => (
    <Card className="bg-slate-900/50 border-slate-800">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Target className="w-5 h-5 text-teal-400" />
          Paso 1: Tu Examen
        </CardTitle>
        <CardDescription>
          Selecciona el examen que vas a preparar
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label className="text-slate-300">Tipo de Examen</Label>
          <Select 
            value={formData.exam_type}
            onValueChange={(value) => handleChange('exam_type', value)}
          >
            <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-slate-800 border-slate-700">
              {EXAM_TYPES.map(exam => (
                <SelectItem key={exam.id} value={exam.id} className="text-white">
                  {exam.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        {formData.exam_type === 'OET' && (
          <div className="space-y-2">
            <Label className="text-slate-300">Profesión OET</Label>
            <Select 
              value={formData.profession}
              onValueChange={(value) => handleChange('profession', value)}
            >
              <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                {OET_PROFESSIONS.map(prof => (
                  <SelectItem key={prof.id} value={prof.id} className="text-white">
                    {prof.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}
        
        <div className="space-y-2">
          <Label className="text-slate-300">Fecha de Examen</Label>
          <Input
            type="date"
            value={formData.target_date}
            onChange={(e) => handleChange('target_date', e.target.value)}
            min={new Date().toISOString().split('T')[0]}
            className="bg-slate-800 border-slate-700 text-white"
          />
        </div>
        
        <Button 
          onClick={() => setStep(2)}
          disabled={!formData.target_date}
          className="w-full bg-teal-500 hover:bg-teal-600"
        >
          Siguiente
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </CardContent>
    </Card>
  );

  // Step 2: Study Preferences
  const renderStep2 = () => (
    <Card className="bg-slate-900/50 border-slate-800">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Clock className="w-5 h-5 text-teal-400" />
          Paso 2: Tu Disponibilidad
        </CardTitle>
        <CardDescription>
          Personaliza tu plan de estudio
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label className="text-slate-300">Nivel Actual (CEFR)</Label>
          <Select 
            value={formData.current_level}
            onValueChange={(value) => handleChange('current_level', value)}
          >
            <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-slate-800 border-slate-700">
              {CEFR_LEVELS.map(level => (
                <SelectItem key={level} value={level} className="text-white">
                  {level}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-xs text-slate-500">
            Si no estás seguro, realiza el Test de Nivel primero
          </p>
        </div>
        
        <div className="space-y-2">
          <Label className="text-slate-300">Horas por Semana</Label>
          <div className="flex items-center gap-4">
            <Input
              type="number"
              min="5"
              max="40"
              value={formData.hours_per_week}
              onChange={(e) => handleChange('hours_per_week', parseInt(e.target.value) || 10)}
              className="bg-slate-800 border-slate-700 text-white w-24"
            />
            <span className="text-slate-400">horas/semana</span>
          </div>
        </div>
        
        <div className="space-y-3">
          <Label className="text-slate-300">Áreas de Enfoque</Label>
          <div className="grid grid-cols-2 gap-3">
            {['listening', 'reading', 'writing', 'speaking'].map(skill => {
              const Icon = SKILL_ICONS[skill];
              const isSelected = formData.focus_areas.includes(skill);
              
              return (
                <div
                  key={skill}
                  onClick={() => toggleFocusArea(skill)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all flex items-center gap-3 ${
                    isSelected 
                      ? 'border-teal-500 bg-teal-500/10' 
                      : 'border-slate-700 hover:border-slate-600'
                  }`}
                >
                  <Checkbox checked={isSelected} className="pointer-events-none" />
                  <Icon className={`w-4 h-4 ${isSelected ? 'text-teal-400' : 'text-slate-400'}`} />
                  <span className={`capitalize ${isSelected ? 'text-white' : 'text-slate-400'}`}>
                    {skill}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
        
        <div className="flex gap-3">
          <Button 
            variant="outline"
            onClick={() => setStep(1)}
            className="flex-1 border-slate-700"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Atrás
          </Button>
          <Button 
            onClick={generatePlan}
            disabled={loading || formData.focus_areas.length === 0}
            className="flex-1 bg-teal-500 hover:bg-teal-600"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generando...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generar Plan con IA
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  // Step 3: View Plan
  const renderStep3 = () => (
    <div className="space-y-6">
      <Card className="bg-slate-900/50 border-slate-800">
        <CardHeader className="text-center">
          <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-8 h-8 text-green-400" />
          </div>
          <CardTitle className="text-white text-2xl">¡Plan Generado!</CardTitle>
          <CardDescription>
            Tu plan personalizado de {plan?.total_weeks} semanas está listo
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Overview */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 bg-slate-800/50 rounded-lg">
              <p className="text-2xl font-bold text-white">{plan?.total_weeks}</p>
              <p className="text-xs text-slate-400">Semanas</p>
            </div>
            <div className="p-3 bg-slate-800/50 rounded-lg">
              <p className="text-2xl font-bold text-white">{plan?.hours_per_week}h</p>
              <p className="text-xs text-slate-400">Por Semana</p>
            </div>
            <div className="p-3 bg-slate-800/50 rounded-lg">
              <p className="text-2xl font-bold text-teal-400">{plan?.target_level}</p>
              <p className="text-xs text-slate-400">Meta</p>
            </div>
          </div>
          
          {/* Milestones */}
          {plan?.milestones?.length > 0 && (
            <div>
              <h3 className="text-white font-medium mb-3">Hitos</h3>
              <div className="space-y-2">
                {plan.milestones.map((milestone, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                    <Badge className="bg-purple-500/20 text-purple-300 shrink-0">
                      Semana {milestone.week}
                    </Badge>
                    <div>
                      <p className="text-white text-sm">{milestone.goal}</p>
                      <p className="text-xs text-slate-400">{milestone.assessment}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Recommendations */}
          {plan?.recommendations?.length > 0 && (
            <div>
              <h3 className="text-white font-medium mb-3">Recomendaciones</h3>
              <ul className="space-y-2">
                {plan.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-slate-300">
                    <Sparkles className="w-4 h-4 text-teal-400 mt-0.5 shrink-0" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* First Week Preview */}
          {plan?.weekly_plans?.[0] && (
            <div>
              <h3 className="text-white font-medium mb-3">Semana 1: {plan.weekly_plans[0].theme}</h3>
              <div className="space-y-2">
                {plan.weekly_plans[0].daily_schedule?.slice(0, 3).map((day, idx) => (
                  <div key={idx} className="p-3 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-medium">{day.day}</span>
                      <span className="text-xs text-slate-400">{day.total_minutes} min</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {day.tasks?.map((task, tidx) => (
                        <Badge key={tidx} variant="outline" className="text-xs border-slate-700 text-slate-400">
                          {task.activity}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
      
      <div className="flex gap-3">
        <Button
          variant="outline"
          onClick={() => navigate('/student/my-packs')}
          className="flex-1 border-slate-700"
        >
          Ir al Dashboard
        </Button>
        <Button
          onClick={() => navigate(`/student/plan/${plan?.id}`)}
          className="flex-1 bg-teal-500 hover:bg-teal-600"
        >
          Ver Plan Completo
        </Button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-2xl mx-auto">
        <Button 
          variant="ghost" 
          onClick={() => step > 1 && !plan ? setStep(step - 1) : navigate(-1)}
          className="mb-6 text-slate-400"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          {step > 1 && !plan ? 'Paso Anterior' : 'Volver'}
        </Button>
        
        {/* Progress */}
        {step < 3 && (
          <div className="flex items-center justify-center gap-2 mb-8">
            {[1, 2].map(s => (
              <div 
                key={s}
                className={`w-3 h-3 rounded-full transition-all ${
                  s <= step ? 'bg-teal-500' : 'bg-slate-700'
                }`}
              />
            ))}
          </div>
        )}
        
        {step === 1 && renderStep1()}
        {step === 2 && renderStep2()}
        {step === 3 && renderStep3()}
      </div>
    </div>
  );
}
