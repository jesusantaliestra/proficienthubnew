import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  Gift, Users, Clock, TrendingUp, ArrowLeft, RefreshCw, 
  Calendar, CheckCircle, XCircle, Plus, Play, Settings,
  Video, Sparkles, Globe, Mic, BarChart3
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, BarChart, Bar, FunnelChart, Funnel, 
  LabelList, PieChart, Pie, Cell
} from 'recharts';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;
const CHART_COLORS = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];

export default function DemoManagement() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('demos');
  const [demos, setDemos] = useState([]);
  const [demoConfig, setDemoConfig] = useState(null);
  const [funnelData, setFunnelData] = useState(null);
  const [demoAnalytics, setDemoAnalytics] = useState(null);
  const [heygenConfig, setHeygenConfig] = useState(null);
  const [avatars, setAvatars] = useState([]);
  const [voices, setVoices] = useState([]);
  const [tutorials, setTutorials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [extending, setExtending] = useState(null);
  const [extensionDays, setExtensionDays] = useState(7);
  
  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    await Promise.all([
      loadDemos(),
      loadDemoConfig(),
      loadFunnelData(),
      loadDemoAnalytics(),
      loadHeygenConfig(),
      loadTutorials()
    ]);
    setLoading(false);
  };

  const loadDemos = async () => {
    try {
      const res = await axios.get(`${API_URL}/demo/admin/list`, { headers });
      setDemos(res.data.demos || []);
    } catch (err) {
      console.error('Error loading demos:', err);
    }
  };

  const loadDemoConfig = async () => {
    try {
      const res = await axios.get(`${API_URL}/demo/admin/config`, { headers });
      setDemoConfig(res.data);
    } catch (err) {
      console.error('Error loading demo config:', err);
    }
  };

  const loadFunnelData = async () => {
    try {
      const res = await axios.get(`${API_URL}/conversion-analytics/funnel?days=30`, { headers });
      setFunnelData(res.data);
    } catch (err) {
      console.error('Error loading funnel:', err);
    }
  };

  const loadDemoAnalytics = async () => {
    try {
      const res = await axios.get(`${API_URL}/conversion-analytics/demo-analytics?days=30`, { headers });
      setDemoAnalytics(res.data);
    } catch (err) {
      console.error('Error loading analytics:', err);
    }
  };

  const loadHeygenConfig = async () => {
    try {
      const res = await axios.get(`${API_URL}/heygen/admin/config`, { headers });
      setHeygenConfig(res.data);
    } catch (err) {
      console.error('Error loading HeyGen config:', err);
    }
  };

  const loadTutorials = async () => {
    try {
      const res = await axios.get(`${API_URL}/heygen/tutorials`, { headers });
      setTutorials(res.data.videos || []);
    } catch (err) {
      console.error('Error loading tutorials:', err);
    }
  };

  const loadAvatars = async () => {
    try {
      const res = await axios.get(`${API_URL}/heygen/admin/avatars`, { headers });
      setAvatars(res.data.avatars || []);
    } catch (err) {
      toast.error('Error cargando avatares');
    }
  };

  const loadVoices = async () => {
    try {
      const res = await axios.get(`${API_URL}/heygen/admin/voices`, { headers });
      setVoices(res.data.voices || []);
    } catch (err) {
      toast.error('Error cargando voces');
    }
  };

  const extendDemo = async (demoId) => {
    setExtending(demoId);
    try {
      await axios.post(`${API_URL}/demo/extend`, {
        institution_id: demoId,
        additional_days: extensionDays
      }, { headers });
      toast.success(`Demo extendida ${extensionDays} días`);
      loadDemos();
    } catch (err) {
      toast.error('Error al extender demo');
    }
    setExtending(null);
  };

  const convertDemo = async (demoId) => {
    try {
      await axios.post(`${API_URL}/demo/admin/convert/${demoId}`, {}, { headers });
      toast.success('Demo convertida a cliente');
      loadDemos();
      loadDemoAnalytics();
    } catch (err) {
      toast.error('Error al convertir demo');
    }
  };

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
                <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center">
                  <Gift className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">Demo & Tutoriales Premium</h1>
                  <p className="text-sm text-slate-400">Gestión de demos y videos HeyGen</p>
                </div>
              </div>
            </div>
            
            <Button onClick={loadAllData} variant="outline" className="border-slate-700">
              <RefreshCw className="w-4 h-4 mr-2" />
              Actualizar
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-slate-800/50 border border-slate-700">
            <TabsTrigger value="demos" className="data-[state=active]:bg-emerald-600">
              <Gift className="w-4 h-4 mr-2" />
              Demos Activas
            </TabsTrigger>
            <TabsTrigger value="funnel" className="data-[state=active]:bg-emerald-600">
              <TrendingUp className="w-4 h-4 mr-2" />
              Conversión
            </TabsTrigger>
            <TabsTrigger value="heygen" className="data-[state=active]:bg-emerald-600">
              <Video className="w-4 h-4 mr-2" />
              HeyGen
            </TabsTrigger>
            <TabsTrigger value="config" className="data-[state=active]:bg-emerald-600">
              <Settings className="w-4 h-4 mr-2" />
              Configuración
            </TabsTrigger>
          </TabsList>

          {/* Demos Tab */}
          <TabsContent value="demos" className="space-y-6">
            {/* Stats */}
            {demoAnalytics && (
              <div className="grid md:grid-cols-4 gap-4">
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-slate-400">Demos Activas</p>
                        <p className="text-2xl font-bold text-white">{demoAnalytics.active_demos}</p>
                      </div>
                      <Gift className="w-8 h-8 text-emerald-400" />
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-slate-400">Convertidas</p>
                        <p className="text-2xl font-bold text-white">{demoAnalytics.converted_demos}</p>
                      </div>
                      <CheckCircle className="w-8 h-8 text-green-400" />
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-slate-400">Expiradas</p>
                        <p className="text-2xl font-bold text-white">{demoAnalytics.expired_demos}</p>
                      </div>
                      <XCircle className="w-8 h-8 text-red-400" />
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-slate-400">Tasa Conversión</p>
                        <p className="text-2xl font-bold text-emerald-400">{demoAnalytics.conversion_rate}%</p>
                      </div>
                      <TrendingUp className="w-8 h-8 text-violet-400" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Demo List */}
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle className="text-white">Demos Registradas</CardTitle>
                <CardDescription>Gestiona las demos activas y extiende su duración</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {demos.length === 0 ? (
                    <p className="text-center text-slate-500 py-8">No hay demos registradas</p>
                  ) : (
                    demos.map((demo) => (
                      <div 
                        key={demo.demo_id}
                        className={`p-4 rounded-xl border ${
                          demo.is_expired 
                            ? 'bg-red-900/20 border-red-800' 
                            : demo.status === 'converted'
                            ? 'bg-green-900/20 border-green-800'
                            : 'bg-slate-800/50 border-slate-700'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h4 className="font-bold text-white">{demo.institution_name}</h4>
                              <Badge className={
                                demo.is_expired ? 'bg-red-500' :
                                demo.status === 'converted' ? 'bg-green-500' :
                                'bg-emerald-500'
                              }>
                                {demo.is_expired ? 'Expirada' : 
                                 demo.status === 'converted' ? 'Convertida' : 
                                 `${demo.remaining_days} días restantes`}
                              </Badge>
                            </div>
                            <p className="text-sm text-slate-400">{demo.contact_email}</p>
                            <p className="text-xs text-slate-500 mt-1">
                              ID: {demo.demo_id} • Estudiantes: {demo.num_students} • 
                              Extensiones: {demo.extended_count || 0}
                            </p>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            {demo.status !== 'converted' && (
                              <>
                                <div className="flex items-center gap-2">
                                  <Input 
                                    type="number"
                                    value={extensionDays}
                                    onChange={(e) => setExtensionDays(parseInt(e.target.value) || 7)}
                                    className="w-16 bg-slate-800 border-slate-700 text-white text-center"
                                    min={1}
                                    max={30}
                                  />
                                  <Button 
                                    size="sm"
                                    onClick={() => extendDemo(demo.demo_id)}
                                    disabled={extending === demo.demo_id}
                                    className="bg-blue-600 hover:bg-blue-700"
                                  >
                                    <Plus className="w-4 h-4 mr-1" />
                                    Extender
                                  </Button>
                                </div>
                                <Button 
                                  size="sm"
                                  onClick={() => convertDemo(demo.demo_id)}
                                  className="bg-emerald-600 hover:bg-emerald-700"
                                >
                                  <CheckCircle className="w-4 h-4 mr-1" />
                                  Convertir
                                </Button>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Funnel Tab */}
          {/* Conversion Funnel Tab */}
          <TabsContent value="funnel" className="space-y-6">
            {funnelData && (
              <>
                {/* Link to Full Analytics Dashboard */}
                <div className="flex justify-end">
                  <Button
                    onClick={() => navigate('/superadmin/conversion-analytics')}
                    className="bg-gradient-to-r from-violet-600 to-indigo-600"
                  >
                    <BarChart3 className="w-4 h-4 mr-2" />
                    Ver Dashboard Completo
                  </Button>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  {/* Funnel Chart */}
                  <Card className="bg-slate-900/50 border-slate-800">
                    <CardHeader>
                      <CardTitle className="text-white">Funnel de Conversión</CardTitle>
                      <CardDescription>Últimos 30 días</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={400}>
                        <BarChart 
                          data={funnelData.funnel} 
                          layout="vertical"
                          margin={{ left: 120 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                          <XAxis type="number" stroke="#94a3b8" />
                          <YAxis 
                            dataKey="label" 
                            type="category" 
                            stroke="#94a3b8"
                            width={110}
                            tick={{ fontSize: 11 }}
                          />
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: '#1e293b', 
                              border: '1px solid #334155',
                              borderRadius: '8px'
                            }}
                            formatter={(value, name) => [value, 'Usuarios']}
                          />
                          <Bar dataKey="count" fill="#8b5cf6" radius={[0, 4, 4, 0]}>
                            {funnelData.funnel.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  {/* Conversion Rates */}
                  <Card className="bg-slate-900/50 border-slate-800">
                    <CardHeader>
                      <CardTitle className="text-white">Tasas de Conversión</CardTitle>
                      <CardDescription>Conversión entre etapas</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {funnelData.funnel.map((stage, idx) => (
                          <div key={stage.stage} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <div 
                                className="w-3 h-3 rounded-full"
                                style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }}
                              />
                              <span className="text-white text-sm">{stage.label}</span>
                            </div>
                            <div className="flex items-center gap-4">
                              <span className="text-slate-400 text-sm">{stage.count}</span>
                              <Badge className={
                                stage.step_conversion >= 50 ? 'bg-green-500' :
                                stage.step_conversion >= 20 ? 'bg-yellow-500' :
                                'bg-red-500'
                              }>
                                {stage.step_conversion}%
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      <div className="mt-6 p-4 bg-emerald-900/30 rounded-xl border border-emerald-800">
                        <p className="text-emerald-300 text-sm">Conversión Total</p>
                        <p className="text-3xl font-bold text-white">{funnelData.overall_conversion}%</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </>
            )}
          </TabsContent>

          {/* HeyGen Tab */}
          <TabsContent value="heygen" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* HeyGen Status */}
              <Card className="bg-slate-900/50 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Video className="w-5 h-5 text-violet-400" />
                    Estado de HeyGen
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                    <span className="text-slate-300">API Key Configurada</span>
                    <Badge className={heygenConfig?.api_key_configured ? 'bg-green-500' : 'bg-red-500'}>
                      {heygenConfig?.api_key_configured ? 'Sí' : 'No'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                    <span className="text-slate-300">Servicio Habilitado</span>
                    <Badge className={heygenConfig?.enabled ? 'bg-green-500' : 'bg-slate-500'}>
                      {heygenConfig?.enabled ? 'Activo' : 'Inactivo'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                    <span className="text-slate-300">Tutoriales Generados</span>
                    <span className="text-white font-bold">{tutorials.length}</span>
                  </div>
                  
                  <div className="flex gap-2 pt-4">
                    <Button onClick={loadAvatars} variant="outline" className="flex-1 border-slate-700">
                      <Sparkles className="w-4 h-4 mr-2" />
                      Ver Avatares
                    </Button>
                    <Button onClick={loadVoices} variant="outline" className="flex-1 border-slate-700">
                      <Mic className="w-4 h-4 mr-2" />
                      Ver Voces
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Generate Tutorial */}
              <Card className="bg-slate-900/50 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-white">Generar Tutorial</CardTitle>
                  <CardDescription>Crea un nuevo video tutorial con avatar</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button 
                    className="w-full bg-gradient-to-r from-violet-600 to-purple-600"
                    onClick={() => navigate('/superadmin/heygen-studio')}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Abrir Estudio HeyGen
                  </Button>
                  
                  <p className="text-xs text-slate-500 mt-4 text-center">
                    Genera videos con avatares realistas para tutoriales de onboarding
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Avatars Grid */}
            {avatars.length > 0 && (
              <Card className="bg-slate-900/50 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-white">Avatares Disponibles</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                    {avatars.slice(0, 12).map((avatar) => (
                      <div 
                        key={avatar.avatar_id}
                        className="bg-slate-800/50 rounded-xl overflow-hidden border border-slate-700 hover:border-violet-500 transition-colors cursor-pointer"
                      >
                        {avatar.preview_image_url && (
                          <img 
                            src={avatar.preview_image_url} 
                            alt={avatar.avatar_name}
                            className="w-full aspect-square object-cover"
                          />
                        )}
                        <div className="p-2">
                          <p className="text-xs text-white truncate">{avatar.avatar_name}</p>
                          <p className="text-xs text-slate-500">{avatar.gender}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Generated Tutorials */}
            {tutorials.length > 0 && (
              <Card className="bg-slate-900/50 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-white">Tutoriales Generados</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {tutorials.map((video) => (
                      <div 
                        key={video.id}
                        className="bg-slate-800/50 rounded-xl overflow-hidden border border-slate-700"
                      >
                        {video.thumbnail_url && (
                          <img 
                            src={video.thumbnail_url} 
                            alt={video.title}
                            className="w-full aspect-video object-cover"
                          />
                        )}
                        <div className="p-4">
                          <h4 className="font-bold text-white mb-1">{video.title}</h4>
                          <div className="flex items-center gap-2 text-xs text-slate-400">
                            <Globe className="w-3 h-3" />
                            {video.language === 'es' ? 'Español' : 'English'}
                            <span>•</span>
                            <span>{video.duration}s</span>
                          </div>
                          {video.video_url && (
                            <a 
                              href={video.video_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="mt-3 inline-flex items-center text-violet-400 text-sm hover:text-violet-300"
                            >
                              <Play className="w-4 h-4 mr-1" />
                              Ver video
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Config Tab */}
          <TabsContent value="config" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Demo Config */}
              <Card className="bg-slate-900/50 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-white">Configuración de Demo</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm text-slate-400">Duración por defecto (días)</label>
                    <Input 
                      type="number"
                      value={demoConfig?.default_duration_days || 7}
                      className="mt-1 bg-slate-800 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-slate-400">Máximo estudiantes en demo</label>
                    <Input 
                      type="number"
                      value={demoConfig?.max_students_demo || 50}
                      className="mt-1 bg-slate-800 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-slate-400">Features habilitados</label>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {(demoConfig?.features_enabled || []).map((feature) => (
                        <Badge key={feature} className="bg-emerald-500/20 text-emerald-400">
                          {feature.replace('_', ' ')}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* HeyGen Config */}
              <Card className="bg-slate-900/50 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-white">Configuración HeyGen</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-emerald-900/30 rounded-xl border border-emerald-800">
                    <p className="text-emerald-300 text-sm">API Key</p>
                    <p className="text-white font-mono text-sm mt-1">
                      {heygenConfig?.api_key_configured ? '••••••••••••••••' : 'No configurada'}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm text-slate-400">Avatar por defecto</label>
                    <Input 
                      value={heygenConfig?.default_avatar_id || ''}
                      placeholder="Selecciona un avatar"
                      className="mt-1 bg-slate-800 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-slate-400">Voz Español por defecto</label>
                    <Input 
                      value={heygenConfig?.default_voice_id_es || ''}
                      placeholder="ID de voz en español"
                      className="mt-1 bg-slate-800 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-slate-400">Voz Inglés por defecto</label>
                    <Input 
                      value={heygenConfig?.default_voice_id_en || ''}
                      placeholder="ID de voz en inglés"
                      className="mt-1 bg-slate-800 border-slate-700 text-white"
                    />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
