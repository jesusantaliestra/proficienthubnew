import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import {
  Building2, Users, GraduationCap, BookOpen, Brain, TrendingUp, 
  DollarSign, Activity, Search, RefreshCw, ChevronRight, Settings,
  BarChart3, Award, Zap, Clock, Globe, Shield, Gift, ArrowUpRight,
  ArrowDownRight, Eye, MessageSquare
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SuperadminDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [institutions, setInstitutions] = useState([]);
  const [activities, setActivities] = useState([]);
  const [revenueReport, setRevenueReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [grantCreditsModal, setGrantCreditsModal] = useState({ open: false, institution: null });
  const [creditsToGrant, setCreditsToGrant] = useState(100);
  const [grantReason, setGrantReason] = useState('');

  const token = localStorage.getItem('token');

  const fetchStats = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/superadmin/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      if (error.response?.status === 403) {
        toast.error('Superadmin access required');
        navigate('/admin');
      }
    }
  }, [token, navigate]);

  const fetchInstitutions = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/superadmin/institutions`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { search: searchQuery, limit: 20 }
      });
      setInstitutions(response.data.institutions || []);
    } catch (error) {
      console.error('Failed to fetch institutions:', error);
    }
  }, [token, searchQuery]);

  const fetchActivities = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/superadmin/activity-log`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { limit: 15 }
      });
      setActivities(response.data.activities || []);
    } catch (error) {
      console.error('Failed to fetch activities:', error);
    }
  }, [token]);

  const fetchRevenueReport = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/superadmin/revenue-report`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { period: selectedPeriod }
      });
      setRevenueReport(response.data);
    } catch (error) {
      console.error('Failed to fetch revenue report:', error);
    }
  }, [token, selectedPeriod]);

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      await Promise.all([fetchStats(), fetchInstitutions(), fetchActivities(), fetchRevenueReport()]);
      setLoading(false);
    };
    fetchAll();
  }, [fetchStats, fetchInstitutions, fetchActivities, fetchRevenueReport]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchInstitutions();
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, fetchInstitutions]);

  const handleGrantCredits = async () => {
    if (!grantCreditsModal.institution) return;
    try {
      await axios.post(`${API_URL}/superadmin/grant-credits`, null, {
        headers: { Authorization: `Bearer ${token}` },
        params: {
          institution_id: grantCreditsModal.institution.id,
          credits: creditsToGrant,
          reason: grantReason || 'Promotional credits'
        }
      });
      toast.success(`Granted ${creditsToGrant} credits successfully!`);
      setGrantCreditsModal({ open: false, institution: null });
      setCreditsToGrant(100);
      setGrantReason('');
      fetchInstitutions();
    } catch (error) {
      toast.error('Failed to grant credits');
    }
  };

  const refresh = () => {
    fetchStats();
    fetchInstitutions();
    fetchActivities();
    fetchRevenueReport();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  // Verify superadmin access
  if (!user?.is_superadmin && user?.user_type !== 'admin') {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="p-8 text-center">
            <Shield className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Access Denied</h2>
            <p className="text-gray-600">You need Superadmin access to view this page.</p>
            <Button onClick={() => navigate('/admin')} className="mt-4">
              Go to Admin Panel
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const platformStats = stats?.platform_stats || {};
  const examStats = stats?.exam_stats || {};
  const aiStats = stats?.ai_stats || {};
  const growthStats = stats?.growth_stats || {};
  const businessMetrics = stats?.business_metrics || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/30 backdrop-blur-lg border-b border-white/10 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Superadmin Dashboard</h1>
                <p className="text-purple-300 text-sm">ProficientHub Platform Overview</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button 
                variant="outline" 
                size="sm"
                onClick={refresh}
                className="border-purple-500/50 text-purple-300 hover:bg-purple-500/20"
                data-testid="refresh-stats-btn"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => navigate('/admin')}
                className="border-white/20 text-white hover:bg-white/10"
              >
                <Settings className="w-4 h-4 mr-2" />
                Admin Panel
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8" data-testid="superadmin-dashboard">
        {/* Main Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard
            title="Institutions"
            value={platformStats.total_institutions || 0}
            icon={Building2}
            change={growthStats.new_institutions_this_week}
            changeLabel="new this week"
            color="purple"
          />
          <StatCard
            title="Total Students"
            value={platformStats.total_students || 0}
            icon={GraduationCap}
            change={growthStats.new_students_this_week}
            changeLabel="new this week"
            color="blue"
          />
          <StatCard
            title="Active Users (7d)"
            value={platformStats.active_users_7d || 0}
            icon={Users}
            subtext={`${platformStats.active_users_30d || 0} in 30d`}
            color="green"
          />
          <StatCard
            title="Total Exams"
            value={examStats.total_exams_taken || 0}
            icon={BookOpen}
            change={examStats.exams_this_week}
            changeLabel="this week"
            color="amber"
          />
        </div>

        {/* AI & Revenue Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className="bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border-indigo-500/30">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-indigo-300 text-sm font-medium">AI Interactions</p>
                  <p className="text-4xl font-bold text-white mt-1">{aiStats.total_ai_interactions?.toLocaleString() || 0}</p>
                  <p className="text-indigo-400 text-sm mt-1">{aiStats.ai_interactions_this_week || 0} this week</p>
                </div>
                <div className="w-16 h-16 rounded-2xl bg-indigo-500/30 flex items-center justify-center">
                  <Brain className="w-8 h-8 text-indigo-300" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border-emerald-500/30">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-emerald-300 text-sm font-medium">Credits Purchased</p>
                  <p className="text-4xl font-bold text-white mt-1">{aiStats.total_credits_purchased?.toLocaleString() || 0}</p>
                  <p className="text-emerald-400 text-sm mt-1">{aiStats.total_credits_used || 0} used</p>
                </div>
                <div className="w-16 h-16 rounded-2xl bg-emerald-500/30 flex items-center justify-center">
                  <Zap className="w-8 h-8 text-emerald-300" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-amber-500/20 to-orange-500/20 border-amber-500/30">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-amber-300 text-sm font-medium">Est. Revenue</p>
                  <p className="text-4xl font-bold text-white mt-1">${businessMetrics.estimated_revenue_from_credits?.toFixed(2) || '0.00'}</p>
                  <p className="text-amber-400 text-sm mt-1">{businessMetrics.platform_engagement_rate || 0}% engagement</p>
                </div>
                <div className="w-16 h-16 rounded-2xl bg-amber-500/30 flex items-center justify-center">
                  <DollarSign className="w-8 h-8 text-amber-300" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Institutions List */}
          <div className="lg:col-span-2">
            <Card className="bg-white/5 border-white/10">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-white flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-purple-400" />
                    Institutions
                  </CardTitle>
                  <div className="relative w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <Input
                      placeholder="Search institutions..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                      data-testid="institution-search"
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {institutions.length === 0 ? (
                    <p className="text-gray-400 text-center py-8">No institutions found</p>
                  ) : (
                    institutions.map((inst) => (
                      <div 
                        key={inst.id}
                        className="p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
                        data-testid={`institution-row-${inst.id}`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-lg">
                              {inst.institution_name?.charAt(0) || 'I'}
                            </div>
                            <div>
                              <h4 className="font-semibold text-white">{inst.institution_name || inst.name}</h4>
                              <p className="text-sm text-gray-400">{inst.email}</p>
                              <div className="flex items-center gap-2 mt-1">
                                <Badge variant="outline" className="text-xs border-purple-500/50 text-purple-300">
                                  <Users className="w-3 h-3 mr-1" />
                                  {inst.student_count || 0} students
                                </Badge>
                                {inst.has_zoom_configured && (
                                  <Badge variant="outline" className="text-xs border-blue-500/50 text-blue-300">Zoom</Badge>
                                )}
                                {inst.has_messaging_configured && (
                                  <Badge variant="outline" className="text-xs border-green-500/50 text-green-300">SMS</Badge>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            <div className="text-right">
                              <p className="text-sm text-gray-400">AI Credits</p>
                              <p className="text-lg font-semibold text-white">{inst.ai_credits?.available || 0}</p>
                            </div>
                            <Button
                              size="sm"
                              variant="outline"
                              className="border-emerald-500/50 text-emerald-400 hover:bg-emerald-500/20"
                              onClick={() => setGrantCreditsModal({ open: true, institution: inst })}
                              data-testid={`grant-credits-${inst.id}`}
                            >
                              <Gift className="w-4 h-4 mr-1" />
                              Grant
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="text-gray-400 hover:text-white hover:bg-white/10"
                              onClick={() => navigate(`/admin/institution/${inst.id}`)}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Activity Feed */}
          <div>
            <Card className="bg-white/5 border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-green-400" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-[500px] overflow-y-auto">
                  {activities.length === 0 ? (
                    <p className="text-gray-400 text-center py-4">No recent activity</p>
                  ) : (
                    activities.map((activity, index) => (
                      <div 
                        key={index}
                        className="p-3 rounded-lg bg-white/5 border border-white/10"
                      >
                        <div className="flex items-start gap-3">
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                            activity.type === 'exam' ? 'bg-blue-500/20 text-blue-400' :
                            activity.type === 'ai' ? 'bg-purple-500/20 text-purple-400' :
                            'bg-green-500/20 text-green-400'
                          }`}>
                            {activity.type === 'exam' ? <BookOpen className="w-4 h-4" /> :
                             activity.type === 'ai' ? <Brain className="w-4 h-4" /> :
                             <Users className="w-4 h-4" />}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-white truncate">{activity.description}</p>
                            <p className="text-xs text-gray-400 mt-1">
                              {new Date(activity.timestamp).toLocaleString()}
                            </p>
                          </div>
                          {activity.score !== undefined && (
                            <Badge className="bg-blue-500/20 text-blue-300">
                              {activity.score.toFixed(1)}
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Exam Distribution */}
            <Card className="bg-white/5 border-white/10 mt-4">
              <CardHeader className="pb-2">
                <CardTitle className="text-white flex items-center gap-2 text-lg">
                  <BarChart3 className="w-5 h-5 text-amber-400" />
                  Exam Distribution
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(examStats.exam_distribution || {}).slice(0, 6).map(([exam, count]) => (
                    <div key={exam} className="flex items-center justify-between">
                      <span className="text-gray-300 text-sm">{exam}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24">
                          <Progress 
                            value={(count / Math.max(...Object.values(examStats.exam_distribution || {1: 1}))) * 100} 
                            className="h-2"
                          />
                        </div>
                        <span className="text-white font-medium text-sm w-12 text-right">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Business Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
          <MetricCard
            title="Avg Credits/Institution"
            value={businessMetrics.avg_credits_per_institution?.toFixed(0) || 0}
            icon={Zap}
          />
          <MetricCard
            title="Student:Institution Ratio"
            value={`${businessMetrics.student_to_institution_ratio?.toFixed(1) || 0}:1`}
            icon={Users}
          />
          <MetricCard
            title="Platform Engagement"
            value={`${businessMetrics.platform_engagement_rate?.toFixed(1) || 0}%`}
            icon={TrendingUp}
          />
          <MetricCard
            title="Free Credits Given"
            value={aiStats.total_free_credits_given || 0}
            icon={Gift}
          />
        </div>
      </main>

      {/* Grant Credits Modal */}
      {grantCreditsModal.open && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gift className="w-5 h-5 text-emerald-500" />
                Grant AI Credits
              </CardTitle>
              <CardDescription>
                Grant credits to {grantCreditsModal.institution?.institution_name || 'Institution'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 block mb-2">Number of Credits</label>
                <Input
                  type="number"
                  value={creditsToGrant}
                  onChange={(e) => setCreditsToGrant(parseInt(e.target.value) || 0)}
                  min={1}
                  data-testid="credits-input"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 block mb-2">Reason (optional)</label>
                <Input
                  value={grantReason}
                  onChange={(e) => setGrantReason(e.target.value)}
                  placeholder="e.g., Promotional, Welcome bonus..."
                  data-testid="grant-reason-input"
                />
              </div>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => setGrantCreditsModal({ open: false, institution: null })}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleGrantCredits}
                  className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                  data-testid="confirm-grant-btn"
                >
                  Grant {creditsToGrant} Credits
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

// Stat Card Component
const StatCard = ({ title, value, icon: Icon, change, changeLabel, subtext, color }) => {
  const colorClasses = {
    purple: 'from-purple-500/20 to-fuchsia-500/20 border-purple-500/30',
    blue: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30',
    green: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/30',
    amber: 'from-amber-500/20 to-orange-500/20 border-amber-500/30'
  };

  const iconColorClasses = {
    purple: 'bg-purple-500/30 text-purple-300',
    blue: 'bg-blue-500/30 text-blue-300',
    green: 'bg-emerald-500/30 text-emerald-300',
    amber: 'bg-amber-500/30 text-amber-300'
  };

  return (
    <Card className={`bg-gradient-to-br ${colorClasses[color]} border`}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-300 text-sm font-medium">{title}</p>
            <p className="text-3xl font-bold text-white mt-1">{value?.toLocaleString()}</p>
            {change !== undefined && (
              <div className="flex items-center gap-1 mt-1">
                <ArrowUpRight className="w-3 h-3 text-emerald-400" />
                <span className="text-emerald-400 text-xs">+{change} {changeLabel}</span>
              </div>
            )}
            {subtext && <p className="text-gray-400 text-xs mt-1">{subtext}</p>}
          </div>
          <div className={`w-12 h-12 rounded-xl ${iconColorClasses[color]} flex items-center justify-center`}>
            <Icon className="w-6 h-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Metric Card Component
const MetricCard = ({ title, value, icon: Icon }) => (
  <Card className="bg-white/5 border-white/10">
    <CardContent className="p-4">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center">
          <Icon className="w-5 h-5 text-purple-400" />
        </div>
        <div>
          <p className="text-gray-400 text-xs">{title}</p>
          <p className="text-xl font-bold text-white">{value}</p>
        </div>
      </div>
    </CardContent>
  </Card>
);

export default SuperadminDashboard;
