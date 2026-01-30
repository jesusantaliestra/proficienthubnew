import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import {
  Brain, Bot, Calendar, Target, Mic, Video, Settings, Save,
  CheckCircle, AlertTriangle, Sparkles, Users, BookOpen
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Agent icons and colors
const AGENT_CONFIG = {
  mock_coach: {
    icon: Target,
    color: 'from-orange-500 to-red-500',
    bgColor: 'bg-orange-100',
    textColor: 'text-orange-600',
    description: 'Ayuda a los estudiantes durante el examen cuando se atascan'
  },
  exam_tutor: {
    icon: BookOpen,
    color: 'from-blue-500 to-indigo-500',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-600',
    description: 'Tutor especializado en el contenido del examen'
  },
  study_planner: {
    icon: Calendar,
    color: 'from-green-500 to-emerald-500',
    bgColor: 'bg-green-100',
    textColor: 'text-green-600',
    description: 'Planifica el estudio y hace seguimiento del progreso'
  }
};

const AVATAR_TIERS = {
  none: { name: 'Sin Avatar', description: 'Solo texto', price: 'Incluido' },
  basic: { name: 'Básico (Rive)', description: 'Avatar 2D animado', price: 'Incluido' },
  premium: { name: 'Premium (HeyGen)', description: 'Video avatar realista', price: 'Premium' }
};

export default function AIAgentsConfig() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState(null);
  const [activeTab, setActiveTab] = useState('agents');

  const token = localStorage.getItem('token');
  const headers = { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/ai-agents/config`, { headers });
      if (res.ok) {
        const data = await res.json();
        setConfig(data);
      }
    } catch (err) {
      console.error('Error loading AI config:', err);
      toast.error('Error al cargar configuración');
    }
    setLoading(false);
  };

  const saveConfig = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API_URL}/api/ai-agents/config`, {
        method: 'PUT',
        headers,
        body: JSON.stringify({
          ai_tutor_enabled: config.ai_tutor_enabled,
          agents: config.agents,
          default_avatar_tier: config.default_avatar_tier,
          elevenlabs_voice_id: config.elevenlabs_voice_id,
          heygen_avatar_id: config.heygen_avatar_id,
          custom_knowledge_base: config.custom_knowledge_base
        })
      });

      if (res.ok) {
        toast.success('Configuración guardada');
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Error al guardar');
      }
    } catch (err) {
      toast.error('Error de conexión');
    }
    setSaving(false);
  };

  const updateAgent = (agentType, field, value) => {
    setConfig(prev => ({
      ...prev,
      agents: prev.agents.map(agent => 
        agent.agent_type === agentType 
          ? { ...agent, [field]: value }
          : agent
      )
    }));
  };

  const getEnabledAgentsCount = () => {
    return config?.agents?.filter(a => a.is_enabled).length || 0;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 p-8 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!config) {
    return (
      <div className="min-h-screen bg-slate-50 p-8 flex items-center justify-center">
        <Card className="p-8 text-center">
          <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
          <p>No se pudo cargar la configuración de AI</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8" data-testid="ai-agents-config">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-2">
          <div className="p-3 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Configuración de AI Tutores</h1>
            <p className="text-slate-500">Personaliza tus agentes de inteligencia artificial</p>
          </div>
        </div>

        {/* Status Banner */}
        <div className={`mt-4 p-4 rounded-xl flex items-center justify-between ${
          config.ai_tutor_enabled ? 'bg-green-50 border border-green-200' : 'bg-slate-100'
        }`}>
          <div className="flex items-center gap-3">
            <Switch 
              checked={config.ai_tutor_enabled}
              onCheckedChange={(checked) => setConfig(prev => ({ ...prev, ai_tutor_enabled: checked }))}
            />
            <div>
              <p className="font-medium">AI Tutor {config.ai_tutor_enabled ? 'Activado' : 'Desactivado'}</p>
              <p className="text-sm text-slate-500">
                {getEnabledAgentsCount()} agente(s) configurado(s)
              </p>
            </div>
          </div>
          <Button onClick={saveConfig} disabled={saving}>
            {saving ? (
              <span className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Guardando...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Save className="w-4 h-4" />
                Guardar Cambios
              </span>
            )}
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-white shadow-sm mb-6">
          <TabsTrigger value="agents" className="flex items-center gap-2">
            <Bot className="w-4 h-4" />
            Agentes
          </TabsTrigger>
          <TabsTrigger value="avatars" className="flex items-center gap-2">
            <Video className="w-4 h-4" />
            Avatares
          </TabsTrigger>
          <TabsTrigger value="knowledge" className="flex items-center gap-2">
            <BookOpen className="w-4 h-4" />
            Contenido
          </TabsTrigger>
        </TabsList>

        {/* Agents Tab */}
        <TabsContent value="agents">
          <div className="grid gap-6">
            {config.agents.map((agent) => {
              const agentInfo = AGENT_CONFIG[agent.agent_type];
              const Icon = agentInfo?.icon || Bot;
              
              return (
                <Card key={agent.agent_type} className={`overflow-hidden ${!agent.is_enabled ? 'opacity-60' : ''}`}>
                  <div className={`h-2 bg-gradient-to-r ${agentInfo?.color || 'from-gray-400 to-gray-500'}`} />
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between gap-6">
                      {/* Agent Info */}
                      <div className="flex items-start gap-4 flex-1">
                        <div className={`p-3 rounded-xl ${agentInfo?.bgColor || 'bg-gray-100'}`}>
                          <Icon className={`w-6 h-6 ${agentInfo?.textColor || 'text-gray-600'}`} />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <Switch 
                              checked={agent.is_enabled}
                              onCheckedChange={(checked) => updateAgent(agent.agent_type, 'is_enabled', checked)}
                            />
                            <span className="font-medium text-slate-700">
                              {agent.agent_type === 'mock_coach' ? 'Mock Exam Coach' :
                               agent.agent_type === 'exam_tutor' ? 'Exam Tutor' : 'Study Planner'}
                            </span>
                            {agent.is_enabled && (
                              <Badge className="bg-green-100 text-green-700">Activo</Badge>
                            )}
                          </div>
                          <p className="text-sm text-slate-500 mb-4">
                            {agentInfo?.description}
                          </p>

                          {/* Custom Name */}
                          <div className="grid md:grid-cols-2 gap-4">
                            <div>
                              <Label className="text-sm font-medium">Nombre Personalizado</Label>
                              <Input 
                                value={agent.custom_name || ''}
                                onChange={(e) => updateAgent(agent.agent_type, 'custom_name', e.target.value)}
                                placeholder={agent.agent_type === 'mock_coach' ? 'Ej: Coach María' :
                                             agent.agent_type === 'exam_tutor' ? 'Ej: Prof. García' : 'Ej: Planificador Ana'}
                                className="mt-1"
                              />
                              <p className="text-xs text-slate-400 mt-1">
                                Los estudiantes verán este nombre
                              </p>
                            </div>
                            
                            <div>
                              <Label className="text-sm font-medium">Tipo de Avatar</Label>
                              <select 
                                className="w-full mt-1 p-2 border rounded-md"
                                value={agent.avatar_tier || 'basic'}
                                onChange={(e) => updateAgent(agent.agent_type, 'avatar_tier', e.target.value)}
                              >
                                {Object.entries(AVATAR_TIERS).map(([key, tier]) => (
                                  <option key={key} value={key}>
                                    {tier.name} - {tier.description}
                                  </option>
                                ))}
                              </select>
                            </div>
                          </div>

                          {/* Custom Personality */}
                          <div className="mt-4">
                            <Label className="text-sm font-medium">Personalidad (opcional)</Label>
                            <Textarea 
                              value={agent.custom_personality || ''}
                              onChange={(e) => updateAgent(agent.agent_type, 'custom_personality', e.target.value)}
                              placeholder="Describe cómo quieres que se comporte este agente..."
                              className="mt-1 h-20"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Info Box */}
          <Card className="mt-6 bg-blue-50 border-blue-200">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="font-medium text-blue-800">Tip: Mock Exam Coach</p>
                  <p className="text-sm text-blue-600">
                    Este agente puede ayudar a los estudiantes durante el examen si se atascan. 
                    Les guía sin darles la respuesta directa, fomentando el aprendizaje.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Avatars Tab */}
        <TabsContent value="avatars">
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mic className="w-5 h-5 text-violet-500" />
                  Voz (ElevenLabs)
                </CardTitle>
                <CardDescription>
                  Configura la voz de los agentes
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div>
                  <Label>Voice ID de ElevenLabs</Label>
                  <Input 
                    value={config.elevenlabs_voice_id || ''}
                    onChange={(e) => setConfig(prev => ({ ...prev, elevenlabs_voice_id: e.target.value }))}
                    placeholder="Ej: 21m00Tcm4TlvDq8ikWAM"
                    className="mt-1"
                  />
                  <p className="text-xs text-slate-400 mt-2">
                    Obtén tu Voice ID desde el panel de ElevenLabs
                  </p>
                </div>
                
                {config.elevenlabs_voice_id && (
                  <div className="mt-4 p-3 bg-green-50 rounded-lg flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-sm text-green-700">Voz configurada</span>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Video className="w-5 h-5 text-violet-500" />
                  Video Avatar (HeyGen)
                </CardTitle>
                <CardDescription>
                  Avatar premium con video realista
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div>
                  <Label>Avatar ID de HeyGen</Label>
                  <Input 
                    value={config.heygen_avatar_id || ''}
                    onChange={(e) => setConfig(prev => ({ ...prev, heygen_avatar_id: e.target.value }))}
                    placeholder="ID del avatar de HeyGen"
                    className="mt-1"
                  />
                  <p className="text-xs text-slate-400 mt-2">
                    Solo disponible en plan Premium
                  </p>
                </div>
                
                {config.heygen_avatar_id && (
                  <div className="mt-4 p-3 bg-green-50 rounded-lg flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-sm text-green-700">Avatar premium configurado</span>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Avatar Tiers Comparison */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Comparación de Niveles de Avatar</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                {Object.entries(AVATAR_TIERS).map(([key, tier]) => (
                  <div key={key} className={`p-4 rounded-lg border-2 ${
                    config.default_avatar_tier === key ? 'border-violet-500 bg-violet-50' : 'border-slate-200'
                  }`}>
                    <h4 className="font-bold">{tier.name}</h4>
                    <p className="text-sm text-slate-500 mb-2">{tier.description}</p>
                    <Badge variant={key === 'premium' ? 'default' : 'secondary'}>
                      {tier.price}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Knowledge Base Tab */}
        <TabsContent value="knowledge">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-violet-500" />
                Base de Conocimiento Personalizada
              </CardTitle>
              <CardDescription>
                Añade contenido específico de tu academia que los agentes utilizarán
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div>
                <Label>Contenido adicional para los agentes</Label>
                <Textarea 
                  value={config.custom_knowledge_base || ''}
                  onChange={(e) => setConfig(prev => ({ ...prev, custom_knowledge_base: e.target.value }))}
                  placeholder="Añade información específica de tu academia, metodología, consejos especiales, etc. Los agentes usarán este contexto en sus respuestas."
                  className="mt-1 h-48"
                />
                <p className="text-xs text-slate-400 mt-2">
                  Este contenido se combina con el material oficial del examen
                </p>
              </div>

              <div className="mt-6 p-4 bg-slate-50 rounded-lg">
                <h4 className="font-medium mb-2">Contexto que ya incluimos:</h4>
                <ul className="text-sm text-slate-600 space-y-1">
                  <li>• Estructura y formato oficial del examen</li>
                  <li>• Criterios de evaluación oficiales</li>
                  <li>• Perfil y progreso del estudiante</li>
                  <li>• Historial de exámenes y puntuaciones</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Save Button Fixed */}
      <div className="fixed bottom-6 right-6">
        <Button 
          size="lg"
          onClick={saveConfig} 
          disabled={saving}
          className="shadow-lg"
        >
          {saving ? 'Guardando...' : 'Guardar Cambios'}
        </Button>
      </div>
    </div>
  );
}
