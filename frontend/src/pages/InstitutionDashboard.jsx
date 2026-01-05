import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Users, GraduationCap, BarChart3, TrendingUp, TrendingDown, AlertTriangle,
  Plus, Search, LogOut, Settings, BookOpen, Brain, ChevronRight, Award,
  Clock, Target, Activity, UserPlus, Download, Filter
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import axios from 'axios';
import { toast, Toaster } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function InstitutionDashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [metrics, setMetrics] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addStudentOpen, setAddStudentOpen] = useState(false);
  const [newStudent, setNewStudent] = useState({ name: '', email: '', password: '' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [metricsRes, studentsRes] = await Promise.all([
        axios.get(`${API_URL}/institution/metrics`),
        axios.get(`${API_URL}/institution/students`)
      ]);
      setMetrics(metricsRes.data);
      setStudents(studentsRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddStudent = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/institution/students`, newStudent);
      toast.success('Student added successfully!');
      setAddStudentOpen(false);
      setNewStudent({ name: '', email: '', password: '' });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add student');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const getRiskColor = (risk) => {
    if (risk < 0.3) return 'text-emerald-400';
    if (risk < 0.6) return 'text-amber-400';
    return 'text-red-400';
  };

  const getRiskBadge = (risk) => {
    if (risk < 0.3) return { label: 'Low Risk', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' };
    if (risk < 0.6) return { label: 'Medium Risk', color: 'bg-amber-500/10 text-amber-400 border-amber-500/20' };
    return { label: 'High Risk', color: 'bg-red-500/10 text-red-400 border-red-500/20' };
  };

  // Chart data
  const progressData = [
    { month: 'Jan', score: 65 },
    { month: 'Feb', score: 68 },
    { month: 'Mar', score: 72 },
    { month: 'Apr', score: 75 },
    { month: 'May', score: 78 },
    { month: 'Jun', score: 82 }
  ];

  const examDistribution = [
    { name: 'IELTS', value: 35, color: '#ef4444' },
    { name: 'TOEFL', value: 30, color: '#3b82f6' },
    { name: 'Cambridge', value: 20, color: '#8b5cf6' },
    { name: 'PTE', value: 10, color: '#f59e0b' },
    { name: 'OET', value: 5, color: '#10b981' }
  ];

  const riskDistribution = [
    { range: '0-30%', students: 45, color: '#10b981' },
    { range: '31-60%', students: 30, color: '#f59e0b' },
    { range: '61-100%', students: 25, color: '#ef4444' }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-slate-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex" data-testid="institution-dashboard">
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
              <p className="text-xs text-slate-500">Institution Portal</p>
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
            onClick={() => setActiveTab('students')}
            className={`sidebar-item w-full ${activeTab === 'students' ? 'active' : ''}`}
            data-testid="nav-students"
          >
            <Users className="w-5 h-5" />
            <span>Students</span>
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`sidebar-item w-full ${activeTab === 'analytics' ? 'active' : ''}`}
            data-testid="nav-analytics"
          >
            <Activity className="w-5 h-5" />
            <span>Analytics</span>
          </button>
          <button
            onClick={() => setActiveTab('exams')}
            className={`sidebar-item w-full ${activeTab === 'exams' ? 'active' : ''}`}
            data-testid="nav-exams"
          >
            <BookOpen className="w-5 h-5" />
            <span>Exams</span>
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
                Welcome back, {user?.name || 'Institution'}
              </h1>
              <p className="text-slate-400">{user?.institution_name || 'Your Institution'}</p>
            </div>
            <div className="flex items-center gap-4">
              <Dialog open={addStudentOpen} onOpenChange={setAddStudentOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-blue-500 hover:bg-blue-600 rounded-full" data-testid="add-student-btn">
                    <UserPlus className="w-4 h-4 mr-2" />
                    Add Student
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-slate-900 border-slate-800">
                  <DialogHeader>
                    <DialogTitle className="text-white">Add New Student</DialogTitle>
                  </DialogHeader>
                  <form onSubmit={handleAddStudent} className="space-y-4">
                    <div className="space-y-2">
                      <Label className="text-slate-300">Full Name</Label>
                      <Input
                        value={newStudent.name}
                        onChange={(e) => setNewStudent(prev => ({ ...prev, name: e.target.value }))}
                        className="bg-slate-800 border-slate-700 text-white"
                        placeholder="John Doe"
                        required
                        data-testid="new-student-name"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-slate-300">Email</Label>
                      <Input
                        type="email"
                        value={newStudent.email}
                        onChange={(e) => setNewStudent(prev => ({ ...prev, email: e.target.value }))}
                        className="bg-slate-800 border-slate-700 text-white"
                        placeholder="student@example.com"
                        required
                        data-testid="new-student-email"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-slate-300">Password (optional)</Label>
                      <Input
                        type="password"
                        value={newStudent.password}
                        onChange={(e) => setNewStudent(prev => ({ ...prev, password: e.target.value }))}
                        className="bg-slate-800 border-slate-700 text-white"
                        placeholder="Leave blank for auto-generated"
                        data-testid="new-student-password"
                      />
                    </div>
                    <Button type="submit" className="w-full bg-blue-500 hover:bg-blue-600" data-testid="submit-new-student">
                      Add Student
                    </Button>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </header>
        
        <div className="p-8">
          {activeTab === 'overview' && (
            <div className="space-y-8 animate-fade-in" data-testid="overview-tab">
              {/* Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="metric-card" data-testid="metric-total-students">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-slate-400 text-sm">Total Students</p>
                        <p className="text-3xl font-bold text-white font-outfit mt-1">{metrics?.total_students || 0}</p>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
                        <Users className="w-6 h-6 text-blue-400" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center gap-2 text-sm">
                      <TrendingUp className="w-4 h-4 text-emerald-400" />
                      <span className="text-emerald-400">+12%</span>
                      <span className="text-slate-500">from last month</span>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="metric-card" data-testid="metric-pass-probability">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-slate-400 text-sm">Avg Pass Probability</p>
                        <p className="text-3xl font-bold text-emerald-400 font-outfit mt-1">{metrics?.avg_pass_probability || 0}%</p>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                        <Target className="w-6 h-6 text-emerald-400" />
                      </div>
                    </div>
                    <Progress value={metrics?.avg_pass_probability || 0} className="mt-4 h-2" />
                  </CardContent>
                </Card>
                
                <Card className="metric-card" data-testid="metric-at-risk">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-slate-400 text-sm">At Risk Students</p>
                        <p className="text-3xl font-bold text-amber-400 font-outfit mt-1">{metrics?.at_risk_students || 0}</p>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center">
                        <AlertTriangle className="w-6 h-6 text-amber-400" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center gap-2 text-sm">
                      <TrendingDown className="w-4 h-4 text-emerald-400" />
                      <span className="text-emerald-400">-3</span>
                      <span className="text-slate-500">from last week</span>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="metric-card" data-testid="metric-exams-completed">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-slate-400 text-sm">Exams Completed</p>
                        <p className="text-3xl font-bold text-purple-400 font-outfit mt-1">{metrics?.exams_completed || 0}</p>
                      </div>
                      <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                        <BookOpen className="w-6 h-6 text-purple-400" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center gap-2 text-sm">
                      <span className="text-slate-400">Avg Score:</span>
                      <span className="text-white font-medium">{metrics?.avg_score || 0}%</span>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              {/* Charts Row */}
              <div className="grid lg:grid-cols-2 gap-6">
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardHeader>
                    <CardTitle className="text-white font-outfit">Performance Trend</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={progressData}>
                        <defs>
                          <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                        <XAxis dataKey="month" stroke="#64748b" />
                        <YAxis stroke="#64748b" />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                          labelStyle={{ color: '#f8fafc' }}
                        />
                        <Area type="monotone" dataKey="score" stroke="#3b82f6" fill="url(#scoreGradient)" strokeWidth={2} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
                
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardHeader>
                    <CardTitle className="text-white font-outfit">Exam Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={examDistribution}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={100}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {examDistribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                        />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
              
              {/* Risk Distribution */}
              <Card className="bg-slate-900/50 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-white font-outfit">Risk Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={riskDistribution} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis type="number" stroke="#64748b" />
                      <YAxis dataKey="range" type="category" stroke="#64748b" width={80} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                      />
                      <Bar dataKey="students" radius={[0, 4, 4, 0]}>
                        {riskDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          )}
          
          {activeTab === 'students' && (
            <div className="space-y-6 animate-fade-in" data-testid="students-tab">
              <div className="flex items-center justify-between">
                <div className="relative w-80">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <Input
                    placeholder="Search students..."
                    className="pl-10 bg-slate-900 border-slate-800 text-white"
                    data-testid="search-students"
                  />
                </div>
                <div className="flex gap-3">
                  <Button variant="outline" className="border-slate-700 text-slate-300">
                    <Filter className="w-4 h-4 mr-2" />
                    Filter
                  </Button>
                  <Button variant="outline" className="border-slate-700 text-slate-300">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </div>
              </div>
              
              <Card className="bg-slate-900/50 border-slate-800 overflow-hidden">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Student</th>
                      <th>Pass Probability</th>
                      <th>Risk Score</th>
                      <th>Engagement</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="text-center py-12">
                          <div className="space-y-3">
                            <Users className="w-12 h-12 text-slate-600 mx-auto" />
                            <p className="text-slate-500">No students yet. Add your first student to get started.</p>
                            <Button 
                              onClick={() => setAddStudentOpen(true)}
                              className="bg-blue-500 hover:bg-blue-600"
                            >
                              <UserPlus className="w-4 h-4 mr-2" />
                              Add Student
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ) : (
                      students.map((student) => {
                        const riskBadge = getRiskBadge(student.risk_score);
                        return (
                          <tr key={student.id} data-testid={`student-row-${student.id}`}>
                            <td>
                              <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center">
                                  <span className="text-white font-medium">
                                    {student.name.charAt(0).toUpperCase()}
                                  </span>
                                </div>
                                <div>
                                  <p className="text-white font-medium">{student.name}</p>
                                  <p className="text-slate-500 text-xs">{student.email}</p>
                                </div>
                              </div>
                            </td>
                            <td>
                              <div className="flex items-center gap-2">
                                <Progress value={student.pass_probability * 100} className="w-20 h-2" />
                                <span className="text-emerald-400 font-medium">
                                  {Math.round(student.pass_probability * 100)}%
                                </span>
                              </div>
                            </td>
                            <td>
                              <span className={`font-medium ${getRiskColor(student.risk_score)}`}>
                                {Math.round(student.risk_score * 100)}%
                              </span>
                            </td>
                            <td>
                              <div className="flex items-center gap-2">
                                <Activity className="w-4 h-4 text-purple-400" />
                                <span className="text-white">{Math.round(student.engagement_score * 100)}%</span>
                              </div>
                            </td>
                            <td>
                              <Badge className={riskBadge.color}>
                                {riskBadge.label}
                              </Badge>
                            </td>
                            <td>
                              <Button variant="ghost" size="sm" className="text-slate-400 hover:text-white">
                                View Details
                                <ChevronRight className="w-4 h-4 ml-1" />
                              </Button>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </Card>
            </div>
          )}
          
          {activeTab === 'analytics' && (
            <div className="space-y-6 animate-fade-in" data-testid="analytics-tab">
              <h2 className="text-2xl font-bold text-white font-outfit">Advanced Analytics</h2>
              <div className="grid lg:grid-cols-3 gap-6">
                <Card className="bg-slate-900/50 border-slate-800 col-span-2">
                  <CardHeader>
                    <CardTitle className="text-white">Weekly Progress</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={400}>
                      <LineChart data={progressData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                        <XAxis dataKey="month" stroke="#64748b" />
                        <YAxis stroke="#64748b" />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                        />
                        <Line type="monotone" dataKey="score" stroke="#3b82f6" strokeWidth={3} dot={{ fill: '#3b82f6' }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
                
                <div className="space-y-6">
                  <Card className="bg-slate-900/50 border-slate-800">
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                          <Award className="w-8 h-8 text-emerald-400" />
                        </div>
                        <div>
                          <p className="text-slate-400 text-sm">High Performers</p>
                          <p className="text-3xl font-bold text-white">{metrics?.high_performers || 0}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-slate-900/50 border-slate-800">
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-2xl bg-blue-500/10 flex items-center justify-center">
                          <Clock className="w-8 h-8 text-blue-400" />
                        </div>
                        <div>
                          <p className="text-slate-400 text-sm">Avg Study Time</p>
                          <p className="text-3xl font-bold text-white">4.2h</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-slate-900/50 border-slate-800">
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-2xl bg-purple-500/10 flex items-center justify-center">
                          <Brain className="w-8 h-8 text-purple-400" />
                        </div>
                        <div>
                          <p className="text-slate-400 text-sm">AI Tutoring Sessions</p>
                          <p className="text-3xl font-bold text-white">1,240</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'exams' && (
            <div className="space-y-6 animate-fade-in" data-testid="exams-tab">
              <h2 className="text-2xl font-bold text-white font-outfit">Exam Management</h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {['TOEFL', 'IELTS', 'Cambridge', 'PTE', 'OET'].map((exam) => (
                  <Card 
                    key={exam}
                    className="bg-slate-900/50 border-slate-800 hover:border-slate-700 transition-all cursor-pointer card-hover"
                    data-testid={`exam-manage-${exam.toLowerCase()}`}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className={`w-12 h-12 rounded-xl badge-${exam.toLowerCase()} flex items-center justify-center`}>
                          <BookOpen className="w-6 h-6 text-white" />
                        </div>
                        <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">Active</Badge>
                      </div>
                      <h3 className="text-xl font-bold text-white mb-2">{exam}</h3>
                      <p className="text-slate-400 text-sm mb-4">Full exam simulation with AI feedback</p>
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-500">Students enrolled</span>
                        <span className="text-white font-medium">{Math.floor(Math.random() * 50) + 10}</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
