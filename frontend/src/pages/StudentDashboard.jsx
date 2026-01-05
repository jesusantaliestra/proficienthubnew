import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  GraduationCap, BookOpen, Brain, Mic, BarChart3, Clock, Target, Award,
  ChevronRight, Play, CheckCircle, TrendingUp, Calendar, LogOut, Settings,
  MessageSquare, Headphones, PenTool, BookMarked
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';
import axios from 'axios';
import { toast, Toaster } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function StudentDashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [examHistory, setExamHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedExam, setSelectedExam] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await axios.get(`${API_URL}/exams/history`);
      setExamHistory(response.data.attempts || []);
    } catch (error) {
      console.error('Failed to fetch history:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/', { replace: true });
  };

  const examTypes = [
    { id: 'toefl', name: 'TOEFL', color: 'from-blue-500 to-blue-700', icon: '🎓', description: 'Test of English as a Foreign Language' },
    { id: 'ielts', name: 'IELTS', color: 'from-red-500 to-red-700', icon: '🌍', description: 'International English Language Testing System' },
    { id: 'cambridge', name: 'Cambridge', color: 'from-purple-500 to-purple-700', icon: '🏛️', description: 'Cambridge English Qualifications' },
    { id: 'pte', name: 'PTE', color: 'from-amber-500 to-amber-700', icon: '💻', description: 'Pearson Test of English' },
    { id: 'oet', name: 'OET', color: 'from-emerald-500 to-emerald-700', icon: '⚕️', description: 'Occupational English Test' }
  ];

  const sections = [
    { id: 'reading', name: 'Reading', icon: BookOpen, color: 'text-blue-400' },
    { id: 'listening', name: 'Listening', icon: Headphones, color: 'text-purple-400' },
    { id: 'speaking', name: 'Speaking', icon: Mic, color: 'text-amber-400' },
    { id: 'writing', name: 'Writing', icon: PenTool, color: 'text-emerald-400' }
  ];

  const skillsData = [
    { skill: 'Reading', score: 75 },
    { skill: 'Listening', score: 68 },
    { skill: 'Speaking', score: 72 },
    { skill: 'Writing', score: 65 },
    { skill: 'Grammar', score: 70 },
    { skill: 'Vocabulary', score: 78 }
  ];

  const progressData = [
    { week: 'W1', score: 60 },
    { week: 'W2', score: 65 },
    { week: 'W3', score: 62 },
    { week: 'W4', score: 70 },
    { week: 'W5', score: 75 },
    { week: 'W6', score: 78 }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-slate-400">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex" data-testid="student-dashboard">
      <Toaster position="top-right" richColors />
      
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900/50 border-r border-slate-800 flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="text-lg font-bold text-white font-outfit">ProficientHub</span>
              <p className="text-xs text-slate-500">Student Portal</p>
            </div>
          </div>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          <button
            onClick={() => setActiveTab('overview')}
            className={`sidebar-item w-full ${activeTab === 'overview' ? 'active' : ''}`}
            data-testid="nav-overview"
          >
            <BarChart3 className="w-5 h-5" />
            <span>Overview</span>
          </button>
          <button
            onClick={() => setActiveTab('practice')}
            className={`sidebar-item w-full ${activeTab === 'practice' ? 'active' : ''}`}
            data-testid="nav-practice"
          >
            <BookOpen className="w-5 h-5" />
            <span>Practice</span>
          </button>
          <button
            onClick={() => setActiveTab('tutor')}
            className={`sidebar-item w-full ${activeTab === 'tutor' ? 'active' : ''}`}
            data-testid="nav-tutor"
          >
            <Brain className="w-5 h-5" />
            <span>AI Tutor</span>
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`sidebar-item w-full ${activeTab === 'history' ? 'active' : ''}`}
            data-testid="nav-history"
          >
            <Clock className="w-5 h-5" />
            <span>History</span>
          </button>
        </nav>
        
        <div className="p-4 border-t border-slate-800 space-y-2">
          <button className="sidebar-item w-full" data-testid="nav-settings">
            <Settings className="w-5 h-5" />
            <span>Settings</span>
          </button>
          <button 
            onClick={handleLogout}
            className="sidebar-item w-full text-red-400 hover:text-red-300 hover:bg-red-500/10"
            data-testid="logout-btn"
          >
            <LogOut className="w-5 h-5" />
            <span>Log Out</span>
          </button>
        </div>
      </aside>
      
      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Header */}
        <header className="sticky top-0 z-10 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800 px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white font-outfit">
                Welcome back, {user?.name || 'Student'}!
              </h1>
              <p className="text-slate-400">Let's continue your learning journey</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-slate-400">Current Streak</p>
                <p className="text-2xl font-bold text-amber-400">🔥 7 days</p>
              </div>
            </div>
          </div>
        </header>
        
        <div className="p-8">
          {activeTab === 'overview' && (
            <div className="space-y-8 animate-fade-in" data-testid="overview-section">
              {/* Quick Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card className="metric-card" data-testid="stat-exams">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-slate-400 text-sm">Exams Completed</p>
                        <p className="text-3xl font-bold text-white font-outfit mt-1">{examHistory.length}</p>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
                        <BookOpen className="w-6 h-6 text-blue-400" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="metric-card" data-testid="stat-score">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-slate-400 text-sm">Average Score</p>
                        <p className="text-3xl font-bold text-emerald-400 font-outfit mt-1">
                          {examHistory.length > 0 
                            ? Math.round(examHistory.reduce((a, b) => a + b.score, 0) / examHistory.length)
                            : 0}%
                        </p>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                        <Target className="w-6 h-6 text-emerald-400" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="metric-card" data-testid="stat-time">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-slate-400 text-sm">Study Time</p>
                        <p className="text-3xl font-bold text-purple-400 font-outfit mt-1">12.5h</p>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                        <Clock className="w-6 h-6 text-purple-400" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="metric-card" data-testid="stat-goal">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-slate-400 text-sm">Goal Progress</p>
                        <p className="text-3xl font-bold text-amber-400 font-outfit mt-1">72%</p>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center">
                        <Award className="w-6 h-6 text-amber-400" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              {/* Charts */}
              <div className="grid lg:grid-cols-2 gap-6">
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardHeader>
                    <CardTitle className="text-white font-outfit">Progress Over Time</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                      <LineChart data={progressData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                        <XAxis dataKey="week" stroke="#64748b" />
                        <YAxis stroke="#64748b" />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                        />
                        <Line type="monotone" dataKey="score" stroke="#3b82f6" strokeWidth={3} dot={{ fill: '#3b82f6' }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
                
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardHeader>
                    <CardTitle className="text-white font-outfit">Skills Breakdown</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                      <RadarChart data={skillsData}>
                        <PolarGrid stroke="#334155" />
                        <PolarAngleAxis dataKey="skill" stroke="#64748b" />
                        <PolarRadiusAxis stroke="#64748b" />
                        <Radar name="Score" dataKey="score" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
              
              {/* Quick Actions */}
              <div>
                <h3 className="text-xl font-bold text-white font-outfit mb-4">Continue Learning</h3>
                <div className="grid md:grid-cols-3 gap-4">
                  {examTypes.slice(0, 3).map((exam) => (
                    <Card 
                      key={exam.id}
                      className="bg-slate-900/50 border-slate-800 hover:border-slate-700 cursor-pointer card-hover"
                      onClick={() => {
                        setSelectedExam(exam.id);
                        setActiveTab('practice');
                      }}
                      data-testid={`quick-action-${exam.id}`}
                    >
                      <CardContent className="p-6">
                        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${exam.color} flex items-center justify-center mb-4`}>
                          <span className="text-2xl">{exam.icon}</span>
                        </div>
                        <h4 className="text-lg font-bold text-white">{exam.name}</h4>
                        <p className="text-slate-400 text-sm mt-1">{exam.description}</p>
                        <Button className="w-full mt-4 bg-slate-800 hover:bg-slate-700">
                          <Play className="w-4 h-4 mr-2" />
                          Start Practice
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'practice' && (
            <div className="space-y-8 animate-fade-in" data-testid="practice-section">
              <div>
                <h2 className="text-2xl font-bold text-white font-outfit mb-2">Choose Your Exam</h2>
                <p className="text-slate-400">Select an exam type to start practicing</p>
              </div>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {examTypes.map((exam) => (
                  <Card 
                    key={exam.id}
                    className={`bg-slate-900/50 border-slate-800 hover:border-blue-500/50 cursor-pointer transition-all duration-300 ${selectedExam === exam.id ? 'border-blue-500 ring-2 ring-blue-500/20' : ''}`}
                    onClick={() => setSelectedExam(exam.id)}
                    data-testid={`exam-select-${exam.id}`}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${exam.color} flex items-center justify-center`}>
                          <span className="text-3xl">{exam.icon}</span>
                        </div>
                        {selectedExam === exam.id && (
                          <CheckCircle className="w-6 h-6 text-blue-400" />
                        )}
                      </div>
                      <h3 className="text-xl font-bold text-white mb-2">{exam.name}</h3>
                      <p className="text-slate-400 text-sm">{exam.description}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
              
              {selectedExam && (
                <div className="animate-slide-up">
                  <h3 className="text-xl font-bold text-white font-outfit mb-4">Select Section</h3>
                  <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {sections.map((section) => (
                      <Card 
                        key={section.id}
                        className="bg-slate-900/50 border-slate-800 hover:border-slate-700 cursor-pointer card-hover"
                        data-testid={`section-${section.id}`}
                      >
                        <CardContent className="p-6 text-center">
                          <div className={`w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center mx-auto mb-4 ${section.color}`}>
                            <section.icon className="w-6 h-6" />
                          </div>
                          <h4 className="text-lg font-bold text-white">{section.name}</h4>
                          <Button 
                            className="w-full mt-4 bg-blue-500 hover:bg-blue-600"
                            onClick={() => navigate(`/exam/${selectedExam}/${section.id}`)}
                          >
                            Start
                            <ChevronRight className="w-4 h-4 ml-1" />
                          </Button>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'tutor' && (
            <div className="space-y-6 animate-fade-in" data-testid="tutor-section">
              <div>
                <h2 className="text-2xl font-bold text-white font-outfit mb-2">AI Tutor</h2>
                <p className="text-slate-400">Get personalized help from our AI tutors</p>
              </div>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {examTypes.map((exam) => (
                  <Card 
                    key={exam.id}
                    className="bg-slate-900/50 border-slate-800 hover:border-slate-700 cursor-pointer card-hover"
                    onClick={() => navigate(`/tutor/${exam.id}`)}
                    data-testid={`tutor-${exam.id}`}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4 mb-4">
                        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${exam.color} flex items-center justify-center`}>
                          <Brain className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <h3 className="text-lg font-bold text-white">{exam.name} Tutor</h3>
                          <p className="text-slate-500 text-sm">Expert AI guidance</p>
                        </div>
                      </div>
                      <p className="text-slate-400 text-sm mb-4">
                        Get instant answers to your questions about {exam.name} exam strategies, tips, and practice.
                      </p>
                      <Button className="w-full bg-slate-800 hover:bg-slate-700">
                        <MessageSquare className="w-4 h-4 mr-2" />
                        Start Chat
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
          
          {activeTab === 'history' && (
            <div className="space-y-6 animate-fade-in" data-testid="history-section">
              <div>
                <h2 className="text-2xl font-bold text-white font-outfit mb-2">Practice History</h2>
                <p className="text-slate-400">View your past exam attempts and performance</p>
              </div>
              
              {examHistory.length === 0 ? (
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardContent className="py-16 text-center">
                    <BookMarked className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">No Practice History Yet</h3>
                    <p className="text-slate-400 mb-6">Start practicing to see your progress here</p>
                    <Button 
                      className="bg-blue-500 hover:bg-blue-600"
                      onClick={() => setActiveTab('practice')}
                    >
                      <Play className="w-4 h-4 mr-2" />
                      Start Practicing
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <Card className="bg-slate-900/50 border-slate-800 overflow-hidden">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Exam</th>
                        <th>Section</th>
                        <th>Score</th>
                        <th>Time Spent</th>
                        <th>Feedback</th>
                      </tr>
                    </thead>
                    <tbody>
                      {examHistory.map((attempt) => (
                        <tr key={attempt.id}>
                          <td>{new Date(attempt.created_at).toLocaleDateString()}</td>
                          <td>
                            <Badge className={`badge-${attempt.exam_type}`}>
                              {attempt.exam_type.toUpperCase()}
                            </Badge>
                          </td>
                          <td className="capitalize">{attempt.section}</td>
                          <td>
                            <span className={attempt.score >= 70 ? 'text-emerald-400' : 'text-amber-400'}>
                              {attempt.score}%
                            </span>
                          </td>
                          <td>{Math.round(attempt.time_spent / 60)} min</td>
                          <td className="max-w-xs truncate text-slate-400">{attempt.feedback}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Card>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
