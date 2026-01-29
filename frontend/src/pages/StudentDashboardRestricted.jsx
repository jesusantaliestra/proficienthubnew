import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import {
  GraduationCap, BookOpen, Brain, Mic, BarChart3, Clock, Target, Award,
  ChevronRight, Play, CheckCircle, TrendingUp, Calendar, LogOut, Settings,
  MessageSquare, Headphones, PenTool, BookMarked, Video, Star, Zap, Trophy,
  Flame, Gift, Users, Lock, Crown
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';
import axios from 'axios';
import { toast, Toaster } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Exam configuration with colors and icons
const EXAM_CONFIG = {
  toefl: { name: 'TOEFL', color: 'from-blue-500 to-blue-700', icon: '🎓', description: 'Test of English as a Foreign Language' },
  ielts: { name: 'IELTS', color: 'from-red-500 to-red-700', icon: '🌍', description: 'International English Language Testing System' },
  cambridge: { name: 'Cambridge', color: 'from-purple-500 to-purple-700', icon: '🏛️', description: 'Cambridge English Qualifications' },
  trinity: { name: 'Trinity', color: 'from-pink-500 to-pink-700', icon: '🎭', description: 'Trinity College London GESE & ISE' },
  toeic: { name: 'TOEIC', color: 'from-indigo-500 to-indigo-700', icon: '💼', description: 'Test of English for International Communication' },
  celpip: { name: 'CELPIP', color: 'from-cyan-500 to-cyan-700', icon: '🍁', description: 'Canadian English Language Proficiency Index' },
  pte: { name: 'PTE', color: 'from-amber-500 to-amber-700', icon: '💻', description: 'Pearson Test of English' },
  oet: { name: 'OET', color: 'from-emerald-500 to-emerald-700', icon: '⚕️', description: 'Occupational English Test' }
};

// Badge definitions
const BADGES = [
  { id: 'first_exam', name: 'First Steps', icon: '🎯', description: 'Complete your first exam', xp: 50 },
  { id: 'streak_7', name: 'Week Warrior', icon: '🔥', description: '7 day study streak', xp: 100 },
  { id: 'streak_30', name: 'Monthly Master', icon: '💪', description: '30 day study streak', xp: 500 },
  { id: 'perfect_score', name: 'Perfectionist', icon: '⭐', description: 'Get 100% on any section', xp: 200 },
  { id: 'speed_demon', name: 'Speed Demon', icon: '⚡', description: 'Complete exam in record time', xp: 150 },
  { id: 'night_owl', name: 'Night Owl', icon: '🦉', description: 'Study after midnight', xp: 50 },
  { id: 'early_bird', name: 'Early Bird', icon: '🐦', description: 'Study before 6 AM', xp: 50 },
  { id: 'social_learner', name: 'Social Learner', icon: '👥', description: 'Join a live class', xp: 75 },
  { id: 'tutor_friend', name: 'AI Best Friend', icon: '🤖', description: 'Have 10 AI tutor sessions', xp: 100 },
  { id: 'vocabulary_master', name: 'Vocabulary Master', icon: '📚', description: 'Learn 500 words', xp: 300 },
];

// Level thresholds
const LEVELS = [
  { level: 1, name: 'Beginner', minXP: 0, maxXP: 100 },
  { level: 2, name: 'Novice', minXP: 100, maxXP: 300 },
  { level: 3, name: 'Apprentice', minXP: 300, maxXP: 600 },
  { level: 4, name: 'Intermediate', minXP: 600, maxXP: 1000 },
  { level: 5, name: 'Advanced', minXP: 1000, maxXP: 1500 },
  { level: 6, name: 'Expert', minXP: 1500, maxXP: 2200 },
  { level: 7, name: 'Master', minXP: 2200, maxXP: 3000 },
  { level: 8, name: 'Grandmaster', minXP: 3000, maxXP: 4000 },
  { level: 9, name: 'Legend', minXP: 4000, maxXP: 5500 },
  { level: 10, name: 'Champion', minXP: 5500, maxXP: Infinity },
];

export default function StudentDashboardRestricted() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [examHistory, setExamHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [studentData, setStudentData] = useState(null);
  const [gamificationData, setGamificationData] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [upcomingClasses, setUpcomingClasses] = useState([]);
  const [challenges, setChallenges] = useState([]);

  // Get the exam the student is assigned to
  const assignedExam = studentData?.current_exam || user?.current_exam;
  const examConfig = assignedExam ? EXAM_CONFIG[assignedExam] : null;

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [historyRes, profileRes, classesRes] = await Promise.all([
        axios.get(`${API_URL}/exams/history`, { headers }),
        axios.get(`${API_URL}/student/profile`, { headers }),
        axios.get(`${API_URL}/student/upcoming-classes`, { headers }).catch(() => ({ data: { classes: [] } }))
      ]);
      
      setExamHistory(historyRes.data.attempts || []);
      setStudentData(profileRes.data);
      setUpcomingClasses(classesRes.data.classes || []);
      
      // Fetch gamification data from new endpoints
      try {
        const [badgesRes, streakRes, pointsRes, leaderboardRes] = await Promise.all([
          axios.get(`${API_URL}/gamification/badges/my`, { headers }),
          axios.get(`${API_URL}/gamification/streak`, { headers }),
          axios.get(`${API_URL}/gamification/points`, { headers }),
          axios.get(`${API_URL}/gamification/leaderboard?timeframe=weekly&limit=10`, { headers })
        ]);
        
        setGamificationData({
          gamification_enabled: true,
          badges: badgesRes.data.earned || [],
          badges_in_progress: badgesRes.data.in_progress || [],
          total_badges: badgesRes.data.total_badges || 0,
          xp: pointsRes.data.total_points || 0,
          badge_points: pointsRes.data.badge_points || 0,
          activity_points: pointsRes.data.activity_points || 0,
          streak: streakRes.data.current_streak || 0,
          longest_streak: streakRes.data.longest_streak || 0
        });
        
        setLeaderboard(leaderboardRes.data.leaderboard || []);
        
        // Record activity for streak
        await axios.post(`${API_URL}/gamification/streak/activity`, {}, { headers }).catch(() => {});
        
        // Check for new badges
        const badgeCheckRes = await axios.post(`${API_URL}/gamification/badges/check`, {}, { headers }).catch(() => ({ data: { newly_earned: [] } }));
        if (badgeCheckRes.data.newly_earned?.length > 0) {
          badgeCheckRes.data.newly_earned.forEach(badge => {
            toast.success(`🏆 New Badge: ${badge.name}!`, { description: badge.description });
          });
        }
      } catch (gamErr) {
        console.log('Gamification not available:', gamErr);
        setGamificationData({ gamification_enabled: false });
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/', { replace: true });
  };

  const getCurrentLevel = () => {
    const xp = gamificationData?.xp || 0;
    return LEVELS.find(l => xp >= l.minXP && xp < l.maxXP) || LEVELS[0];
  };

  const getXPProgress = () => {
    const xp = gamificationData?.xp || 0;
    const level = getCurrentLevel();
    const levelXP = xp - level.minXP;
    const levelRange = level.maxXP === Infinity ? 1000 : level.maxXP - level.minXP;
    return Math.min((levelXP / levelRange) * 100, 100);
  };

  const sections = [
    { id: 'reading', name: 'Reading', icon: BookOpen, color: 'text-blue-400' },
    { id: 'listening', name: 'Listening', icon: Headphones, color: 'text-purple-400' },
    { id: 'speaking', name: 'Speaking', icon: Mic, color: 'text-amber-400' },
    { id: 'writing', name: 'Writing', icon: PenTool, color: 'text-emerald-400' }
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

  // If no exam assigned, show restricted message
  if (!assignedExam) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <Card className="bg-slate-900 border-slate-800 max-w-md">
          <CardContent className="p-8 text-center">
            <Lock className="w-16 h-16 text-slate-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">No Exam Assigned</h2>
            <p className="text-slate-400 mb-6">
              Your institution has not yet assigned you an exam to prepare for. 
              Please contact your administrator.
            </p>
            <Button onClick={handleLogout} variant="outline">
              <LogOut className="w-4 h-4 mr-2" /> Log Out
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex" data-testid="student-dashboard-restricted">
      <Toaster position="top-right" richColors />
      
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900/50 border-r border-slate-800 flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${examConfig?.color || 'from-blue-500 to-blue-600'} flex items-center justify-center`}>
              <span className="text-xl">{examConfig?.icon || '📚'}</span>
            </div>
            <div>
              <span className="text-lg font-bold text-white font-outfit">{examConfig?.name || 'ProficientHub'}</span>
              <p className="text-xs text-slate-500">Student Portal</p>
            </div>
          </div>
        </div>
        
        {/* XP and Level Display */}
        {gamificationData?.gamification_enabled && (
          <div className="p-4 border-b border-slate-800">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-amber-400">Level {getCurrentLevel().level}</span>
              <span className="text-xs text-slate-500">{gamificationData?.xp || 0} XP</span>
            </div>
            <Progress value={getXPProgress()} className="h-2 bg-slate-800" />
            <p className="text-xs text-slate-500 mt-1">{getCurrentLevel().name}</p>
          </div>
        )}
        
        <nav className="flex-1 p-4 space-y-2">
          {[
            { id: 'overview', icon: BarChart3, label: 'Overview' },
            { id: 'practice', icon: BookOpen, label: 'Practice' },
            { id: 'tutor', icon: Brain, label: 'AI Tutor' },
            { id: 'classes', icon: Video, label: 'Live Classes' },
            ...(gamificationData?.gamification_enabled ? [
              { id: 'achievements', icon: Trophy, label: 'Achievements' },
              { id: 'leaderboard', icon: Users, label: 'Leaderboard' },
            ] : []),
            { id: 'history', icon: Clock, label: 'History' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`sidebar-item w-full ${activeTab === item.id ? 'active' : ''}`}
              data-testid={`nav-${item.id}`}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        
        {/* Streak Display */}
        {gamificationData?.gamification_enabled && (
          <div className="p-4 border-t border-slate-800">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center">
                <Flame className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{gamificationData?.streak || 0}</p>
                <p className="text-xs text-slate-500">Day Streak</p>
              </div>
            </div>
          </div>
        )}
        
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
        {/* Header with Exam Badge */}
        <header className="sticky top-0 z-10 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800 px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white font-outfit">
                Welcome back, {user?.name || 'Student'}!
              </h1>
              <div className="flex items-center gap-2 mt-1">
                <Badge className={`bg-gradient-to-r ${examConfig?.color} text-white border-0`}>
                  {examConfig?.icon} {examConfig?.name} Preparation
                </Badge>
                <span className="text-slate-500 text-sm">|</span>
                <span className="text-slate-400 text-sm">{studentData?.credits || 0} credits remaining</span>
              </div>
            </div>
            {gamificationData?.gamification_enabled && (
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-sm text-slate-400">Daily XP</p>
                  <p className="text-xl font-bold text-green-400">+{gamificationData?.daily_xp || 0}</p>
                </div>
              </div>
            )}
          </div>
        </header>
        
        <div className="p-8">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-8 animate-fade-in" data-testid="overview-section">
              {/* Quick Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card className="bg-slate-900/50 border-slate-800" data-testid="stat-exams">
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
                
                <Card className="bg-slate-900/50 border-slate-800" data-testid="stat-avg-score">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-slate-400 text-sm">Average Score</p>
                        <p className="text-3xl font-bold text-white font-outfit mt-1">
                          {examHistory.length > 0 
                            ? Math.round(examHistory.reduce((a, b) => a + (b.score || 0), 0) / examHistory.length)
                            : 0}%
                        </p>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-green-500/10 flex items-center justify-center">
                        <TrendingUp className="w-6 h-6 text-green-400" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="bg-slate-900/50 border-slate-800" data-testid="stat-credits">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-slate-400 text-sm">Credits Left</p>
                        <p className="text-3xl font-bold text-white font-outfit mt-1">{studentData?.credits || 0}</p>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center">
                        <Zap className="w-6 h-6 text-amber-400" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                {gamificationData?.gamification_enabled && (
                  <Card className="bg-slate-900/50 border-slate-800" data-testid="stat-badges">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-slate-400 text-sm">Badges Earned</p>
                          <p className="text-3xl font-bold text-white font-outfit mt-1">
                            {gamificationData?.badges?.length || 0}
                          </p>
                        </div>
                        <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                          <Trophy className="w-6 h-6 text-purple-400" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Active Challenges */}
              {gamificationData?.gamification_enabled && challenges.length > 0 && (
                <Card className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 border-purple-500/30">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <Gift className="w-5 h-5 text-pink-400" />
                      Weekly Challenges
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-3 gap-4">
                      {challenges.slice(0, 3).map((challenge, i) => (
                        <div key={i} className="bg-slate-900/50 rounded-xl p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-lg">{challenge.icon}</span>
                            <Badge className="bg-amber-500/20 text-amber-400">+{challenge.xp_reward} XP</Badge>
                          </div>
                          <h4 className="font-semibold text-white mb-1">{challenge.name}</h4>
                          <p className="text-xs text-slate-400 mb-3">{challenge.description}</p>
                          <Progress value={(challenge.progress / challenge.target) * 100} className="h-2 bg-slate-800" />
                          <p className="text-xs text-slate-500 mt-1">{challenge.progress}/{challenge.target}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Upcoming Live Classes */}
              {upcomingClasses.length > 0 && (
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <Video className="w-5 h-5 text-blue-400" />
                      Upcoming Live Classes
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {upcomingClasses.slice(0, 3).map((cls, i) => (
                        <div key={i} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                          <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                              <Video className="w-6 h-6 text-blue-400" />
                            </div>
                            <div>
                              <h4 className="font-semibold text-white">{cls.title}</h4>
                              <p className="text-sm text-slate-400">{cls.instructor}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-sm text-slate-400">{new Date(cls.start_time).toLocaleDateString()}</p>
                            <p className="text-sm text-blue-400">{new Date(cls.start_time).toLocaleTimeString()}</p>
                          </div>
                          <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                            Join
                          </Button>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Practice Sections - Only for Assigned Exam */}
              <Card className="bg-slate-900/50 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Target className="w-5 h-5 text-green-400" />
                    {examConfig?.name} Practice Sections
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-4 gap-4">
                    {sections.map((section) => (
                      <button
                        key={section.id}
                        onClick={() => navigate(`/exam/${assignedExam}?section=${section.id}`)}
                        className="p-6 bg-slate-800/50 rounded-xl hover:bg-slate-800 transition-all group"
                        data-testid={`practice-${section.id}`}
                      >
                        <section.icon className={`w-8 h-8 ${section.color} mb-3`} />
                        <h4 className="font-semibold text-white mb-1">{section.name}</h4>
                        <p className="text-xs text-slate-500">Practice {examConfig?.name} {section.name}</p>
                        <ChevronRight className="w-5 h-5 text-slate-500 mt-3 group-hover:translate-x-1 transition-transform" />
                      </button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Practice Tab - Only Assigned Exam */}
          {activeTab === 'practice' && (
            <div className="space-y-6 animate-fade-in" data-testid="practice-section">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-white">{examConfig?.name} Practice</h2>
                  <p className="text-slate-400">{examConfig?.description}</p>
                </div>
              </div>
              
              {/* Single Exam Card - Not a list */}
              <Card className={`bg-gradient-to-br ${examConfig?.color} border-0 overflow-hidden`}>
                <CardContent className="p-8">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-6xl mb-4 block">{examConfig?.icon}</span>
                      <h3 className="text-3xl font-bold text-white mb-2">{examConfig?.name}</h3>
                      <p className="text-white/80 mb-6">{examConfig?.description}</p>
                      <div className="flex gap-3">
                        <Button 
                          onClick={() => navigate(`/exam/${assignedExam}`)}
                          className="bg-white text-gray-900 hover:bg-gray-100"
                          data-testid="start-full-exam"
                        >
                          <Play className="w-4 h-4 mr-2" /> Start Full Exam
                        </Button>
                        <Button 
                          onClick={() => navigate(`/tutor?exam=${assignedExam}`)}
                          variant="outline"
                          className="border-white/30 text-white hover:bg-white/10"
                        >
                          <Brain className="w-4 h-4 mr-2" /> AI Tutor
                        </Button>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="bg-white/20 rounded-xl p-4 backdrop-blur">
                        <p className="text-white/80 text-sm">Your Progress</p>
                        <p className="text-4xl font-bold text-white">
                          {examHistory.filter(e => e.exam_type === assignedExam).length}
                        </p>
                        <p className="text-white/60 text-sm">exams completed</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Section Practice */}
              <div className="grid md:grid-cols-2 gap-6">
                {sections.map((section) => (
                  <Card key={section.id} className="bg-slate-900/50 border-slate-800 hover:border-slate-700 transition-colors cursor-pointer"
                    onClick={() => navigate(`/exam/${assignedExam}?section=${section.id}`)}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className={`w-14 h-14 rounded-xl bg-slate-800 flex items-center justify-center`}>
                          <section.icon className={`w-7 h-7 ${section.color}`} />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-bold text-white text-lg">{section.name}</h4>
                          <p className="text-slate-400 text-sm">Practice {examConfig?.name} {section.name} skills</p>
                        </div>
                        <ChevronRight className="w-6 h-6 text-slate-500" />
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Achievements Tab */}
          {activeTab === 'achievements' && gamificationData?.gamification_enabled && (
            <div className="space-y-6 animate-fade-in" data-testid="achievements-section">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">Achievements & Badges</h2>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-amber-400 font-bold text-lg">{gamificationData?.xp || 0} XP</p>
                    <p className="text-slate-500 text-xs">Total Points</p>
                  </div>
                  <div className="text-right">
                    <p className="text-white font-bold text-lg">{gamificationData?.total_badges || 0}/15</p>
                    <p className="text-slate-500 text-xs">Badges Earned</p>
                  </div>
                </div>
              </div>

              {/* Earned Badges */}
              {gamificationData?.badges?.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Trophy className="w-5 h-5 text-amber-400" />
                    Earned Badges
                  </h3>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {gamificationData.badges.map((badge) => (
                      <Card key={badge.id} className="bg-gradient-to-br from-amber-900/30 to-orange-900/30 border-2 border-amber-500/50">
                        <CardContent className="p-6 text-center">
                          <div className="w-16 h-16 mx-auto mb-3 rounded-full bg-amber-500/20 flex items-center justify-center">
                            <Award className="w-8 h-8 text-amber-400" />
                          </div>
                          <h4 className="font-bold text-white mb-1">{badge.name}</h4>
                          <p className="text-sm text-slate-400 mb-3">{badge.description}</p>
                          <div className="flex items-center justify-center gap-2">
                            <Badge className="bg-amber-500/20 text-amber-400 border-0">+{badge.points} XP</Badge>
                            <Badge className={`border-0 ${
                              badge.rarity === 'legendary' ? 'bg-purple-500/20 text-purple-400' :
                              badge.rarity === 'rare' ? 'bg-blue-500/20 text-blue-400' :
                              badge.rarity === 'uncommon' ? 'bg-green-500/20 text-green-400' :
                              'bg-slate-500/20 text-slate-400'
                            }`}>{badge.rarity}</Badge>
                          </div>
                          <p className="text-xs text-green-400 mt-2">✓ Earned {badge.earned_at ? new Date(badge.earned_at).toLocaleDateString() : ''}</p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* In Progress Badges */}
              {gamificationData?.badges_in_progress?.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Target className="w-5 h-5 text-blue-400" />
                    Almost There!
                  </h3>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {gamificationData.badges_in_progress.map((badge) => (
                      <Card key={badge.id} className="bg-slate-900/50 border-slate-800 border-2">
                        <CardContent className="p-6">
                          <div className="flex items-start gap-4">
                            <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                              <Award className="w-6 h-6 text-blue-400" />
                            </div>
                            <div className="flex-1">
                              <h4 className="font-bold text-white mb-1">{badge.name}</h4>
                              <p className="text-sm text-slate-400 mb-2">{badge.description}</p>
                              <div className="w-full bg-slate-700 rounded-full h-2">
                                <div 
                                  className="bg-gradient-to-r from-blue-500 to-blue-400 h-2 rounded-full transition-all"
                                  style={{ width: `${badge.progress}%` }}
                                />
                              </div>
                              <p className="text-xs text-slate-500 mt-1">{badge.progress}% complete</p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* All Available Badges */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Gift className="w-5 h-5 text-slate-400" />
                  All Available Badges
                </h3>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {BADGES.map((badge) => {
                    const earned = gamificationData?.badges?.some(b => b.id === badge.id);
                    return (
                      <Card key={badge.id} className={`border-2 ${earned ? 'bg-gradient-to-br from-amber-900/30 to-orange-900/30 border-amber-500/50' : 'bg-slate-900/50 border-slate-800 opacity-60'}`}>
                        <CardContent className="p-6 text-center">
                          <span className={`text-5xl block mb-3 ${!earned && 'grayscale'}`}>{badge.icon}</span>
                          <h4 className="font-bold text-white mb-1">{badge.name}</h4>
                          <p className="text-sm text-slate-400 mb-3">{badge.description}</p>
                          <Badge className={earned ? 'bg-amber-500/20 text-amber-400 border-0' : 'bg-slate-700 text-slate-400 border-0'}>
                            +{badge.xp} XP
                          </Badge>
                          {earned && <p className="text-xs text-green-400 mt-2">✓ Earned</p>}
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Leaderboard Tab */}
          {activeTab === 'leaderboard' && gamificationData?.gamification_enabled && (
            <div className="space-y-6 animate-fade-in" data-testid="leaderboard-section">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">Institution Leaderboard</h2>
                <div className="flex gap-2">
                  {['daily', 'weekly', 'monthly', 'all_time'].map(tf => (
                    <button
                      key={tf}
                      className="px-3 py-1 rounded-lg text-sm font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
                    >
                      {tf.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </button>
                  ))}
                </div>
              </div>

              {/* Top 3 Podium */}
              {leaderboard.length >= 3 && (
                <div className="flex items-end justify-center gap-4 mb-8">
                  {/* 2nd Place */}
                  <div className="text-center">
                    <div className="w-20 h-20 mx-auto mb-2 rounded-full bg-gradient-to-br from-slate-400 to-slate-600 flex items-center justify-center border-4 border-slate-300">
                      <span className="text-2xl font-bold text-white">2</span>
                    </div>
                    <p className="text-white font-medium">{leaderboard[1]?.name}</p>
                    <p className="text-amber-400 font-bold">{leaderboard[1]?.points} pts</p>
                    <div className="h-24 w-20 bg-slate-700 rounded-t-lg mt-2"></div>
                  </div>
                  {/* 1st Place */}
                  <div className="text-center">
                    <div className="w-24 h-24 mx-auto mb-2 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center border-4 border-amber-300 relative">
                      <span className="text-3xl font-bold text-white">1</span>
                      <Crown className="w-8 h-8 text-amber-300 absolute -top-4" />
                    </div>
                    <p className="text-white font-bold text-lg">{leaderboard[0]?.name}</p>
                    <p className="text-amber-400 font-bold text-xl">{leaderboard[0]?.points} pts</p>
                    <div className="h-32 w-24 bg-amber-600/30 rounded-t-lg mt-2 border-t-4 border-amber-400"></div>
                  </div>
                  {/* 3rd Place */}
                  <div className="text-center">
                    <div className="w-20 h-20 mx-auto mb-2 rounded-full bg-gradient-to-br from-orange-500 to-orange-700 flex items-center justify-center border-4 border-orange-400">
                      <span className="text-2xl font-bold text-white">3</span>
                    </div>
                    <p className="text-white font-medium">{leaderboard[2]?.name}</p>
                    <p className="text-amber-400 font-bold">{leaderboard[2]?.points} pts</p>
                    <div className="h-16 w-20 bg-orange-700/30 rounded-t-lg mt-2"></div>
                  </div>
                </div>
              )}
              
              <Card className="bg-slate-900/50 border-slate-800">
                <CardContent className="p-0">
                  <div className="divide-y divide-slate-800">
                    {leaderboard.map((entry, index) => (
                      <div key={entry.user_id || index} className={`flex items-center gap-4 p-4 ${entry.is_current_user ? 'bg-blue-500/10 border-l-4 border-blue-500' : ''}`}>
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                          index === 0 ? 'bg-amber-500 text-amber-900' :
                          index === 1 ? 'bg-slate-400 text-slate-900' :
                          index === 2 ? 'bg-orange-600 text-orange-100' :
                          'bg-slate-700 text-slate-300'
                        }`}>
                          {entry.rank || index + 1}
                        </div>
                        <div className="flex-1">
                          <p className="font-semibold text-white flex items-center gap-2">
                            {entry.name}
                            {entry.is_current_user && <Badge className="bg-blue-500/20 text-blue-400 border-0 text-xs">You</Badge>}
                          </p>
                          <p className="text-sm text-slate-400">{entry.exams_completed || 0} exams completed</p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-amber-400">{entry.points} pts</p>
                          <p className="text-sm text-slate-500">Avg: {entry.avg_score || 0}%</p>
                        </div>
                      </div>
                    ))}
                    {leaderboard.length === 0 && (
                      <div className="p-8 text-center">
                        <Users className="w-12 h-12 text-slate-600 mx-auto mb-2" />
                        <p className="text-slate-400">No leaderboard data yet</p>
                        <p className="text-slate-500 text-sm">Complete exams to appear on the leaderboard!</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Live Classes Tab */}
          {activeTab === 'classes' && (
            <div className="space-y-6 animate-fade-in" data-testid="classes-section">
              <h2 className="text-2xl font-bold text-white">Live Classes</h2>
              
              {upcomingClasses.length === 0 ? (
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardContent className="p-12 text-center">
                    <Video className="w-16 h-16 text-slate-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-white mb-2">No Upcoming Classes</h3>
                    <p className="text-slate-400">Your institution has not scheduled any live classes yet.</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4">
                  {upcomingClasses.map((cls, i) => (
                    <Card key={i} className="bg-slate-900/50 border-slate-800">
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className="w-16 h-16 rounded-xl bg-blue-500/20 flex items-center justify-center">
                              <Video className="w-8 h-8 text-blue-400" />
                            </div>
                            <div>
                              <h4 className="font-bold text-white text-lg">{cls.title}</h4>
                              <p className="text-slate-400">{cls.instructor}</p>
                              <p className="text-sm text-slate-500 mt-1">
                                <Calendar className="w-4 h-4 inline mr-1" />
                                {new Date(cls.start_time).toLocaleString()}
                              </p>
                            </div>
                          </div>
                          <Button className="bg-blue-600 hover:bg-blue-700" data-testid={`join-class-${i}`}>
                            <Play className="w-4 h-4 mr-2" /> Join Class
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* AI Tutor Tab */}
          {activeTab === 'tutor' && (
            <div className="space-y-6 animate-fade-in" data-testid="tutor-section">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-white">AI Tutor</h2>
                  <p className="text-slate-400">Get personalized help for your {examConfig?.name} preparation</p>
                </div>
              </div>
              
              <Card className="bg-gradient-to-br from-purple-900/30 to-blue-900/30 border-purple-500/30">
                <CardContent className="p-8 text-center">
                  <Brain className="w-20 h-20 text-purple-400 mx-auto mb-6" />
                  <h3 className="text-2xl font-bold text-white mb-4">Your Personal {examConfig?.name} Tutor</h3>
                  <p className="text-slate-300 mb-6 max-w-lg mx-auto">
                    Practice speaking, get instant feedback on your writing, and receive personalized tips to improve your score.
                  </p>
                  <Button 
                    onClick={() => navigate(`/tutor?exam=${assignedExam}`)}
                    className="bg-purple-600 hover:bg-purple-700"
                    size="lg"
                    data-testid="start-tutor-session"
                  >
                    <MessageSquare className="w-5 h-5 mr-2" /> Start Tutoring Session
                  </Button>
                </CardContent>
              </Card>
            </div>
          )}

          {/* History Tab */}
          {activeTab === 'history' && (
            <div className="space-y-6 animate-fade-in" data-testid="history-section">
              <h2 className="text-2xl font-bold text-white">Exam History</h2>
              
              {examHistory.length === 0 ? (
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardContent className="p-12 text-center">
                    <Clock className="w-16 h-16 text-slate-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-white mb-2">No Exams Yet</h3>
                    <p className="text-slate-400 mb-6">Start practicing to see your history here.</p>
                    <Button onClick={() => setActiveTab('practice')} className="bg-blue-600 hover:bg-blue-700">
                      Start Practicing
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4">
                  {examHistory.map((exam, i) => (
                    <Card key={i} className="bg-slate-900/50 border-slate-800">
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${examConfig?.color} flex items-center justify-center`}>
                              <span>{examConfig?.icon}</span>
                            </div>
                            <div>
                              <h4 className="font-semibold text-white">{examConfig?.name} - {exam.section || 'Full Exam'}</h4>
                              <p className="text-sm text-slate-400">{new Date(exam.completed_at).toLocaleString()}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className={`text-2xl font-bold ${exam.score >= 70 ? 'text-green-400' : exam.score >= 50 ? 'text-amber-400' : 'text-red-400'}`}>
                              {exam.score}%
                            </p>
                            <p className="text-sm text-slate-500">{exam.time_taken || 'N/A'}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
