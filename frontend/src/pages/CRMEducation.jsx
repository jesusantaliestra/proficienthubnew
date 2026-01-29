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
      toast.success('Lead updated');
    } catch (error) {
      toast.error('Error updating lead');
    }
  };

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
            { id: 'analytics', label: 'Analytics', icon: BarChart3 }
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
                    return (
                      <div 
                        key={stage.id}
                        className="w-72 flex-shrink-0"
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

                        <div className="space-y-2">
                          {stageLeads.length === 0 ? (
                            <div className="bg-slate-900/50 border border-dashed border-slate-700 rounded-lg p-4 text-center">
                              <p className="text-slate-500 text-sm">No leads</p>
                            </div>
                          ) : (
                            stageLeads.map(lead => (
                              <Card 
                                key={lead.id}
                                className="bg-slate-900 border-slate-800 hover:border-slate-700 transition-colors cursor-pointer"
                              >
                                <CardContent className="p-3">
                                  <div className="flex items-start justify-between mb-2">
                                    <h4 className="text-white font-medium text-sm line-clamp-1">
                                      {lead.institution_name}
                                    </h4>
                                    <span className={`text-xs px-1.5 py-0.5 rounded ${getScoreColor(lead.lead_score)}`}>
                                      {lead.lead_score}
                                    </span>
                                  </div>
                                  <p className="text-slate-400 text-xs mb-2">{lead.contact_name}</p>
                                  <div className="flex items-center gap-2 text-slate-500 text-xs">
                                    <Building className="w-3 h-3" />
                                    <span>{lead.estimated_students || 0} students</span>
                                  </div>
                                  {lead.exam_types_interested?.length > 0 && (
                                    <div className="flex flex-wrap gap-1 mt-2">
                                      {lead.exam_types_interested.slice(0, 3).map(exam => (
                                        <span 
                                          key={exam}
                                          className="text-xs bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded"
                                        >
                                          {exam}
                                        </span>
                                      ))}
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
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
