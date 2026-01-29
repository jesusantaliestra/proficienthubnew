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
  FileText, Video, Headphones, Layers, Trash2, Globe, Store, ShoppingCart, Star, Package, Play, Radio, Calendar, Palette, Zap, Cog, Library,
  Key, Link2, Building2, Users2
} from 'lucide-react';
import CRMSupreme from '../components/CRMSupreme';
import InstitutionSettings from '../components/InstitutionSettings';
import ContentLibrary from '../components/ContentLibrary';
import PushNotificationsPanel from '../components/PushNotificationsPanel';
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
  const [marketplaceData, setMarketplaceData] = useState(null);
  const [myListings, setMyListings] = useState([]);
  const [marketplaceLoading, setMarketplaceLoading] = useState(false);
  const [addListingOpen, setAddListingOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [newListing, setNewListing] = useState({
    title: '',
    description: '',
    category: 'tutoring',
    price: '',
    price_type: 'per_student',
    exam_types: [],
    delivery_method: 'online'
  });
  const [videoClassesData, setVideoClassesData] = useState(null);
  const [videoClassesLoading, setVideoClassesLoading] = useState(false);
  const [addClassOpen, setAddClassOpen] = useState(false);
  const [newVideoClass, setNewVideoClass] = useState({
    title: '',
    description: '',
    exam_type: 'ielts',
    skill: 'speaking',
    class_type: 'live',
    duration_minutes: 60,
    scheduled_at: ''
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
    if (activeTab === 'crm') {
      fetchCrmData();
    }
  }, [activeTab]);

  const fetchCrmData = async () => {
    setCrmLoading(true);
    try {
      const response = await axios.get(`${API_URL}/crm/leads`);
      setCrmData(response.data);
    } catch (error) {
      console.error('Failed to fetch CRM data:', error);
      toast.error('Failed to load CRM data');
    } finally {
      setCrmLoading(false);
    }
  };

  const handleCreateLead = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/crm/leads`, {
        ...newLead,
        students_count: parseInt(newLead.students_count) || 0,
        estimated_value: parseFloat(newLead.estimated_value) || 0
      });
      toast.success('Lead created successfully!');
      setAddLeadOpen(false);
      setNewLead({
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
      fetchCrmData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create lead');
    }
  };

  const handleUpdateLeadStage = async (leadId, newStage) => {
    try {
      await axios.put(`${API_URL}/crm/leads/${leadId}`, { stage: newStage });
      toast.success('Lead stage updated!');
      fetchCrmData();
    } catch (error) {
      toast.error('Failed to update lead');
    }
  };

  const handleAddActivity = async (e) => {
    e.preventDefault();
    if (!selectedLead) return;
    try {
      await axios.post(`${API_URL}/crm/leads/${selectedLead.id}/activities`, {
        lead_id: selectedLead.id,
        ...newActivity
      });
      toast.success('Activity added!');
      setAddActivityOpen(false);
      setNewActivity({ activity_type: 'call', description: '', outcome: '' });
      fetchCrmData();
    } catch (error) {
      toast.error('Failed to add activity');
    }
  };

  const fetchMarketplaceData = async () => {
    setMarketplaceLoading(true);
    try {
      const [listingsRes, myListingsRes] = await Promise.all([
        axios.get(`${API_URL}/marketplace/listings${selectedCategory !== 'all' ? `?category=${selectedCategory}` : ''}`),
        axios.get(`${API_URL}/marketplace/my-listings`)
      ]);
      setMarketplaceData(listingsRes.data);
      setMyListings(myListingsRes.data.listings || []);
    } catch (error) {
      console.error('Failed to fetch marketplace data:', error);
      toast.error('Failed to load marketplace');
    } finally {
      setMarketplaceLoading(false);
    }
  };

  const handleCreateListing = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/marketplace/listings`, {
        ...newListing,
        price: parseFloat(newListing.price) || 0
      });
      toast.success('Listing created successfully!');
      setAddListingOpen(false);
      setNewListing({
        title: '',
        description: '',
        category: 'tutoring',
        price: '',
        price_type: 'per_student',
        exam_types: [],
        delivery_method: 'online'
      });
      fetchMarketplaceData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create listing');
    }
  };

  useEffect(() => {
    if (activeTab === 'marketplace') {
      fetchMarketplaceData();
    }
    if (activeTab === 'classes') {
      fetchVideoClasses();
    }
  }, [activeTab, selectedCategory]);

  const fetchVideoClasses = async () => {
    setVideoClassesLoading(true);
    try {
      const response = await axios.get(`${API_URL}/video-classes`);
      setVideoClassesData(response.data);
    } catch (error) {
      console.error('Failed to fetch video classes:', error);
      toast.error('Failed to load video classes');
    } finally {
      setVideoClassesLoading(false);
    }
  };

  const handleCreateVideoClass = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/video-classes`, {
        ...newVideoClass,
        duration_minutes: parseInt(newVideoClass.duration_minutes) || 60
      });
      toast.success('Video class created!');
      setAddClassOpen(false);
      setNewVideoClass({
        title: '',
        description: '',
        exam_type: 'ielts',
        skill: 'speaking',
        class_type: 'live',
        duration_minutes: 60,
        scheduled_at: ''
      });
      fetchVideoClasses();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create class');
    }
  };

  const handleStartClass = async (classId) => {
    try {
      await axios.put(`${API_URL}/video-classes/${classId}/status?status=live`);
      toast.success('Class is now live!');
      fetchVideoClasses();
    } catch (error) {
      toast.error('Failed to start class');
    }
  };

  const handleEndClass = async (classId) => {
    try {
      await axios.put(`${API_URL}/video-classes/${classId}/status?status=ended`);
      toast.success('Class ended');
      fetchVideoClasses();
    } catch (error) {
      toast.error('Failed to end class');
    }
  };

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
            { id: 'crm-supreme', icon: Zap, label: 'CRM Supreme', badge: 'PRO' },
            { id: 'marketplace', icon: Store, label: 'Marketplace' },
            { id: 'classes', icon: Video, label: 'Video Classes' },
            { id: 'library', icon: FolderOpen, label: 'Library' },
            { id: 'notifications', icon: Radio, label: 'Push Notif.', badge: 'NEW' },
            { id: 'analytics', icon: Activity, label: 'Analytics' },
            { id: 'exams', icon: BookOpen, label: 'Exams' },
            { id: 'settings', icon: Cog, label: 'Settings' }
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`sidebar-item w-full ${activeTab === item.id ? 'active' : ''}`}
              data-testid={`nav-${item.id}`}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
              {item.badge && (
                <span className="ml-auto text-[10px] font-bold bg-gradient-to-r from-purple-500 to-pink-500 text-white px-2 py-0.5 rounded-full">{item.badge}</span>
              )}
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
          <button 
            onClick={() => navigate('/institution/whitelabel')} 
            className="sidebar-item w-full" 
            data-testid="nav-whitelabel"
          >
            <Palette className="w-5 h-5" />
            <span>White-Label</span>
          </button>
          
          {/* Enterprise Features Section */}
          <div className="pt-4 mt-4 border-t border-gray-200">
            <p className="text-xs text-gray-400 uppercase font-bold mb-2 px-2">Enterprise</p>
            <button 
              onClick={() => navigate('/institution/api-keys')} 
              className="sidebar-item w-full" 
              data-testid="nav-api-keys"
            >
              <Key className="w-5 h-5" />
              <span>API Keys</span>
            </button>
            <button 
              onClick={() => navigate('/institution/integrations')} 
              className="sidebar-item w-full" 
              data-testid="nav-integrations"
            >
              <Link2 className="w-5 h-5" />
              <span>Integrations</span>
            </button>
            <button 
              onClick={() => navigate('/institution/erp')} 
              className="sidebar-item w-full" 
              data-testid="nav-erp"
            >
              <Building2 className="w-5 h-5" />
              <span>ERP / Billing</span>
            </button>
            <button 
              onClick={() => navigate('/institution/crm')} 
              className="sidebar-item w-full" 
              data-testid="nav-crm"
            >
              <Users2 className="w-5 h-5" />
              <span>CRM</span>
            </button>
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
          
          {/* B2B Marketplace Tab */}
          {activeTab === 'marketplace' && (
            <div className="space-y-6 animate-fade-in" data-testid="marketplace-tab">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-extrabold text-gray-900">B2B Academy Marketplace</h2>
                  <p className="text-gray-500">Buy and sell services to other academies</p>
                </div>
                <div className="flex gap-2">
                  <Dialog open={addListingOpen} onOpenChange={setAddListingOpen}>
                    <DialogTrigger asChild>
                      <Button className="btn-duo flex items-center gap-2">
                        <Plus className="w-4 h-4" />
                        Sell Service
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-md">
                      <DialogHeader>
                        <DialogTitle className="text-gray-900 font-extrabold">Create New Listing</DialogTitle>
                      </DialogHeader>
                      <form onSubmit={handleCreateListing} className="space-y-4">
                        <div>
                          <Label>Title *</Label>
                          <Input
                            value={newListing.title}
                            onChange={(e) => setNewListing({...newListing, title: e.target.value})}
                            required
                            className="input-duo"
                            placeholder="e.g., IELTS Speaking Practice Sessions"
                          />
                        </div>
                        <div>
                          <Label>Category *</Label>
                          <Select 
                            value={newListing.category} 
                            onValueChange={(v) => setNewListing({...newListing, category: v})}
                          >
                            <SelectTrigger className="input-duo">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="tutoring">👨‍🏫 Tutoring Services</SelectItem>
                              <SelectItem value="materials">📚 Study Materials</SelectItem>
                              <SelectItem value="courses">🎓 Full Courses</SelectItem>
                              <SelectItem value="exam_prep">📝 Exam Preparation</SelectItem>
                              <SelectItem value="teacher_training">👩‍🎓 Teacher Training</SelectItem>
                              <SelectItem value="mock_exams">✍️ Mock Exams</SelectItem>
                              <SelectItem value="speaking_practice">🗣️ Speaking Practice</SelectItem>
                              <SelectItem value="writing_review">✏️ Writing Review</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label>Price ($) *</Label>
                            <Input
                              type="number"
                              step="0.01"
                              value={newListing.price}
                              onChange={(e) => setNewListing({...newListing, price: e.target.value})}
                              required
                              className="input-duo"
                              placeholder="29.99"
                            />
                          </div>
                          <div>
                            <Label>Price Type</Label>
                            <Select 
                              value={newListing.price_type} 
                              onValueChange={(v) => setNewListing({...newListing, price_type: v})}
                            >
                              <SelectTrigger className="input-duo">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="per_student">Per Student</SelectItem>
                                <SelectItem value="per_session">Per Session</SelectItem>
                                <SelectItem value="per_course">Per Course</SelectItem>
                                <SelectItem value="flat_fee">Flat Fee</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                        <div>
                          <Label>Delivery Method</Label>
                          <Select 
                            value={newListing.delivery_method} 
                            onValueChange={(v) => setNewListing({...newListing, delivery_method: v})}
                          >
                            <SelectTrigger className="input-duo">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="online">🌐 Online</SelectItem>
                              <SelectItem value="in_person">🏢 In Person</SelectItem>
                              <SelectItem value="hybrid">🔄 Hybrid</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label>Description *</Label>
                          <Textarea
                            value={newListing.description}
                            onChange={(e) => setNewListing({...newListing, description: e.target.value})}
                            required
                            className="input-duo"
                            rows={3}
                            placeholder="Describe what you're offering..."
                          />
                        </div>
                        <Button type="submit" className="btn-duo w-full">Create Listing</Button>
                      </form>
                    </DialogContent>
                  </Dialog>
                </div>
              </div>

              {marketplaceLoading ? (
                <div className="flex items-center justify-center py-20">
                  <div className="w-12 h-12 border-4 border-[#58CC02] border-t-transparent rounded-full animate-spin"></div>
                </div>
              ) : (
                <>
                  {/* Category Filters */}
                  <div className="flex gap-2 flex-wrap">
                    <Button 
                      size="sm" 
                      variant={selectedCategory === 'all' ? 'default' : 'outline'}
                      onClick={() => setSelectedCategory('all')}
                      className={selectedCategory === 'all' ? 'bg-[#58CC02] hover:bg-[#46a302]' : ''}
                    >
                      All
                    </Button>
                    {['tutoring', 'materials', 'courses', 'exam_prep', 'speaking_practice', 'writing_review'].map((cat) => (
                      <Button 
                        key={cat}
                        size="sm" 
                        variant={selectedCategory === cat ? 'default' : 'outline'}
                        onClick={() => setSelectedCategory(cat)}
                        className={selectedCategory === cat ? 'bg-[#58CC02] hover:bg-[#46a302]' : ''}
                      >
                        {cat.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                      </Button>
                    ))}
                  </div>

                  {/* My Listings Section */}
                  {myListings.length > 0 && (
                    <Card className="bg-gradient-to-r from-purple-50 to-indigo-50 border-2 border-purple-200 rounded-2xl">
                      <CardHeader>
                        <CardTitle className="text-gray-900 font-extrabold flex items-center gap-2">
                          <Package className="w-5 h-5 text-purple-600" />
                          My Listings ({myListings.length})
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {myListings.map((listing) => (
                            <div key={listing.id} className="bg-white rounded-xl p-4 border border-purple-100">
                              <div className="flex items-center justify-between mb-2">
                                <Badge variant="outline" className="text-purple-600 border-purple-200">{listing.category}</Badge>
                                <span className="font-bold text-green-600">${listing.price}</span>
                              </div>
                              <h4 className="font-bold text-gray-900 truncate">{listing.title}</h4>
                              <div className="flex items-center justify-between mt-3 text-sm text-gray-500">
                                <span>🛒 {listing.sales_count} sales</span>
                                <span>⭐ {listing.rating || 'No ratings'}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* All Marketplace Listings */}
                  <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                    <CardHeader>
                      <CardTitle className="text-gray-900 font-extrabold flex items-center gap-2">
                        <Store className="w-5 h-5 text-[#58CC02]" />
                        Marketplace Listings ({marketplaceData?.total || 0})
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {marketplaceData?.listings?.length > 0 ? (
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {marketplaceData.listings.map((listing) => (
                            <div key={listing.id} className="bg-gray-50 rounded-xl p-4 hover:shadow-md transition-shadow border border-gray-100">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-2xl">{listing.category_info?.icon || '📦'}</span>
                                {listing.is_featured && (
                                  <Badge className="bg-yellow-100 text-yellow-700 border-yellow-200">⭐ Featured</Badge>
                                )}
                              </div>
                              <h4 className="font-bold text-gray-900 mb-1">{listing.title}</h4>
                              <p className="text-sm text-gray-500 line-clamp-2 mb-3">{listing.description}</p>
                              <div className="flex items-center justify-between">
                                <div>
                                  <span className="text-xl font-extrabold text-green-600">${listing.price}</span>
                                  <span className="text-xs text-gray-400 ml-1">/{listing.price_type?.replace('_', ' ')}</span>
                                </div>
                                <Badge variant="outline" className="text-xs">{listing.delivery_method}</Badge>
                              </div>
                              <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-200">
                                <span className="text-xs text-gray-500">{listing.seller_name}</span>
                                <div className="flex items-center gap-2 text-xs text-gray-500">
                                  <span className="flex items-center gap-1">
                                    <Star className="w-3 h-3 text-yellow-500" /> {listing.rating || '0'}
                                  </span>
                                  <span>•</span>
                                  <span>{listing.sales_count} sold</span>
                                </div>
                              </div>
                              <Button size="sm" variant="outline" className="w-full mt-3">
                                <ShoppingCart className="w-3 h-3 mr-2" /> View Details
                              </Button>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-12">
                          <Store className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                          <h3 className="text-lg font-bold text-gray-700 mb-2">No listings yet</h3>
                          <p className="text-gray-500 mb-4">Be the first to offer your services!</p>
                          <Button onClick={() => setAddListingOpen(true)} className="btn-duo">
                            <Plus className="w-4 h-4 mr-2" /> Create Your First Listing
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </>
              )}
            </div>
          )}
          
          {/* Video Classes Tab */}
          {activeTab === 'classes' && (
            <div className="space-y-6 animate-fade-in" data-testid="classes-tab">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-extrabold text-gray-900">Video Classes & Streaming</h2>
                  <p className="text-gray-500">Schedule live classes or upload recorded lessons</p>
                </div>
                <Dialog open={addClassOpen} onOpenChange={setAddClassOpen}>
                  <DialogTrigger asChild>
                    <Button className="btn-duo flex items-center gap-2">
                      <Plus className="w-4 h-4" />
                      Create Class
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-md">
                    <DialogHeader>
                      <DialogTitle className="text-gray-900 font-extrabold">Create Video Class</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleCreateVideoClass} className="space-y-4">
                      <div>
                        <Label>Title *</Label>
                        <Input
                          value={newVideoClass.title}
                          onChange={(e) => setNewVideoClass({...newVideoClass, title: e.target.value})}
                          required
                          className="input-duo"
                          placeholder="e.g., IELTS Speaking Part 2 Masterclass"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label>Exam Type</Label>
                          <Select 
                            value={newVideoClass.exam_type} 
                            onValueChange={(v) => setNewVideoClass({...newVideoClass, exam_type: v})}
                          >
                            <SelectTrigger className="input-duo">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="ielts">IELTS</SelectItem>
                              <SelectItem value="toefl">TOEFL</SelectItem>
                              <SelectItem value="cambridge">Cambridge</SelectItem>
                              <SelectItem value="trinity">Trinity</SelectItem>
                              <SelectItem value="pte">PTE</SelectItem>
                              <SelectItem value="oet">OET</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label>Skill Focus</Label>
                          <Select 
                            value={newVideoClass.skill} 
                            onValueChange={(v) => setNewVideoClass({...newVideoClass, skill: v})}
                          >
                            <SelectTrigger className="input-duo">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="reading">📖 Reading</SelectItem>
                              <SelectItem value="writing">✍️ Writing</SelectItem>
                              <SelectItem value="listening">🎧 Listening</SelectItem>
                              <SelectItem value="speaking">🗣️ Speaking</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label>Class Type</Label>
                          <Select 
                            value={newVideoClass.class_type} 
                            onValueChange={(v) => setNewVideoClass({...newVideoClass, class_type: v})}
                          >
                            <SelectTrigger className="input-duo">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="live">🔴 Live Class</SelectItem>
                              <SelectItem value="recorded">📹 Recorded</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label>Duration (min)</Label>
                          <Input
                            type="number"
                            value={newVideoClass.duration_minutes}
                            onChange={(e) => setNewVideoClass({...newVideoClass, duration_minutes: e.target.value})}
                            className="input-duo"
                          />
                        </div>
                      </div>
                      {newVideoClass.class_type === 'live' && (
                        <div>
                          <Label>Scheduled Date & Time</Label>
                          <Input
                            type="datetime-local"
                            value={newVideoClass.scheduled_at}
                            onChange={(e) => setNewVideoClass({...newVideoClass, scheduled_at: e.target.value})}
                            className="input-duo"
                          />
                        </div>
                      )}
                      <div>
                        <Label>Description</Label>
                        <Textarea
                          value={newVideoClass.description}
                          onChange={(e) => setNewVideoClass({...newVideoClass, description: e.target.value})}
                          className="input-duo"
                          rows={2}
                          placeholder="What will students learn?"
                        />
                      </div>
                      <Button type="submit" className="btn-duo w-full">Create Class</Button>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>

              {videoClassesLoading ? (
                <div className="flex items-center justify-center py-20">
                  <div className="w-12 h-12 border-4 border-[#58CC02] border-t-transparent rounded-full animate-spin"></div>
                </div>
              ) : (
                <>
                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-4">
                    <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-xl">
                      <CardContent className="p-4 flex items-center gap-4">
                        <Radio className="w-10 h-10" />
                        <div>
                          <div className="text-3xl font-extrabold">{videoClassesData?.stats?.total_live || 0}</div>
                          <div className="text-sm opacity-90">Live Classes</div>
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl">
                      <CardContent className="p-4 flex items-center gap-4">
                        <Video className="w-10 h-10" />
                        <div>
                          <div className="text-3xl font-extrabold">{videoClassesData?.stats?.total_recorded || 0}</div>
                          <div className="text-sm opacity-90">Recorded</div>
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl">
                      <CardContent className="p-4 flex items-center gap-4">
                        <Calendar className="w-10 h-10" />
                        <div>
                          <div className="text-3xl font-extrabold">{videoClassesData?.stats?.upcoming || 0}</div>
                          <div className="text-sm opacity-90">Upcoming</div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Live Classes */}
                  <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                    <CardHeader>
                      <CardTitle className="text-gray-900 font-extrabold flex items-center gap-2">
                        <Radio className="w-5 h-5 text-red-500" />
                        Live Classes ({videoClassesData?.live_classes?.length || 0})
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {videoClassesData?.live_classes?.length > 0 ? (
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {videoClassesData.live_classes.map((cls) => (
                            <div key={cls.id} className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                              <div className="flex items-center justify-between mb-2">
                                <Badge className={`${
                                  cls.status === 'live' ? 'bg-red-100 text-red-700 border-red-200' :
                                  cls.status === 'scheduled' ? 'bg-yellow-100 text-yellow-700 border-yellow-200' :
                                  'bg-gray-100 text-gray-700 border-gray-200'
                                }`}>
                                  {cls.status === 'live' ? '🔴 LIVE' : cls.status === 'scheduled' ? '📅 Scheduled' : cls.status}
                                </Badge>
                                <Badge variant="outline">{cls.exam_type.toUpperCase()}</Badge>
                              </div>
                              <h4 className="font-bold text-gray-900 mb-1">{cls.title}</h4>
                              <p className="text-sm text-gray-500 line-clamp-2 mb-3">{cls.description}</p>
                              <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                                <span>⏱️ {cls.duration_minutes} min</span>
                                <span>👥 {cls.enrolled_count}/{cls.max_students}</span>
                              </div>
                              {cls.scheduled_at && (
                                <p className="text-xs text-gray-400 mb-3">
                                  📅 {new Date(cls.scheduled_at).toLocaleString()}
                                </p>
                              )}
                              {cls.room_code && (
                                <div className="bg-blue-50 rounded-lg p-2 text-center mb-3">
                                  <p className="text-xs text-blue-600">Room Code</p>
                                  <p className="text-lg font-bold text-blue-700">{cls.room_code}</p>
                                </div>
                              )}
                              <div className="flex gap-2">
                                {cls.status === 'scheduled' && (
                                  <Button size="sm" onClick={() => handleStartClass(cls.id)} className="flex-1 bg-red-500 hover:bg-red-600 text-white">
                                    <Play className="w-3 h-3 mr-1" /> Start
                                  </Button>
                                )}
                                {cls.status === 'live' && (
                                  <Button size="sm" onClick={() => handleEndClass(cls.id)} variant="outline" className="flex-1">
                                    End Class
                                  </Button>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <Radio className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                          <p className="text-gray-500">No live classes scheduled</p>
                          <Button onClick={() => setAddClassOpen(true)} variant="outline" className="mt-3">
                            Schedule a Live Class
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Recorded Classes */}
                  <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                    <CardHeader>
                      <CardTitle className="text-gray-900 font-extrabold flex items-center gap-2">
                        <Video className="w-5 h-5 text-blue-500" />
                        Recorded Classes ({videoClassesData?.recorded_classes?.length || 0})
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {videoClassesData?.recorded_classes?.length > 0 ? (
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {videoClassesData.recorded_classes.map((cls) => (
                            <div key={cls.id} className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                              <div className="flex items-center justify-between mb-2">
                                <Badge variant="outline">{cls.exam_type.toUpperCase()}</Badge>
                                <span className="text-xs text-gray-400">{cls.skill}</span>
                              </div>
                              <h4 className="font-bold text-gray-900 mb-1">{cls.title}</h4>
                              <p className="text-sm text-gray-500 line-clamp-2 mb-3">{cls.description}</p>
                              <div className="flex items-center justify-between text-sm text-gray-500">
                                <span>⏱️ {cls.duration_minutes} min</span>
                                <span>👁️ {cls.views_count || 0} views</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <Video className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                          <p className="text-gray-500">No recorded classes yet</p>
                          <Button onClick={() => { setNewVideoClass({...newVideoClass, class_type: 'recorded'}); setAddClassOpen(true); }} variant="outline" className="mt-3">
                            Upload a Recording
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </>
              )}
            </div>
          )}
          
          {activeTab === 'library' && (
            <div className="space-y-6 animate-fade-in" data-testid="library-tab">
              <ContentLibrary />
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
          
          {/* CRM & Sales Pipeline Tab */}
          {activeTab === 'crm' && (
            <div className="space-y-6 animate-fade-in" data-testid="crm-tab">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-extrabold text-gray-900">CRM & Sales Pipeline</h2>
                <div className="flex gap-2">
                  <Button onClick={fetchCrmData} variant="outline" disabled={crmLoading}>
                    {crmLoading ? 'Loading...' : 'Refresh'}
                  </Button>
                  <Dialog open={addLeadOpen} onOpenChange={setAddLeadOpen}>
                    <DialogTrigger asChild>
                      <Button className="btn-duo flex items-center gap-2">
                        <Plus className="w-4 h-4" />
                        Add Lead
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-md">
                      <DialogHeader>
                        <DialogTitle className="text-gray-900 font-extrabold">Add New Lead</DialogTitle>
                      </DialogHeader>
                      <form onSubmit={handleCreateLead} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="col-span-2">
                            <Label>Institution Name *</Label>
                            <Input
                              value={newLead.institution_name}
                              onChange={(e) => setNewLead({...newLead, institution_name: e.target.value})}
                              required
                              className="input-duo"
                            />
                          </div>
                          <div>
                            <Label>Contact Name *</Label>
                            <Input
                              value={newLead.contact_name}
                              onChange={(e) => setNewLead({...newLead, contact_name: e.target.value})}
                              required
                              className="input-duo"
                            />
                          </div>
                          <div>
                            <Label>Email *</Label>
                            <Input
                              type="email"
                              value={newLead.email}
                              onChange={(e) => setNewLead({...newLead, email: e.target.value})}
                              required
                              className="input-duo"
                            />
                          </div>
                          <div>
                            <Label>Phone</Label>
                            <Input
                              value={newLead.phone}
                              onChange={(e) => setNewLead({...newLead, phone: e.target.value})}
                              className="input-duo"
                            />
                          </div>
                          <div>
                            <Label>Country</Label>
                            <Input
                              value={newLead.country}
                              onChange={(e) => setNewLead({...newLead, country: e.target.value})}
                              className="input-duo"
                            />
                          </div>
                          <div>
                            <Label>Est. Students</Label>
                            <Input
                              type="number"
                              value={newLead.students_count}
                              onChange={(e) => setNewLead({...newLead, students_count: e.target.value})}
                              className="input-duo"
                            />
                          </div>
                          <div>
                            <Label>Est. Deal Value ($)</Label>
                            <Input
                              type="number"
                              value={newLead.estimated_value}
                              onChange={(e) => setNewLead({...newLead, estimated_value: e.target.value})}
                              className="input-duo"
                            />
                          </div>
                          <div className="col-span-2">
                            <Label>Notes</Label>
                            <Textarea
                              value={newLead.notes}
                              onChange={(e) => setNewLead({...newLead, notes: e.target.value})}
                              className="input-duo"
                              rows={2}
                            />
                          </div>
                        </div>
                        <Button type="submit" className="btn-duo w-full">Create Lead</Button>
                      </form>
                    </DialogContent>
                  </Dialog>
                </div>
              </div>

              {crmLoading ? (
                <div className="flex items-center justify-center py-20">
                  <div className="w-12 h-12 border-4 border-[#58CC02] border-t-transparent rounded-full animate-spin"></div>
                </div>
              ) : (
                <>
                  {/* CRM Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl">
                      <CardContent className="p-4 text-center">
                        <div className="text-3xl font-extrabold">{crmData?.stats?.total_leads || 0}</div>
                        <div className="text-sm opacity-90">Total Leads</div>
                      </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl">
                      <CardContent className="p-4 text-center">
                        <div className="text-3xl font-extrabold">${(crmData?.stats?.pipeline_value || 0).toLocaleString()}</div>
                        <div className="text-sm opacity-90">Pipeline Value</div>
                      </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl">
                      <CardContent className="p-4 text-center">
                        <div className="text-3xl font-extrabold">${(crmData?.stats?.won_value || 0).toLocaleString()}</div>
                        <div className="text-sm opacity-90">Won Value</div>
                      </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-xl">
                      <CardContent className="p-4 text-center">
                        <div className="text-3xl font-extrabold">{crmData?.stats?.conversion_rate || 0}%</div>
                        <div className="text-sm opacity-90">Conversion Rate</div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Sales Pipeline Kanban */}
                  <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                    <CardHeader>
                      <CardTitle className="text-gray-900 font-extrabold">Sales Pipeline</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex gap-4 overflow-x-auto pb-4">
                        {crmData?.stages && Object.entries(crmData.stages).map(([stageId, stageInfo]) => (
                          <div key={stageId} className="min-w-[280px] flex-shrink-0">
                            <div 
                              className="rounded-t-xl px-4 py-2 text-white font-bold text-sm flex items-center justify-between"
                              style={{ backgroundColor: stageInfo.color }}
                            >
                              <span>{stageInfo.label}</span>
                              <Badge className="bg-white/20 text-white border-0">
                                {crmData?.pipeline?.[stageId]?.length || 0}
                              </Badge>
                            </div>
                            <div className="bg-gray-50 rounded-b-xl p-3 min-h-[300px] space-y-3">
                              {crmData?.pipeline?.[stageId]?.map((lead) => (
                                <div 
                                  key={lead.id}
                                  className="bg-white rounded-xl p-3 shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer"
                                  onClick={() => setSelectedLead(lead)}
                                >
                                  <div className="font-bold text-gray-900 text-sm truncate">{lead.institution_name}</div>
                                  <div className="text-xs text-gray-500 truncate">{lead.contact_name}</div>
                                  <div className="flex items-center justify-between mt-2">
                                    <span className="text-xs text-gray-400">{lead.country || 'N/A'}</span>
                                    <span className="text-sm font-bold text-green-600">${(lead.estimated_value || 0).toLocaleString()}</span>
                                  </div>
                                  {lead.students_count > 0 && (
                                    <div className="mt-2 text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded-full inline-block">
                                      {lead.students_count} students
                                    </div>
                                  )}
                                </div>
                              ))}
                              {(!crmData?.pipeline?.[stageId] || crmData.pipeline[stageId].length === 0) && (
                                <div className="text-center text-gray-400 text-sm py-8">No leads</div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Lead Detail Modal */}
                  {selectedLead && (
                    <Dialog open={!!selectedLead} onOpenChange={() => setSelectedLead(null)}>
                      <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-2xl">
                        <DialogHeader>
                          <DialogTitle className="text-gray-900 font-extrabold flex items-center gap-2">
                            <Target className="w-5 h-5 text-[#58CC02]" />
                            {selectedLead.institution_name}
                          </DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4">
                          {/* Lead Info */}
                          <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-xl">
                            <div>
                              <p className="text-xs text-gray-500">Contact</p>
                              <p className="font-semibold">{selectedLead.contact_name}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">Email</p>
                              <p className="font-semibold">{selectedLead.email}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">Phone</p>
                              <p className="font-semibold">{selectedLead.phone || 'N/A'}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">Country</p>
                              <p className="font-semibold">{selectedLead.country || 'N/A'}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">Est. Students</p>
                              <p className="font-semibold">{selectedLead.students_count || 0}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">Deal Value</p>
                              <p className="font-semibold text-green-600">${(selectedLead.estimated_value || 0).toLocaleString()}</p>
                            </div>
                          </div>

                          {/* Stage Selector */}
                          <div>
                            <Label className="text-gray-700 font-semibold mb-2 block">Move to Stage</Label>
                            <div className="flex flex-wrap gap-2">
                              {crmData?.stages && Object.entries(crmData.stages).map(([stageId, stageInfo]) => (
                                <Button
                                  key={stageId}
                                  size="sm"
                                  variant={selectedLead.stage === stageId ? "default" : "outline"}
                                  onClick={() => handleUpdateLeadStage(selectedLead.id, stageId)}
                                  style={{ 
                                    backgroundColor: selectedLead.stage === stageId ? stageInfo.color : 'transparent',
                                    borderColor: stageInfo.color,
                                    color: selectedLead.stage === stageId ? 'white' : stageInfo.color
                                  }}
                                >
                                  {stageInfo.label}
                                </Button>
                              ))}
                            </div>
                          </div>

                          {/* Add Activity */}
                          <div className="border-t pt-4">
                            <div className="flex items-center justify-between mb-3">
                              <Label className="text-gray-700 font-semibold">Activities</Label>
                              <Dialog open={addActivityOpen} onOpenChange={setAddActivityOpen}>
                                <DialogTrigger asChild>
                                  <Button size="sm" variant="outline" className="flex items-center gap-1">
                                    <Plus className="w-3 h-3" /> Add Activity
                                  </Button>
                                </DialogTrigger>
                                <DialogContent className="bg-white rounded-xl">
                                  <DialogHeader>
                                    <DialogTitle>Add Activity</DialogTitle>
                                  </DialogHeader>
                                  <form onSubmit={handleAddActivity} className="space-y-4">
                                    <div>
                                      <Label>Activity Type</Label>
                                      <Select 
                                        value={newActivity.activity_type} 
                                        onValueChange={(v) => setNewActivity({...newActivity, activity_type: v})}
                                      >
                                        <SelectTrigger className="input-duo">
                                          <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                          <SelectItem value="call">📞 Call</SelectItem>
                                          <SelectItem value="email">📧 Email</SelectItem>
                                          <SelectItem value="meeting">🤝 Meeting</SelectItem>
                                          <SelectItem value="demo">🖥️ Demo</SelectItem>
                                          <SelectItem value="note">📝 Note</SelectItem>
                                        </SelectContent>
                                      </Select>
                                    </div>
                                    <div>
                                      <Label>Description</Label>
                                      <Textarea
                                        value={newActivity.description}
                                        onChange={(e) => setNewActivity({...newActivity, description: e.target.value})}
                                        required
                                        className="input-duo"
                                        rows={3}
                                      />
                                    </div>
                                    <div>
                                      <Label>Outcome</Label>
                                      <Input
                                        value={newActivity.outcome}
                                        onChange={(e) => setNewActivity({...newActivity, outcome: e.target.value})}
                                        className="input-duo"
                                        placeholder="e.g., Scheduled demo for Friday"
                                      />
                                    </div>
                                    <Button type="submit" className="btn-duo w-full">Add Activity</Button>
                                  </form>
                                </DialogContent>
                              </Dialog>
                            </div>
                            <div className="space-y-2 max-h-[200px] overflow-y-auto">
                              {selectedLead.activities_count > 0 ? (
                                <p className="text-sm text-gray-500">{selectedLead.activities_count} activities recorded</p>
                              ) : (
                                <p className="text-sm text-gray-400 text-center py-4">No activities yet</p>
                              )}
                            </div>
                          </div>
                        </div>
                      </DialogContent>
                    </Dialog>
                  )}
                </>
              )}
            </div>
          )}
          
          {/* CRM Supreme Tab */}
          {activeTab === 'crm-supreme' && (
            <div className="space-y-6 animate-fade-in" data-testid="crm-supreme-tab">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-extrabold text-gray-900 flex items-center gap-2">
                    <Zap className="w-7 h-7 text-purple-500" />
                    CRM Supreme
                    <span className="text-sm font-bold bg-gradient-to-r from-purple-500 to-pink-500 text-white px-3 py-1 rounded-full">PRO</span>
                  </h2>
                  <p className="text-gray-500">Advanced email automation, templates, and reporting</p>
                </div>
              </div>
              <CRMSupreme />
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

          {/* Push Notifications Tab */}
          {activeTab === 'notifications' && (
            <div className="space-y-6 animate-fade-in" data-testid="notifications-tab">
              <PushNotificationsPanel />
            </div>
          )}

          {/* Settings Tab */}
          {activeTab === 'settings' && (
            <div className="space-y-6 animate-fade-in" data-testid="settings-tab">
              <InstitutionSettings />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
