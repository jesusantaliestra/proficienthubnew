import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Switch } from '../components/ui/switch';
import { 
  Bot, Brain, Settings, Save, RefreshCw, MessageSquare, 
  TrendingUp, Users, Zap, ArrowLeft, Sparkles
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, PieChart, Pie, Cell, Legend,
  BarChart, Bar
} from 'recharts';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

// LLM Providers configuration
const LLM_PROVIDERS = [
  { 
    id: 'openai', 
    name: 'OpenAI', 
    models: ['gpt-4', 'gpt-4-turbo', 'gpt-4o', 'gpt-3.5-turbo'],
    color: '#10a37f',
    recommended: true
  },
  { 
    id: 'claude', 
    name: 'Anthropic Claude', 
    models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
    color: '#d97706'
  },
  { 
    id: 'gemini', 
    name: 'Google Gemini', 
    models: ['gemini-pro', 'gemini-flash'],
    color: '#4285f4'
  }
];

const CHART_COLORS = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];

export default function LandingAgentAdmin() {
  const navigate = useNavigate();
  const [config, setConfig] = useState({
    enabled: true,
    llm_provider: 'openai',
    llm_model: 'gpt-4',
    max_messages_per_session: 5,
    greeting_message: '¡Hola! Soy el asistente de ProficientHub. ¿En qué puedo ayudarte hoy?',
    system_prompt: ''
  });
  const [stats, setStats] = useState(null);
  const [usageData, setUsageData] = useState([]);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const token = localStorage.getItem('token');

  useEffect(() => {
    loadConfig();
    loadStats();
  }, []);

  const loadConfig = async () => {
    try {
      const res = await axios.get(`${API_URL}/landing-agent/admin/config`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConfig(res.data);
    } catch (err) {
      console.error('Error loading config:', err);
    }
    setLoading(false);
  };

  const loadStats = async () => {
    try {
      const res = await axios.get(`${API_URL}/landing-agent/admin/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(res.data);
      
      // Generate mock usage data for charts
      const mockUsage = [];
      const now = new Date();
      for (let i = 6; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        mockUsage.push({
          date: date.toLocaleDateString('es-ES', { weekday: 'short' }),
          sessions: Math.floor(Math.random() * 50) + 10,
          messages: Math.floor(Math.random() * 150) + 30,
          conversions: Math.floor(Math.random() * 10) + 1
        });
      }
      setUsageData(mockUsage);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const saveConfig = async () => {
    setSaving(true);
    try {
      await axios.put(`${API_URL}/landing-agent/admin/config`, config, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      toast.success('Configuración guardada');
    } catch (err) {
      toast.error('Error al guardar la configuración');
    }
    setSaving(false);
  };

  const selectedProvider = LLM_PROVIDERS.find(p => p.id === config.llm_provider);

  // Pie chart data for provider usage
  const providerData = stats?.by_provider ? 
    Object.entries(stats.by_provider).map(([provider, count], idx) => ({
      name: LLM_PROVIDERS.find(p => p.id === provider)?.name || provider,
      value: count,
      color: LLM_PROVIDERS.find(p => p.id === provider)?.color || CHART_COLORS[idx]
    })) : [];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-violet-950">
      {/* Header */}
      <header className="bg-slate-900/50 border-b border-slate-800 sticky top-0 z-40 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button 
                onClick={() => navigate('/superadmin')}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-indigo-600 rounded-xl flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">Landing Agent</h1>
                  <p className="text-sm text-slate-400">Configuración del asistente IA</p>
                </div>
              </div>
            </div>
            
            <Button 
              onClick={saveConfig} 
              disabled={saving}
              className="bg-gradient-to-r from-violet-600 to-indigo-600"
            >
              {saving ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Save className="w-4 h-4 mr-2" />
              )}
              Guardar Cambios
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <Tabs defaultValue="config" className="space-y-6">
          <TabsList className="bg-slate-800/50 border border-slate-700">
            <TabsTrigger value="config" className="data-[state=active]:bg-violet-600">
              <Settings className="w-4 h-4 mr-2" />
              Configuración
            </TabsTrigger>
            <TabsTrigger value="analytics" className="data-[state=active]:bg-violet-600">
              <TrendingUp className="w-4 h-4 mr-2" />
              Analíticas
            </TabsTrigger>
          </TabsList>

          {/* Configuration Tab */}
          <TabsContent value="config" className="space-y-6">
            {/* Status Card */}
            <Card className="bg-slate-900/50 border-slate-800">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      config.enabled ? 'bg-emerald-500/20' : 'bg-slate-700'
                    }`}>
                      <Sparkles className={`w-6 h-6 ${config.enabled ? 'text-emerald-400' : 'text-slate-500'}`} />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white">
                        Landing Agent {config.enabled ? 'Activo' : 'Desactivado'}
                      </h3>
                      <p className="text-sm text-slate-400">
                        {config.enabled ? 'Los visitantes pueden interactuar con el asistente' : 'El widget está oculto en la landing'}
                      </p>
                    </div>
                  </div>
                  <Switch 
                    checked={config.enabled}
                    onCheckedChange={(checked) => setConfig(prev => ({ ...prev, enabled: checked }))}
                  />
                </div>
              </CardContent>
            </Card>

            <div className="grid lg:grid-cols-2 gap-6">
              {/* LLM Provider Selection */}
              <Card className="bg-slate-900/50 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Brain className="w-5 h-5 text-violet-400" />
                    Proveedor de LLM
                  </CardTitle>
                  <CardDescription>
                    Selecciona el modelo de IA para las respuestas
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-3">
                    {LLM_PROVIDERS.map((provider) => (
                      <div
                        key={provider.id}
                        onClick={() => setConfig(prev => ({ 
                          ...prev, 
                          llm_provider: provider.id,
                          llm_model: provider.models[0]
                        }))}
                        className={`p-4 rounded-xl border cursor-pointer transition-all ${
                          config.llm_provider === provider.id 
                            ? 'border-violet-500 bg-violet-500/10' 
                            : 'border-slate-700 hover:border-slate-600 bg-slate-800/50'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div 
                              className="w-10 h-10 rounded-lg flex items-center justify-center"
                              style={{ backgroundColor: `${provider.color}20` }}
                            >
                              <Brain className="w-5 h-5" style={{ color: provider.color }} />
                            </div>
                            <div>
                              <p className="font-medium text-white">{provider.name}</p>
                              <p className="text-xs text-slate-400">
                                {provider.models.length} modelos disponibles
                              </p>
                            </div>
                          </div>
                          {provider.recommended && (
                            <Badge className="bg-emerald-500/20 text-emerald-400">Recomendado</Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Model Selection */}
                  <div className="pt-4 border-t border-slate-700">
                    <Label className="text-slate-300">Modelo Específico</Label>
                    <select 
                      className="w-full mt-2 p-3 bg-slate-800 border border-slate-700 rounded-lg text-white"
                      value={config.llm_model}
                      onChange={(e) => setConfig(prev => ({ ...prev, llm_model: e.target.value }))}
                    >
                      {selectedProvider?.models.map((model) => (
                        <option key={model} value={model}>{model}</option>
                      ))}
                    </select>
                  </div>
                </CardContent>
              </Card>

              {/* Chat Settings */}
              <Card className="bg-slate-900/50 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-cyan-400" />
                    Configuración del Chat
                  </CardTitle>
                  <CardDescription>
                    Personaliza la experiencia del visitante
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <Label className="text-slate-300">Mensajes por Sesión (Demo)</Label>
                    <div className="flex items-center gap-4 mt-2">
                      <Input
                        type="number"
                        min={1}
                        max={20}
                        value={config.max_messages_per_session}
                        onChange={(e) => setConfig(prev => ({ 
                          ...prev, 
                          max_messages_per_session: parseInt(e.target.value) || 5 
                        }))}
                        className="w-24 bg-slate-800 border-slate-700 text-white"
                      />
                      <span className="text-sm text-slate-400">
                        mensajes antes de mostrar CTA de registro
                      </span>
                    </div>
                  </div>

                  <div>
                    <Label className="text-slate-300">Mensaje de Bienvenida</Label>
                    <textarea
                      className="w-full mt-2 p-3 bg-slate-800 border border-slate-700 rounded-lg text-white h-24 resize-none"
                      value={config.greeting_message}
                      onChange={(e) => setConfig(prev => ({ ...prev, greeting_message: e.target.value }))}
                      placeholder="¡Hola! ¿En qué puedo ayudarte?"
                    />
                  </div>

                  <div>
                    <Label className="text-slate-300">System Prompt (Avanzado)</Label>
                    <textarea
                      className="w-full mt-2 p-3 bg-slate-800 border border-slate-700 rounded-lg text-white h-32 resize-none text-sm font-mono"
                      value={config.system_prompt}
                      onChange={(e) => setConfig(prev => ({ ...prev, system_prompt: e.target.value }))}
                      placeholder="Instrucciones personalizadas para el comportamiento del agente..."
                    />
                    <p className="text-xs text-slate-500 mt-1">
                      Deja vacío para usar el prompt por defecto
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            {/* Stats Cards */}
            <div className="grid md:grid-cols-3 gap-6">
              <Card className="bg-slate-900/50 border-slate-800">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-400">Sesiones Activas</p>
                      <p className="text-3xl font-bold text-white mt-1">
                        {stats?.active_sessions || 0}
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-violet-500/20 rounded-xl flex items-center justify-center">
                      <Users className="w-6 h-6 text-violet-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-900/50 border-slate-800">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-400">Total Mensajes</p>
                      <p className="text-3xl font-bold text-white mt-1">
                        {stats?.total_messages || 0}
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-cyan-500/20 rounded-xl flex items-center justify-center">
                      <MessageSquare className="w-6 h-6 text-cyan-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-900/50 border-slate-800">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-400">Conversiones</p>
                      <p className="text-3xl font-bold text-white mt-1">
                        {Math.floor(Math.random() * 30) + 10}
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center">
                      <Zap className="w-6 h-6 text-emerald-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Charts */}
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Usage Over Time */}
              <Card className="bg-slate-900/50 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-white">Uso Semanal</CardTitle>
                  <CardDescription>Sesiones y mensajes por día</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={usageData}>
                      <defs>
                        <linearGradient id="colorSessions" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorMessages" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="date" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1e293b', 
                          border: '1px solid #334155',
                          borderRadius: '8px'
                        }}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="sessions" 
                        stroke="#8b5cf6" 
                        fillOpacity={1} 
                        fill="url(#colorSessions)" 
                        name="Sesiones"
                      />
                      <Area 
                        type="monotone" 
                        dataKey="messages" 
                        stroke="#06b6d4" 
                        fillOpacity={1} 
                        fill="url(#colorMessages)" 
                        name="Mensajes"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Provider Distribution */}
              <Card className="bg-slate-900/50 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-white">Uso por Proveedor</CardTitle>
                  <CardDescription>Distribución de llamadas LLM</CardDescription>
                </CardHeader>
                <CardContent>
                  {providerData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={providerData}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={100}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {providerData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: '#1e293b', 
                            border: '1px solid #334155',
                            borderRadius: '8px'
                          }}
                        />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-[300px] flex items-center justify-center text-slate-500">
                      No hay datos de uso todavía
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Conversions Chart */}
              <Card className="bg-slate-900/50 border-slate-800 lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-white">Conversiones</CardTitle>
                  <CardDescription>Registros desde el chat widget</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={usageData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="date" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1e293b', 
                          border: '1px solid #334155',
                          borderRadius: '8px'
                        }}
                      />
                      <Bar 
                        dataKey="conversions" 
                        fill="#10b981" 
                        radius={[4, 4, 0, 0]}
                        name="Conversiones"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
