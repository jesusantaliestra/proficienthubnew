import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { 
  ArrowLeft, TrendingUp, Users, MessageSquare, DollarSign, 
  Target, BarChart3, Activity, Filter, RefreshCw, Eye,
  MousePointer, ShoppingCart, CheckCircle, Clock, Percent
} from 'lucide-react';
import {
  BarChart, Bar, LineChart, Line, FunnelChart, Funnel, LabelList,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  AreaChart, Area, Cell, PieChart, Pie
} from 'recharts';
import axios from 'axios';
import { toast } from 'sonner';
import LanguageSelector from '../components/LanguageSelector';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Funnel stage colors
const STAGE_COLORS = [
  '#8b5cf6', '#7c3aed', '#6d28d9', '#5b21b6', '#4c1d95',
  '#4338ca', '#3730a3', '#312e81', '#1e3a8a', '#1e40af'
];

const STAGE_ICONS = {
  landing_visit: Eye,
  chat_widget_opened: MessageSquare,
  chat_interaction: MousePointer,
  demo_requested: Target,
  demo_activated: CheckCircle,
  demo_engaged: Activity,
  pricing_viewed: DollarSign,
  checkout_started: ShoppingCart,
  payment_completed: CheckCircle,
  converted_to_customer: Users
};

export default function ConversionAnalyticsDashboard() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('30');
  const [funnelData, setFunnelData] = useState(null);
  const [trends, setTrends] = useState(null);
  const [demoAnalytics, setDemoAnalytics] = useState(null);
  const [chatMetrics, setChatMetrics] = useState(null);
  
  const token = localStorage.getItem('token');

  useEffect(() => {
    loadAllData();
  }, [period]);

  const loadAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadFunnelData(),
        loadTrends(),
        loadDemoAnalytics(),
        loadChatMetrics()
      ]);
    } catch (err) {
      console.error('Error loading analytics:', err);
      toast.error('Error al cargar analíticas');
    }
    setLoading(false);
  };

  const loadFunnelData = async () => {
    const res = await axios.get(
      `${API_URL}/api/conversion-analytics/funnel?days=${period}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setFunnelData(res.data);
  };

  const loadTrends = async () => {
    const res = await axios.get(
      `${API_URL}/api/conversion-analytics/trends?days=${period}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setTrends(res.data);
  };

  const loadDemoAnalytics = async () => {
    const res = await axios.get(
      `${API_URL}/api/conversion-analytics/demo-analytics?days=${period}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setDemoAnalytics(res.data);
  };

  const loadChatMetrics = async () => {
    const res = await axios.get(
      `${API_URL}/api/conversion-analytics/chat-widget-metrics?days=${period}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setChatMetrics(res.data);
  };

  // Prepare funnel chart data
  const funnelChartData = funnelData?.funnel?.map((stage, index) => ({
    name: stage.label,
    value: stage.count,
    conversion: stage.conversion_rate,
    stepConversion: stage.step_conversion,
    fill: STAGE_COLORS[index % STAGE_COLORS.length]
  })) || [];

  // Prepare area chart data for trends
  const trendChartData = trends?.trends?.map(day => ({
    date: day.date?.slice(5) || '',
    visits: day.landing_visit || 0,
    demos: day.demo_requested || 0,
    conversions: day.converted_to_customer || 0
  })) || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-violet-950/20 to-slate-950">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur-xl border-b border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => navigate('/superadmin/demo-management')}
                className="text-slate-400 hover:text-white"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Volver
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                  <BarChart3 className="w-6 h-6 text-violet-400" />
                  Conversion Analytics
                </h1>
                <p className="text-slate-400 text-sm">Funnel de conversión y métricas de engagement</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Select value={period} onValueChange={setPeriod}>
                <SelectTrigger className="w-[140px] bg-slate-800 border-slate-700 text-white">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700">
                  <SelectItem value="7">7 días</SelectItem>
                  <SelectItem value="14">14 días</SelectItem>
                  <SelectItem value="30">30 días</SelectItem>
                  <SelectItem value="60">60 días</SelectItem>
                  <SelectItem value="90">90 días</SelectItem>
                </SelectContent>
              </Select>
              <Button
                variant="outline"
                size="sm"
                onClick={loadAllData}
                className="border-slate-700 text-slate-300"
                disabled={loading}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Actualizar
              </Button>
              <LanguageSelector variant="compact" />
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {/* Total Visits */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Visitas Totales</p>
                  <p className="text-3xl font-bold text-white mt-1">
                    {funnelData?.total_visits?.toLocaleString() || 0}
                  </p>
                  <p className="text-slate-500 text-xs mt-1">Últimos {period} días</p>
                </div>
                <div className="w-12 h-12 rounded-xl bg-violet-500/20 flex items-center justify-center">
                  <Eye className="w-6 h-6 text-violet-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Demo Requests */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Demos Solicitados</p>
                  <p className="text-3xl font-bold text-white mt-1">
                    {demoAnalytics?.total_demos?.toLocaleString() || 0}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge className="bg-emerald-500/20 text-emerald-400 text-xs">
                      {demoAnalytics?.active_demos || 0} activos
                    </Badge>
                  </div>
                </div>
                <div className="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center">
                  <Target className="w-6 h-6 text-amber-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Conversion Rate */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Tasa de Conversión</p>
                  <p className="text-3xl font-bold text-white mt-1">
                    {funnelData?.overall_conversion || 0}%
                  </p>
                  <p className="text-slate-500 text-xs mt-1">Visita → Cliente</p>
                </div>
                <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                  <Percent className="w-6 h-6 text-emerald-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Chat Engagement */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Chat Engagement</p>
                  <p className="text-3xl font-bold text-white mt-1">
                    {chatMetrics?.engagement_rate || 0}%
                  </p>
                  <p className="text-slate-500 text-xs mt-1">
                    {chatMetrics?.total_messages || 0} mensajes
                  </p>
                </div>
                <div className="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center">
                  <MessageSquare className="w-6 h-6 text-cyan-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Funnel Chart */}
        <Card className="bg-slate-900/50 border-slate-800 mb-8">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-violet-400" />
              Funnel de Conversión
            </CardTitle>
            <CardDescription className="text-slate-400">
              10 etapas del proceso de conversión
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={funnelChartData}
                  layout="vertical"
                  margin={{ top: 20, right: 30, left: 120, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis type="number" stroke="#94a3b8" />
                  <YAxis 
                    dataKey="name" 
                    type="category" 
                    stroke="#94a3b8"
                    width={110}
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      border: '1px solid #334155',
                      borderRadius: '8px'
                    }}
                    formatter={(value, name, props) => [
                      <span key="value">
                        {value.toLocaleString()} ({props.payload.conversion}%)
                      </span>,
                      'Cantidad'
                    ]}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {funnelChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                    <LabelList 
                      dataKey="stepConversion" 
                      position="right" 
                      formatter={(val) => `${val}%`}
                      fill="#94a3b8"
                      fontSize={11}
                    />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            {/* Funnel Stage Details */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-6 pt-6 border-t border-slate-800">
              {funnelData?.funnel?.slice(0, 5).map((stage, index) => {
                const Icon = STAGE_ICONS[stage.stage] || Activity;
                return (
                  <div 
                    key={stage.stage}
                    className="p-3 rounded-lg bg-slate-800/50 border border-slate-700"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <Icon className="w-4 h-4" style={{ color: STAGE_COLORS[index] }} />
                      <span className="text-xs text-slate-400">{stage.label}</span>
                    </div>
                    <p className="text-xl font-bold text-white">{stage.count.toLocaleString()}</p>
                    <p className="text-xs text-slate-500">{stage.conversion_rate}% del total</p>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Trends Chart */}
        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Activity className="w-5 h-5 text-cyan-400" />
                Tendencia Diaria
              </CardTitle>
              <CardDescription className="text-slate-400">
                Visitas, demos y conversiones por día
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendChartData}>
                    <defs>
                      <linearGradient id="colorVisits" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorDemos" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorConversions" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} />
                    <YAxis stroke="#94a3b8" fontSize={11} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1e293b',
                        border: '1px solid #334155',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="visits"
                      name="Visitas"
                      stroke="#8b5cf6"
                      fillOpacity={1}
                      fill="url(#colorVisits)"
                    />
                    <Area
                      type="monotone"
                      dataKey="demos"
                      name="Demos"
                      stroke="#f59e0b"
                      fillOpacity={1}
                      fill="url(#colorDemos)"
                    />
                    <Area
                      type="monotone"
                      dataKey="conversions"
                      name="Conversiones"
                      stroke="#10b981"
                      fillOpacity={1}
                      fill="url(#colorConversions)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Demo Analytics */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-amber-400" />
                Analíticas de Demos
              </CardTitle>
              <CardDescription className="text-slate-400">
                Rendimiento del programa de demos
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Demo Stats */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
                    <p className="text-slate-400 text-sm">Tasa Demo→Cliente</p>
                    <p className="text-2xl font-bold text-emerald-400">
                      {demoAnalytics?.conversion_rate || 0}%
                    </p>
                  </div>
                  <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
                    <p className="text-slate-400 text-sm">Engagement Promedio</p>
                    <p className="text-2xl font-bold text-cyan-400">
                      {demoAnalytics?.avg_engagement_events || 0}
                    </p>
                    <p className="text-slate-500 text-xs">eventos/demo</p>
                  </div>
                </div>

                {/* Demo Status Breakdown */}
                <div className="p-4 rounded-lg bg-slate-800/30 border border-slate-700">
                  <h4 className="text-white font-medium mb-3">Estado de Demos</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Activos</span>
                      <Badge className="bg-emerald-500/20 text-emerald-400">
                        {demoAnalytics?.active_demos || 0}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Convertidos</span>
                      <Badge className="bg-violet-500/20 text-violet-400">
                        {demoAnalytics?.converted_demos || 0}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Expirados</span>
                      <Badge className="bg-slate-500/20 text-slate-400">
                        {demoAnalytics?.expired_demos || 0}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Chat Widget Stats */}
                <div className="p-4 rounded-lg bg-cyan-900/20 border border-cyan-800/30">
                  <h4 className="text-cyan-300 font-medium mb-3 flex items-center gap-2">
                    <MessageSquare className="w-4 h-4" />
                    Chat Widget
                  </h4>
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div>
                      <p className="text-xl font-bold text-white">{chatMetrics?.chat_opened || 0}</p>
                      <p className="text-xs text-slate-400">Abiertos</p>
                    </div>
                    <div>
                      <p className="text-xl font-bold text-white">{chatMetrics?.unique_sessions || 0}</p>
                      <p className="text-xs text-slate-400">Sesiones</p>
                    </div>
                    <div>
                      <p className="text-xl font-bold text-white">{chatMetrics?.avg_messages_per_session || 0}</p>
                      <p className="text-xs text-slate-400">Msgs/Sesión</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Stage Details Table */}
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">Detalle por Etapa</CardTitle>
            <CardDescription className="text-slate-400">
              Métricas detalladas de cada etapa del funnel
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">#</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Etapa</th>
                    <th className="text-right py-3 px-4 text-slate-400 font-medium">Cantidad</th>
                    <th className="text-right py-3 px-4 text-slate-400 font-medium">% del Total</th>
                    <th className="text-right py-3 px-4 text-slate-400 font-medium">Conversión Etapa</th>
                  </tr>
                </thead>
                <tbody>
                  {funnelData?.funnel?.map((stage, index) => {
                    const Icon = STAGE_ICONS[stage.stage] || Activity;
                    return (
                      <tr key={stage.stage} className="border-b border-slate-800 hover:bg-slate-800/30">
                        <td className="py-3 px-4">
                          <div 
                            className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                            style={{ backgroundColor: STAGE_COLORS[index], color: 'white' }}
                          >
                            {index + 1}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <Icon className="w-4 h-4 text-slate-400" />
                            <span className="text-white">{stage.label}</span>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-right text-white font-medium">
                          {stage.count.toLocaleString()}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <Badge variant="outline" className="border-slate-600 text-slate-300">
                            {stage.conversion_rate}%
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <Badge 
                            className={
                              stage.step_conversion >= 80 ? 'bg-emerald-500/20 text-emerald-400' :
                              stage.step_conversion >= 50 ? 'bg-amber-500/20 text-amber-400' :
                              stage.step_conversion >= 20 ? 'bg-orange-500/20 text-orange-400' :
                              'bg-red-500/20 text-red-400'
                            }
                          >
                            {stage.step_conversion}%
                          </Badge>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
