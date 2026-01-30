import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { 
  BookOpen, CheckCircle, Lock, Play, Trophy, 
  TrendingUp, Clock, Star, ArrowRight, Plus,
  Brain, Target, Award, Layers, FileText, Info
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import LanguageSelector from '../components/LanguageSelector';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function SequentialExamDashboard() {
  const { examType } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();
  
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [examModes, setExamModes] = useState(null);
  const [inProgressExams, setInProgressExams] = useState([]);
  const [showModeDialog, setShowModeDialog] = useState(false);
  const [selectedExam, setSelectedExam] = useState(null);
  const [startingExam, setStartingExam] = useState(false);
  
  const token = localStorage.getItem('token');

  useEffect(() => {
    loadDashboard();
    loadExamModes();
    loadInProgressExams();
  }, [examType]);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const res = await axios.get(
        `${API_URL}/api/sequential-exams/dashboard/${examType}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setDashboard(res.data);
    } catch (err) {
      console.error('Error loading dashboard:', err);
      toast.error('Error loading exam dashboard');
    }
    setLoading(false);
  };

  const loadExamModes = async () => {
    try {
      const res = await axios.get(
        `${API_URL}/api/sequential-exams/available-modes/${examType}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setExamModes(res.data);
    } catch (err) {
      console.error('Error loading exam modes:', err);
    }
  };

  const loadInProgressExams = async () => {
    try {
      const res = await axios.get(
        `${API_URL}/api/sequential-exams/in-progress`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setInProgressExams(res.data.exams_in_progress || []);
    } catch (err) {
      console.error('Error loading in-progress exams:', err);
    }
  };

  const startExam = (examId) => {
    // Check if this exam is already in progress
    const inProgress = inProgressExams.find(e => e.exam_id === examId && e.exam_type === examType);
    if (inProgress) {
      // Resume the exam
      navigate(`/exam/${examType}/${examId}?mode=${inProgress.mode}`);
      return;
    }
    // Show mode selection dialog
    setSelectedExam(examId);
    setShowModeDialog(true);
  };

  const handleStartExamWithMode = async (mode, section = null) => {
    setStartingExam(true);
    try {
      const payload = {
        exam_id: selectedExam,
        mode: mode,
        ...(section && { section })
      };
      
      await axios.post(
        `${API_URL}/api/sequential-exams/start/${examType}/${selectedExam}`,
        payload,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setShowModeDialog(false);
      
      // Navigate to exam
      if (mode === 'full') {
        navigate(`/exam/${examType}?exam_id=${selectedExam}&mode=full`);
      } else {
        navigate(`/exam/${examType}/${section}?exam_id=${selectedExam}&mode=section`);
      }
    } catch (err) {
      console.error('Error starting exam:', err);
      toast.error(err.response?.data?.detail || 'Error al iniciar el examen');
    }
    setStartingExam(false);
  };

  const handleUpsell = () => {
    navigate(`/pricing?exam=${examType}&upsell=true`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!dashboard || dashboard.exams.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 flex items-center justify-center p-6">
        <Card className="bg-slate-900/50 border-slate-800 max-w-md w-full">
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 bg-violet-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <BookOpen className="w-8 h-8 text-violet-400" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-3">No Exams Yet</h2>
            <p className="text-slate-400 mb-6">
              {dashboard?.message || 'Purchase a plan to unlock your first set of exams!'}
            </p>
            <Button 
              onClick={() => navigate('/pricing')}
              className="bg-gradient-to-r from-violet-600 to-indigo-600"
            >
              View Plans
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const { stats, exams, has_ai, next_exam } = dashboard;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950">
      {/* Header */}
      <header className="bg-slate-900/50 border-b border-slate-800 sticky top-0 z-40 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">
                {examType.toUpperCase()} Exams
              </h1>
              <p className="text-slate-400">
                {stats.completed} / {stats.total_purchased} completed
              </p>
            </div>
            
            <div className="flex items-center gap-4">
              {has_ai && (
                <Badge className="bg-gradient-to-r from-violet-500 to-indigo-500">
                  <Brain className="w-3 h-3 mr-1" />
                  AI Tutor Enabled
                </Badge>
              )}
              <Button onClick={handleUpsell} variant="outline" className="border-emerald-500 text-emerald-400">
                <Plus className="w-4 h-4 mr-2" />
                Get More Exams
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Total Exams</p>
                  <p className="text-2xl font-bold text-white">{stats.total_purchased}</p>
                </div>
                <BookOpen className="w-8 h-8 text-violet-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Completed</p>
                  <p className="text-2xl font-bold text-emerald-400">{stats.completed}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-emerald-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Remaining</p>
                  <p className="text-2xl font-bold text-amber-400">{stats.remaining}</p>
                </div>
                <Target className="w-8 h-8 text-amber-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Progress</p>
                  <p className="text-2xl font-bold text-cyan-400">{stats.completion_rate}%</p>
                </div>
                <TrendingUp className="w-8 h-8 text-cyan-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Progress Bar */}
        <Card className="bg-slate-900/50 border-slate-800 mb-8">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Your Progress</h3>
              <span className="text-sm text-slate-400">
                {stats.completed} of {stats.total_purchased} exams
              </span>
            </div>
            <Progress value={stats.completion_rate} className="h-3" />
            
            {next_exam && (
              <div className="mt-4 flex items-center justify-between p-4 bg-gradient-to-r from-violet-900/30 to-indigo-900/30 rounded-xl border border-violet-800/50">
                <div className="flex items-center gap-3">
                  <Play className="w-5 h-5 text-violet-400" />
                  <div>
                    <p className="text-white font-medium">Next Up: Exam {next_exam}</p>
                    <p className="text-sm text-slate-400">Continue your preparation</p>
                  </div>
                </div>
                <Button 
                  onClick={() => startExam(next_exam)}
                  className="bg-gradient-to-r from-violet-600 to-indigo-600"
                >
                  Start Now
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Exam Grid */}
        <h3 className="text-xl font-bold text-white mb-4">Your Exams</h3>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {exams.map((exam) => (
            <Card 
              key={exam.exam_id}
              className={`bg-slate-900/50 border-slate-800 overflow-hidden transition-all hover:border-slate-700 ${
                exam.status === 'completed' ? 'ring-2 ring-emerald-500/30' : ''
              }`}
            >
              <div className={`h-1.5 ${
                exam.status === 'completed' 
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500' 
                  : 'bg-gradient-to-r from-violet-500 to-indigo-500'
              }`} />
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <Badge className={
                    exam.status === 'completed'
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : 'bg-violet-500/20 text-violet-400'
                  }>
                    {exam.exam_id}
                  </Badge>
                  {exam.status === 'completed' && (
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                  )}
                </div>
                
                <h4 className="font-bold text-white mb-1">
                  Exam {exam.exam_number}
                </h4>
                
                {exam.status === 'completed' ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Star className="w-4 h-4 text-amber-400" />
                      <span className="text-white font-bold">{exam.score || '—'}%</span>
                    </div>
                    <Button 
                      size="sm" 
                      variant="outline"
                      className="w-full border-slate-700"
                      onClick={() => navigate(`/results/${examType}/${exam.exam_id}`)}
                    >
                      View Results
                    </Button>
                  </div>
                ) : (
                  <Button 
                    size="sm"
                    className="w-full mt-2 bg-gradient-to-r from-violet-600 to-indigo-600"
                    onClick={() => startExam(exam.exam_id)}
                  >
                    <Play className="w-4 h-4 mr-1" />
                    Start
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
          
          {/* Upsell Card */}
          <Card 
            className="bg-gradient-to-br from-emerald-900/30 to-teal-900/30 border-emerald-800/50 cursor-pointer hover:border-emerald-600/50 transition-colors"
            onClick={handleUpsell}
          >
            <CardContent className="p-4 h-full flex flex-col items-center justify-center text-center min-h-[150px]">
              <Plus className="w-10 h-10 text-emerald-400 mb-2" />
              <h4 className="font-bold text-white">Get More</h4>
              <p className="text-sm text-emerald-300">Unlock next 5 exams</p>
            </CardContent>
          </Card>
        </div>

        {/* Achievement Section */}
        {stats.completed > 0 && (
          <Card className="bg-slate-900/50 border-slate-800 mt-8">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Trophy className="w-5 h-5 text-amber-400" />
                Achievements
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                {stats.completed >= 1 && (
                  <Badge className="bg-amber-500/20 text-amber-400 py-2 px-4">
                    <Award className="w-4 h-4 mr-2" />
                    First Exam Complete
                  </Badge>
                )}
                {stats.completed >= 5 && (
                  <Badge className="bg-violet-500/20 text-violet-400 py-2 px-4">
                    <Star className="w-4 h-4 mr-2" />
                    5 Exams Complete
                  </Badge>
                )}
                {stats.completed >= 10 && (
                  <Badge className="bg-emerald-500/20 text-emerald-400 py-2 px-4">
                    <Trophy className="w-4 h-4 mr-2" />
                    10 Exams Complete
                  </Badge>
                )}
                {stats.completion_rate >= 50 && (
                  <Badge className="bg-cyan-500/20 text-cyan-400 py-2 px-4">
                    <TrendingUp className="w-4 h-4 mr-2" />
                    Halfway There!
                  </Badge>
                )}
                {stats.completion_rate === 100 && (
                  <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white py-2 px-4">
                    <Trophy className="w-4 h-4 mr-2" />
                    All Exams Complete!
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
