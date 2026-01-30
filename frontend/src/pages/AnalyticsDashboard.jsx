import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { 
  TrendingUp, TrendingDown, Users, DollarSign, Target, Activity,
  BarChart3, PieChart, LineChart, Download, RefreshCw, Calendar,
  AlertTriangle, CheckCircle, Clock, Zap
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function AnalyticsDashboard() {
  const [activeTab, setActiveTab] = useState('executive');
  const [period, setPeriod] = useState('month');
  const [loading, setLoading] = useState(true);
  const [executiveData, setExecutiveData] = useState(null);
  const [revenueData, setRevenueData] = useState(null);
  const [leadSourceData, setLeadSourceData] = useState(null);
  const [engagementData, setEngagementData] = useState(null);
  const [velocityData, setVelocityData] = useState(null);
  const [cohortData, setCohortData] = useState(null);

  const token = localStorage.getItem('token');

  const fetchData = async (endpoint) => {
    const res = await fetch(`${API_URL}/api/analytics-dashboard/${endpoint}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Failed to fetch');
    return res.json();
  };

  useEffect(() => {
    loadAllData();
  }, [period]);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [exec, rev, leads, engage, vel, cohort] = await Promise.all([
        fetchData(`executive-summary?period=${period}`),
        fetchData('revenue'),
        fetchData('lead-sources'),
        fetchData('student-engagement'),
        fetchData('pipeline-velocity'),
        fetchData('cohort-analysis')
      ]);
      setExecutiveData(exec);
      setRevenueData(rev);
      setLeadSourceData(leads);
      setEngagementData(engage);
      setVelocityData(vel);
      setCohortData(cohort);
    } catch (err) {
      console.error('Error loading analytics:', err);
    }
    setLoading(false);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(value);
  };

  const KPICard = ({ title, value, change, trend, icon: Icon, subtitle }) => (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <h3 className="text-2xl font-bold mt-1">{value}</h3>
            {change !== undefined && (
              <div className="flex items-center mt-2">
                {trend === 'up' ? (
                  <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
                )}
                <span className={`text-sm ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                  {change > 0 ? '+' : ''}{change}%
                </span>
                <span className="text-gray-400 text-sm ml-1">vs prev</span>
              </div>
            )}
            {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
          </div>
          <div className="p-3 bg-indigo-100 rounded-full">
            <Icon className="w-6 h-6 text-indigo-600" />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const ProgressBar = ({ label, value, max, color = 'bg-indigo-600' }) => (
    <div className="mb-4">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium">{value} / {max}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`${color} rounded-full h-2 transition-all duration-500`}
          style={{ width: `${Math.min((value / max) * 100, 100)}%` }}
        />
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-indigo-600 mx-auto mb-4" />
          <p className="text-gray-600">Cargando analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8" data-testid="analytics-dashboard">
      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-500 mt-1">Métricas avanzadas y pronósticos para tu institución</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex bg-white rounded-lg p-1 shadow-sm">
              {['week', 'month', 'quarter', 'year'].map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                    period === p 
                      ? 'bg-indigo-600 text-white' 
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {p === 'week' ? 'Semana' : p === 'month' ? 'Mes' : p === 'quarter' ? 'Trimestre' : 'Año'}
                </button>
              ))}
            </div>
            <Button variant="outline" size="sm" onClick={loadAllData}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Actualizar
            </Button>
          </div>
        </div>
      </div>

      {/* Executive Summary KPIs */}
      {executiveData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <KPICard
            title="Total Estudiantes"
            value={executiveData.kpis.total_students.value}
            change={executiveData.kpis.total_students.change}
            trend={executiveData.kpis.total_students.trend}
            icon={Users}
          />
          <KPICard
            title="Ingresos"
            value={formatCurrency(executiveData.kpis.revenue.value)}
            change={executiveData.kpis.revenue.change}
            trend={executiveData.kpis.revenue.trend}
            icon={DollarSign}
          />
          <KPICard
            title="Total Leads"
            value={executiveData.kpis.total_leads.value}
            change={executiveData.kpis.total_leads.change}
            trend={executiveData.kpis.total_leads.trend}
            icon={Target}
          />
          <KPICard
            title="Tasa de Conversión"
            value={`${executiveData.kpis.conversion_rate.value}%`}
            icon={Activity}
            subtitle="Leads a clientes"
          />
        </div>
      )}

      {/* Quick Insights */}
      {executiveData && (
        <Card className="mb-8 bg-gradient-to-r from-indigo-500 to-purple-600 text-white">
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <Zap className="w-5 h-5 mr-2" />
              Insights Rápidos
            </h3>
            <div className="grid md:grid-cols-3 gap-4">
              {executiveData.quick_insights.map((insight, i) => (
                <div key={i} className="flex items-start">
                  <CheckCircle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm opacity-90">{insight}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabs for Detailed Analytics */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="bg-white p-1 shadow-sm">
          <TabsTrigger value="executive" className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Resumen
          </TabsTrigger>
          <TabsTrigger value="revenue" className="flex items-center gap-2">
            <LineChart className="w-4 h-4" />
            Ingresos
          </TabsTrigger>
          <TabsTrigger value="leads" className="flex items-center gap-2">
            <PieChart className="w-4 h-4" />
            Fuentes
          </TabsTrigger>
          <TabsTrigger value="engagement" className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            Engagement
          </TabsTrigger>
          <TabsTrigger value="pipeline" className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Pipeline
          </TabsTrigger>
        </TabsList>

        {/* Revenue Tab */}
        <TabsContent value="revenue">
          {revenueData && (
            <div className="grid lg:grid-cols-3 gap-6">
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle>Ingresos Mensuales</CardTitle>
                  <CardDescription>Evolución de ingresos y deals cerrados</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {revenueData.monthly_breakdown.slice(-6).map((month) => (
                      <div key={month.month} className="flex items-center gap-4">
                        <span className="w-20 text-sm text-gray-500">{month.month}</span>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-gray-100 rounded-full h-4">
                              <div 
                                className="bg-green-500 rounded-full h-4"
                                style={{ 
                                  width: `${Math.min(
                                    (month.revenue / Math.max(...revenueData.monthly_breakdown.map(m => m.revenue || 1))) * 100, 
                                    100
                                  )}%` 
                                }}
                              />
                            </div>
                            <span className="text-sm font-medium w-24 text-right">
                              {formatCurrency(month.revenue)}
                            </span>
                          </div>
                        </div>
                        <Badge variant={month.deals_won > 0 ? 'default' : 'secondary'}>
                          {month.deals_won} deals
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Resumen</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Ingresos Totales</span>
                      <span className="font-bold">{formatCurrency(revenueData.summary.total_revenue)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Deals Ganados</span>
                      <span className="font-bold text-green-600">{revenueData.summary.total_deals_won}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Deals Perdidos</span>
                      <span className="font-bold text-red-600">{revenueData.summary.total_deals_lost}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Promedio por Deal</span>
                      <span className="font-bold">{formatCurrency(revenueData.summary.avg_deal_size)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Win Rate</span>
                      <span className="font-bold text-indigo-600">{revenueData.summary.win_rate}%</span>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-blue-50 border-blue-200">
                  <CardHeader>
                    <CardTitle className="text-lg text-blue-800">Pronóstico</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {revenueData.forecast.map((f) => (
                      <div key={f.month} className="flex justify-between py-2 border-b border-blue-100 last:border-0">
                        <span className="text-blue-700">{f.month}</span>
                        <div className="text-right">
                          <span className="font-bold text-blue-800">{formatCurrency(f.predicted_revenue)}</span>
                          <span className="text-xs text-blue-500 ml-2">({Math.round(f.confidence * 100)}%)</span>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </TabsContent>

        {/* Lead Sources Tab */}
        <TabsContent value="leads">
          {leadSourceData && (
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Rendimiento por Fuente</CardTitle>
                  <CardDescription>Comparación de conversión y valor por fuente de leads</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {leadSourceData.sources.map((source) => (
                      <div key={source.source} className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="font-medium">{source.label}</span>
                          <div className="flex items-center gap-2">
                            <Badge variant={source.conversion_rate >= 20 ? 'default' : 'secondary'}>
                              {source.conversion_rate}% conv.
                            </Badge>
                            <span className="text-sm text-gray-500">{source.leads} leads</span>
                          </div>
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-sm">
                          <div className="bg-green-50 p-2 rounded text-center">
                            <div className="font-bold text-green-700">{source.won}</div>
                            <div className="text-green-600 text-xs">Ganados</div>
                          </div>
                          <div className="bg-yellow-50 p-2 rounded text-center">
                            <div className="font-bold text-yellow-700">{source.in_pipeline}</div>
                            <div className="text-yellow-600 text-xs">En Pipeline</div>
                          </div>
                          <div className="bg-red-50 p-2 rounded text-center">
                            <div className="font-bold text-red-700">{source.lost}</div>
                            <div className="text-red-600 text-xs">Perdidos</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recomendaciones</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {leadSourceData.recommendations.filter(Boolean).map((rec, i) => (
                      <div key={i} className="flex items-start gap-3 p-3 bg-indigo-50 rounded-lg">
                        <div className="p-1 bg-indigo-100 rounded">
                          <Zap className="w-4 h-4 text-indigo-600" />
                        </div>
                        <p className="text-sm text-indigo-800">{rec}</p>
                      </div>
                    ))}
                  </div>

                  {leadSourceData.top_performing && (
                    <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                      <h4 className="font-medium text-green-800 mb-2">Mejor Fuente</h4>
                      <p className="text-2xl font-bold text-green-700">
                        {leadSourceData.top_performing.replace('_', ' ').toUpperCase()}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* Engagement Tab */}
        <TabsContent value="engagement">
          {engagementData && (
            <div className="grid lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full" />
                    Activos ({engagementData.categories.active.count})
                  </CardTitle>
                  <CardDescription>{engagementData.categories.active.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {engagementData.categories.active.students.slice(0, 5).map((s) => (
                      <div key={s.id} className="flex justify-between items-center p-2 bg-green-50 rounded">
                        <div>
                          <p className="font-medium text-sm">{s.name}</p>
                          <p className="text-xs text-gray-500">{s.recent_attempts} intentos recientes</p>
                        </div>
                        <Badge className="bg-green-100 text-green-700">{s.avg_score}%</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                    En Riesgo ({engagementData.categories.at_risk.count})
                  </CardTitle>
                  <CardDescription>{engagementData.categories.at_risk.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {engagementData.categories.at_risk.students.slice(0, 5).map((s) => (
                      <div key={s.id} className="flex justify-between items-center p-2 bg-yellow-50 rounded">
                        <div>
                          <p className="font-medium text-sm">{s.name}</p>
                          <p className="text-xs text-gray-500">{s.recent_attempts} intentos</p>
                        </div>
                        <AlertTriangle className="w-4 h-4 text-yellow-600" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full" />
                    Inactivos ({engagementData.categories.inactive.count})
                  </CardTitle>
                  <CardDescription>{engagementData.categories.inactive.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {engagementData.categories.inactive.students.slice(0, 5).map((s) => (
                      <div key={s.id} className="flex justify-between items-center p-2 bg-red-50 rounded">
                        <div>
                          <p className="font-medium text-sm">{s.name}</p>
                          <p className="text-xs text-gray-500">Sin actividad reciente</p>
                        </div>
                        <Button size="sm" variant="outline" className="h-7 text-xs">
                          Re-enganchar
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="lg:col-span-3">
                <CardHeader>
                  <CardTitle>Recomendaciones de Engagement</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-3 gap-4">
                    {engagementData.recommendations.map((rec, i) => (
                      <div key={i} className="p-4 border rounded-lg hover:border-indigo-300 transition-colors">
                        <p className="text-sm">{rec}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* Pipeline Velocity Tab */}
        <TabsContent value="pipeline">
          {velocityData && (
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Velocidad del Pipeline</CardTitle>
                  <CardDescription>Tiempo promedio para cerrar deals</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div className="text-center p-6 bg-indigo-50 rounded-xl">
                      <p className="text-gray-500 mb-2">Ciclo Promedio de Venta</p>
                      <p className="text-5xl font-bold text-indigo-600">
                        {velocityData.velocity.total_cycle.avg_days}
                      </p>
                      <p className="text-gray-500">días</p>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div className="p-3 bg-green-50 rounded-lg">
                        <p className="text-2xl font-bold text-green-600">
                          {velocityData.velocity.total_cycle.min_days}
                        </p>
                        <p className="text-xs text-gray-500">Más rápido</p>
                      </div>
                      <div className="p-3 bg-yellow-50 rounded-lg">
                        <p className="text-2xl font-bold text-yellow-600">
                          {velocityData.benchmarks.ideal_cycle_days}
                        </p>
                        <p className="text-xs text-gray-500">Ideal</p>
                      </div>
                      <div className="p-3 bg-red-50 rounded-lg">
                        <p className="text-2xl font-bold text-red-600">
                          {velocityData.velocity.total_cycle.max_days}
                        </p>
                        <p className="text-xs text-gray-500">Más lento</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Salud del Pipeline</CardTitle>
                  <CardDescription>Leads estancados que requieren atención</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="mb-6">
                    <ProgressBar 
                      label="Leads Activos"
                      value={velocityData.pipeline_health.total_in_pipeline - velocityData.pipeline_health.stale_leads}
                      max={velocityData.pipeline_health.total_in_pipeline}
                      color="bg-green-500"
                    />
                    <ProgressBar 
                      label="Leads Estancados (14+ días)"
                      value={velocityData.pipeline_health.stale_leads}
                      max={velocityData.pipeline_health.total_in_pipeline}
                      color="bg-red-500"
                    />
                  </div>

                  {velocityData.stale_leads.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-3 text-red-700">Requieren Atención Inmediata</h4>
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {velocityData.stale_leads.map((lead) => (
                          <div key={lead.id} className="flex justify-between items-center p-2 bg-red-50 rounded text-sm">
                            <div>
                              <p className="font-medium">{lead.name}</p>
                              <p className="text-xs text-gray-500">{lead.stage}</p>
                            </div>
                            <Badge variant="destructive">{lead.days_stale} días</Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* Executive Summary Tab */}
        <TabsContent value="executive">
          <div className="grid lg:grid-cols-2 gap-6">
            {cohortData && (
              <Card>
                <CardHeader>
                  <CardTitle>Análisis de Cohortes</CardTitle>
                  <CardDescription>Rendimiento de estudiantes por mes de inscripción</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {cohortData.cohorts.slice(-6).map((cohort) => (
                      <div key={cohort.cohort} className="flex items-center gap-4">
                        <span className="w-20 text-sm font-medium">{cohort.cohort}</span>
                        <div className="flex-1 flex items-center gap-2">
                          <Badge variant="outline">{cohort.enrolled} est.</Badge>
                          <Badge className="bg-indigo-100 text-indigo-700">{cohort.avg_score}% prom</Badge>
                          <span className="text-xs text-gray-400">
                            {cohort.exams_per_student} exámenes/est
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {cohortData.insights.best_performing_cohort && (
                    <div className="mt-4 p-3 bg-green-50 rounded-lg">
                      <p className="text-sm text-green-700">
                        Mejor cohorte: <strong>{cohortData.insights.best_performing_cohort}</strong>
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader>
                <CardTitle>Exportar Reportes</CardTitle>
                <CardDescription>Descarga reportes detallados</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-3">
                  {['executive', 'revenue', 'leads', 'students'].map((type) => (
                    <Button
                      key={type}
                      variant="outline"
                      className="justify-start"
                      onClick={() => window.open(`${API_URL}/api/analytics-dashboard/export/${type}?format=json`, '_blank')}
                    >
                      <Download className="w-4 h-4 mr-2" />
                      {type === 'executive' ? 'Resumen Ejecutivo' : 
                       type === 'revenue' ? 'Ingresos' :
                       type === 'leads' ? 'Lead Sources' : 'Estudiantes'}
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
