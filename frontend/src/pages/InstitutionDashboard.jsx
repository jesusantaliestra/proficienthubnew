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
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import {
  Users, GraduationCap, BarChart3, TrendingUp, TrendingDown, AlertTriangle,
  Plus, Search, LogOut, Settings, BookOpen, Brain, ChevronRight, Award,
  Clock, Target, Activity, UserPlus, Download, Filter, FolderOpen, 
  FileText, Video, Headphones, Layers, Trash2, Globe
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import axios from 'axios';
import { toast, Toaster } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SUPPORTED_LANGUAGES = {
  en: 'English',
  es: 'Español',
  pt: 'Português',
  de: 'Deutsch',
  it: 'Italiano',
  fr: 'Français'
};

export default function InstitutionDashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [metrics, setMetrics] = useState(null);
  const [students, setStudents] = useState([]);
  const [libraryItems, setLibraryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addStudentOpen, setAddStudentOpen] = useState(false);
  const [addLibraryOpen, setAddLibraryOpen] = useState(false);
  const [newStudent, setNewStudent] = useState({ name: '', email: '', exam_type: 'ielts', credits: 100 });
  const [createdStudentInfo, setCreatedStudentInfo] = useState(null);
  const [newLibraryItem, setNewLibraryItem] = useState({ 
    title: '', 
    item_type: 'material', 
    content: '', 
    description: '', 
    exam_type: '',
    tags: []
  });
  const [selectedLanguage, setSelectedLanguage] = useState(user?.language || 'en');
  const [analyticsData, setAnalyticsData] = useState(null);
  const [studentsAnalytics, setStudentsAnalytics] = useState([]);
  const [atRiskStudents, setAtRiskStudents] = useState([]);
  const [cohortData, setCohortData] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [selectedStudentAnalytics, setSelectedStudentAnalytics] = useState(null);
  const [crmData, setCrmData] = useState(null);
  const [crmLoading, setCrmLoading] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);
  const [addLeadOpen, setAddLeadOpen] = useState(false);
  const [addActivityOpen, setAddActivityOpen] = useState(false);
  const [newLead, setNewLead] = useState({
    institution_name: '',
    contact_name: '',
    email: '',
    phone: '',
    country: '',
    students_count: '',
    exam_types: [],
    estimated_value: '',
    notes: ''
  });
  const [newActivity, setNewActivity] = useState({
    activity_type: 'call',
    description: '',
    outcome: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [metricsRes, studentsRes, libraryRes] = await Promise.all([
        axios.get(`${API_URL}/institution/metrics`),
        axios.get(`${API_URL}/institution/students`),
        axios.get(`${API_URL}/library/items`)
      ]);
      setMetrics(metricsRes.data);
      setStudents(studentsRes.data);
      setLibraryItems(libraryRes.data);
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
      const response = await axios.post(`${API_URL}/institution/students/create`, newStudent);
      setCreatedStudentInfo(response.data);
      toast.success('Student created with provisional credentials!');
      setNewStudent({ name: '', email: '', exam_type: 'ielts', credits: 100 });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add student');
    }
  };

  const handleAddLibraryItem = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/library/items`, newLibraryItem);
      toast.success('Library item added!');
      setAddLibraryOpen(false);
      setNewLibraryItem({ title: '', item_type: 'material', content: '', description: '', exam_type: '', tags: [] });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add item');
    }
  };

  const handleDeleteLibraryItem = async (itemId) => {
    try {
      await axios.delete(`${API_URL}/library/items/${itemId}`);
      toast.success('Item deleted');
      fetchData();
    } catch (error) {
      toast.error('Failed to delete item');
    }
  };

  const handleLanguageChange = async (lang) => {
    setSelectedLanguage(lang);
    try {
      await axios.put(`${API_URL}/auth/settings`, { language: lang });
      toast.success(`Language changed to ${SUPPORTED_LANGUAGES[lang]}`);
    } catch (error) {
      console.error('Failed to update language:', error);
    }
  };

  const fetchAnalyticsData = async () => {
    setAnalyticsLoading(true);
    try {
      const [overviewRes, studentsRes, atRiskRes, cohortsRes] = await Promise.all([
        axios.get(`${API_URL}/institution/analytics/overview`),
        axios.get(`${API_URL}/institution/analytics/students`),
        axios.get(`${API_URL}/institution/analytics/at-risk`),
        axios.get(`${API_URL}/institution/analytics/cohorts`)
      ]);
      setAnalyticsData(overviewRes.data);
      setStudentsAnalytics(studentsRes.data.students || []);
      setAtRiskStudents(atRiskRes.data.students || []);
      setCohortData(cohortsRes.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      toast.error('Failed to load analytics data');
    } finally {
      setAnalyticsLoading(false);
    }
  };

  const fetchStudentDetailedAnalytics = async (studentId) => {
    try {
      const response = await axios.get(`${API_URL}/institution/analytics/student/${studentId}`);
      setSelectedStudentAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch student analytics:', error);
      toast.error('Failed to load student details');
    }
  };

  useEffect(() => {
    if (activeTab === 'analytics') {
      fetchAnalyticsData();
    }
  }, [activeTab]);

  const handleLogout = () => {
    logout();
    navigate('/', { replace: true });
  };

  const getRiskColor = (risk) => {
    if (risk < 0.3) return 'text-green-600';
    if (risk < 0.6) return 'text-orange-500';
    return 'text-red-500';
  };

  const getRiskBadge = (risk) => {
    if (risk < 0.3) return { label: 'Low Risk', color: 'bg-green-100 text-green-700 border-green-200' };
    if (risk < 0.6) return { label: 'Medium Risk', color: 'bg-orange-100 text-orange-700 border-orange-200' };
    return { label: 'High Risk', color: 'bg-red-100 text-red-700 border-red-200' };
  };

  const progressData = [
    { month: 'Jan', score: 65 },
    { month: 'Feb', score: 68 },
    { month: 'Mar', score: 72 },
    { month: 'Apr', score: 75 },
    { month: 'May', score: 78 },
    { month: 'Jun', score: 82 }
  ];

  const examDistribution = [
    { name: 'IELTS', value: 25, color: '#FF4B4B' },
    { name: 'TOEFL', value: 25, color: '#1CB0F6' },
    { name: 'Cambridge', value: 15, color: '#CE82FF' },
    { name: 'Trinity', value: 10, color: '#EC4899' },
    { name: 'TOEIC', value: 8, color: '#6366F1' },
    { name: 'CELPIP', value: 5, color: '#06B6D4' },
    { name: 'PTE', value: 7, color: '#FF9600' },
    { name: 'OET', value: 5, color: '#58CC02' }
  ];

  const getItemIcon = (type) => {
    switch (type) {
      case 'material': return FileText;
      case 'flashcard': return Layers;
      case 'audio': return Headphones;
      case 'video': return Video;
      default: return FileText;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-[#58CC02] border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-gray-500 font-semibold">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex" data-testid="institution-dashboard">
      <Toaster position="top-right" richColors />
      
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r-2 border-gray-100 flex flex-col">
        <div className="p-6 border-b-2 border-gray-100">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-[#58CC02] flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="text-lg font-extrabold text-gray-800">ProficientHub</span>
              <p className="text-xs text-gray-400 font-semibold">Institution Portal</p>
            </div>
          </div>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          {[
            { id: 'overview', icon: BarChart3, label: 'Overview' },
            { id: 'students', icon: Users, label: 'Students' },
            { id: 'crm', icon: Target, label: 'CRM & Sales' },
            { id: 'library', icon: FolderOpen, label: 'Library' },
            { id: 'analytics', icon: Activity, label: 'Analytics' },
            { id: 'exams', icon: BookOpen, label: 'Exams' }
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
        
        <div className="p-4 border-t-2 border-gray-100 space-y-2">
          <div className="px-4 py-2">
            <Label className="text-xs text-gray-400 font-semibold mb-2 block">Language</Label>
            <Select value={selectedLanguage} onValueChange={handleLanguageChange}>
              <SelectTrigger className="w-full text-sm">
                <Globe className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(SUPPORTED_LANGUAGES).map(([code, name]) => (
                  <SelectItem key={code} value={code}>{name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <button className="sidebar-item w-full" data-testid="nav-settings">
            <Settings className="w-5 h-5" />
            <span>Settings</span>
          </button>
          <button 
            onClick={handleLogout}
            className="sidebar-item w-full text-red-500 hover:text-red-600 hover:bg-red-50"
            data-testid="logout-btn"
          >
            <LogOut className="w-5 h-5" />
            <span>Log Out</span>
          </button>
        </div>
      </aside>
      
      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <header className="sticky top-0 z-10 bg-white/95 backdrop-blur border-b-2 border-gray-100 px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-extrabold text-gray-900">
                Welcome back, {user?.name || 'Institution'}
              </h1>
              <p className="text-gray-500 font-semibold">{user?.institution_name || 'Your Institution'}</p>
            </div>
            <div className="flex items-center gap-4">
              <Dialog open={addStudentOpen} onOpenChange={setAddStudentOpen}>
                <DialogTrigger asChild>
                  <button className="btn-duo px-4 py-2.5 text-sm flex items-center gap-2" data-testid="add-student-btn">
                    <UserPlus className="w-4 h-4" />
                    Add Student
                  </button>
                </DialogTrigger>
                <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-md">
                  <DialogHeader>
                    <DialogTitle className="text-gray-900 font-extrabold">Add New Student</DialogTitle>
                  </DialogHeader>
                  
                  {createdStudentInfo ? (
                    <div className="space-y-4">
                      <div className="p-4 bg-green-50 border border-green-200 rounded-xl">
                        <p className="text-green-800 font-semibold mb-2">✓ Student Created Successfully!</p>
                        <div className="space-y-2 text-sm">
                          <p><strong>Name:</strong> {createdStudentInfo.name}</p>
                          <p><strong>Email:</strong> {createdStudentInfo.email}</p>
                          <p><strong>Provisional Password:</strong> 
                            <code className="bg-yellow-100 px-2 py-0.5 rounded ml-2 font-mono">
                              {createdStudentInfo.provisional_password}
                            </code>
                          </p>
                          <p><strong>Credits:</strong> {createdStudentInfo.credits}</p>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600">
                        Share these credentials with the student. They will be required to change their password on first login.
                      </p>
                      <div className="flex gap-3">
                        <button 
                          onClick={() => {
                            navigator.clipboard.writeText(`Email: ${createdStudentInfo.email}\nPassword: ${createdStudentInfo.provisional_password}`);
                            toast.success('Credentials copied!');
                          }}
                          className="flex-1 btn-duo-outline py-2"
                        >
                          Copy Credentials
                        </button>
                        <button 
                          onClick={() => {
                            setCreatedStudentInfo(null);
                            setAddStudentOpen(false);
                          }}
                          className="flex-1 btn-duo py-2"
                        >
                          Done
                        </button>
                      </div>
                    </div>
                  ) : (
                  <form onSubmit={handleAddStudent} className="space-y-4">
                    <div className="space-y-2">
                      <Label className="text-gray-700 font-semibold">Full Name</Label>
                      <Input
                        value={newStudent.name}
                        onChange={(e) => setNewStudent(prev => ({ ...prev, name: e.target.value }))}
                        className="input-duo"
                        placeholder="John Doe"
                        required
                        data-testid="new-student-name"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-gray-700 font-semibold">Email</Label>
                      <Input
                        type="email"
                        value={newStudent.email}
                        onChange={(e) => setNewStudent(prev => ({ ...prev, email: e.target.value }))}
                        className="input-duo"
                        placeholder="student@example.com"
                        required
                        data-testid="new-student-email"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-gray-700 font-semibold">Exam Type</Label>
                      <Select 
                        value={newStudent.exam_type} 
                        onValueChange={(value) => setNewStudent(prev => ({ ...prev, exam_type: value }))}
                      >
                        <SelectTrigger className="input-duo" data-testid="new-student-exam">
                          <SelectValue placeholder="Select exam" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="ielts">IELTS</SelectItem>
                          <SelectItem value="toefl">TOEFL</SelectItem>
                          <SelectItem value="cambridge">Cambridge</SelectItem>
                          <SelectItem value="trinity">Trinity</SelectItem>
                          <SelectItem value="toeic">TOEIC</SelectItem>
                          <SelectItem value="celpip">CELPIP</SelectItem>
                          <SelectItem value="pte">PTE</SelectItem>
                          <SelectItem value="oet">OET</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="text-gray-700 font-semibold">Initial Credits</Label>
                      <Input
                        type="number"
                        value={newStudent.credits}
                        onChange={(e) => setNewStudent(prev => ({ ...prev, credits: parseInt(e.target.value) || 100 }))}
                        className="input-duo"
                        min="1"
                        data-testid="new-student-credits"
                      />
                      <p className="text-xs text-gray-500">Credits for AI tutoring, writing feedback, and voice practice</p>
                    </div>
                    <button type="submit" className="btn-duo w-full py-3" data-testid="submit-new-student">
                      Create Student
                    </button>
                  </form>
                  )}
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
                        <p className="text-gray-500 text-sm font-semibold">Total Students</p>
                        <p className="text-3xl font-extrabold text-gray-900 mt-1">{metrics?.total_students || 0}</p>
                      </div>
                      <div className="feature-icon feature-icon-blue">
                        <Users className="w-6 h-6" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center gap-2 text-sm">
                      <TrendingUp className="w-4 h-4 text-green-500" />
                      <span className="text-green-600 font-semibold">+12%</span>
                      <span className="text-gray-400">from last month</span>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="metric-card" data-testid="metric-pass-probability">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-500 text-sm font-semibold">Avg Pass Probability</p>
                        <p className="text-3xl font-extrabold text-[#58CC02] mt-1">{metrics?.avg_pass_probability || 0}%</p>
                      </div>
                      <div className="feature-icon feature-icon-green">
                        <Target className="w-6 h-6" />
                      </div>
                    </div>
                    <Progress value={metrics?.avg_pass_probability || 0} className="mt-4 h-2" />
                  </CardContent>
                </Card>
                
                <Card className="metric-card" data-testid="metric-at-risk">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-500 text-sm font-semibold">At Risk Students</p>
                        <p className="text-3xl font-extrabold text-orange-500 mt-1">{metrics?.at_risk_students || 0}</p>
                      </div>
                      <div className="feature-icon feature-icon-orange">
                        <AlertTriangle className="w-6 h-6" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center gap-2 text-sm">
                      <TrendingDown className="w-4 h-4 text-green-500" />
                      <span className="text-green-600 font-semibold">-3</span>
                      <span className="text-gray-400">from last week</span>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="metric-card" data-testid="metric-exams-completed">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-500 text-sm font-semibold">Exams Completed</p>
                        <p className="text-3xl font-extrabold text-purple-500 mt-1">{metrics?.exams_completed || 0}</p>
                      </div>
                      <div className="feature-icon feature-icon-purple">
                        <BookOpen className="w-6 h-6" />
                      </div>
                    </div>
                    <div className="mt-4 flex items-center gap-2 text-sm">
                      <span className="text-gray-400">Avg Score:</span>
                      <span className="text-gray-900 font-bold">{metrics?.avg_score || 0}%</span>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              {/* Charts */}
              <div className="grid lg:grid-cols-2 gap-6">
                <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                  <CardHeader>
                    <CardTitle className="text-gray-900 font-extrabold">Performance Trend</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={progressData}>
                        <defs>
                          <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#58CC02" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#58CC02" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" />
                        <XAxis dataKey="month" stroke="#AFAFAF" />
                        <YAxis stroke="#AFAFAF" />
                        <Tooltip contentStyle={{ backgroundColor: '#fff', border: '2px solid #E5E5E5', borderRadius: '12px' }} />
                        <Area type="monotone" dataKey="score" stroke="#58CC02" fill="url(#scoreGradient)" strokeWidth={3} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
                
                <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                  <CardHeader>
                    <CardTitle className="text-gray-900 font-extrabold">Exam Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie data={examDistribution} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={5} dataKey="value">
                          {examDistribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: '#fff', border: '2px solid #E5E5E5', borderRadius: '12px' }} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
          
          {activeTab === 'students' && (
            <div className="space-y-6 animate-fade-in" data-testid="students-tab">
              <div className="flex items-center justify-between">
                <div className="relative w-80">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input placeholder="Search students..." className="input-duo pl-10" data-testid="search-students" />
                </div>
                <div className="flex gap-3">
                  <Button variant="outline" className="border-2 border-gray-200 text-gray-600 font-semibold">
                    <Filter className="w-4 h-4 mr-2" />
                    Filter
                  </Button>
                  <Button variant="outline" className="border-2 border-gray-200 text-gray-600 font-semibold">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </div>
              </div>
              
              <Card className="bg-white border-2 border-gray-100 rounded-2xl overflow-hidden">
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
                            <Users className="w-12 h-12 text-gray-300 mx-auto" />
                            <p className="text-gray-500 font-semibold">No students yet. Add your first student to get started.</p>
                            <button onClick={() => setAddStudentOpen(true)} className="btn-duo px-4 py-2">
                              <UserPlus className="w-4 h-4 mr-2" />
                              Add Student
                            </button>
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
                                <div className="w-10 h-10 rounded-full bg-[#58CC02] flex items-center justify-center">
                                  <span className="text-white font-bold">{student.name.charAt(0).toUpperCase()}</span>
                                </div>
                                <div>
                                  <p className="text-gray-900 font-semibold">{student.name}</p>
                                  <p className="text-gray-400 text-xs">{student.email}</p>
                                </div>
                              </div>
                            </td>
                            <td>
                              <div className="flex items-center gap-2">
                                <Progress value={student.pass_probability * 100} className="w-20 h-2" />
                                <span className="text-[#58CC02] font-bold">{Math.round(student.pass_probability * 100)}%</span>
                              </div>
                            </td>
                            <td>
                              <span className={`font-bold ${getRiskColor(student.risk_score)}`}>
                                {Math.round(student.risk_score * 100)}%
                              </span>
                            </td>
                            <td>
                              <div className="flex items-center gap-2">
                                <Activity className="w-4 h-4 text-purple-500" />
                                <span className="text-gray-900 font-semibold">{Math.round(student.engagement_score * 100)}%</span>
                              </div>
                            </td>
                            <td>
                              <Badge className={`${riskBadge.color} font-semibold border`}>{riskBadge.label}</Badge>
                            </td>
                            <td>
                              <Button variant="ghost" size="sm" className="text-gray-500 hover:text-gray-900 font-semibold">
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
          
          {activeTab === 'library' && (
            <div className="space-y-6 animate-fade-in" data-testid="library-tab">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-extrabold text-gray-900">Institution Library</h2>
                  <p className="text-gray-500">Upload materials, create flashcards, audio summaries, and videos</p>
                </div>
                <Dialog open={addLibraryOpen} onOpenChange={setAddLibraryOpen}>
                  <DialogTrigger asChild>
                    <button className="btn-duo px-4 py-2.5 text-sm flex items-center gap-2" data-testid="add-library-btn">
                      <Plus className="w-4 h-4" />
                      Add Item
                    </button>
                  </DialogTrigger>
                  <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-lg">
                    <DialogHeader>
                      <DialogTitle className="text-gray-900 font-extrabold">Add Library Item</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleAddLibraryItem} className="space-y-4">
                      <div className="space-y-2">
                        <Label className="text-gray-700 font-semibold">Title</Label>
                        <Input
                          value={newLibraryItem.title}
                          onChange={(e) => setNewLibraryItem(prev => ({ ...prev, title: e.target.value }))}
                          className="input-duo"
                          placeholder="e.g., IELTS Reading Tips"
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label className="text-gray-700 font-semibold">Type</Label>
                        <Select
                          value={newLibraryItem.item_type}
                          onValueChange={(value) => setNewLibraryItem(prev => ({ ...prev, item_type: value }))}
                        >
                          <SelectTrigger className="input-duo">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="material">Study Material</SelectItem>
                            <SelectItem value="flashcard">Flashcards</SelectItem>
                            <SelectItem value="audio">Audio Summary</SelectItem>
                            <SelectItem value="video">Video Class</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label className="text-gray-700 font-semibold">Exam Type (optional)</Label>
                        <Select
                          value={newLibraryItem.exam_type}
                          onValueChange={(value) => setNewLibraryItem(prev => ({ ...prev, exam_type: value }))}
                        >
                          <SelectTrigger className="input-duo">
                            <SelectValue placeholder="Select exam" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="toefl">TOEFL</SelectItem>
                            <SelectItem value="ielts">IELTS</SelectItem>
                            <SelectItem value="cambridge">Cambridge</SelectItem>
                            <SelectItem value="trinity">Trinity</SelectItem>
                            <SelectItem value="toeic">TOEIC</SelectItem>
                            <SelectItem value="celpip">CELPIP</SelectItem>
                            <SelectItem value="pte">PTE</SelectItem>
                            <SelectItem value="oet">OET</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label className="text-gray-700 font-semibold">Description</Label>
                        <Textarea
                          value={newLibraryItem.description}
                          onChange={(e) => setNewLibraryItem(prev => ({ ...prev, description: e.target.value }))}
                          className="input-duo min-h-[100px]"
                          placeholder="Brief description of this content..."
                        />
                      </div>
                      <div className="space-y-2">
                        <Label className="text-gray-700 font-semibold">Content</Label>
                        <Textarea
                          value={newLibraryItem.content}
                          onChange={(e) => setNewLibraryItem(prev => ({ ...prev, content: e.target.value }))}
                          className="input-duo min-h-[150px]"
                          placeholder="Paste your content here or add URL for video/audio..."
                        />
                      </div>
                      <button type="submit" className="btn-duo w-full py-3">
                        Add to Library
                      </button>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
              
              {/* Library Items Grid */}
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {libraryItems.length === 0 ? (
                  <Card className="col-span-full bg-white border-2 border-gray-100 rounded-2xl p-12 text-center">
                    <FolderOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-gray-900 mb-2">Library is Empty</h3>
                    <p className="text-gray-500 mb-6">Start adding materials, flashcards, and videos for your students</p>
                    <button onClick={() => setAddLibraryOpen(true)} className="btn-duo px-6 py-3">
                      <Plus className="w-4 h-4 mr-2" />
                      Add First Item
                    </button>
                  </Card>
                ) : (
                  libraryItems.map((item) => {
                    const ItemIcon = getItemIcon(item.item_type);
                    return (
                      <Card key={item.id} className="card-duo" data-testid={`library-item-${item.id}`}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div className={`feature-icon ${
                              item.item_type === 'material' ? 'feature-icon-blue' :
                              item.item_type === 'flashcard' ? 'feature-icon-purple' :
                              item.item_type === 'audio' ? 'feature-icon-orange' :
                              'feature-icon-green'
                            }`}>
                              <ItemIcon className="w-6 h-6" />
                            </div>
                            <button
                              onClick={() => handleDeleteLibraryItem(item.id)}
                              className="text-gray-400 hover:text-red-500 transition-colors"
                            >
                              <Trash2 className="w-5 h-5" />
                            </button>
                          </div>
                          <h3 className="text-lg font-bold text-gray-900 mb-2">{item.title}</h3>
                          <p className="text-gray-500 text-sm mb-4 line-clamp-2">{item.description || 'No description'}</p>
                          <div className="flex items-center gap-2">
                            <Badge className="bg-gray-100 text-gray-600 border-gray-200 capitalize font-semibold">
                              {item.item_type}
                            </Badge>
                            {item.exam_type && (
                              <Badge className={`badge-${item.exam_type} font-semibold`}>
                                {item.exam_type.toUpperCase()}
                              </Badge>
                            )}
                            {item.offline_available && (
                              <Badge className="bg-green-100 text-green-600 border-green-200 font-semibold">
                                Offline
                              </Badge>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })
                )}
              </div>
            </div>
          )}
          
          {activeTab === 'analytics' && (
            <div className="space-y-6 animate-fade-in" data-testid="analytics-tab">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-extrabold text-gray-900">Predictive Analytics & Risk Management</h2>
                <Button onClick={fetchAnalyticsData} variant="outline" disabled={analyticsLoading}>
                  {analyticsLoading ? 'Loading...' : 'Refresh Data'}
                </Button>
              </div>

              {analyticsLoading ? (
                <div className="flex items-center justify-center py-20">
                  <div className="w-12 h-12 border-4 border-[#58CC02] border-t-transparent rounded-full animate-spin"></div>
                </div>
              ) : (
                <>
                  {/* Impact Metrics Banner */}
                  <div className="bg-gradient-to-r from-[#58CC02] to-[#46a302] rounded-2xl p-6 text-white">
                    <h3 className="text-lg font-bold mb-4">🚀 Your AI-Powered Impact</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-4xl font-extrabold">10x</div>
                        <div className="text-sm opacity-90">Student Capacity</div>
                      </div>
                      <div className="text-center">
                        <div className="text-4xl font-extrabold text-yellow-300">+23%</div>
                        <div className="text-sm opacity-90">Pass Rate Increase</div>
                      </div>
                      <div className="text-center">
                        <div className="text-4xl font-extrabold">-60%</div>
                        <div className="text-sm opacity-90">No-Show Reduction</div>
                      </div>
                      <div className="text-center">
                        <div className="text-4xl font-extrabold">⚡ Seconds</div>
                        <div className="text-sm opacity-90">Feedback Time</div>
                      </div>
                    </div>
                  </div>

                  {/* KPIs Row */}
                  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                    <Card className="bg-white border-2 border-gray-100 rounded-xl">
                      <CardContent className="p-4 text-center">
                        <Users className="w-8 h-8 mx-auto mb-2 text-blue-500" />
                        <div className="text-2xl font-extrabold text-gray-900">{analyticsData?.kpis?.total_students || 0}</div>
                        <div className="text-xs text-gray-500">Total Students</div>
                      </CardContent>
                    </Card>
                    <Card className="bg-white border-2 border-gray-100 rounded-xl">
                      <CardContent className="p-4 text-center">
                        <Activity className="w-8 h-8 mx-auto mb-2 text-green-500" />
                        <div className="text-2xl font-extrabold text-gray-900">{analyticsData?.kpis?.active_students || 0}</div>
                        <div className="text-xs text-gray-500">Active (7 days)</div>
                      </CardContent>
                    </Card>
                    <Card className="bg-white border-2 border-gray-100 rounded-xl">
                      <CardContent className="p-4 text-center">
                        <Award className="w-8 h-8 mx-auto mb-2 text-yellow-500" />
                        <div className="text-2xl font-extrabold text-gray-900">{analyticsData?.kpis?.pass_rate || 0}%</div>
                        <div className="text-xs text-gray-500">Pass Rate</div>
                      </CardContent>
                    </Card>
                    <Card className="bg-white border-2 border-gray-100 rounded-xl">
                      <CardContent className="p-4 text-center">
                        <TrendingUp className="w-8 h-8 mx-auto mb-2 text-purple-500" />
                        <div className="text-2xl font-extrabold text-gray-900">{analyticsData?.kpis?.engagement_rate || 0}%</div>
                        <div className="text-xs text-gray-500">Engagement</div>
                      </CardContent>
                    </Card>
                    <Card className="bg-white border-2 border-gray-100 rounded-xl">
                      <CardContent className="p-4 text-center">
                        <Target className="w-8 h-8 mx-auto mb-2 text-indigo-500" />
                        <div className="text-2xl font-extrabold text-gray-900">{analyticsData?.kpis?.average_score || 0}</div>
                        <div className="text-xs text-gray-500">Avg Score</div>
                      </CardContent>
                    </Card>
                    <Card className="bg-white border-2 border-gray-100 rounded-xl">
                      <CardContent className="p-4 text-center">
                        <BookOpen className="w-8 h-8 mx-auto mb-2 text-cyan-500" />
                        <div className="text-2xl font-extrabold text-gray-900">{analyticsData?.kpis?.total_exams_taken || 0}</div>
                        <div className="text-xs text-gray-500">Exams Taken</div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Risk Distribution & At-Risk Students */}
                  <div className="grid lg:grid-cols-3 gap-6">
                    {/* Risk Distribution Chart */}
                    <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                      <CardHeader>
                        <CardTitle className="text-gray-900 font-extrabold flex items-center gap-2">
                          <AlertTriangle className="w-5 h-5 text-orange-500" />
                          Risk Distribution
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          <div className="flex items-center justify-between p-3 bg-red-50 rounded-xl border border-red-200">
                            <div className="flex items-center gap-2">
                              <div className="w-3 h-3 rounded-full bg-red-500"></div>
                              <span className="font-semibold text-red-700">High Risk</span>
                            </div>
                            <span className="text-2xl font-extrabold text-red-600">{analyticsData?.risk_distribution?.high_risk || 0}</span>
                          </div>
                          <div className="flex items-center justify-between p-3 bg-orange-50 rounded-xl border border-orange-200">
                            <div className="flex items-center gap-2">
                              <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                              <span className="font-semibold text-orange-700">Medium Risk</span>
                            </div>
                            <span className="text-2xl font-extrabold text-orange-600">{analyticsData?.risk_distribution?.medium_risk || 0}</span>
                          </div>
                          <div className="flex items-center justify-between p-3 bg-green-50 rounded-xl border border-green-200">
                            <div className="flex items-center gap-2">
                              <div className="w-3 h-3 rounded-full bg-green-500"></div>
                              <span className="font-semibold text-green-700">Low Risk</span>
                            </div>
                            <span className="text-2xl font-extrabold text-green-600">{analyticsData?.risk_distribution?.low_risk || 0}</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {/* At-Risk Students */}
                    <Card className="bg-white border-2 border-gray-100 rounded-2xl lg:col-span-2">
                      <CardHeader>
                        <CardTitle className="text-gray-900 font-extrabold flex items-center gap-2">
                          <AlertTriangle className="w-5 h-5 text-red-500" />
                          Students Requiring Attention ({atRiskStudents.length})
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3 max-h-[300px] overflow-y-auto">
                          {atRiskStudents.length === 0 ? (
                            <div className="text-center py-8 text-gray-500">
                              <Award className="w-12 h-12 mx-auto mb-2 text-green-500" />
                              <p className="font-semibold">All students are on track!</p>
                            </div>
                          ) : (
                            atRiskStudents.slice(0, 5).map((student) => (
                              <div key={student.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                                <div className="flex items-center gap-3">
                                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                                    student.dropout_category === 'high' ? 'bg-red-100' : 'bg-orange-100'
                                  }`}>
                                    <span className="font-bold text-sm">{student.name?.charAt(0) || '?'}</span>
                                  </div>
                                  <div>
                                    <p className="font-semibold text-gray-900">{student.name}</p>
                                    <p className="text-xs text-gray-500">{student.exam_type?.toUpperCase()} • {student.primary_concern}</p>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <Badge className={`${
                                    student.dropout_category === 'high' ? 'bg-red-100 text-red-700 border-red-200' : 
                                    'bg-orange-100 text-orange-700 border-orange-200'
                                  }`}>
                                    {student.pass_probability}% Pass
                                  </Badge>
                                  <p className="text-xs text-gray-500 mt-1">Dropout: {student.dropout_risk}%</p>
                                </div>
                              </div>
                            ))
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Cohort Analysis */}
                  <div className="grid lg:grid-cols-2 gap-6">
                    {/* By Exam Type */}
                    <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                      <CardHeader>
                        <CardTitle className="text-gray-900 font-extrabold">📊 Performance by Exam Type</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {cohortData?.by_exam_type?.map((cohort) => (
                            <div key={cohort.cohort_name} className="p-3 bg-gray-50 rounded-xl">
                              <div className="flex items-center justify-between mb-2">
                                <span className="font-bold text-gray-900">{cohort.cohort_name}</span>
                                <Badge variant="outline">{cohort.total_students} students</Badge>
                              </div>
                              <div className="grid grid-cols-3 gap-2 text-sm">
                                <div className="text-center">
                                  <div className="text-lg font-bold text-blue-600">{cohort.average_score}</div>
                                  <div className="text-xs text-gray-500">Avg Score</div>
                                </div>
                                <div className="text-center">
                                  <div className="text-lg font-bold text-green-600">{cohort.pass_rate}%</div>
                                  <div className="text-xs text-gray-500">Pass Rate</div>
                                </div>
                                <div className="text-center">
                                  <div className="text-lg font-bold text-purple-600">{cohort.active_rate}%</div>
                                  <div className="text-xs text-gray-500">Active</div>
                                </div>
                              </div>
                            </div>
                          ))}
                          {(!cohortData?.by_exam_type || cohortData.by_exam_type.length === 0) && (
                            <p className="text-center text-gray-500 py-4">No cohort data available</p>
                          )}
                        </div>
                      </CardContent>
                    </Card>

                    {/* By Enrollment Month */}
                    <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                      <CardHeader>
                        <CardTitle className="text-gray-900 font-extrabold">📅 Performance by Enrollment Month</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {cohortData?.by_enrollment_month?.map((cohort) => (
                            <div key={cohort.cohort_name} className="p-3 bg-gray-50 rounded-xl">
                              <div className="flex items-center justify-between mb-2">
                                <span className="font-bold text-gray-900">{cohort.cohort_name}</span>
                                <Badge variant="outline">{cohort.total_students} students</Badge>
                              </div>
                              <div className="grid grid-cols-3 gap-2 text-sm">
                                <div className="text-center">
                                  <div className="text-lg font-bold text-blue-600">{cohort.average_score}</div>
                                  <div className="text-xs text-gray-500">Avg Score</div>
                                </div>
                                <div className="text-center">
                                  <div className="text-lg font-bold text-green-600">{cohort.total_attempts}</div>
                                  <div className="text-xs text-gray-500">Attempts</div>
                                </div>
                                <div className="text-center">
                                  <div className="text-lg font-bold text-purple-600">{cohort.retention_rate}%</div>
                                  <div className="text-xs text-gray-500">Retention</div>
                                </div>
                              </div>
                            </div>
                          ))}
                          {(!cohortData?.by_enrollment_month || cohortData.by_enrollment_month.length === 0) && (
                            <p className="text-center text-gray-500 py-4">No monthly data available</p>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* All Students with Predictions */}
                  <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                    <CardHeader>
                      <CardTitle className="text-gray-900 font-extrabold">🎯 All Students - Pass Probability & Dropout Risk</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b border-gray-200">
                              <th className="text-left py-3 px-4 font-bold text-gray-700">Student</th>
                              <th className="text-left py-3 px-4 font-bold text-gray-700">Exam</th>
                              <th className="text-center py-3 px-4 font-bold text-gray-700">Avg Score</th>
                              <th className="text-center py-3 px-4 font-bold text-gray-700">Pass Prob.</th>
                              <th className="text-center py-3 px-4 font-bold text-gray-700">Dropout Risk</th>
                              <th className="text-center py-3 px-4 font-bold text-gray-700">Status</th>
                            </tr>
                          </thead>
                          <tbody>
                            {studentsAnalytics.slice(0, 10).map((student) => (
                              <tr key={student.id} className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="py-3 px-4">
                                  <div className="flex items-center gap-2">
                                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center font-bold text-sm">
                                      {student.name?.charAt(0) || '?'}
                                    </div>
                                    <div>
                                      <p className="font-semibold text-gray-900">{student.name}</p>
                                      <p className="text-xs text-gray-500">{student.email}</p>
                                    </div>
                                  </div>
                                </td>
                                <td className="py-3 px-4">
                                  <Badge variant="outline">{student.exam_type?.toUpperCase()}</Badge>
                                </td>
                                <td className="py-3 px-4 text-center">
                                  <span className="font-bold">{student.performance?.average_score || 0}</span>
                                </td>
                                <td className="py-3 px-4 text-center">
                                  <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-sm font-bold ${
                                    student.pass_prediction?.pass_probability >= 75 ? 'bg-green-100 text-green-700' :
                                    student.pass_prediction?.pass_probability >= 50 ? 'bg-yellow-100 text-yellow-700' :
                                    'bg-red-100 text-red-700'
                                  }`}>
                                    {student.pass_prediction?.pass_probability || 0}%
                                  </div>
                                </td>
                                <td className="py-3 px-4 text-center">
                                  <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-sm font-bold ${
                                    student.dropout_risk?.dropout_risk <= 30 ? 'bg-green-100 text-green-700' :
                                    student.dropout_risk?.dropout_risk <= 60 ? 'bg-orange-100 text-orange-700' :
                                    'bg-red-100 text-red-700'
                                  }`}>
                                    {student.dropout_risk?.dropout_risk || 0}%
                                  </div>
                                </td>
                                <td className="py-3 px-4 text-center">
                                  <Badge className={`${
                                    student.pass_prediction?.risk_level === 'low' ? 'bg-green-100 text-green-700 border-green-200' :
                                    student.pass_prediction?.risk_level === 'medium' ? 'bg-orange-100 text-orange-700 border-orange-200' :
                                    'bg-red-100 text-red-700 border-red-200'
                                  }`}>
                                    {student.pass_prediction?.risk_level || 'unknown'}
                                  </Badge>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                        {studentsAnalytics.length === 0 && (
                          <p className="text-center text-gray-500 py-8">No student analytics available. Add students to see predictions.</p>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </>
              )}
            </div>
          )}
          
          {activeTab === 'exams' && (
            <div className="space-y-6 animate-fade-in" data-testid="exams-tab">
              <h2 className="text-2xl font-extrabold text-gray-900">Exam Management</h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[
                  { id: 'toefl', name: 'TOEFL', color: 'bg-blue-500' },
                  { id: 'ielts', name: 'IELTS', color: 'bg-red-500' },
                  { id: 'cambridge', name: 'Cambridge', color: 'bg-purple-500' },
                  { id: 'trinity', name: 'Trinity', color: 'bg-pink-500' },
                  { id: 'toeic', name: 'TOEIC', color: 'bg-indigo-500' },
                  { id: 'celpip', name: 'CELPIP', color: 'bg-cyan-500' },
                  { id: 'pte', name: 'PTE', color: 'bg-orange-500' },
                  { id: 'oet', name: 'OET', color: 'bg-green-500' }
                ].map((exam) => (
                  <Card key={exam.id} className="card-duo" data-testid={`exam-manage-${exam.id}`}>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className={`w-12 h-12 rounded-xl ${exam.color} flex items-center justify-center`}>
                          <BookOpen className="w-6 h-6 text-white" />
                        </div>
                        <Badge className="bg-green-100 text-green-700 border-green-200 font-semibold">Active</Badge>
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2">{exam.name}</h3>
                      <p className="text-gray-500 text-sm mb-4">Full exam simulation with AI feedback</p>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Students enrolled</span>
                        <span className="text-gray-900 font-bold">{Math.floor(Math.random() * 50) + 10}</span>
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
