import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Label } from '../components/ui/label';
import {
  ClipboardList,
  Clock,
  CheckCircle2,
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  Play,
  Target,
  Brain,
  Loader2
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function PlacementTestPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [phase, setPhase] = useState('intro'); // intro | test | results
  const [session, setSession] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  // Timer
  useEffect(() => {
    if (phase === 'test' && timeLeft > 0) {
      const timer = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            handleSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [phase, timeLeft]);

  const startTest = async (examType = 'OET') => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/placement-test/start?exam_type=${examType}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSession({ id: data.session_id });
        setQuestions(data.questions);
        setTimeLeft(data.time_limit_minutes * 60);
        setPhase('test');
      } else {
        toast.error('Error al iniciar el test');
      }
    } catch (error) {
      toast.error('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (questionId, answer) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleSubmit = async () => {
    if (!session) return;
    
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const answersArray = Object.entries(answers).map(([question_id, answer]) => ({
        question_id,
        answer
      }));
      
      const response = await fetch(`${API_URL}/api/placement-test/submit`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          test_session_id: session.id,
          answers: answersArray
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setResults(data);
        setPhase('results');
      } else {
        toast.error('Error al enviar el test');
      }
    } catch (error) {
      toast.error('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Intro Phase
  if (phase === 'intro') {
    return (
      <div className="min-h-screen bg-slate-950 p-6">
        <div className="max-w-2xl mx-auto">
          <Button 
            variant="ghost" 
            onClick={() => navigate(-1)}
            className="mb-6 text-slate-400"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Volver
          </Button>
          
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader className="text-center">
              <div className="w-16 h-16 bg-teal-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <ClipboardList className="w-8 h-8 text-teal-400" />
              </div>
              <CardTitle className="text-white text-2xl">Test de Nivel</CardTitle>
              <CardDescription className="text-slate-400">
                Evalúa tu nivel de inglés para personalizar tu preparación
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                  <Clock className="w-5 h-5 text-blue-400 mt-0.5" />
                  <div>
                    <p className="text-white font-medium">Duración</p>
                    <p className="text-sm text-slate-400">Aproximadamente 20 minutos</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                  <Target className="w-5 h-5 text-green-400 mt-0.5" />
                  <div>
                    <p className="text-white font-medium">Secciones</p>
                    <p className="text-sm text-slate-400">Gramática, Vocabulario, Comprensión lectora</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                  <Brain className="w-5 h-5 text-purple-400 mt-0.5" />
                  <div>
                    <p className="text-white font-medium">Resultado</p>
                    <p className="text-sm text-slate-400">Nivel CEFR estimado y áreas de mejora</p>
                  </div>
                </div>
              </div>
              
              <Button 
                onClick={() => startTest('OET')}
                disabled={loading}
                className="w-full bg-teal-500 hover:bg-teal-600"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Play className="w-4 h-4 mr-2" />
                )}
                Comenzar Test
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Test Phase
  if (phase === 'test') {
    const currentQuestion = questions[currentIndex];
    const progress = ((currentIndex + 1) / questions.length) * 100;
    
    return (
      <div className="min-h-screen bg-slate-950 p-6">
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-slate-400 text-sm">
                Pregunta {currentIndex + 1} de {questions.length}
              </p>
              <Badge className="mt-1 bg-blue-500/20 text-blue-300">
                {currentQuestion?.section}
              </Badge>
            </div>
            <div className={`text-2xl font-mono font-bold ${timeLeft < 60 ? 'text-red-400' : 'text-white'}`}>
              {formatTime(timeLeft)}
            </div>
          </div>
          
          <Progress value={progress} className="mb-6 h-2" />
          
          {/* Question */}
          <Card className="bg-slate-900/50 border-slate-800 mb-6">
            <CardContent className="p-6">
              <p className="text-white text-lg mb-6">{currentQuestion?.question_text}</p>
              
              <RadioGroup
                value={answers[currentQuestion?.id] || ''}
                onValueChange={(value) => handleAnswer(currentQuestion?.id, value)}
                className="space-y-3"
              >
                {currentQuestion?.options?.map((option, idx) => (
                  <div 
                    key={idx}
                    className={`flex items-center space-x-3 p-3 rounded-lg border transition-all cursor-pointer ${
                      answers[currentQuestion?.id] === option 
                        ? 'border-teal-500 bg-teal-500/10' 
                        : 'border-slate-700 hover:border-slate-600'
                    }`}
                    onClick={() => handleAnswer(currentQuestion?.id, option)}
                  >
                    <RadioGroupItem value={option} id={`option-${idx}`} />
                    <Label htmlFor={`option-${idx}`} className="text-white cursor-pointer flex-1">
                      {option}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </CardContent>
          </Card>
          
          {/* Navigation */}
          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={() => setCurrentIndex(prev => Math.max(0, prev - 1))}
              disabled={currentIndex === 0}
              className="border-slate-700"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Anterior
            </Button>
            
            {currentIndex === questions.length - 1 ? (
              <Button
                onClick={handleSubmit}
                disabled={loading}
                className="bg-teal-500 hover:bg-teal-600"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                Finalizar Test
              </Button>
            ) : (
              <Button
                onClick={() => setCurrentIndex(prev => Math.min(questions.length - 1, prev + 1))}
                className="bg-teal-500 hover:bg-teal-600"
              >
                Siguiente
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            )}
          </div>
          
          {/* Question Navigation */}
          <div className="mt-6 flex flex-wrap gap-2 justify-center">
            {questions.map((q, idx) => (
              <button
                key={q.id}
                onClick={() => setCurrentIndex(idx)}
                className={`w-8 h-8 rounded-full text-sm font-medium transition-all ${
                  idx === currentIndex
                    ? 'bg-teal-500 text-white'
                    : answers[q.id]
                    ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                }`}
              >
                {idx + 1}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Results Phase
  if (phase === 'results') {
    return (
      <div className="min-h-screen bg-slate-950 p-6">
        <div className="max-w-2xl mx-auto">
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader className="text-center">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle2 className="w-8 h-8 text-green-400" />
              </div>
              <CardTitle className="text-white text-2xl">¡Test Completado!</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Level */}
              <div className="text-center p-6 bg-slate-800/50 rounded-xl">
                <p className="text-slate-400 mb-2">Tu nivel estimado</p>
                <p className="text-5xl font-bold text-teal-400">{results?.estimated_level}</p>
              </div>
              
              {/* Score */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-slate-800/50 rounded-lg text-center">
                  <p className="text-3xl font-bold text-white">{results?.score}%</p>
                  <p className="text-sm text-slate-400">Puntuación</p>
                </div>
                <div className="p-4 bg-slate-800/50 rounded-lg text-center">
                  <p className="text-3xl font-bold text-white">{results?.correct}/{results?.total}</p>
                  <p className="text-sm text-slate-400">Correctas</p>
                </div>
              </div>
              
              {/* By Section */}
              {results?.by_section && (
                <div className="space-y-3">
                  <p className="text-white font-medium">Por Sección:</p>
                  {Object.entries(results.by_section).map(([section, data]) => (
                    <div key={section} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                      <span className="text-slate-300 capitalize">{section}</span>
                      <Badge className={data.percentage >= 60 ? 'bg-green-500/20 text-green-300' : 'bg-orange-500/20 text-orange-300'}>
                        {Math.round(data.percentage)}%
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
              
              {/* Weak Areas */}
              {results?.weak_areas?.length > 0 && (
                <div className="p-4 bg-orange-500/10 border border-orange-500/20 rounded-lg">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-orange-400 mt-0.5" />
                    <div>
                      <p className="text-white font-medium">Áreas a Mejorar</p>
                      <p className="text-sm text-slate-400">
                        {results.weak_areas.join(', ')}
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Actions */}
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => navigate('/student/my-packs')}
                  className="flex-1 border-slate-700"
                >
                  Ver Dashboard
                </Button>
                <Button
                  onClick={() => navigate('/student/create-plan')}
                  className="flex-1 bg-teal-500 hover:bg-teal-600"
                >
                  <Brain className="w-4 h-4 mr-2" />
                  Crear Plan de Estudio
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return null;
}
