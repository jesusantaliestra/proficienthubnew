import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { 
  Clock, ArrowLeft, ArrowRight, CheckCircle, XCircle,
  AlertTriangle, BookOpen, Send, Loader2
} from 'lucide-react';
import axios from 'axios';
import { toast, Toaster } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function ExamSimulator() {
  const { examType, section } = useParams();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState(null);
  const [startTime] = useState(Date.now());

  const examNames = {
    toefl: 'TOEFL',
    ielts: 'IELTS',
    cambridge: 'Cambridge',
    pte: 'PTE',
    oet: 'OET'
  };

  useEffect(() => {
    fetchQuestions();
  }, [examType, section]);

  useEffect(() => {
    if (timeLeft <= 0 || results) return;
    
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft, results]);

  const fetchQuestions = async () => {
    try {
      const response = await axios.get(`${API_URL}/exams/${examType}/practice?section=${section}`);
      setQuestions(response.data.questions || []);
      setTimeLeft(response.data.time_limit * 60); // Convert minutes to seconds
    } catch (error) {
      console.error('Failed to fetch questions:', error);
      toast.error('Failed to load exam questions');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswer = (questionId, answer) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    const timeSpent = Math.round((Date.now() - startTime) / 1000);
    
    try {
      const formattedAnswers = questions.map(q => ({
        question_id: q.id,
        answer: answers[q.id] || '',
        is_correct: answers[q.id] === q.correct_answer
      }));

      const response = await axios.post(`${API_URL}/exams/submit`, {
        exam_type: examType,
        section: section,
        answers: formattedAnswers,
        time_spent: timeSpent
      });

      setResults(response.data);
      toast.success('Exam submitted successfully!');
    } catch (error) {
      console.error('Submit error:', error);
      toast.error('Failed to submit exam');
    } finally {
      setSubmitting(false);
    }
  };

  const getTimerColor = () => {
    if (timeLeft < 60) return 'text-red-500 animate-pulse';
    if (timeLeft < 300) return 'text-amber-500';
    return 'text-white';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-slate-400">Loading exam...</p>
        </div>
      </div>
    );
  }

  if (results) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6" data-testid="exam-results">
        <Toaster position="top-right" richColors />
        <Card className="max-w-2xl w-full bg-slate-900/50 border-slate-800">
          <CardHeader className="text-center">
            <div className={`w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center ${results.score >= 70 ? 'bg-emerald-500/20' : 'bg-amber-500/20'}`}>
              {results.score >= 70 ? (
                <CheckCircle className="w-10 h-10 text-emerald-400" />
              ) : (
                <AlertTriangle className="w-10 h-10 text-amber-400" />
              )}
            </div>
            <CardTitle className="text-3xl text-white font-outfit">
              {results.score >= 70 ? 'Great Job!' : 'Keep Practicing!'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center">
              <div className="text-6xl font-bold text-white font-outfit mb-2">{results.score}%</div>
              <p className="text-slate-400">Your Score</p>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-800/50 rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-blue-400">{Math.round(results.time_spent / 60)}</p>
                <p className="text-slate-500 text-sm">Minutes Spent</p>
              </div>
              <div className="bg-slate-800/50 rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-purple-400">{examNames[examType]}</p>
                <p className="text-slate-500 text-sm capitalize">{section}</p>
              </div>
            </div>
            
            <div className="bg-slate-800/30 rounded-xl p-6">
              <h4 className="text-white font-semibold mb-3">AI Feedback</h4>
              <p className="text-slate-300 text-sm leading-relaxed">{results.feedback}</p>
            </div>
            
            <div className="flex gap-4">
              <Button 
                variant="outline" 
                className="flex-1 border-slate-700"
                onClick={() => navigate('/student/dashboard')}
                data-testid="back-to-dashboard"
              >
                Back to Dashboard
              </Button>
              <Button 
                className="flex-1 bg-blue-500 hover:bg-blue-600"
                onClick={() => window.location.reload()}
                data-testid="try-again"
              >
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentQ = questions[currentQuestion];

  return (
    <div className="min-h-screen bg-slate-950" data-testid="exam-simulator">
      <Toaster position="top-right" richColors />
      
      {/* Header */}
      <header className="bg-slate-900/50 border-b border-slate-800 px-6 py-4 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              onClick={() => navigate(-1)}
              className="text-slate-400 hover:text-white"
              data-testid="exit-exam"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-lg font-bold text-white font-outfit">
                {examNames[examType]} - <span className="capitalize">{section}</span>
              </h1>
              <p className="text-xs text-slate-500">Question {currentQuestion + 1} of {questions.length}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-6">
            <div className={`flex items-center gap-2 font-mono text-lg ${getTimerColor()}`}>
              <Clock className="w-5 h-5" />
              <span data-testid="timer">{formatTime(timeLeft)}</span>
            </div>
            <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20">
              {Math.round((Object.keys(answers).length / questions.length) * 100)}% Complete
            </Badge>
          </div>
        </div>
      </header>

      {/* Progress */}
      <div className="max-w-4xl mx-auto px-6 py-4">
        <Progress value={(currentQuestion + 1) / questions.length * 100} className="h-2" />
        <div className="flex justify-between mt-2">
          {questions.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentQuestion(index)}
              className={`w-8 h-8 rounded-full text-xs font-medium transition-all ${
                index === currentQuestion 
                  ? 'bg-blue-500 text-white' 
                  : answers[questions[index]?.id]
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-slate-800 text-slate-500'
              }`}
              data-testid={`question-nav-${index}`}
            >
              {index + 1}
            </button>
          ))}
        </div>
      </div>

      {/* Question */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        {currentQ && (
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-8 space-y-6">
              {/* Passage if exists */}
              {currentQ.passage && (
                <div className="bg-slate-800/50 rounded-xl p-6 mb-6">
                  <div className="flex items-center gap-2 text-slate-400 text-sm mb-3">
                    <BookOpen className="w-4 h-4" />
                    <span>Reading Passage</span>
                  </div>
                  <p className="text-slate-200 leading-relaxed">{currentQ.passage}</p>
                </div>
              )}

              {/* Question */}
              <div>
                <Badge className="mb-4 capitalize">{currentQ.type.replace('_', ' ')}</Badge>
                <h2 className="text-xl font-semibold text-white mb-6">{currentQ.question}</h2>
              </div>

              {/* Answer Options */}
              {currentQ.type === 'multiple_choice' || currentQ.type === 'true_false_not_given' ? (
                <RadioGroup
                  value={answers[currentQ.id] || ''}
                  onValueChange={(value) => handleAnswer(currentQ.id, value)}
                  className="space-y-3"
                >
                  {currentQ.options.map((option, index) => (
                    <div
                      key={index}
                      className={`flex items-center space-x-3 p-4 rounded-xl border transition-all cursor-pointer ${
                        answers[currentQ.id] === option
                          ? 'border-blue-500 bg-blue-500/10'
                          : 'border-slate-700 hover:border-slate-600 bg-slate-800/30'
                      }`}
                      onClick={() => handleAnswer(currentQ.id, option)}
                      data-testid={`option-${index}`}
                    >
                      <RadioGroupItem value={option} id={`option-${index}`} />
                      <Label htmlFor={`option-${index}`} className="text-slate-200 cursor-pointer flex-1">
                        {option}
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              ) : currentQ.type === 'essay' ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-sm text-slate-400">
                    <span>Min: {currentQ.min_words} words</span>
                    <span>Max: {currentQ.max_words} words</span>
                  </div>
                  <Textarea
                    value={answers[currentQ.id] || ''}
                    onChange={(e) => handleAnswer(currentQ.id, e.target.value)}
                    placeholder="Write your essay here..."
                    className="min-h-[300px] bg-slate-800 border-slate-700 text-white"
                    data-testid="essay-input"
                  />
                  <p className="text-sm text-slate-500">
                    Word count: {(answers[currentQ.id] || '').split(/\s+/).filter(Boolean).length}
                  </p>
                </div>
              ) : currentQ.type === 'fill_blank' ? (
                <input
                  type="text"
                  value={answers[currentQ.id] || ''}
                  onChange={(e) => handleAnswer(currentQ.id, e.target.value)}
                  placeholder="Type your answer..."
                  className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  data-testid="fill-blank-input"
                />
              ) : null}

              {/* Navigation */}
              <div className="flex justify-between pt-6 border-t border-slate-800">
                <Button
                  variant="outline"
                  onClick={() => setCurrentQuestion(prev => Math.max(0, prev - 1))}
                  disabled={currentQuestion === 0}
                  className="border-slate-700"
                  data-testid="prev-question"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Previous
                </Button>
                
                {currentQuestion === questions.length - 1 ? (
                  <Button
                    onClick={handleSubmit}
                    disabled={submitting}
                    className="bg-emerald-500 hover:bg-emerald-600"
                    data-testid="submit-exam"
                  >
                    {submitting ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4 mr-2" />
                    )}
                    Submit Exam
                  </Button>
                ) : (
                  <Button
                    onClick={() => setCurrentQuestion(prev => Math.min(questions.length - 1, prev + 1))}
                    className="bg-blue-500 hover:bg-blue-600"
                    data-testid="next-question"
                  >
                    Next
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
