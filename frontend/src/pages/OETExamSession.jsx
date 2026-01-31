import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Textarea } from '../components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import {
  Headphones,
  BookOpen,
  FileText,
  Mic,
  Play,
  Pause,
  Clock,
  ChevronRight,
  ChevronLeft,
  CheckCircle,
  AlertCircle,
  Flag,
  Home,
  Volume2,
  X,
  Send,
  Brain,
  HelpCircle,
  RotateCcw,
  Save
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Section icons mapping
const sectionIcons = {
  listening: Headphones,
  reading: BookOpen,
  writing: FileText,
  speaking: Mic
};

// Section colors
const sectionColors = {
  listening: 'from-blue-500 to-cyan-500',
  reading: 'from-emerald-500 to-green-500',
  writing: 'from-purple-500 to-violet-500',
  speaking: 'from-orange-500 to-amber-500'
};

export default function OETExamSession() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { sessionId, mockId } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [examData, setExamData] = useState(null);
  const [currentSection, setCurrentSection] = useState('listening');
  const [currentPart, setCurrentPart] = useState('part_a');
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [flaggedQuestions, setFlaggedQuestions] = useState(new Set());
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [isPaused, setIsPaused] = useState(false);
  const [showExitDialog, setShowExitDialog] = useState(false);
  const [showCoachDialog, setShowCoachDialog] = useState(false);
  const [coachQuestion, setCoachQuestion] = useState('');
  const [coachResponse, setCoachResponse] = useState('');
  const [coachLoading, setCoachLoading] = useState(false);
  const [audioPlaying, setAudioPlaying] = useState(false);
  
  // Fetch exam content
  useEffect(() => {
    fetchExamContent();
  }, [mockId]);

  // Timer effect
  useEffect(() => {
    if (timeRemaining !== null && timeRemaining > 0 && !isPaused) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            handleSectionTimeout();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [timeRemaining, isPaused]);

  const fetchExamContent = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/oet-exam/mock/${mockId || 'NUR-013-v2'}/content?section=${currentSection}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setExamData(data);
        
        // Set timer based on section
        const sectionTimes = {
          listening: 50 * 60,
          reading: 60 * 60,
          writing: 45 * 60,
          speaking: 20 * 60
        };
        setTimeRemaining(sectionTimes[currentSection]);
      }
    } catch (error) {
      console.error('Error fetching exam content:', error);
      toast.error('Error al cargar el contenido del examen');
    } finally {
      setLoading(false);
    }
  };

  const handleSectionTimeout = () => {
    toast.warning(`Tiempo agotado para la sección ${currentSection}`);
    // Auto-save and move to next section
    saveProgress();
  };

  const formatTime = (seconds) => {
    if (seconds === null) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswer = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const toggleFlag = (questionId) => {
    setFlaggedQuestions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(questionId)) {
        newSet.delete(questionId);
      } else {
        newSet.add(questionId);
      }
      return newSet;
    });
  };

  const saveProgress = async () => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API_URL}/api/oet-exam/session/${sessionId}/save`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          section: currentSection,
          answers,
          time_remaining: timeRemaining
        })
      });
      toast.success('Progreso guardado');
    } catch (error) {
      toast.error('Error al guardar el progreso');
    }
  };

  const askCoach = async () => {
    if (!coachQuestion.trim()) return;
    
    setCoachLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/oet-exam/coach/ask`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: coachQuestion,
          section: currentSection,
          context: `Currently on ${currentSection} section, part ${currentPart}`
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setCoachResponse(data.response);
      }
    } catch (error) {
      toast.error('Error al contactar al coach');
    } finally {
      setCoachLoading(false);
    }
  };

  const goToNextSection = () => {
    const sections = ['listening', 'reading', 'writing', 'speaking'];
    const currentIndex = sections.indexOf(currentSection);
    if (currentIndex < sections.length - 1) {
      setCurrentSection(sections[currentIndex + 1]);
      setCurrentPart('part_a');
      setCurrentQuestion(0);
      fetchExamContent();
    }
  };

  // Mock data for demonstration
  const mockListeningData = {
    part_a: {
      title: 'Part A: Consultation Extracts',
      instructions: 'Complete the notes using information from the audio. Use 1-3 words per gap.',
      questions: [
        { id: 1, text: 'Duration of symptoms:', answer_type: 'text' },
        { id: 2, text: 'Type of experience reported (visual):', answer_type: 'text' },
        { id: 3, text: 'Frequency of night-time toilet visits:', answer_type: 'text' },
        { id: 4, text: 'Day of week patient initially stated incorrectly:', answer_type: 'text' },
        { id: 5, text: 'Current heart medication and dose:', answer_type: 'text' },
        { id: 6, text: 'New medication started recently:', answer_type: 'text' },
        { id: 7, text: 'Reason medication was prescribed:', answer_type: 'text' },
        { id: 8, text: 'Medication dose:', answer_type: 'text' },
        { id: 9, text: 'Who fills patient\'s dosette box:', answer_type: 'text' },
        { id: 10, text: 'Location of soreness after stumble:', answer_type: 'text' },
        { id: 11, text: 'Number of proper meals per day:', answer_type: 'text' },
        { id: 12, text: 'Safety device patient forgets to wear:', answer_type: 'text' }
      ]
    },
    part_b: {
      title: 'Part B: Workplace Extracts',
      instructions: 'Choose the best answer A, B, or C.',
      questions: [
        {
          id: 25,
          text: 'What does the ward sister want the nurse to do?',
          options: ['A. Ensure the overnight events are properly recorded', 'B. Conduct a comprehensive pain assessment', 'C. Arrange an urgent medical review'],
          answer_type: 'choice'
        },
        {
          id: 26,
          text: 'What do the nurses agree was the main problem?',
          options: ['A. The verification procedure wasn\'t correctly followed', 'B. The ward layout caused patient confusion', 'C. There were insufficient staff for medication rounds'],
          answer_type: 'choice'
        },
        {
          id: 27,
          text: 'What is the main purpose of this message?',
          options: ['A. To change the time and location of the session', 'B. To list required preparation materials', 'C. To outline what the simulation will involve'],
          answer_type: 'choice'
        }
      ]
    }
  };

  const SectionIcon = sectionIcons[currentSection] || Headphones;

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-teal-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400">Cargando examen...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      {/* Exam Header */}
      <header className="bg-slate-900/95 backdrop-blur-lg border-b border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            {/* Section Info */}
            <div className="flex items-center gap-3">
              <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${sectionColors[currentSection]} flex items-center justify-center`}>
                <SectionIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-sm font-bold text-white capitalize">{currentSection}</h1>
                <p className="text-xs text-slate-400">OET Mock NUR-013</p>
              </div>
            </div>

            {/* Timer */}
            <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              timeRemaining && timeRemaining < 300 ? 'bg-red-500/20 text-red-400' : 'bg-slate-800 text-slate-300'
            }`}>
              <Clock className="w-4 h-4" />
              <span className="font-mono text-lg font-bold">{formatTime(timeRemaining)}</span>
              <Button 
                variant="ghost" 
                size="sm" 
                className="ml-2 h-7 w-7 p-0"
                onClick={() => setIsPaused(!isPaused)}
              >
                {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
              </Button>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                className="border-slate-700 text-slate-300 hover:bg-slate-800"
                onClick={() => setShowCoachDialog(true)}
              >
                <Brain className="w-4 h-4 mr-2" />
                AI Coach
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="border-slate-700 text-slate-300 hover:bg-slate-800"
                onClick={saveProgress}
              >
                <Save className="w-4 h-4 mr-2" />
                Guardar
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="text-slate-400 hover:text-white"
                onClick={() => setShowExitDialog(true)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Section Navigation */}
      <div className="bg-slate-900/50 border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-1 py-2 overflow-x-auto">
            {['listening', 'reading', 'writing', 'speaking'].map((section, idx) => (
              <React.Fragment key={section}>
                <Button
                  variant={currentSection === section ? 'default' : 'ghost'}
                  size="sm"
                  className={currentSection === section 
                    ? 'bg-teal-500 text-white' 
                    : 'text-slate-400 hover:text-white'}
                  onClick={() => {
                    setCurrentSection(section);
                    fetchExamContent();
                  }}
                >
                  {React.createElement(sectionIcons[section], { className: 'w-4 h-4 mr-2' })}
                  <span className="capitalize">{section}</span>
                </Button>
                {idx < 3 && <ChevronRight className="w-4 h-4 text-slate-600" />}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Question Navigator */}
          <div className="lg:col-span-1">
            <Card className="bg-slate-900/50 border-slate-800 sticky top-28">
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-sm">Navegación</CardTitle>
              </CardHeader>
              <CardContent>
                {/* Part Tabs */}
                <div className="flex gap-1 mb-4">
                  {['part_a', 'part_b', 'part_c'].map((part) => (
                    <Button
                      key={part}
                      variant={currentPart === part ? 'default' : 'outline'}
                      size="sm"
                      className={currentPart === part 
                        ? 'bg-teal-500 flex-1' 
                        : 'flex-1 border-slate-700 text-slate-400'}
                      onClick={() => {
                        setCurrentPart(part);
                        setCurrentQuestion(0);
                      }}
                    >
                      {part.replace('_', ' ').toUpperCase()}
                    </Button>
                  ))}
                </div>

                {/* Question Grid */}
                <div className="grid grid-cols-6 gap-1">
                  {Array.from({ length: 12 }, (_, i) => (
                    <button
                      key={i}
                      onClick={() => setCurrentQuestion(i)}
                      className={`w-8 h-8 rounded text-xs font-medium transition-colors ${
                        currentQuestion === i
                          ? 'bg-teal-500 text-white'
                          : answers[`${currentPart}_${i + 1}`]
                            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                            : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                      } ${flaggedQuestions.has(`${currentPart}_${i + 1}`) ? 'ring-2 ring-orange-500' : ''}`}
                    >
                      {i + 1}
                    </button>
                  ))}
                </div>

                {/* Legend */}
                <div className="mt-4 pt-4 border-t border-slate-800 space-y-2 text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-teal-500 rounded"></div>
                    <span className="text-slate-400">Actual</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-emerald-500/20 border border-emerald-500/30 rounded"></div>
                    <span className="text-slate-400">Respondida</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-slate-800 rounded ring-2 ring-orange-500"></div>
                    <span className="text-slate-400">Marcada</span>
                  </div>
                </div>

                {/* Progress */}
                <div className="mt-4 pt-4 border-t border-slate-800">
                  <div className="flex justify-between text-xs text-slate-400 mb-2">
                    <span>Progreso</span>
                    <span>{Object.keys(answers).length}/42</span>
                  </div>
                  <Progress value={(Object.keys(answers).length / 42) * 100} className="h-2 bg-slate-800" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Question Content */}
          <div className="lg:col-span-3">
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <Badge className="bg-slate-700 text-slate-300 mb-2">
                      {currentPart.replace('_', ' ').toUpperCase()}
                    </Badge>
                    <CardTitle className="text-white">
                      {mockListeningData[currentPart]?.title || 'Question Section'}
                    </CardTitle>
                    <CardDescription>
                      {mockListeningData[currentPart]?.instructions}
                    </CardDescription>
                  </div>
                  {currentSection === 'listening' && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="border-blue-500/30 text-blue-400 hover:bg-blue-500/10"
                      onClick={() => setAudioPlaying(!audioPlaying)}
                    >
                      {audioPlaying ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
                      {audioPlaying ? 'Pausar Audio' : 'Reproducir Audio'}
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Current Question */}
                {mockListeningData[currentPart]?.questions[currentQuestion] && (
                  <div className="p-6 bg-slate-800/50 rounded-xl border border-slate-700">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <span className="w-8 h-8 bg-teal-500 rounded-lg flex items-center justify-center text-white font-bold">
                          {currentQuestion + 1}
                        </span>
                        <p className="text-white font-medium">
                          {mockListeningData[currentPart].questions[currentQuestion].text}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className={`${flaggedQuestions.has(`${currentPart}_${currentQuestion + 1}`) ? 'text-orange-400' : 'text-slate-500'}`}
                        onClick={() => toggleFlag(`${currentPart}_${currentQuestion + 1}`)}
                      >
                        <Flag className="w-4 h-4" />
                      </Button>
                    </div>

                    {/* Answer Input */}
                    {mockListeningData[currentPart].questions[currentQuestion].answer_type === 'text' ? (
                      <Input
                        placeholder="Escribe tu respuesta..."
                        className="bg-slate-900 border-slate-700 text-white"
                        value={answers[`${currentPart}_${currentQuestion + 1}`] || ''}
                        onChange={(e) => handleAnswer(`${currentPart}_${currentQuestion + 1}`, e.target.value)}
                      />
                    ) : (
                      <RadioGroup
                        value={answers[`${currentPart}_${currentQuestion + 1}`] || ''}
                        onValueChange={(value) => handleAnswer(`${currentPart}_${currentQuestion + 1}`, value)}
                        className="space-y-3"
                      >
                        {mockListeningData[currentPart].questions[currentQuestion].options?.map((option, idx) => (
                          <div key={idx} className="flex items-center space-x-3 p-3 rounded-lg bg-slate-900 hover:bg-slate-800 transition-colors cursor-pointer">
                            <RadioGroupItem value={option.charAt(0)} id={`option-${idx}`} />
                            <Label htmlFor={`option-${idx}`} className="text-slate-300 cursor-pointer flex-1">
                              {option}
                            </Label>
                          </div>
                        ))}
                      </RadioGroup>
                    )}
                  </div>
                )}

                {/* Navigation */}
                <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                  <Button
                    variant="outline"
                    className="border-slate-700 text-slate-300"
                    disabled={currentQuestion === 0}
                    onClick={() => setCurrentQuestion(prev => prev - 1)}
                  >
                    <ChevronLeft className="w-4 h-4 mr-2" />
                    Anterior
                  </Button>
                  
                  <div className="text-sm text-slate-500">
                    Pregunta {currentQuestion + 1} de {mockListeningData[currentPart]?.questions.length || 12}
                  </div>
                  
                  <Button
                    className="bg-teal-500 hover:bg-teal-600"
                    onClick={() => {
                      if (currentQuestion < (mockListeningData[currentPart]?.questions.length || 12) - 1) {
                        setCurrentQuestion(prev => prev + 1);
                      }
                    }}
                  >
                    Siguiente
                    <ChevronRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Section Actions */}
            <div className="mt-4 flex justify-end gap-3">
              <Button
                variant="outline"
                className="border-slate-700 text-slate-300"
                onClick={saveProgress}
              >
                <Save className="w-4 h-4 mr-2" />
                Guardar y Continuar Después
              </Button>
              <Button
                className="bg-emerald-500 hover:bg-emerald-600"
                onClick={goToNextSection}
              >
                Finalizar Sección
                <CheckCircle className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        </div>
      </main>

      {/* Exit Dialog */}
      <Dialog open={showExitDialog} onOpenChange={setShowExitDialog}>
        <DialogContent className="bg-slate-900 border-slate-700">
          <DialogHeader>
            <DialogTitle className="text-white">¿Salir del examen?</DialogTitle>
            <DialogDescription>
              Tu progreso se guardará automáticamente. Podrás continuar más tarde desde donde lo dejaste.
            </DialogDescription>
          </DialogHeader>
          <div className="flex gap-3 mt-4">
            <Button
              variant="outline"
              className="flex-1 border-slate-700"
              onClick={() => setShowExitDialog(false)}
            >
              Cancelar
            </Button>
            <Button
              className="flex-1 bg-red-500 hover:bg-red-600"
              onClick={() => {
                saveProgress();
                navigate('/oet/nurse');
              }}
            >
              Salir
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* AI Coach Dialog */}
      <Dialog open={showCoachDialog} onOpenChange={setShowCoachDialog}>
        <DialogContent className="bg-slate-900 border-slate-700 max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-400" />
              AI Mock Exam Coach
            </DialogTitle>
            <DialogDescription>
              Pregunta sobre estrategias, formato del examen, o dudas técnicas. El coach no te dará respuestas a las preguntas del examen.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 mt-4">
            <div className="relative">
              <Textarea
                placeholder="Escribe tu pregunta al coach..."
                className="bg-slate-800 border-slate-700 text-white resize-none pr-12"
                rows={3}
                value={coachQuestion}
                onChange={(e) => setCoachQuestion(e.target.value)}
              />
              <Button
                size="sm"
                className="absolute bottom-2 right-2 bg-purple-500 hover:bg-purple-600"
                onClick={askCoach}
                disabled={coachLoading}
              >
                {coachLoading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
            
            {coachResponse && (
              <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                <p className="text-slate-300 text-sm whitespace-pre-wrap">{coachResponse}</p>
              </div>
            )}

            {/* Quick Questions */}
            <div className="space-y-2">
              <p className="text-xs text-slate-500">Preguntas rápidas:</p>
              <div className="flex flex-wrap gap-2">
                {[
                  '¿Cuánto tiempo para esta sección?',
                  '¿Consejos para el listening?',
                  '¿Cómo gestionar el tiempo?'
                ].map((q, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    size="sm"
                    className="text-xs border-slate-700 text-slate-400"
                    onClick={() => {
                      setCoachQuestion(q);
                      askCoach();
                    }}
                  >
                    {q}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
