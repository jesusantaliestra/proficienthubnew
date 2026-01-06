import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { Progress } from '../components/ui/progress';
import { 
  BookOpen, Headphones, Mic, PenTool, Clock, ChevronRight, 
  ChevronLeft, Check, X, Play, Pause, Square, Volume2,
  AlertCircle, CheckCircle, Loader2, RotateCcw
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function ExamSimulator() {
  const navigate = useNavigate();
  const { examType = 'ielts' } = useParams();
  const { user } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [examData, setExamData] = useState(null);
  const [currentSection, setCurrentSection] = useState('reading');
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [results, setResults] = useState(null);
  
  // Speaking test state
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [preparationTime, setPreparationTime] = useState(0);
  const [speakingTime, setSpeakingTime] = useState(0);
  const [speakingPhase, setSpeakingPhase] = useState('idle'); // idle, preparing, speaking, done
  
  // Audio refs
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);

  const sectionIcons = {
    reading: BookOpen,
    listening: Headphones,
    speaking: Mic,
    writing: PenTool
  };

  useEffect(() => {
    fetchExamData();
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [examType, currentSection]);

  const fetchExamData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/exams/${examType}/practice?section=${currentSection}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setExamData(response.data);
      setTimeRemaining(response.data.time_limit * 60);
      setCurrentQuestionIndex(0);
      setAnswers({});
    } catch (error) {
      console.error('Error fetching exam:', error);
      toast.error('Error loading exam');
    } finally {
      setLoading(false);
    }
  };

  // Timer effect
  useEffect(() => {
    if (timeRemaining > 0 && !showResults) {
      timerRef.current = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            clearInterval(timerRef.current);
            handleSubmitSection();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [currentSection, showResults]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerChange = (questionId, answer) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  // Recording functions for speaking tests
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(audioBlob);
        setAudioUrl(URL.createObjectURL(audioBlob));
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setSpeakingPhase('speaking');
    } catch (error) {
      console.error('Error starting recording:', error);
      toast.error('Could not access microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setSpeakingPhase('done');
    }
  };

  const startSpeakingTest = () => {
    const question = examData?.questions?.[currentQuestionIndex];
    if (!question) return;

    setSpeakingPhase('preparing');
    setPreparationTime(question.preparation_time || 60);
    setSpeakingTime(question.speaking_time || 120);

    // Preparation countdown
    const prepTimer = setInterval(() => {
      setPreparationTime(prev => {
        if (prev <= 1) {
          clearInterval(prepTimer);
          startRecording();
          // Start speaking countdown
          const speakTimer = setInterval(() => {
            setSpeakingTime(prev => {
              if (prev <= 1) {
                clearInterval(speakTimer);
                stopRecording();
                return 0;
              }
              return prev - 1;
            });
          }, 1000);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const submitSpeakingResponse = async () => {
    if (!audioBlob) return;

    try {
      setIsSubmitting(true);
      const token = localStorage.getItem('token');
      
      // Convert blob to base64
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = async () => {
        const base64Audio = reader.result.split(',')[1];
        
        const response = await axios.post(
          `${API_URL}/speaking-test/submit`,
          {
            exam_type: examType,
            prompt_id: examData?.questions?.[currentQuestionIndex]?.id || 'unknown',
            audio_base64: base64Audio
          },
          { headers: { Authorization: `Bearer ${token}` } }
        );

        toast.success('Speaking response submitted!');
        setResults(response.data);
        setShowResults(true);
      };
    } catch (error) {
      console.error('Error submitting speaking:', error);
      toast.error('Error submitting response');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitSection = async () => {
    setIsSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      
      // Calculate score locally for reading/listening
      let correctCount = 0;
      let totalQuestions = 0;
      
      examData?.questions?.forEach((q, idx) => {
        if (q.questions) {
          q.questions.forEach(subQ => {
            totalQuestions++;
            if (answers[subQ.id] === subQ.correct_answer) {
              correctCount++;
            }
          });
        } else if (q.correct_answer) {
          totalQuestions++;
          if (answers[q.id] === q.correct_answer) {
            correctCount++;
          }
        }
      });

      const score = totalQuestions > 0 ? (correctCount / totalQuestions) * 100 : 0;
      
      // Save attempt
      await axios.post(
        `${API_URL}/exams/submit`,
        {
          exam_type: examType,
          section: currentSection,
          answers,
          score,
          time_taken: (examData?.time_limit * 60) - timeRemaining
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setResults({
        score: score.toFixed(1),
        correct: correctCount,
        total: totalQuestions,
        bandScore: calculateBandScore(score)
      });
      setShowResults(true);
      toast.success('Section completed!');
    } catch (error) {
      console.error('Error submitting:', error);
      toast.error('Error submitting answers');
    } finally {
      setIsSubmitting(false);
    }
  };

  const calculateBandScore = (percentage) => {
    if (percentage >= 90) return 9;
    if (percentage >= 80) return 8;
    if (percentage >= 70) return 7;
    if (percentage >= 60) return 6;
    if (percentage >= 50) return 5;
    if (percentage >= 40) return 4;
    return 3;
  };

  const renderQuestion = () => {
    if (!examData?.questions) return null;
    
    if (currentSection === 'reading') {
      return renderReadingQuestion();
    } else if (currentSection === 'speaking') {
      return renderSpeakingQuestion();
    } else if (currentSection === 'writing') {
      return renderWritingQuestion();
    }
    return null;
  };

  const renderReadingQuestion = () => {
    const passage = examData.questions[currentQuestionIndex];
    if (!passage) return null;

    return (
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Passage */}
        <Card className="h-fit">
          <CardHeader>
            <CardTitle className="text-lg">{passage.passage?.title || 'Reading Passage'}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed">
              {passage.passage?.passage || passage.passage}
            </div>
          </CardContent>
        </Card>

        {/* Questions */}
        <div className="space-y-4">
          {(passage.questions || [passage]).map((q, idx) => (
            <Card key={q.id} className={answers[q.id] ? 'border-green-300 bg-green-50' : ''}>
              <CardContent className="p-4">
                <p className="font-semibold mb-3">
                  {idx + 1}. {q.question}
                </p>
                <div className="space-y-2">
                  {q.options?.map((option, optIdx) => (
                    <label
                      key={optIdx}
                      className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all
                        ${answers[q.id] === option.charAt(0) 
                          ? 'border-[#58CC02] bg-green-50' 
                          : 'border-gray-200 hover:border-gray-300'
                        }`}
                    >
                      <input
                        type="radio"
                        name={q.id}
                        value={option.charAt(0)}
                        checked={answers[q.id] === option.charAt(0)}
                        onChange={() => handleAnswerChange(q.id, option.charAt(0))}
                        className="w-4 h-4 text-[#58CC02]"
                      />
                      <span className="text-sm">{option}</span>
                    </label>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  };

  const renderSpeakingQuestion = () => {
    const question = examData.questions[currentQuestionIndex];
    if (!question) return null;

    return (
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mic className="w-5 h-5 text-[#58CC02]" />
              Speaking Task
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Prompt */}
            <div className="bg-gray-50 rounded-xl p-6">
              <h3 className="font-bold text-lg mb-3">{question.topic || 'Speaking Prompt'}</h3>
              <p className="text-gray-700 whitespace-pre-line">
                {question.cue_card || question.prompt}
              </p>
            </div>

            {/* Speaking Controls */}
            {speakingPhase === 'idle' && (
              <Button 
                className="w-full bg-[#58CC02] hover:bg-[#46A302]"
                onClick={startSpeakingTest}
              >
                <Play className="w-4 h-4 mr-2" />
                Start Speaking Test
              </Button>
            )}

            {speakingPhase === 'preparing' && (
              <div className="text-center py-8">
                <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-yellow-100 flex items-center justify-center">
                  <span className="text-3xl font-bold text-yellow-600">{preparationTime}</span>
                </div>
                <p className="text-lg font-semibold text-yellow-600">Preparation Time</p>
                <p className="text-gray-500">Read the prompt and prepare your response</p>
              </div>
            )}

            {speakingPhase === 'speaking' && (
              <div className="text-center py-8">
                <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center animate-pulse">
                  <Mic className="w-10 h-10 text-red-600" />
                </div>
                <p className="text-3xl font-bold text-red-600 mb-2">{formatTime(speakingTime)}</p>
                <p className="text-lg font-semibold">Recording...</p>
                <Button 
                  variant="outline" 
                  className="mt-4"
                  onClick={stopRecording}
                >
                  <Square className="w-4 h-4 mr-2" />
                  Stop Early
                </Button>
              </div>
            )}

            {speakingPhase === 'done' && (
              <div className="space-y-4">
                <div className="flex items-center justify-center gap-2 text-green-600">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-semibold">Recording Complete</span>
                </div>
                
                {audioUrl && (
                  <audio controls className="w-full" src={audioUrl} />
                )}

                <div className="flex gap-3">
                  <Button 
                    variant="outline" 
                    className="flex-1"
                    onClick={() => {
                      setAudioBlob(null);
                      setAudioUrl(null);
                      setSpeakingPhase('idle');
                    }}
                  >
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Re-record
                  </Button>
                  <Button 
                    className="flex-1 bg-[#58CC02] hover:bg-[#46A302]"
                    onClick={submitSpeakingResponse}
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <Check className="w-4 h-4 mr-2" />
                    )}
                    Submit for Evaluation
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderWritingQuestion = () => {
    const task = examData.questions[currentQuestionIndex];
    if (!task) return null;

    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PenTool className="w-5 h-5 text-[#58CC02]" />
              Writing Task
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-gray-50 rounded-xl p-6">
              <p className="text-gray-700">{task.prompt}</p>
              <div className="mt-4 flex gap-4 text-sm text-gray-500">
                <span>Minimum: {task.min_words} words</span>
                {task.max_words && <span>Maximum: {task.max_words} words</span>}
              </div>
            </div>

            <Textarea
              placeholder="Write your response here..."
              className="min-h-[400px] text-base"
              value={answers[task.id] || ''}
              onChange={(e) => handleAnswerChange(task.id, e.target.value)}
            />

            <div className="flex justify-between items-center text-sm text-gray-500">
              <span>
                Word count: {(answers[task.id] || '').split(/\s+/).filter(Boolean).length}
              </span>
              <Button 
                className="bg-[#58CC02] hover:bg-[#46A302]"
                onClick={handleSubmitSection}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Check className="w-4 h-4 mr-2" />
                )}
                Submit Essay
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-[#58CC02]" />
      </div>
    );
  }

  if (showResults) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-2xl mx-auto px-6">
          <Card>
            <CardHeader className="text-center">
              <CheckCircle className="w-16 h-16 mx-auto text-[#58CC02] mb-4" />
              <CardTitle className="text-2xl">Section Complete!</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {results?.evaluation ? (
                // Speaking results
                <div className="space-y-4">
                  <div className="bg-green-50 rounded-xl p-6 text-center">
                    <div className="text-4xl font-bold text-[#58CC02] mb-2">
                      Band {results.evaluation.overall_score || 6}
                    </div>
                    <p className="text-gray-600">Overall Score</p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    {['fluency_score', 'lexical_score', 'grammar_score', 'pronunciation_score'].map(key => (
                      results.evaluation[key] && (
                        <div key={key} className="bg-gray-50 rounded-lg p-4 text-center">
                          <div className="text-2xl font-bold text-gray-900">
                            {results.evaluation[key]}
                          </div>
                          <p className="text-sm text-gray-500 capitalize">
                            {key.replace('_score', '').replace('_', ' ')}
                          </p>
                        </div>
                      )
                    ))}
                  </div>

                  {results.evaluation.feedback && (
                    <div className="bg-blue-50 rounded-xl p-4">
                      <h4 className="font-semibold text-blue-800 mb-2">Feedback</h4>
                      <p className="text-blue-700 text-sm">{results.evaluation.feedback}</p>
                    </div>
                  )}

                  {results.transcription && (
                    <div className="bg-gray-50 rounded-xl p-4">
                      <h4 className="font-semibold text-gray-800 mb-2">Your Response (Transcribed)</h4>
                      <p className="text-gray-600 text-sm">{results.transcription}</p>
                    </div>
                  )}
                </div>
              ) : (
                // Reading/Listening results
                <div className="space-y-4">
                  <div className="bg-green-50 rounded-xl p-6 text-center">
                    <div className="text-4xl font-bold text-[#58CC02] mb-2">
                      {results?.score}%
                    </div>
                    <p className="text-gray-600">
                      {results?.correct}/{results?.total} correct
                    </p>
                    <p className="text-lg font-semibold text-gray-700 mt-2">
                      Estimated Band Score: {results?.bandScore}
                    </p>
                  </div>
                </div>
              )}

              <div className="flex gap-3">
                <Button 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => navigate('/student/dashboard')}
                >
                  Back to Dashboard
                </Button>
                <Button 
                  className="flex-1 bg-[#58CC02] hover:bg-[#46A302]"
                  onClick={() => {
                    setShowResults(false);
                    setResults(null);
                    setAnswers({});
                    setSpeakingPhase('idle');
                    setAudioBlob(null);
                    setAudioUrl(null);
                    fetchExamData();
                  }}
                >
                  Practice Again
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-xl font-bold text-gray-900">
                {examType.toUpperCase()} Practice
              </h1>
              <Badge className="bg-[#58CC02] text-white border-0 capitalize">
                {currentSection}
              </Badge>
            </div>
            
            <div className="flex items-center gap-4">
              <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
                timeRemaining < 300 ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'
              }`}>
                <Clock className="w-4 h-4" />
                <span className="font-mono font-bold">{formatTime(timeRemaining)}</span>
              </div>
              
              <Button 
                variant="outline" 
                onClick={() => navigate('/student/dashboard')}
              >
                Exit
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Section Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-2 py-4">
            {['reading', 'listening', 'speaking', 'writing'].map((section) => {
              const Icon = sectionIcons[section];
              return (
                <button
                  key={section}
                  onClick={() => setCurrentSection(section)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all ${
                    currentSection === section
                      ? 'bg-[#58CC02] text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="capitalize">{section}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {renderQuestion()}

        {/* Navigation for reading/listening */}
        {(currentSection === 'reading' || currentSection === 'listening') && (
          <div className="flex justify-between items-center mt-8">
            <Button
              variant="outline"
              disabled={currentQuestionIndex === 0}
              onClick={() => setCurrentQuestionIndex(prev => prev - 1)}
            >
              <ChevronLeft className="w-4 h-4 mr-2" />
              Previous
            </Button>

            <div className="flex items-center gap-2">
              {examData?.questions?.map((_, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentQuestionIndex(idx)}
                  className={`w-8 h-8 rounded-full text-sm font-semibold transition-all ${
                    currentQuestionIndex === idx
                      ? 'bg-[#58CC02] text-white'
                      : answers[examData.questions[idx]?.id || `q${idx}`]
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {idx + 1}
                </button>
              ))}
            </div>

            {currentQuestionIndex === (examData?.questions?.length || 1) - 1 ? (
              <Button 
                className="bg-[#58CC02] hover:bg-[#46A302]"
                onClick={handleSubmitSection}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Check className="w-4 h-4 mr-2" />
                )}
                Submit Section
              </Button>
            ) : (
              <Button
                onClick={() => setCurrentQuestionIndex(prev => prev + 1)}
              >
                Next
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
