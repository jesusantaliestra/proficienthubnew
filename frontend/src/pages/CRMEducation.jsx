import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
  ArrowLeft, Users, Plus, Search, Filter, MoreVertical,
  Phone, Mail, Building, Calendar, Target, TrendingUp,
  CheckCircle, Clock, AlertCircle, ChevronRight, Star,
  GraduationCap, DollarSign, BarChart3, X, MapPin, Globe,
  MessageSquare, Activity, Edit2, Trash2, GripVertical
} from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function CRMEducation() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [activeView, setActiveView] = useState('pipeline');
  const [pipelineStages, setPipelineStages] = useState([]);
  const [leads, setLeads] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showNewLead, setShowNewLead] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStage, setSelectedStage] = useState(null);
  const [selectedLead, setSelectedLead] = useState(null);
  const [draggedLead, setDraggedLead] = useState(null);
  const [dragOverStage, setDragOverStage] = useState(null);

  const [newLeadForm, setNewLeadForm] = useState({
    institution_name: '',
    contact_name: '',
    contact_email: '',
    contact_phone: '',
    contact_role: '',
    estimated_students: '',
    exam_types_interested: [],
    country: '',
    source: 'website'
  });

  const examTypes = ['ielts', 'toefl', 'pte', 'oet', 'cambridge', 'celpip', 'toeic'];
  const leadSources = ['website', 'referral', 'ads', 'event', 'cold_outreach', 'partner'];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch pipeline stages
      const stagesRes = await fetch(`${API_URL}/api/crm-edu/pipeline-stages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const stagesData = await stagesRes.json();
      setPipelineStages(stagesData.stages || []);

      // Fetch leads
      const leadsRes = await fetch(`${API_URL}/api/crm-edu/leads?per_page=100`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const leadsData = await leadsRes.json();
      setLeads(leadsData.leads || []);

      // Fetch tasks
      const tasksRes = await fetch(`${API_URL}/api/crm-edu/tasks?status=pending`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const tasksData = await tasksRes.json();
      setTasks(tasksData.tasks || []);

      // Fetch analytics
      const analyticsRes = await fetch(`${API_URL}/api/crm-edu/analytics/pipeline`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const analyticsData = await analyticsRes.json();
      setAnalytics(analyticsData);

    } catch (error) {
      console.error('Error fetching CRM data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createLead = async () => {
    try {
      const response = await fetch(`${API_URL}/api/crm-edu/leads`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...newLeadForm,
          estimated_students: parseInt(newLeadForm.estimated_students) || 0
        })
      });

      if (response.ok) {
        toast.success('Lead created successfully');
        setShowNewLead(false);
        setNewLeadForm({
          institution_name: '',
          contact_name: '',
          contact_email: '',
          contact_phone: '',
          contact_role: '',
          estimated_students: '',
          exam_types_interested: [],
          country: '',
          source: 'website'
        });
        fetchData();
      } else {
        toast.error('Failed to create lead');
      }
    } catch (error) {
      toast.error('Error creating lead');
    }
  };

  const updateLeadStage = async (leadId, newStage) => {
    try {
      await fetch(`${API_URL}/api/crm-edu/leads/${leadId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ stage: newStage })
      });
      fetchData();
      toast.success('Lead moved to ' + newStage.replace('_', ' '));
    } catch (error) {
      toast.error('Error updating lead');
    }
  };

  // Drag and Drop handlers
  const handleDragStart = (e, lead) => {
    setDraggedLead(lead);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', lead.id);
  };

  const handleDragOver = (e, stageId) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverStage(stageId);
  };

  const handleDragLeave = () => {
    setDragOverStage(null);
  };

  const handleDrop = async (e, stageId) => {
    e.preventDefault();
    setDragOverStage(null);
    
    if (draggedLead && draggedLead.stage !== stageId) {
      // Optimistic update
      setLeads(prevLeads => 
        prevLeads.map(l => l.id === draggedLead.id ? { ...l, stage: stageId } : l)
      );
      await updateLeadStage(draggedLead.id, stageId);
    }
    setDraggedLead(null);
  };

  const handleDragEnd = () => {
    setDraggedLead(null);
    setDragOverStage(null);
  };

  // Calculate education-specific metrics
  const getEducationMetrics = useCallback(() => {
    const totalStudents = leads.reduce((acc, l) => acc + (l.estimated_students || 0), 0);
    const totalValue = leads.reduce((acc, l) => acc + (l.estimated_value || 0), 0);
    const avgValuePerStudent = totalStudents > 0 ? totalValue / totalStudents : 0;
    
    // Conversion by exam type
    const examConversions = {};
    examTypes.forEach(exam => {
      const examLeads = leads.filter(l => l.exam_types_interested?.includes(exam));
      const converted = examLeads.filter(l => ['active', 'onboarding'].includes(l.stage));
      examConversions[exam] = {
        total: examLeads.length,
        converted: converted.length,
        rate: examLeads.length > 0 ? (converted.length / examLeads.length * 100).toFixed(1) : 0
      };
    });

    return { totalStudents, totalValue, avgValuePerStudent, examConversions };
  }, [leads]);

  const getLeadsByStage = (stageId) => {
    return leads.filter(lead => lead.stage === stageId);
  };

  const getScoreColor = (score) => {
    if (score >= 70) return 'text-green-400 bg-green-500/20';
    if (score >= 40) return 'text-amber-400 bg-amber-500/20';
    return 'text-red-400 bg-red-500/20';
  };

  const filteredLeads = leads.filter(lead => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      lead.institution_name?.toLowerCase().includes(query) ||
      lead.contact_name?.toLowerCase().includes(query) ||
      lead.contact_email?.toLowerCase().includes(query)
    );
  });

  // Notification Settings State
  const [notificationSettings, setNotificationSettings] = useState([]);
  const [showNotificationConfig, setShowNotificationConfig] = useState(false);
  const [newNotification, setNewNotification] = useState({
    name: '',
    trigger_stage: 'qualified',
    notify_on_enter: true,
    notify_on_exit: false,
    notification_channels: ['in_app'],
    recipients: ['owner'],
    include_lead_details: true,
    is_active: true
  });

  const fetchNotificationSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/crm-edu/notification-settings`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setNotificationSettings(data.settings || []);
    } catch (error) {
      console.error('Error fetching notification settings:', error);
    }
  };

  const createNotificationSetting = async () => {
    try {
      const response = await fetch(`${API_URL}/api/crm-edu/notification-settings`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newNotification)
      });
      
      if (response.ok) {
        toast.success('Notification setting created');
        setShowNotificationConfig(false);
        setNewNotification({
          name: '',
          trigger_stage: 'qualified',
          notify_on_enter: true,
          notify_on_exit: false,
          notification_channels: ['in_app'],
          recipients: ['owner'],
          include_lead_details: true,
          is_active: true
        });
        fetchNotificationSettings();
      } else {
        toast.error('Failed to create notification setting');
      }
    } catch (error) {
      toast.error('Error creating notification setting');
    }
  };

  const toggleNotificationSetting = async (settingId, isActive) => {
    try {
      await fetch(`${API_URL}/api/crm-edu/notification-settings/${settingId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_active: !isActive })
      });
      fetchNotificationSettings();
      toast.success(isActive ? 'Notification disabled' : 'Notification enabled');
    } catch (error) {
      toast.error('Error updating notification setting');
    }
  };

  const deleteNotificationSetting = async (settingId) => {
    try {
      await fetch(`${API_URL}/api/crm-edu/notification-settings/${settingId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchNotificationSettings();
      toast.success('Notification setting deleted');
    } catch (error) {
      toast.error('Error deleting notification setting');
    }
  };

  useEffect(() => {
    if (activeView === 'settings') {
      fetchNotificationSettings();
    }
  }, [activeView]);

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-full mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => navigate(-1)} className="text-slate-400">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                <GraduationCap className="w-6 h-6 text-indigo-400" />
                CRM Education
              </h1>
              <p className="text-slate-400 text-sm mt-1">
                {leads.length} leads • {tasks.length} pending tasks
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <Input
                placeholder="Search leads..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 bg-slate-800 border-slate-700 text-white w-64"
              />
            </div>
            <Button onClick={() => setShowNewLead(true)} className="bg-indigo-600 hover:bg-indigo-700">
              <Plus className="w-4 h-4 mr-2" /> New Lead
            </Button>
          </div>
        </div>

        {/* View Tabs */}
        <div className="flex gap-2 mb-6">
          {[
            { id: 'pipeline', label: 'Pipeline', icon: Target },
            { id: 'list', label: 'List View', icon: Users },
            { id: 'analytics', label: 'Analytics', icon: BarChart3 },
            { id: 'settings', label: 'Notifications', icon: AlertCircle }
          ].map(view => (
            <button
              key={view.id}
              onClick={() => setActiveView(view.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeView === view.id
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              <view.icon className="w-4 h-4" />
              {view.label}
            </button>
          ))}
        </div>

        {/* New Lead Modal */}
        {showNewLead && (
          <Card className="bg-slate-900 border-slate-700 mb-6">
            <CardHeader>
              <CardTitle className="text-white">Add New Lead</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-slate-300 text-sm mb-1 block">Institution Name *</label>
                  <Input
                    placeholder="e.g., ABC Language School"
                    value={newLeadForm.institution_name}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, institution_name: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
                <div>
                  <label className="text-slate-300 text-sm mb-1 block">Contact Name *</label>
                  <Input
                    placeholder="Full name"
                    value={newLeadForm.contact_name}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, contact_name: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
                <div>
                  <label className="text-slate-300 text-sm mb-1 block">Email *</label>
                  <Input
                    type="email"
                    placeholder="email@example.com"
                    value={newLeadForm.contact_email}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, contact_email: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
                <div>
                  <label className="text-slate-300 text-sm mb-1 block">Phone</label>
                  <Input
                    placeholder="+1 234 567 8900"
                    value={newLeadForm.contact_phone}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, contact_phone: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
                <div>
                  <label className="text-slate-300 text-sm mb-1 block">Role</label>
                  <Input
                    placeholder="e.g., Director, Manager"
                    value={newLeadForm.contact_role}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, contact_role: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
                <div>
                  <label className="text-slate-300 text-sm mb-1 block">Estimated Students</label>
                  <Input
                    type="number"
                    placeholder="Number of students"
                    value={newLeadForm.estimated_students}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, estimated_students: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
                <div>
                  <label className="text-slate-300 text-sm mb-1 block">Country</label>
                  <Input
                    placeholder="Country"
                    value={newLeadForm.country}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, country: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
                <div>
                  <label className="text-slate-300 text-sm mb-1 block">Source</label>
                  <select
                    value={newLeadForm.source}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, source: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-md px-3 py-2"
                  >
                    {leadSources.map(source => (
                      <option key={source} value={source}>{source.replace('_', ' ')}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="mt-4">
                <label className="text-slate-300 text-sm mb-2 block">Exam Types Interested</label>
                <div className="flex flex-wrap gap-2">
                  {examTypes.map(exam => (
                    <button
                      key={exam}
                      onClick={() => {
                        const types = newLeadForm.exam_types_interested;
                        setNewLeadForm({
                          ...newLeadForm,
                          exam_types_interested: types.includes(exam)
                            ? types.filter(t => t !== exam)
                            : [...types, exam]
                        });
                      }}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                        newLeadForm.exam_types_interested.includes(exam)
                          ? 'bg-indigo-600 text-white'
                          : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                      }`}
                    >
                      {exam.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <Button variant="ghost" onClick={() => setShowNewLead(false)} className="text-slate-400">
                  Cancel
                </Button>
                <Button 
                  onClick={createLead}
                  disabled={!newLeadForm.institution_name || !newLeadForm.contact_name || !newLeadForm.contact_email}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  Create Lead
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          </div>
        ) : (
          <>
            {/* Pipeline View */}
            {activeView === 'pipeline' && (
              <div className="overflow-x-auto pb-4">
                <div className="flex gap-4 min-w-max">
                  {pipelineStages.filter(s => s.id !== 'churned' && s.id !== 'lost').map(stage => {
                    const stageLeads = getLeadsByStage(stage.id);
                    const isDragOver = dragOverStage === stage.id;
                    return (
                      <div 
                        key={stage.id}
                        className={`w-72 flex-shrink-0 transition-all duration-200 ${
                          isDragOver ? 'scale-[1.02]' : ''
                        }`}
                        onDragOver={(e) => handleDragOver(e, stage.id)}
                        onDragLeave={handleDragLeave}
                        onDrop={(e) => handleDrop(e, stage.id)}
                      >
                        <div 
                          className="flex items-center justify-between mb-3 px-2"
                          style={{ borderLeftColor: stage.color }}
                        >
                          <div className="flex items-center gap-2">
                            <div 
                              className="w-3 h-3 rounded-full"
                              style={{ backgroundColor: stage.color }}
                            />
                            <h3 className="text-white font-medium text-sm">{stage.name}</h3>
                          </div>
                          <span className="text-slate-500 text-sm">{stageLeads.length}</span>
                        </div>

                        <div className={`space-y-2 min-h-[200px] p-2 rounded-lg transition-colors ${
                          isDragOver ? 'bg-indigo-600/10 border-2 border-dashed border-indigo-500' : 'border-2 border-transparent'
                        }`}>
                          {stageLeads.length === 0 ? (
                            <div className="bg-slate-900/50 border border-dashed border-slate-700 rounded-lg p-4 text-center">
                              <p className="text-slate-500 text-sm">Drop leads here</p>
                            </div>
                          ) : (
                            stageLeads.map(lead => (
                              <Card 
                                key={lead.id}
                                draggable
                                onDragStart={(e) => handleDragStart(e, lead)}
                                onDragEnd={handleDragEnd}
                                onClick={() => setSelectedLead(lead)}
                                className={`bg-slate-900 border-slate-800 hover:border-indigo-500/50 transition-all cursor-grab active:cursor-grabbing ${
                                  draggedLead?.id === lead.id ? 'opacity-50 scale-95' : ''
                                }`}
                                data-testid={`lead-card-${lead.id}`}
                              >
                                <CardContent className="p-3">
                                  <div className="flex items-start justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                      <GripVertical className="w-3 h-3 text-slate-600" />
                                      <h4 className="text-white font-medium text-sm line-clamp-1">
                                        {lead.institution_name}
                                      </h4>
                                    </div>
                                    <span className={`text-xs px-1.5 py-0.5 rounded ${getScoreColor(lead.lead_score)}`}>
                                      {lead.lead_score || '-'}
                                    </span>
                                  </div>
                                  <p className="text-slate-400 text-xs mb-2 pl-5">{lead.contact_name}</p>
                                  <div className="flex items-center gap-2 text-slate-500 text-xs pl-5">
                                    <Building className="w-3 h-3" />
                                    <span>{lead.estimated_students || 0} students</span>
                                    {lead.country && (
                                      <>
                                        <Globe className="w-3 h-3 ml-2" />
                                        <span>{lead.country}</span>
                                      </>
                                    )}
                                  </div>
                                  {lead.exam_types_interested?.length > 0 && (
                                    <div className="flex flex-wrap gap-1 mt-2 pl-5">
                                      {lead.exam_types_interested.slice(0, 3).map(exam => (
                                        <span 
                                          key={exam}
                                          className="text-xs bg-indigo-600/20 text-indigo-300 px-1.5 py-0.5 rounded"
                                        >
                                          {exam.toUpperCase()}
                                        </span>
                                      ))}
                                      {lead.exam_types_interested.length > 3 && (
                                        <span className="text-xs text-slate-500">+{lead.exam_types_interested.length - 3}</span>
                                      )}
                                    </div>
                                  )}
                                </CardContent>
                              </Card>
                            ))
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* List View */}
            {activeView === 'list' && (
              <Card className="bg-slate-900 border-slate-800">
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-slate-800">
                          <th className="text-left p-4 text-slate-400 font-medium text-sm">Institution</th>
                          <th className="text-left p-4 text-slate-400 font-medium text-sm">Contact</th>
                          <th className="text-left p-4 text-slate-400 font-medium text-sm">Stage</th>
                          <th className="text-left p-4 text-slate-400 font-medium text-sm">Score</th>
                          <th className="text-left p-4 text-slate-400 font-medium text-sm">Students</th>
                          <th className="text-left p-4 text-slate-400 font-medium text-sm">Exams</th>
                          <th className="text-left p-4 text-slate-400 font-medium text-sm"></th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredLeads.map(lead => {
                          const stage = pipelineStages.find(s => s.id === lead.stage);
                          return (
                            <tr key={lead.id} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                              <td className="p-4">
                                <p className="text-white font-medium">{lead.institution_name}</p>
                                <p className="text-slate-500 text-xs">{lead.country}</p>
                              </td>
                              <td className="p-4">
                                <p className="text-white text-sm">{lead.contact_name}</p>
                                <p className="text-slate-500 text-xs">{lead.contact_email}</p>
                              </td>
                              <td className="p-4">
                                <span 
                                  className="px-2 py-1 rounded text-xs font-medium"
                                  style={{ 
                                    backgroundColor: `${stage?.color}20`,
                                    color: stage?.color
                                  }}
                                >
                                  {stage?.name}
                                </span>
                              </td>
                              <td className="p-4">
                                <span className={`px-2 py-1 rounded text-xs font-medium ${getScoreColor(lead.lead_score)}`}>
                                  {lead.lead_score}
                                </span>
                              </td>
                              <td className="p-4 text-slate-300">{lead.estimated_students || '-'}</td>
                              <td className="p-4">
                                <div className="flex gap-1">
                                  {lead.exam_types_interested?.slice(0, 2).map(exam => (
                                    <span key={exam} className="text-xs bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">
                                      {exam}
                                    </span>
                                  ))}
                                  {lead.exam_types_interested?.length > 2 && (
                                    <span className="text-xs text-slate-500">+{lead.exam_types_interested.length - 2}</span>
                                  )}
                                </div>
                              </td>
                              <td className="p-4">
                                <Button size="sm" variant="ghost" className="text-slate-400">
                                  <ChevronRight className="w-4 h-4" />
                                </Button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Analytics View */}
            {activeView === 'analytics' && analytics && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card className="bg-slate-900 border-slate-800">
                  <CardContent className="p-5">
                    <p className="text-slate-400 text-sm">Total Leads</p>
                    <p className="text-3xl font-bold text-white mt-1">{analytics.total_leads}</p>
                  </CardContent>
                </Card>
                <Card className="bg-slate-900 border-slate-800">
                  <CardContent className="p-5">
                    <p className="text-slate-400 text-sm">Active Customers</p>
                    <p className="text-3xl font-bold text-white mt-1">{analytics.active_customers}</p>
                  </CardContent>
                </Card>
                <Card className="bg-slate-900 border-slate-800">
                  <CardContent className="p-5">
                    <p className="text-slate-400 text-sm">Conversion Rate</p>
                    <p className="text-3xl font-bold text-white mt-1">{analytics.conversion_rate}%</p>
                  </CardContent>
                </Card>
                <Card className="bg-slate-900 border-slate-800">
                  <CardContent className="p-5">
                    <p className="text-slate-400 text-sm">Pipeline Value</p>
                    <p className="text-3xl font-bold text-white mt-1">
                      ${Object.values(analytics.by_stage || {}).reduce((acc, s) => acc + (s.value || 0), 0).toLocaleString()}
                    </p>
                  </CardContent>
                </Card>

                {/* Stage Distribution */}
                <Card className="bg-slate-900 border-slate-800 md:col-span-2">
                  <CardHeader>
                    <CardTitle className="text-white text-lg">Leads by Stage</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {pipelineStages.filter(s => s.id !== 'churned' && s.id !== 'lost').map(stage => {
                        const stageData = analytics.by_stage?.[stage.id] || { count: 0 };
                        const percentage = analytics.total_leads > 0 
                          ? (stageData.count / analytics.total_leads * 100) 
                          : 0;
                        return (
                          <div key={stage.id}>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-white">{stage.name}</span>
                              <span className="text-slate-400">{stageData.count}</span>
                            </div>
                            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                              <div 
                                className="h-full rounded-full transition-all"
                                style={{ width: `${percentage}%`, backgroundColor: stage.color }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>

                {/* Sources */}
                <Card className="bg-slate-900 border-slate-800 md:col-span-2">
                  <CardHeader>
                    <CardTitle className="text-white text-lg">Lead Sources</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-3">
                      {Object.entries(analytics.by_source || {}).map(([source, count]) => (
                        <div key={source} className="flex items-center justify-between p-3 bg-slate-800 rounded-lg">
                          <span className="text-white text-sm capitalize">{source.replace('_', ' ')}</span>
                          <span className="text-indigo-400 font-medium">{count}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Education-Specific Metrics */}
                <Card className="bg-slate-900 border-slate-800 md:col-span-2 lg:col-span-4">
                  <CardHeader>
                    <CardTitle className="text-white text-lg flex items-center gap-2">
                      <GraduationCap className="w-5 h-5 text-indigo-400" />
                      Conversion by Exam Type
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
                      {examTypes.map(exam => {
                        const metrics = getEducationMetrics();
                        const examData = metrics.examConversions[exam] || { total: 0, converted: 0, rate: 0 };
                        return (
                          <div key={exam} className="bg-slate-800 rounded-lg p-3 text-center">
                            <p className="text-indigo-400 font-bold text-sm mb-1">{exam.toUpperCase()}</p>
                            <p className="text-2xl font-bold text-white">{examData.rate}%</p>
                            <p className="text-slate-500 text-xs">{examData.converted}/{examData.total} leads</p>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Settings View - Notification Configuration */}
            {activeView === 'settings' && (
              <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold text-white">Notification Settings</h2>
                    <p className="text-slate-400 text-sm">Configure automatic notifications when leads change stages</p>
                  </div>
                  <Button 
                    onClick={() => setShowNotificationConfig(true)}
                    className="bg-indigo-600 hover:bg-indigo-700"
                    data-testid="add-notification-btn"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Notification Rule
                  </Button>
                </div>

                {/* Add New Notification Form */}
                {showNotificationConfig && (
                  <Card className="bg-slate-900 border-slate-700">
                    <CardHeader>
                      <CardTitle className="text-white">Create Notification Rule</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="text-slate-300 text-sm mb-1 block">Rule Name *</label>
                          <Input
                            placeholder="e.g., Hot Lead Alert"
                            value={newNotification.name}
                            onChange={(e) => setNewNotification({ ...newNotification, name: e.target.value })}
                            className="bg-slate-800 border-slate-700 text-white"
                          />
                        </div>
                        <div>
                          <label className="text-slate-300 text-sm mb-1 block">Trigger Stage *</label>
                          <select
                            value={newNotification.trigger_stage}
                            onChange={(e) => setNewNotification({ ...newNotification, trigger_stage: e.target.value })}
                            className="w-full bg-slate-800 border border-slate-700 text-white rounded-md px-3 py-2"
                          >
                            {pipelineStages.map(stage => (
                              <option key={stage.id} value={stage.id}>{stage.name}</option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <label className="text-slate-300 text-sm block">When to Notify</label>
                          <div className="flex gap-4">
                            <label className="flex items-center gap-2 text-slate-300 text-sm cursor-pointer">
                              <input
                                type="checkbox"
                                checked={newNotification.notify_on_enter}
                                onChange={(e) => setNewNotification({ ...newNotification, notify_on_enter: e.target.checked })}
                                className="rounded bg-slate-800 border-slate-700"
                              />
                              On Enter
                            </label>
                            <label className="flex items-center gap-2 text-slate-300 text-sm cursor-pointer">
                              <input
                                type="checkbox"
                                checked={newNotification.notify_on_exit}
                                onChange={(e) => setNewNotification({ ...newNotification, notify_on_exit: e.target.checked })}
                                className="rounded bg-slate-800 border-slate-700"
                              />
                              On Exit
                            </label>
                          </div>
                        </div>
                        <div className="space-y-2">
                          <label className="text-slate-300 text-sm block">Notification Channels</label>
                          <div className="flex gap-4">
                            {['in_app', 'email'].map(channel => (
                              <label key={channel} className="flex items-center gap-2 text-slate-300 text-sm cursor-pointer">
                                <input
                                  type="checkbox"
                                  checked={newNotification.notification_channels.includes(channel)}
                                  onChange={(e) => {
                                    const channels = e.target.checked
                                      ? [...newNotification.notification_channels, channel]
                                      : newNotification.notification_channels.filter(c => c !== channel);
                                    setNewNotification({ ...newNotification, notification_channels: channels });
                                  }}
                                  className="rounded bg-slate-800 border-slate-700"
                                />
                                {channel === 'in_app' ? 'In-App' : 'Email'}
                              </label>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <label className="text-slate-300 text-sm block">Recipients</label>
                        <div className="flex gap-4">
                          {['owner', 'team'].map(recipient => (
                            <label key={recipient} className="flex items-center gap-2 text-slate-300 text-sm cursor-pointer">
                              <input
                                type="checkbox"
                                checked={newNotification.recipients.includes(recipient)}
                                onChange={(e) => {
                                  const recipients = e.target.checked
                                    ? [...newNotification.recipients, recipient]
                                    : newNotification.recipients.filter(r => r !== recipient);
                                  setNewNotification({ ...newNotification, recipients: recipients });
                                }}
                                className="rounded bg-slate-800 border-slate-700"
                              />
                              {recipient === 'owner' ? 'Lead Owner' : 'Entire Team'}
                            </label>
                          ))}
                        </div>
                      </div>

                      <label className="flex items-center gap-2 text-slate-300 text-sm cursor-pointer">
                        <input
                          type="checkbox"
                          checked={newNotification.include_lead_details}
                          onChange={(e) => setNewNotification({ ...newNotification, include_lead_details: e.target.checked })}
                          className="rounded bg-slate-800 border-slate-700"
                        />
                        Include lead details in notification
                      </label>

                      <div className="flex justify-end gap-3 pt-4">
                        <Button variant="ghost" onClick={() => setShowNotificationConfig(false)} className="text-slate-400">
                          Cancel
                        </Button>
                        <Button 
                          onClick={createNotificationSetting}
                          disabled={!newNotification.name}
                          className="bg-indigo-600 hover:bg-indigo-700"
                        >
                          Create Rule
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Existing Notification Rules */}
                <div className="space-y-3">
                  {notificationSettings.length === 0 ? (
                    <Card className="bg-slate-900/50 border-slate-800 border-dashed">
                      <CardContent className="p-8 text-center">
                        <AlertCircle className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                        <h3 className="text-white font-medium mb-1">No notification rules configured</h3>
                        <p className="text-slate-500 text-sm mb-4">Create rules to get notified when leads move between stages</p>
                        <Button 
                          onClick={() => setShowNotificationConfig(true)}
                          variant="outline"
                          className="border-slate-700 text-slate-300"
                        >
                          <Plus className="w-4 h-4 mr-2" />
                          Create First Rule
                        </Button>
                      </CardContent>
                    </Card>
                  ) : (
                    notificationSettings.map(setting => {
                      const stage = pipelineStages.find(s => s.id === setting.trigger_stage);
                      return (
                        <Card 
                          key={setting.id} 
                          className={`bg-slate-900 border-slate-800 ${!setting.is_active ? 'opacity-60' : ''}`}
                          data-testid={`notification-rule-${setting.id}`}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-4">
                                <div 
                                  className="w-3 h-3 rounded-full"
                                  style={{ backgroundColor: stage?.color || '#6366f1' }}
                                />
                                <div>
                                  <h4 className="text-white font-medium">{setting.name}</h4>
                                  <div className="flex items-center gap-2 text-slate-400 text-sm mt-1">
                                    <span 
                                      className="px-2 py-0.5 rounded text-xs"
                                      style={{ backgroundColor: `${stage?.color}20`, color: stage?.color }}
                                    >
                                      {stage?.name}
                                    </span>
                                    <span>•</span>
                                    <span>
                                      {setting.notify_on_enter && 'On Enter'}
                                      {setting.notify_on_enter && setting.notify_on_exit && ' & '}
                                      {setting.notify_on_exit && 'On Exit'}
                                    </span>
                                    <span>•</span>
                                    <span className="flex items-center gap-1">
                                      {setting.notification_channels.includes('in_app') && (
                                        <span className="text-xs bg-slate-800 px-1.5 py-0.5 rounded">App</span>
                                      )}
                                      {setting.notification_channels.includes('email') && (
                                        <span className="text-xs bg-slate-800 px-1.5 py-0.5 rounded">Email</span>
                                      )}
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => toggleNotificationSetting(setting.id, setting.is_active)}
                                  className={setting.is_active ? 'text-green-400' : 'text-slate-500'}
                                >
                                  {setting.is_active ? (
                                    <CheckCircle className="w-5 h-5" />
                                  ) : (
                                    <AlertCircle className="w-5 h-5" />
                                  )}
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => deleteNotificationSetting(setting.id)}
                                  className="text-red-400 hover:text-red-300"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })
                  )}
                </div>

                {/* Quick Setup Presets */}
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="text-white text-lg">Quick Setup Presets</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-slate-400 text-sm mb-4">Click to instantly create common notification rules</p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      {[
                        { name: 'Hot Lead Alert', stage: 'qualified', desc: 'Notify when lead qualifies' },
                        { name: 'Demo Booked', stage: 'demo_scheduled', desc: 'Notify when demo is scheduled' },
                        { name: 'New Customer!', stage: 'active', desc: 'Celebrate when lead converts' }
                      ].map(preset => (
                        <button
                          key={preset.stage}
                          onClick={() => {
                            setNewNotification({
                              ...newNotification,
                              name: preset.name,
                              trigger_stage: preset.stage
                            });
                            setShowNotificationConfig(true);
                          }}
                          className="p-4 bg-slate-800 hover:bg-slate-700 rounded-lg text-left transition-colors"
                        >
                          <p className="text-white font-medium">{preset.name}</p>
                          <p className="text-slate-500 text-sm">{preset.desc}</p>
                        </button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </>
        )}

        {/* Lead Detail Modal */}
        {selectedLead && (
          <div 
            className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedLead(null)}
          >
            <div 
              className="bg-slate-900 rounded-xl border border-slate-700 w-full max-w-2xl max-h-[80vh] overflow-y-auto"
              onClick={e => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="sticky top-0 bg-slate-900 border-b border-slate-800 p-4 flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-bold text-white">{selectedLead.institution_name}</h2>
                  <p className="text-slate-400 text-sm">{selectedLead.contact_name} · {selectedLead.contact_role}</p>
                </div>
                <Button variant="ghost" size="sm" onClick={() => setSelectedLead(null)}>
                  <X className="w-5 h-5 text-slate-400" />
                </Button>
              </div>

              {/* Modal Content */}
              <div className="p-4 space-y-6">
                {/* Contact Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center gap-3 text-slate-300">
                    <Mail className="w-4 h-4 text-slate-500" />
                    <span className="text-sm">{selectedLead.contact_email}</span>
                  </div>
                  {selectedLead.contact_phone && (
                    <div className="flex items-center gap-3 text-slate-300">
                      <Phone className="w-4 h-4 text-slate-500" />
                      <span className="text-sm">{selectedLead.contact_phone}</span>
                    </div>
                  )}
                  {selectedLead.country && (
                    <div className="flex items-center gap-3 text-slate-300">
                      <MapPin className="w-4 h-4 text-slate-500" />
                      <span className="text-sm">{selectedLead.country}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-3 text-slate-300">
                    <Users className="w-4 h-4 text-slate-500" />
                    <span className="text-sm">{selectedLead.estimated_students || 0} students</span>
                  </div>
                </div>

                {/* Stage Selector */}
                <div>
                  <label className="text-slate-400 text-sm mb-2 block">Pipeline Stage</label>
                  <div className="flex flex-wrap gap-2">
                    {pipelineStages.filter(s => s.id !== 'churned' && s.id !== 'lost').map(stage => (
                      <button
                        key={stage.id}
                        onClick={() => {
                          if (stage.id !== selectedLead.stage) {
                            updateLeadStage(selectedLead.id, stage.id);
                            setSelectedLead({ ...selectedLead, stage: stage.id });
                          }
                        }}
                        className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                          selectedLead.stage === stage.id
                            ? 'ring-2 ring-offset-2 ring-offset-slate-900'
                            : 'opacity-60 hover:opacity-100'
                        }`}
                        style={{ 
                          backgroundColor: `${stage.color}20`,
                          color: stage.color,
                          ringColor: stage.color
                        }}
                      >
                        {stage.name}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Exam Types */}
                {selectedLead.exam_types_interested?.length > 0 && (
                  <div>
                    <label className="text-slate-400 text-sm mb-2 block">Exam Types Interested</label>
                    <div className="flex flex-wrap gap-2">
                      {selectedLead.exam_types_interested.map(exam => (
                        <span 
                          key={exam}
                          className="px-3 py-1.5 bg-indigo-600/20 text-indigo-300 rounded-lg text-sm font-medium"
                        >
                          {exam.toUpperCase()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Lead Score & Value */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-slate-800 rounded-lg p-4 text-center">
                    <p className="text-slate-400 text-xs mb-1">Lead Score</p>
                    <p className={`text-2xl font-bold ${getScoreColor(selectedLead.lead_score).split(' ')[0]}`}>
                      {selectedLead.lead_score || '-'}
                    </p>
                  </div>
                  <div className="bg-slate-800 rounded-lg p-4 text-center">
                    <p className="text-slate-400 text-xs mb-1">Est. Value</p>
                    <p className="text-2xl font-bold text-green-400">
                      ${(selectedLead.estimated_value || 0).toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-slate-800 rounded-lg p-4 text-center">
                    <p className="text-slate-400 text-xs mb-1">Source</p>
                    <p className="text-lg font-medium text-white capitalize">
                      {selectedLead.source?.replace('_', ' ') || '-'}
                    </p>
                  </div>
                </div>

                {/* Notes */}
                {selectedLead.notes && (
                  <div>
                    <label className="text-slate-400 text-sm mb-2 block">Notes</label>
                    <p className="text-slate-300 text-sm bg-slate-800 rounded-lg p-3">
                      {selectedLead.notes}
                    </p>
                  </div>
                )}

                {/* Activity Timeline */}
                {selectedLead.activities?.length > 0 && (
                  <div>
                    <label className="text-slate-400 text-sm mb-2 block flex items-center gap-2">
                      <Activity className="w-4 h-4" />
                      Recent Activity
                    </label>
                    <div className="space-y-2">
                      {selectedLead.activities.slice(0, 5).map((activity, idx) => (
                        <div key={idx} className="flex gap-3 text-sm">
                          <div className="w-2 h-2 rounded-full bg-indigo-500 mt-1.5 flex-shrink-0" />
                          <div>
                            <p className="text-slate-300">{activity.content}</p>
                            <p className="text-slate-500 text-xs">
                              {new Date(activity.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Modal Footer */}
              <div className="sticky bottom-0 bg-slate-900 border-t border-slate-800 p-4 flex justify-between">
                <Button variant="ghost" className="text-red-400 hover:text-red-300 hover:bg-red-500/10">
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete Lead
                </Button>
                <div className="flex gap-2">
                  <Button variant="outline" className="border-slate-700 text-slate-300">
                    <MessageSquare className="w-4 h-4 mr-2" />
                    Add Note
                  </Button>
                  <Button className="bg-indigo-600 hover:bg-indigo-700">
                    <Phone className="w-4 h-4 mr-2" />
                    Schedule Call
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
