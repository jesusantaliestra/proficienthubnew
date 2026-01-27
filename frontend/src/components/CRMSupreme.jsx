import React, { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import {
  Mail, Zap, FileText, BarChart3, CheckSquare, Plus, Edit, Trash2, 
  Play, Pause, Copy, Eye, Clock, Users, TrendingUp, Target,
  Send, MessageSquare, Bell, Settings, ChevronRight, Calendar
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Sub-component for Email Templates
const EmailTemplatesSection = ({ templates, onRefresh }) => {
  const [createOpen, setCreateOpen] = useState(false);
  const [editTemplate, setEditTemplate] = useState(null);
  const [newTemplate, setNewTemplate] = useState({
    name: '',
    subject: '',
    body_html: '',
    category: 'follow_up',
    variables: []
  });

  const categories = [
    { value: 'welcome', label: '👋 Welcome', color: 'bg-blue-100 text-blue-700' },
    { value: 'follow_up', label: '📧 Follow-up', color: 'bg-green-100 text-green-700' },
    { value: 'reminder', label: '⏰ Reminder', color: 'bg-orange-100 text-orange-700' },
    { value: 'promotion', label: '🎁 Promotion', color: 'bg-purple-100 text-purple-700' },
    { value: 'notification', label: '🔔 Notification', color: 'bg-gray-100 text-gray-700' },
  ];

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/crm/email-templates`, newTemplate);
      toast.success('Template created successfully!');
      setCreateOpen(false);
      setNewTemplate({ name: '', subject: '', body_html: '', category: 'follow_up', variables: [] });
      onRefresh();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create template');
    }
  };

  const getCategoryStyle = (cat) => {
    const found = categories.find(c => c.value === cat);
    return found?.color || 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-gray-900">Email Templates</h3>
          <p className="text-sm text-gray-500">Create reusable email templates with dynamic variables</p>
        </div>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button className="btn-duo flex items-center gap-2" data-testid="create-template-btn">
              <Plus className="w-4 h-4" /> New Template
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-2xl">
            <DialogHeader>
              <DialogTitle className="text-gray-900 font-extrabold">Create Email Template</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Template Name *</Label>
                  <Input
                    value={newTemplate.name}
                    onChange={(e) => setNewTemplate({...newTemplate, name: e.target.value})}
                    required
                    className="input-duo"
                    placeholder="e.g., Welcome New Lead"
                    data-testid="template-name-input"
                  />
                </div>
                <div>
                  <Label>Category *</Label>
                  <Select 
                    value={newTemplate.category} 
                    onValueChange={(v) => setNewTemplate({...newTemplate, category: v})}
                  >
                    <SelectTrigger className="input-duo">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map(cat => (
                        <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label>Subject Line *</Label>
                <Input
                  value={newTemplate.subject}
                  onChange={(e) => setNewTemplate({...newTemplate, subject: e.target.value})}
                  required
                  className="input-duo"
                  placeholder="e.g., Welcome to {{platform_name}}!"
                  data-testid="template-subject-input"
                />
                <p className="text-xs text-gray-500 mt-1">Use {'{{variable_name}}'} for dynamic content</p>
              </div>
              <div>
                <Label>Email Body (HTML) *</Label>
                <Textarea
                  value={newTemplate.body_html}
                  onChange={(e) => setNewTemplate({...newTemplate, body_html: e.target.value})}
                  required
                  className="input-duo font-mono text-sm"
                  rows={8}
                  placeholder="<h1>Hello {{contact_name}}!</h1><p>Welcome to our platform...</p>"
                  data-testid="template-body-input"
                />
              </div>
              <div className="bg-blue-50 rounded-xl p-3">
                <p className="text-sm font-semibold text-blue-700 mb-2">Available Variables:</p>
                <div className="flex flex-wrap gap-2">
                  {['{{contact_name}}', '{{institution_name}}', '{{platform_name}}', '{{students_count}}', '{{exam_types}}', '{{deal_value}}'].map(v => (
                    <Badge key={v} variant="outline" className="font-mono text-xs cursor-pointer hover:bg-blue-100"
                      onClick={() => setNewTemplate({...newTemplate, body_html: newTemplate.body_html + v})}
                    >{v}</Badge>
                  ))}
                </div>
              </div>
              <Button type="submit" className="btn-duo w-full" data-testid="submit-template-btn">Create Template</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates?.map((template) => (
          <Card key={template.id} className="bg-white border-2 border-gray-100 rounded-xl hover:shadow-md transition-shadow" data-testid={`template-card-${template.id}`}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Mail className="w-5 h-5 text-gray-400" />
                  <Badge className={getCategoryStyle(template.category)}>{template.category}</Badge>
                </div>
                {template.is_default && <Badge variant="outline" className="text-xs">Default</Badge>}
              </div>
              <h4 className="font-bold text-gray-900 mb-1">{template.name}</h4>
              <p className="text-sm text-gray-500 line-clamp-1 mb-3">{template.subject}</p>
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>Used {template.usage_count || 0} times</span>
                <div className="flex gap-1">
                  <Button size="sm" variant="ghost" className="h-7 w-7 p-0">
                    <Eye className="w-3 h-3" />
                  </Button>
                  <Button size="sm" variant="ghost" className="h-7 w-7 p-0">
                    <Copy className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        {(!templates || templates.length === 0) && (
          <div className="col-span-full text-center py-8">
            <Mail className="w-12 h-12 mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">No templates yet. Create your first template!</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Sub-component for Automation Rules
const AutomationRulesSection = ({ rules, templates, onRefresh }) => {
  const [createOpen, setCreateOpen] = useState(false);
  const [newRule, setNewRule] = useState({
    name: '',
    trigger_type: 'lead_created',
    trigger_config: {},
    actions: [{ type: 'send_email', template: '' }],
    is_active: true
  });

  const triggerTypes = [
    { value: 'lead_created', label: '🆕 Lead Created', desc: 'When a new lead is added' },
    { value: 'lead_stage_change', label: '📊 Stage Changed', desc: 'When lead moves to a stage' },
    { value: 'inactivity', label: '💤 Inactivity', desc: 'After X days of no activity' },
    { value: 'score_threshold', label: '🔥 Score Threshold', desc: 'When score reaches X' },
    { value: 'date_based', label: '📅 Date Based', desc: 'On specific dates' },
  ];

  const actionTypes = [
    { value: 'send_email', label: '📧 Send Email' },
    { value: 'create_task', label: '✅ Create Task' },
    { value: 'assign_to', label: '👤 Assign To' },
    { value: 'notify_slack', label: '💬 Slack Notification' },
    { value: 'update_score', label: '📊 Update Score' },
  ];

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/crm/automation-rules`, newRule);
      toast.success('Automation rule created!');
      setCreateOpen(false);
      setNewRule({
        name: '',
        trigger_type: 'lead_created',
        trigger_config: {},
        actions: [{ type: 'send_email', template: '' }],
        is_active: true
      });
      onRefresh();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create rule');
    }
  };

  const addAction = () => {
    setNewRule({
      ...newRule,
      actions: [...newRule.actions, { type: 'send_email', template: '' }]
    });
  };

  const updateAction = (index, field, value) => {
    const actions = [...newRule.actions];
    actions[index] = { ...actions[index], [field]: value };
    setNewRule({ ...newRule, actions });
  };

  const removeAction = (index) => {
    if (newRule.actions.length > 1) {
      const actions = newRule.actions.filter((_, i) => i !== index);
      setNewRule({ ...newRule, actions });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-gray-900">Automation Rules</h3>
          <p className="text-sm text-gray-500">Automate actions based on triggers and conditions</p>
        </div>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button className="btn-duo flex items-center gap-2" data-testid="create-automation-btn">
              <Zap className="w-4 h-4" /> New Automation
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-gray-900 font-extrabold">Create Automation Rule</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <Label>Rule Name *</Label>
                <Input
                  value={newRule.name}
                  onChange={(e) => setNewRule({...newRule, name: e.target.value})}
                  required
                  className="input-duo"
                  placeholder="e.g., Welcome Email on New Lead"
                  data-testid="rule-name-input"
                />
              </div>
              
              <div className="bg-gray-50 rounded-xl p-4">
                <Label className="text-gray-700 font-semibold mb-3 block">Trigger (When)</Label>
                <div className="grid grid-cols-1 gap-2">
                  {triggerTypes.map(trigger => (
                    <div
                      key={trigger.value}
                      onClick={() => setNewRule({...newRule, trigger_type: trigger.value})}
                      className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                        newRule.trigger_type === trigger.value 
                          ? 'border-[#58CC02] bg-green-50' 
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold">{trigger.label}</span>
                        {newRule.trigger_type === trigger.value && (
                          <span className="text-[#58CC02]">✓</span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500">{trigger.desc}</p>
                    </div>
                  ))}
                </div>
                
                {newRule.trigger_type === 'inactivity' && (
                  <div className="mt-3">
                    <Label>Days of inactivity</Label>
                    <Input
                      type="number"
                      value={newRule.trigger_config.days || 7}
                      onChange={(e) => setNewRule({
                        ...newRule, 
                        trigger_config: { ...newRule.trigger_config, days: parseInt(e.target.value) }
                      })}
                      className="input-duo"
                      min="1"
                    />
                  </div>
                )}
                
                {newRule.trigger_type === 'score_threshold' && (
                  <div className="mt-3">
                    <Label>Score threshold</Label>
                    <Input
                      type="number"
                      value={newRule.trigger_config.score || 80}
                      onChange={(e) => setNewRule({
                        ...newRule, 
                        trigger_config: { ...newRule.trigger_config, score: parseInt(e.target.value) }
                      })}
                      className="input-duo"
                      min="1"
                      max="100"
                    />
                  </div>
                )}
              </div>

              <div className="bg-blue-50 rounded-xl p-4">
                <div className="flex items-center justify-between mb-3">
                  <Label className="text-gray-700 font-semibold">Actions (Then)</Label>
                  <Button type="button" size="sm" variant="outline" onClick={addAction}>
                    <Plus className="w-3 h-3 mr-1" /> Add Action
                  </Button>
                </div>
                <div className="space-y-3">
                  {newRule.actions.map((action, index) => (
                    <div key={index} className="bg-white rounded-lg p-3 border border-blue-200">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-bold text-gray-500">ACTION {index + 1}</span>
                        {newRule.actions.length > 1 && (
                          <Button type="button" size="sm" variant="ghost" className="h-6 w-6 p-0 ml-auto" onClick={() => removeAction(index)}>
                            <Trash2 className="w-3 h-3 text-red-500" />
                          </Button>
                        )}
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <Select 
                          value={action.type} 
                          onValueChange={(v) => updateAction(index, 'type', v)}
                        >
                          <SelectTrigger className="input-duo text-sm">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {actionTypes.map(at => (
                              <SelectItem key={at.value} value={at.value}>{at.label}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        
                        {action.type === 'send_email' && (
                          <Select 
                            value={action.template || ''} 
                            onValueChange={(v) => updateAction(index, 'template', v)}
                          >
                            <SelectTrigger className="input-duo text-sm">
                              <SelectValue placeholder="Select template" />
                            </SelectTrigger>
                            <SelectContent>
                              {templates?.map(t => (
                                <SelectItem key={t.id} value={t.name}>{t.name}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        )}
                        
                        {action.type === 'create_task' && (
                          <Input
                            value={action.title || ''}
                            onChange={(e) => updateAction(index, 'title', e.target.value)}
                            placeholder="Task title"
                            className="input-duo text-sm"
                          />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <Button type="submit" className="btn-duo w-full" data-testid="submit-automation-btn">Create Automation</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {rules?.map((rule) => (
          <Card key={rule.id} className="bg-white border-2 border-gray-100 rounded-xl" data-testid={`automation-card-${rule.id}`}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${rule.is_active ? 'bg-green-100' : 'bg-gray-100'}`}>
                    <Zap className={`w-4 h-4 ${rule.is_active ? 'text-green-600' : 'text-gray-400'}`} />
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-900">{rule.name}</h4>
                    <p className="text-xs text-gray-500">Trigger: {rule.trigger_type.replace('_', ' ')}</p>
                  </div>
                </div>
                <Badge className={rule.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}>
                  {rule.is_active ? 'Active' : 'Paused'}
                </Badge>
              </div>
              <div className="space-y-2 mb-3">
                {rule.actions?.map((action, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-gray-600">
                    <ChevronRight className="w-3 h-3" />
                    <span>{action.type.replace('_', ' ')}</span>
                    {action.template && <Badge variant="outline" className="text-xs">{action.template}</Badge>}
                  </div>
                ))}
              </div>
              <div className="flex items-center justify-between text-xs text-gray-400 pt-2 border-t">
                <span>Executed {rule.executions_count || 0} times</span>
                <div className="flex gap-1">
                  <Button size="sm" variant="ghost" className="h-7 w-7 p-0">
                    {rule.is_active ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                  </Button>
                  <Button size="sm" variant="ghost" className="h-7 w-7 p-0">
                    <Edit className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        {(!rules || rules.length === 0) && (
          <div className="col-span-full text-center py-8">
            <Zap className="w-12 h-12 mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">No automation rules yet. Create your first automation!</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Sub-component for CRM Tasks
const TasksSection = ({ tasks, onRefresh }) => {
  const [createOpen, setCreateOpen] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    due_date: '',
    priority: 'medium',
    assigned_to: '',
    lead_id: ''
  });

  const priorities = [
    { value: 'low', label: 'Low', color: 'bg-blue-100 text-blue-700' },
    { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-700' },
    { value: 'high', label: 'High', color: 'bg-orange-100 text-orange-700' },
    { value: 'urgent', label: 'Urgent', color: 'bg-red-100 text-red-700' },
  ];

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/crm/tasks`, newTask);
      toast.success('Task created!');
      setCreateOpen(false);
      setNewTask({ title: '', description: '', due_date: '', priority: 'medium', assigned_to: '', lead_id: '' });
      onRefresh();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create task');
    }
  };

  const getPriorityStyle = (priority) => {
    const found = priorities.find(p => p.value === priority);
    return found?.color || 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-gray-900">Tasks</h3>
          <p className="text-sm text-gray-500">Manage follow-ups and to-dos for your leads</p>
        </div>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button className="btn-duo flex items-center gap-2" data-testid="create-task-btn">
              <CheckSquare className="w-4 h-4" /> New Task
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-md">
            <DialogHeader>
              <DialogTitle className="text-gray-900 font-extrabold">Create Task</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <Label>Task Title *</Label>
                <Input
                  value={newTask.title}
                  onChange={(e) => setNewTask({...newTask, title: e.target.value})}
                  required
                  className="input-duo"
                  placeholder="e.g., Follow up with Oxford Academy"
                  data-testid="task-title-input"
                />
              </div>
              <div>
                <Label>Description</Label>
                <Textarea
                  value={newTask.description}
                  onChange={(e) => setNewTask({...newTask, description: e.target.value})}
                  className="input-duo"
                  rows={3}
                  placeholder="Add details about this task..."
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Due Date</Label>
                  <Input
                    type="date"
                    value={newTask.due_date}
                    onChange={(e) => setNewTask({...newTask, due_date: e.target.value})}
                    className="input-duo"
                  />
                </div>
                <div>
                  <Label>Priority</Label>
                  <Select 
                    value={newTask.priority} 
                    onValueChange={(v) => setNewTask({...newTask, priority: v})}
                  >
                    <SelectTrigger className="input-duo">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {priorities.map(p => (
                        <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <Button type="submit" className="btn-duo w-full" data-testid="submit-task-btn">Create Task</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-3">
        {tasks?.map((task) => (
          <Card key={task.id} className={`bg-white border-2 rounded-xl ${task.is_completed ? 'opacity-60' : ''}`} data-testid={`task-card-${task.id}`}>
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <button className={`w-6 h-6 rounded-md border-2 flex items-center justify-center ${task.is_completed ? 'bg-green-500 border-green-500' : 'border-gray-300'}`}>
                  {task.is_completed && <span className="text-white text-xs">✓</span>}
                </button>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className={`font-semibold ${task.is_completed ? 'line-through text-gray-400' : 'text-gray-900'}`}>{task.title}</h4>
                    <Badge className={getPriorityStyle(task.priority)}>{task.priority}</Badge>
                  </div>
                  {task.description && (
                    <p className="text-sm text-gray-500 mb-2">{task.description}</p>
                  )}
                  <div className="flex items-center gap-4 text-xs text-gray-400">
                    {task.due_date && (
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(task.due_date).toLocaleDateString()}
                      </span>
                    )}
                    {task.lead_name && (
                      <span className="flex items-center gap-1">
                        <Target className="w-3 h-3" />
                        {task.lead_name}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        {(!tasks || tasks.length === 0) && (
          <div className="text-center py-8">
            <CheckSquare className="w-12 h-12 mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">No tasks yet. Create your first task!</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Sub-component for Advanced Reports
const ReportsSection = ({ stats }) => {
  const reportCards = [
    { title: 'Conversion Rate', value: `${stats?.conversion_rate || 0}%`, icon: TrendingUp, color: 'text-green-500', bgColor: 'bg-green-50' },
    { title: 'Avg. Deal Size', value: `$${(stats?.avg_deal_size || 0).toLocaleString()}`, icon: Target, color: 'text-blue-500', bgColor: 'bg-blue-50' },
    { title: 'Response Time', value: `${stats?.avg_response_time || 0}h`, icon: Clock, color: 'text-purple-500', bgColor: 'bg-purple-50' },
    { title: 'Active Leads', value: stats?.active_leads || 0, icon: Users, color: 'text-orange-500', bgColor: 'bg-orange-50' },
  ];

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-bold text-gray-900">Advanced Reports</h3>
        <p className="text-sm text-gray-500">Performance metrics and insights</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {reportCards.map((card, index) => (
          <Card key={index} className="bg-white border-2 border-gray-100 rounded-xl">
            <CardContent className="p-4 text-center">
              <div className={`w-12 h-12 rounded-xl ${card.bgColor} mx-auto mb-3 flex items-center justify-center`}>
                <card.icon className={`w-6 h-6 ${card.color}`} />
              </div>
              <div className="text-2xl font-extrabold text-gray-900">{card.value}</div>
              <div className="text-xs text-gray-500">{card.title}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="bg-white border-2 border-gray-100 rounded-xl">
        <CardHeader>
          <CardTitle className="text-gray-900 font-extrabold">Pipeline Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { stage: 'New Leads', count: stats?.pipeline_stages?.new || 0, color: 'bg-gray-500' },
              { stage: 'Contacted', count: stats?.pipeline_stages?.contacted || 0, color: 'bg-blue-500' },
              { stage: 'Demo Scheduled', count: stats?.pipeline_stages?.demo_scheduled || 0, color: 'bg-purple-500' },
              { stage: 'Proposal Sent', count: stats?.pipeline_stages?.proposal || 0, color: 'bg-orange-500' },
              { stage: 'Negotiation', count: stats?.pipeline_stages?.negotiation || 0, color: 'bg-yellow-500' },
              { stage: 'Won', count: stats?.pipeline_stages?.won || 0, color: 'bg-green-500' },
            ].map((item, index) => {
              const total = Object.values(stats?.pipeline_stages || {}).reduce((a, b) => a + b, 0) || 1;
              const percentage = ((item.count / total) * 100).toFixed(0);
              return (
                <div key={index}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-semibold text-gray-700">{item.stage}</span>
                    <span className="text-sm text-gray-500">{item.count} ({percentage}%)</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div className={`${item.color} h-2 rounded-full`} style={{ width: `${percentage}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Main CRM Supreme Component
export default function CRMSupreme() {
  const [activeSection, setActiveSection] = useState('templates');
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState([]);
  const [rules, setRules] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [templatesRes, rulesRes] = await Promise.all([
        axios.get(`${API_URL}/crm/email-templates`),
        axios.get(`${API_URL}/crm/automation-rules`),
      ]);
      setTemplates(templatesRes.data.templates || []);
      setRules(rulesRes.data.rules || []);
      
      // Mock stats for now
      setStats({
        conversion_rate: 24,
        avg_deal_size: 5400,
        avg_response_time: 4,
        active_leads: 28,
        pipeline_stages: { new: 12, contacted: 8, demo_scheduled: 4, proposal: 2, negotiation: 1, won: 1 }
      });
    } catch (error) {
      console.error('Failed to fetch CRM data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const sections = [
    { id: 'templates', label: 'Email Templates', icon: Mail },
    { id: 'automations', label: 'Automations', icon: Zap },
    { id: 'tasks', label: 'Tasks', icon: CheckSquare },
    { id: 'reports', label: 'Reports', icon: BarChart3 },
  ];

  return (
    <div className="space-y-6" data-testid="crm-supreme">
      {/* Section Navigation */}
      <div className="flex gap-2 border-b-2 border-gray-100 pb-4">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl font-semibold transition-all ${
              activeSection === section.id
                ? 'bg-[#58CC02] text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            data-testid={`crm-section-${section.id}`}
          >
            <section.icon className="w-4 h-4" />
            {section.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-12 h-12 border-4 border-[#58CC02] border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <>
          {activeSection === 'templates' && (
            <EmailTemplatesSection templates={templates} onRefresh={fetchData} />
          )}
          {activeSection === 'automations' && (
            <AutomationRulesSection rules={rules} templates={templates} onRefresh={fetchData} />
          )}
          {activeSection === 'tasks' && (
            <TasksSection tasks={tasks} onRefresh={fetchData} />
          )}
          {activeSection === 'reports' && (
            <ReportsSection stats={stats} />
          )}
        </>
      )}
    </div>
  );
}
