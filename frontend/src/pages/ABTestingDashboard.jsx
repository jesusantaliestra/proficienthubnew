import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Switch } from '../components/ui/switch';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Progress } from '../components/ui/progress';
import {
  ArrowLeft, Beaker, Plus, Play, Pause, Trash2, BarChart3, TrendingUp, TrendingDown,
  Users, Target, DollarSign, CheckCircle, XCircle, AlertCircle, Trophy, Copy,
  ChevronRight, Eye, FlaskConical, Percent, Zap, Calendar, Clock
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, BarChart, Bar } from 'recharts';
import axios from 'axios';
import { toast, Toaster } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function ABTestingDashboard() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [experiments, setExperiments] = useState([]);
  const [selectedExperiment, setSelectedExperiment] = useState(null);
  const [experimentAnalytics, setExperimentAnalytics] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [activeFilter, setActiveFilter] = useState('all'); // all, active, completed
  
  const [newExperiment, setNewExperiment] = useState({
    name: '',
    description: '',
    experiment_type: 'feature',
    target_metric: 'conversion',
    traffic_percentage: 100,
    variants: [
      { name: 'Control', config: {}, weight: 1 },
      { name: 'Variant B', config: {}, weight: 1 }
    ]
  });

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  useEffect(() => {
    fetchExperiments();
  }, [activeFilter]);

  const fetchExperiments = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (activeFilter === 'active') params.append('is_active', 'true');
      if (activeFilter === 'completed') params.append('is_active', 'false');
      
      const response = await axios.get(`${API_URL}/ab-testing/experiments?${params}`, axiosConfig);
      setExperiments(response.data.experiments || []);
    } catch (error) {
      console.error('Failed to fetch experiments:', error);
      toast.error('Failed to load experiments');
    } finally {
      setLoading(false);
    }
  };

  const fetchExperimentDetails = async (experimentId) => {
    try {
      const [detailsRes, analyticsRes] = await Promise.all([
        axios.get(`${API_URL}/ab-testing/experiments/${experimentId}`, axiosConfig),
        axios.get(`${API_URL}/ab-testing/experiments/${experimentId}/analytics?days=30`, axiosConfig)
      ]);
      setSelectedExperiment(detailsRes.data);
      setExperimentAnalytics(analyticsRes.data);
    } catch (error) {
      console.error('Failed to fetch experiment details:', error);
      toast.error('Failed to load experiment details');
    }
  };

  const handleCreateExperiment = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/ab-testing/experiments`, newExperiment, axiosConfig);
      toast.success('Experiment created successfully!');
      setCreateDialogOpen(false);
      setNewExperiment({
        name: '',
        description: '',
        experiment_type: 'feature',
        target_metric: 'conversion',
        traffic_percentage: 100,
        variants: [
          { name: 'Control', config: {}, weight: 1 },
          { name: 'Variant B', config: {}, weight: 1 }
        ]
      });
      fetchExperiments();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create experiment');
    }
  };

  const handleStopExperiment = async (experimentId, winnerId = null) => {
    try {
      await axios.post(`${API_URL}/ab-testing/experiments/${experimentId}/stop`, null, {
        ...axiosConfig,
        params: winnerId ? { winner_variant_id: winnerId } : {}
      });
      toast.success('Experiment stopped');
      fetchExperiments();
      if (selectedExperiment?.id === experimentId) {
        fetchExperimentDetails(experimentId);
      }
    } catch (error) {
      toast.error('Failed to stop experiment');
    }
  };

  const handleDeleteExperiment = async (experimentId) => {
    if (!window.confirm('Are you sure you want to delete this experiment? All data will be lost.')) {
      return;
    }
    try {
      await axios.delete(`${API_URL}/ab-testing/experiments/${experimentId}`, axiosConfig);
      toast.success('Experiment deleted');
      fetchExperiments();
      if (selectedExperiment?.id === experimentId) {
        setSelectedExperiment(null);
        setExperimentAnalytics(null);
      }
    } catch (error) {
      toast.error('Failed to delete experiment');
    }
  };

  const addVariant = () => {
    const variantLetter = String.fromCharCode(65 + newExperiment.variants.length);
    setNewExperiment(prev => ({
      ...prev,
      variants: [...prev.variants, { name: `Variant ${variantLetter}`, config: {}, weight: 1 }]
    }));
  };

  const removeVariant = (index) => {
    if (newExperiment.variants.length <= 2) {
      toast.error('Minimum 2 variants required');
      return;
    }
    setNewExperiment(prev => ({
      ...prev,
      variants: prev.variants.filter((_, i) => i !== index)
    }));
  };

  const updateVariant = (index, field, value) => {
    setNewExperiment(prev => ({
      ...prev,
      variants: prev.variants.map((v, i) => i === index ? { ...v, [field]: value } : v)
    }));
  };

  const experimentTypes = [
    { value: 'feature', label: 'Feature Test', icon: '🔧', description: 'Test new features' },
    { value: 'pricing', label: 'Pricing Test', icon: '💰', description: 'Test pricing strategies' },
    { value: 'ui', label: 'UI/UX Test', icon: '🎨', description: 'Test design changes' },
    { value: 'content', label: 'Content Test', icon: '📝', description: 'Test copy variations' }
  ];

  const targetMetrics = [
    { value: 'conversion', label: 'Conversion Rate', icon: Target },
    { value: 'engagement', label: 'Engagement', icon: Users },
    { value: 'revenue', label: 'Revenue', icon: DollarSign },
    { value: 'signup', label: 'Sign-ups', icon: TrendingUp }
  ];

  const getStatusBadge = (experiment) => {
    if (!experiment.is_active) {
      if (experiment.winner_variant_id) {
        return <Badge className="bg-green-100 text-green-700 border-green-200">Completed - Winner</Badge>;
      }
      return <Badge className="bg-gray-100 text-gray-600 border-gray-200">Completed</Badge>;
    }
    return <Badge className="bg-blue-100 text-blue-700 border-blue-200">Running</Badge>;
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num?.toFixed?.(2) ?? num;
  };

  if (loading && experiments.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-gray-500 font-semibold">Loading experiments...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="ab-testing-dashboard">
      <Toaster position="top-right" richColors />
      
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/institution/dashboard')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                data-testid="back-to-dashboard"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center">
                  <FlaskConical className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">A/B Testing</h1>
                  <p className="text-sm text-gray-500">Experiment & Optimize</p>
                </div>
              </div>
            </div>
            
            <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-purple-600 hover:bg-purple-700 text-white" data-testid="create-experiment-btn">
                  <Plus className="w-4 h-4 mr-2" />
                  New Experiment
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle className="text-gray-900 font-bold text-xl">Create New Experiment</DialogTitle>
                </DialogHeader>
                
                <form onSubmit={handleCreateExperiment} className="space-y-6">
                  <div className="space-y-2">
                    <Label className="text-gray-700 font-semibold">Experiment Name *</Label>
                    <Input
                      value={newExperiment.name}
                      onChange={(e) => setNewExperiment(prev => ({ ...prev, name: e.target.value }))}
                      className="border-2 border-gray-200 rounded-xl"
                      placeholder="e.g., Homepage CTA Test, Pricing Page V2"
                      required
                      data-testid="experiment-name-input"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label className="text-gray-700 font-semibold">Description</Label>
                    <Textarea
                      value={newExperiment.description}
                      onChange={(e) => setNewExperiment(prev => ({ ...prev, description: e.target.value }))}
                      className="border-2 border-gray-200 rounded-xl"
                      placeholder="What are you testing and why?"
                      rows={2}
                    />
                  </div>
                  
                  {/* Experiment Type */}
                  <div className="space-y-2">
                    <Label className="text-gray-700 font-semibold">Experiment Type</Label>
                    <div className="grid grid-cols-4 gap-2">
                      {experimentTypes.map((type) => (
                        <button
                          key={type.value}
                          type="button"
                          onClick={() => setNewExperiment(prev => ({ ...prev, experiment_type: type.value }))}
                          className={`p-3 rounded-xl border-2 transition-all text-center ${
                            newExperiment.experiment_type === type.value
                              ? 'border-purple-500 bg-purple-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <span className="text-2xl block">{type.icon}</span>
                          <span className="text-xs font-medium text-gray-700">{type.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    {/* Target Metric */}
                    <div className="space-y-2">
                      <Label className="text-gray-700 font-semibold">Target Metric</Label>
                      <Select
                        value={newExperiment.target_metric}
                        onValueChange={(v) => setNewExperiment(prev => ({ ...prev, target_metric: v }))}
                      >
                        <SelectTrigger className="border-2 border-gray-200 rounded-xl">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {targetMetrics.map((metric) => (
                            <SelectItem key={metric.value} value={metric.value}>
                              <div className="flex items-center gap-2">
                                <metric.icon className="w-4 h-4" />
                                {metric.label}
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    {/* Traffic Percentage */}
                    <div className="space-y-2">
                      <Label className="text-gray-700 font-semibold">Traffic Percentage</Label>
                      <div className="flex items-center gap-3">
                        <Input
                          type="number"
                          min="1"
                          max="100"
                          value={newExperiment.traffic_percentage}
                          onChange={(e) => setNewExperiment(prev => ({ ...prev, traffic_percentage: parseInt(e.target.value) || 100 }))}
                          className="border-2 border-gray-200 rounded-xl w-24"
                        />
                        <span className="text-gray-500">% of users</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Variants */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Label className="text-gray-700 font-semibold">Variants</Label>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={addVariant}
                        className="text-purple-600"
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add Variant
                      </Button>
                    </div>
                    
                    <div className="space-y-2">
                      {newExperiment.variants.map((variant, index) => (
                        <div key={index} className={`p-3 rounded-xl border-2 ${
                          index === 0 ? 'border-gray-300 bg-gray-50' : 'border-gray-200'
                        }`}>
                          <div className="flex items-center gap-3">
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold ${
                              index === 0 ? 'bg-gray-500' : 'bg-purple-500'
                            }`}>
                              {String.fromCharCode(65 + index)}
                            </div>
                            <Input
                              value={variant.name}
                              onChange={(e) => updateVariant(index, 'name', e.target.value)}
                              className="border-gray-200 rounded-lg flex-1"
                              placeholder="Variant name"
                            />
                            <div className="flex items-center gap-2">
                              <Label className="text-xs text-gray-500">Weight:</Label>
                              <Input
                                type="number"
                                min="1"
                                value={variant.weight}
                                onChange={(e) => updateVariant(index, 'weight', parseInt(e.target.value) || 1)}
                                className="border-gray-200 rounded-lg w-16"
                              />
                            </div>
                            {index > 0 && (
                              <button
                                type="button"
                                onClick={() => removeVariant(index)}
                                className="p-2 hover:bg-red-50 rounded-lg text-red-500"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                          {index === 0 && (
                            <span className="text-xs text-gray-500 ml-11">Control Group</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex gap-3 pt-4">
                    <Button
                      type="button"
                      variant="outline"
                      className="flex-1"
                      onClick={() => setCreateDialogOpen(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      className="flex-1 bg-purple-600 hover:bg-purple-700 text-white"
                      data-testid="create-experiment-submit"
                    >
                      <Play className="w-4 h-4 mr-2" />
                      Launch Experiment
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Filter Tabs */}
        <div className="flex items-center gap-2 mb-6">
          {[
            { value: 'all', label: 'All Experiments' },
            { value: 'active', label: 'Running' },
            { value: 'completed', label: 'Completed' }
          ].map((filter) => (
            <button
              key={filter.value}
              onClick={() => setActiveFilter(filter.value)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeFilter === filter.value
                  ? 'bg-purple-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>
        
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Experiments List */}
          <div className="lg:col-span-1 space-y-4">
            <h2 className="text-lg font-bold text-gray-900">Experiments ({experiments.length})</h2>
            
            {experiments.length === 0 ? (
              <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                <CardContent className="p-8 text-center">
                  <FlaskConical className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <h3 className="font-bold text-gray-700 mb-2">No Experiments</h3>
                  <p className="text-sm text-gray-500 mb-4">Create your first A/B test to start optimizing</p>
                  <Button
                    onClick={() => setCreateDialogOpen(true)}
                    className="bg-purple-600 hover:bg-purple-700 text-white"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Create Experiment
                  </Button>
                </CardContent>
              </Card>
            ) : (
              experiments.map((exp) => (
                <Card
                  key={exp.id}
                  className={`bg-white border-2 rounded-2xl cursor-pointer transition-all ${
                    selectedExperiment?.id === exp.id
                      ? 'border-purple-300 ring-2 ring-purple-100'
                      : 'border-gray-100 hover:border-gray-200'
                  }`}
                  onClick={() => fetchExperimentDetails(exp.id)}
                  data-testid={`experiment-card-${exp.id}`}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xl">
                          {experimentTypes.find(t => t.value === exp.experiment_type)?.icon || '🔬'}
                        </span>
                        {getStatusBadge(exp)}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteExperiment(exp.id);
                        }}
                        className="p-1.5 hover:bg-red-50 rounded-lg text-gray-400 hover:text-red-500"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    
                    <h3 className="font-bold text-gray-900 mb-1">{exp.name}</h3>
                    {exp.description && (
                      <p className="text-sm text-gray-500 line-clamp-1 mb-3">{exp.description}</p>
                    )}
                    
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Users className="w-3 h-3" />
                        {formatNumber(exp.variants?.reduce((acc, v) => acc + (v.impressions || 0), 0) || 0)} imp.
                      </span>
                      <span className="flex items-center gap-1">
                        <Target className="w-3 h-3" />
                        {formatNumber(exp.variants?.reduce((acc, v) => acc + (v.conversions || 0), 0) || 0)} conv.
                      </span>
                      <span className="flex items-center gap-1">
                        <Beaker className="w-3 h-3" />
                        {exp.variants?.length || 0} variants
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
          
          {/* Experiment Details */}
          <div className="lg:col-span-2 space-y-6">
            {selectedExperiment ? (
              <>
                {/* Header */}
                <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <h2 className="text-2xl font-bold text-gray-900">{selectedExperiment.name}</h2>
                          {getStatusBadge(selectedExperiment)}
                        </div>
                        <p className="text-gray-500">{selectedExperiment.description}</p>
                      </div>
                      
                      {selectedExperiment.is_active && (
                        <Button
                          variant="outline"
                          className="border-orange-200 text-orange-600 hover:bg-orange-50"
                          onClick={() => handleStopExperiment(selectedExperiment.id)}
                        >
                          <Pause className="w-4 h-4 mr-2" />
                          Stop Test
                        </Button>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-4 gap-4 mt-6">
                      <div className="text-center p-3 bg-gray-50 rounded-xl">
                        <p className="text-2xl font-bold text-gray-900">
                          {formatNumber(experimentAnalytics?.summary?.total_impressions || 0)}
                        </p>
                        <p className="text-xs text-gray-500">Impressions</p>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-xl">
                        <p className="text-2xl font-bold text-green-600">
                          {formatNumber(experimentAnalytics?.summary?.total_conversions || 0)}
                        </p>
                        <p className="text-xs text-gray-500">Conversions</p>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-xl">
                        <p className="text-2xl font-bold text-purple-600">
                          {((experimentAnalytics?.summary?.total_conversions || 0) / 
                            (experimentAnalytics?.summary?.total_impressions || 1) * 100).toFixed(2)}%
                        </p>
                        <p className="text-xs text-gray-500">Conv. Rate</p>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-xl">
                        <p className="text-2xl font-bold text-blue-600">
                          ${formatNumber(experimentAnalytics?.summary?.total_revenue || 0)}
                        </p>
                        <p className="text-xs text-gray-500">Revenue</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                {/* Variants Performance */}
                <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                  <CardHeader>
                    <CardTitle className="text-gray-900 font-bold">Variant Performance</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {selectedExperiment.variants?.map((variant, index) => {
                        const convRate = variant.conversion_rate || 0;
                        const isWinner = selectedExperiment.winner_variant_id === variant.id;
                        const analysis = selectedExperiment.statistical_analysis?.find(a => a.variant_id === variant.id);
                        
                        return (
                          <div
                            key={variant.id}
                            className={`p-4 rounded-xl border-2 ${
                              isWinner ? 'border-green-300 bg-green-50' :
                              variant.is_control ? 'border-gray-300 bg-gray-50' : 'border-gray-200'
                            }`}
                          >
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center gap-3">
                                <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold ${
                                  isWinner ? 'bg-green-500' :
                                  variant.is_control ? 'bg-gray-500' : 'bg-purple-500'
                                }`}>
                                  {String.fromCharCode(65 + index)}
                                </div>
                                <div>
                                  <div className="flex items-center gap-2">
                                    <h4 className="font-bold text-gray-900">{variant.name}</h4>
                                    {variant.is_control && (
                                      <Badge variant="outline" className="text-xs">Control</Badge>
                                    )}
                                    {isWinner && (
                                      <Badge className="bg-green-100 text-green-700 border-green-200">
                                        <Trophy className="w-3 h-3 mr-1" /> Winner
                                      </Badge>
                                    )}
                                  </div>
                                  <p className="text-xs text-gray-500">
                                    {variant.impressions || 0} impressions • {variant.conversions || 0} conversions
                                  </p>
                                </div>
                              </div>
                              
                              <div className="text-right">
                                <p className="text-2xl font-bold text-gray-900">{convRate.toFixed(2)}%</p>
                                {analysis && (
                                  <p className={`text-sm font-medium ${
                                    analysis.vs_control_lift > 0 ? 'text-green-600' : 
                                    analysis.vs_control_lift < 0 ? 'text-red-600' : 'text-gray-500'
                                  }`}>
                                    {analysis.vs_control_lift > 0 ? '+' : ''}{analysis.vs_control_lift}% vs control
                                  </p>
                                )}
                              </div>
                            </div>
                            
                            <Progress
                              value={convRate}
                              className="h-2"
                            />
                            
                            {analysis && (
                              <div className="mt-3 flex items-center gap-4 text-sm">
                                <span className={`flex items-center gap-1 ${
                                  analysis.is_significant ? 'text-green-600' : 'text-gray-500'
                                }`}>
                                  {analysis.is_significant ? (
                                    <CheckCircle className="w-4 h-4" />
                                  ) : (
                                    <AlertCircle className="w-4 h-4" />
                                  )}
                                  {analysis.confidence_level}% confidence
                                </span>
                                {!selectedExperiment.winner_variant_id && selectedExperiment.is_active && analysis.is_significant && (
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="text-green-600 border-green-200 hover:bg-green-50"
                                    onClick={() => handleStopExperiment(selectedExperiment.id, variant.id)}
                                  >
                                    <Trophy className="w-3 h-3 mr-1" />
                                    Declare Winner
                                  </Button>
                                )}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
                
                {/* Conversion Chart */}
                {experimentAnalytics?.chart_data?.length > 0 && (
                  <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                    <CardHeader>
                      <CardTitle className="text-gray-900 font-bold">Conversions Over Time</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={experimentAnalytics.chart_data}>
                          <defs>
                            <linearGradient id="controlGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#6B7280" stopOpacity={0.3}/>
                              <stop offset="95%" stopColor="#6B7280" stopOpacity={0}/>
                            </linearGradient>
                            <linearGradient id="variantGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#9333EA" stopOpacity={0.3}/>
                              <stop offset="95%" stopColor="#9333EA" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" />
                          <XAxis dataKey="date" stroke="#AFAFAF" />
                          <YAxis stroke="#AFAFAF" />
                          <Tooltip contentStyle={{ backgroundColor: '#fff', border: '2px solid #E5E5E5', borderRadius: '12px' }} />
                          <Legend />
                          {selectedExperiment.variants?.map((variant, index) => (
                            <Area
                              key={variant.id}
                              type="monotone"
                              dataKey={`${variant.name}_conversions`}
                              name={variant.name}
                              stroke={index === 0 ? '#6B7280' : '#9333EA'}
                              fill={index === 0 ? 'url(#controlGradient)' : 'url(#variantGradient)'}
                              strokeWidth={2}
                            />
                          ))}
                        </AreaChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Card className="bg-gradient-to-br from-purple-50 to-indigo-50 border-2 border-purple-100 rounded-2xl">
                <CardContent className="p-12 text-center">
                  <FlaskConical className="w-16 h-16 text-purple-300 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-gray-700 mb-2">Select an Experiment</h3>
                  <p className="text-gray-500">Click on an experiment to view its performance details</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
