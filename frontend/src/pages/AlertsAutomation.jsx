import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { Switch } from '../components/ui/switch';
import { 
  Bell, Settings, CreditCard, Plus, Trash2, Play, Mail, MessageSquare,
  Smartphone, Webhook, Slack, CheckCircle, AlertTriangle, Clock, Zap,
  TrendingUp, Users, Target, DollarSign, ChevronRight
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function AlertsAutomation() {
  const [activeTab, setActiveTab] = useState('rules');
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState(null);
  const [rules, setRules] = useState([]);
  const [channels, setChannels] = useState(null);
  const [logs, setLogs] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [pricing, setPricing] = useState(null);
  const [showNewRule, setShowNewRule] = useState(false);
  const [newRule, setNewRule] = useState({
    name: '',
    alert_type: 'stale_lead',
    trigger_days: 7,
    channels: ['email'],
    recipient_type: 'assigned_user',
    is_enabled: true
  });

  const token = localStorage.getItem('token');

  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [subRes, rulesRes, channelsRes, logsRes, analyticsRes, pricingRes] = await Promise.all([
        fetch(`${API_URL}/api/alerts-automation/subscription`, { headers }),
        fetch(`${API_URL}/api/alerts-automation/rules`, { headers }),
        fetch(`${API_URL}/api/alerts-automation/channels`, { headers }),
        fetch(`${API_URL}/api/alerts-automation/logs?limit=20`, { headers }),
        fetch(`${API_URL}/api/alerts-automation/analytics`, { headers }),
        fetch(`${API_URL}/api/alerts-automation/pricing`)
      ]);

      if (subRes.ok) setSubscription(await subRes.json());
      if (rulesRes.ok) setRules((await rulesRes.json()).rules || []);
      if (channelsRes.ok) setChannels(await channelsRes.json());
      if (logsRes.ok) setLogs((await logsRes.json()).logs || []);
      if (analyticsRes.ok) setAnalytics(await analyticsRes.json());
      if (pricingRes.ok) setPricing(await pricingRes.json());
    } catch (err) {
      console.error('Error loading data:', err);
    }
    setLoading(false);
  };

  const createRule = async () => {
    try {
      const res = await fetch(`${API_URL}/api/alerts-automation/rules`, {
        method: 'POST',
        headers,
        body: JSON.stringify(newRule)
      });
      
      if (res.ok) {
        toast.success('Regla creada exitosamente');
        setShowNewRule(false);
        setNewRule({
          name: '',
          alert_type: 'stale_lead',
          trigger_days: 7,
          channels: ['email'],
          recipient_type: 'assigned_user',
          is_enabled: true
        });
        loadData();
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Error al crear regla');
      }
    } catch (err) {
      toast.error('Error de conexión');
    }
  };

  const toggleRule = async (ruleId, currentEnabled) => {
    try {
      const res = await fetch(`${API_URL}/api/alerts-automation/rules/${ruleId}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify({ is_enabled: !currentEnabled })
      });
      
      if (res.ok) {
        toast.success(`Regla ${!currentEnabled ? 'activada' : 'desactivada'}`);
        loadData();
      }
    } catch (err) {
      toast.error('Error al actualizar regla');
    }
  };

  const deleteRule = async (ruleId) => {
    if (!confirm('¿Eliminar esta regla de alerta?')) return;
    
    try {
      const res = await fetch(`${API_URL}/api/alerts-automation/rules/${ruleId}`, {
        method: 'DELETE',
        headers
      });
      
      if (res.ok) {
        toast.success('Regla eliminada');
        loadData();
      }
    } catch (err) {
      toast.error('Error al eliminar regla');
    }
  };

  const triggerRule = async (ruleId) => {
    try {
      const res = await fetch(`${API_URL}/api/alerts-automation/rules/${ruleId}/trigger`, {
        method: 'POST',
        headers
      });
      
      if (res.ok) {
        toast.success('Alerta enviada');
        loadData();
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Error al enviar alerta');
      }
    } catch (err) {
      toast.error('Error de conexión');
    }
  };

  const upgradeTier = async (tier) => {
    try {
      const res = await fetch(`${API_URL}/api/alerts-automation/subscription`, {
        method: 'PUT',
        headers,
        body: JSON.stringify({ tier })
      });
      
      if (res.ok) {
        toast.success('Suscripción actualizada');
        loadData();
      }
    } catch (err) {
      toast.error('Error al actualizar suscripción');
    }
  };

  const getAlertTypeLabel = (type) => {
    const labels = {
      stale_lead: 'Lead Estancado',
      student_inactive: 'Estudiante Inactivo',
      payment_due: 'Pago Pendiente',
      exam_reminder: 'Recordatorio Examen',
      goal_achieved: 'Meta Alcanzada',
      custom: 'Personalizado'
    };
    return labels[type] || type;
  };

  const getChannelIcon = (channel) => {
    const icons = {
      email: Mail,
      sms: Smartphone,
      whatsapp: MessageSquare,
      webhook: Webhook,
      slack: Slack,
      teams: Users
    };
    const Icon = icons[channel] || Bell;
    return <Icon className="w-4 h-4" />;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8" data-testid="alerts-automation">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-orange-100 rounded-lg">
            <Bell className="w-6 h-6 text-orange-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Alertas Automáticas</h1>
            <p className="text-gray-500">Configura alertas para leads estancados, estudiantes inactivos y más</p>
          </div>
        </div>
        
        {/* Current Plan Banner */}
        {subscription && (
          <div className={`mt-4 p-4 rounded-xl flex items-center justify-between ${
            subscription.tier === 'free' ? 'bg-gray-100' :
            subscription.tier === 'starter' ? 'bg-blue-50 border border-blue-200' :
            subscription.tier === 'professional' ? 'bg-purple-50 border border-purple-200' :
            'bg-gradient-to-r from-indigo-500 to-purple-600 text-white'
          }`}>
            <div>
              <p className={`text-sm ${subscription.tier === 'enterprise' ? 'text-white/80' : 'text-gray-500'}`}>Plan Actual</p>
              <p className={`text-xl font-bold ${subscription.tier === 'enterprise' ? 'text-white' : ''}`}>
                {subscription.tier_details?.name || subscription.tier.toUpperCase()}
              </p>
            </div>
            <div className="text-right">
              <p className={`text-sm ${subscription.tier === 'enterprise' ? 'text-white/80' : 'text-gray-500'}`}>Alertas este mes</p>
              <p className={`text-xl font-bold ${subscription.tier === 'enterprise' ? 'text-white' : ''}`}>
                {subscription.alerts_used_this_month || 0} / {subscription.alerts_remaining === 'unlimited' ? '∞' : subscription.tier_details?.alerts_per_month}
              </p>
            </div>
            {subscription.tier !== 'enterprise' && (
              <Button 
                onClick={() => setActiveTab('pricing')}
                variant={subscription.tier === 'free' ? 'default' : 'outline'}
                className="ml-4"
              >
                Upgrade
              </Button>
            )}
          </div>
        )}
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-white shadow-sm mb-6">
          <TabsTrigger value="rules" className="flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Reglas
          </TabsTrigger>
          <TabsTrigger value="channels" className="flex items-center gap-2">
            <Mail className="w-4 h-4" />
            Canales
          </TabsTrigger>
          <TabsTrigger value="logs" className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Historial
          </TabsTrigger>
          <TabsTrigger value="pricing" className="flex items-center gap-2">
            <CreditCard className="w-4 h-4" />
            Planes
          </TabsTrigger>
        </TabsList>

        {/* Rules Tab */}
        <TabsContent value="rules">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold">Reglas de Alerta</h2>
              <Button onClick={() => setShowNewRule(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Nueva Regla
              </Button>
            </div>

            {/* New Rule Form */}
            {showNewRule && (
              <Card className="border-2 border-indigo-200 bg-indigo-50/50">
                <CardHeader>
                  <CardTitle>Crear Nueva Regla</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label>Nombre de la Regla</Label>
                      <Input 
                        value={newRule.name}
                        onChange={(e) => setNewRule({...newRule, name: e.target.value})}
                        placeholder="Ej: Leads estancados 7 días"
                      />
                    </div>
                    <div>
                      <Label>Tipo de Alerta</Label>
                      <select 
                        className="w-full p-2 border rounded-md"
                        value={newRule.alert_type}
                        onChange={(e) => setNewRule({...newRule, alert_type: e.target.value})}
                      >
                        <option value="stale_lead">Lead Estancado</option>
                        <option value="student_inactive">Estudiante Inactivo</option>
                        <option value="payment_due">Pago Pendiente</option>
                        <option value="exam_reminder">Recordatorio Examen</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label>Días para activar</Label>
                      <Input 
                        type="number"
                        value={newRule.trigger_days}
                        onChange={(e) => setNewRule({...newRule, trigger_days: parseInt(e.target.value)})}
                        min={1}
                        max={90}
                      />
                    </div>
                    <div>
                      <Label>Canal</Label>
                      <select 
                        className="w-full p-2 border rounded-md"
                        value={newRule.channels[0]}
                        onChange={(e) => setNewRule({...newRule, channels: [e.target.value]})}
                      >
                        {channels?.available_channels?.map(ch => (
                          <option key={ch} value={ch}>{ch.toUpperCase()}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button onClick={createRule} disabled={!newRule.name}>
                      Crear Regla
                    </Button>
                    <Button variant="outline" onClick={() => setShowNewRule(false)}>
                      Cancelar
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Rules List */}
            {rules.length === 0 ? (
              <Card className="p-8 text-center">
                <Bell className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No tienes reglas de alerta configuradas</p>
                <Button className="mt-4" onClick={() => setShowNewRule(true)}>
                  Crear Primera Regla
                </Button>
              </Card>
            ) : (
              <div className="grid gap-4">
                {rules.map((rule) => (
                  <Card key={rule.id} className={`${!rule.is_enabled ? 'opacity-60' : ''}`}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <Switch 
                            checked={rule.is_enabled}
                            onCheckedChange={() => toggleRule(rule.id, rule.is_enabled)}
                          />
                          <div>
                            <h3 className="font-semibold">{rule.name}</h3>
                            <div className="flex items-center gap-2 text-sm text-gray-500">
                              <Badge variant="outline">{getAlertTypeLabel(rule.alert_type)}</Badge>
                              <span>•</span>
                              <span>{rule.trigger_days} días</span>
                              <span>•</span>
                              <div className="flex gap-1">
                                {rule.channels?.map(ch => (
                                  <span key={ch} className="text-gray-400">{getChannelIcon(ch)}</span>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-400">{rule.alerts_sent || 0} enviadas</span>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => triggerRule(rule.id)}
                          >
                            <Play className="w-4 h-4" />
                          </Button>
                          <Button 
                            size="sm" 
                            variant="ghost"
                            onClick={() => deleteRule(rule.id)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </TabsContent>

        {/* Channels Tab */}
        <TabsContent value="channels">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {channels && Object.entries(channels.channel_info || {}).map(([key, info]) => {
              const isAvailable = channels.available_channels?.includes(key);
              const isConfigured = channels.configs?.find(c => c.channel === key)?.is_configured;
              
              return (
                <Card key={key} className={!isAvailable ? 'opacity-50' : ''}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3 mb-3">
                      {getChannelIcon(key)}
                      <div>
                        <h3 className="font-semibold">{info.name}</h3>
                        <p className="text-xs text-gray-500">{info.description}</p>
                      </div>
                    </div>
                    
                    {isAvailable ? (
                      <div className="flex items-center justify-between">
                        <Badge variant={isConfigured ? 'default' : 'secondary'}>
                          {isConfigured ? 'Configurado' : 'Sin configurar'}
                        </Badge>
                        <Button size="sm" variant="outline">
                          {isConfigured ? 'Editar' : 'Configurar'}
                        </Button>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between">
                        <Badge variant="outline">No disponible</Badge>
                        <Button size="sm" variant="ghost" onClick={() => setActiveTab('pricing')}>
                          Upgrade
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* Logs Tab */}
        <TabsContent value="logs">
          <Card>
            <CardHeader>
              <CardTitle>Historial de Alertas</CardTitle>
              <CardDescription>Últimas 20 alertas enviadas</CardDescription>
            </CardHeader>
            <CardContent>
              {logs.length === 0 ? (
                <p className="text-center text-gray-500 py-8">No hay alertas enviadas aún</p>
              ) : (
                <div className="space-y-2">
                  {logs.map((log) => (
                    <div key={log.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-full ${
                          log.status === 'sent' ? 'bg-green-100' : 'bg-red-100'
                        }`}>
                          {log.status === 'sent' ? (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          ) : (
                            <AlertTriangle className="w-4 h-4 text-red-600" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-sm">{log.rule_name || 'Alerta'}</p>
                          <p className="text-xs text-gray-500">
                            {getAlertTypeLabel(log.alert_type)} • {log.channels?.join(', ')}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-500">
                          {new Date(log.created_at).toLocaleString('es')}
                        </p>
                        <Badge variant={log.triggered_by === 'manual' ? 'outline' : 'secondary'} className="text-xs">
                          {log.triggered_by === 'manual' ? 'Manual' : 'Automático'}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Pricing Tab */}
        <TabsContent value="pricing">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-center mb-2">Planes de Alertas Automáticas</h2>
            <p className="text-gray-500 text-center">Elige el plan que mejor se adapte a tu institución</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {pricing && Object.entries(pricing.tiers).map(([key, tier]) => {
              const isCurrent = subscription?.tier === key;
              const isPopular = key === 'professional';
              
              return (
                <Card 
                  key={key} 
                  className={`relative ${isCurrent ? 'border-2 border-indigo-500' : ''} ${isPopular ? 'ring-2 ring-purple-500' : ''}`}
                >
                  {isPopular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <Badge className="bg-purple-500">Más Popular</Badge>
                    </div>
                  )}
                  {isCurrent && (
                    <div className="absolute -top-3 right-4">
                      <Badge className="bg-indigo-500">Plan Actual</Badge>
                    </div>
                  )}
                  <CardContent className="p-6 pt-8">
                    <h3 className="text-xl font-bold mb-1">{tier.name}</h3>
                    <div className="mb-4">
                      <span className="text-3xl font-bold">${tier.price_monthly}</span>
                      <span className="text-gray-500">/mes</span>
                    </div>
                    
                    <div className="mb-4 pb-4 border-b">
                      <p className="text-sm font-medium text-gray-700">
                        {tier.alerts_per_month === -1 ? 'Alertas ilimitadas' : `${tier.alerts_per_month} alertas/mes`}
                      </p>
                    </div>
                    
                    <ul className="space-y-2 mb-6">
                      {tier.features.map((feature, i) => (
                        <li key={i} className="flex items-center gap-2 text-sm">
                          <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                    
                    <div className="mb-4">
                      <p className="text-xs text-gray-500 mb-2">Canales disponibles:</p>
                      <div className="flex gap-1">
                        {tier.channels.map(ch => (
                          <span key={ch} className="p-1 bg-gray-100 rounded" title={ch}>
                            {getChannelIcon(ch)}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    <Button 
                      className="w-full"
                      variant={isCurrent ? 'outline' : (isPopular ? 'default' : 'secondary')}
                      disabled={isCurrent}
                      onClick={() => upgradeTier(key)}
                    >
                      {isCurrent ? 'Plan Actual' : (tier.price_monthly === 0 ? 'Seleccionar' : 'Upgrade')}
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Analytics Summary */}
          {analytics && (
            <Card className="mt-8">
              <CardHeader>
                <CardTitle>Tu Uso Actual</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-4 gap-4">
                  <div className="p-4 bg-gray-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-indigo-600">{analytics.stats.total_alerts_sent}</p>
                    <p className="text-sm text-gray-500">Total Alertas Enviadas</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-green-600">{analytics.stats.active_rules}</p>
                    <p className="text-sm text-gray-500">Reglas Activas</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-orange-600">{analytics.subscription.alerts_used}</p>
                    <p className="text-sm text-gray-500">Usadas Este Mes</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-purple-600">
                      {analytics.subscription.usage_percentage || 0}%
                    </p>
                    <p className="text-sm text-gray-500">Uso del Plan</p>
                  </div>
                </div>

                {analytics.recommendations?.length > 0 && (
                  <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <h4 className="font-medium text-yellow-800 mb-2">Recomendaciones</h4>
                    {analytics.recommendations.map((rec, i) => (
                      <p key={i} className="text-sm text-yellow-700 flex items-center gap-2">
                        <Zap className="w-4 h-4" />
                        {rec}
                      </p>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
