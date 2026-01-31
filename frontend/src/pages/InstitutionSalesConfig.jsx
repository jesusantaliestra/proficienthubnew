import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Switch } from '../components/ui/switch';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import {
  Store,
  Link,
  Globe,
  Key,
  Copy,
  Check,
  Plus,
  Trash2,
  Settings,
  ShoppingCart,
  ExternalLink,
  Code,
  Webhook,
  Shield,
  Zap,
  Package,
  Edit,
  Save,
  X,
  Info,
  ArrowRight,
  Building,
  CreditCard,
  Users
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function InstitutionSalesConfig() {
  const { t } = useTranslation();
  const { user } = useAuth();
  
  const [config, setConfig] = useState({
    sales_mode: 'external', // 'proficient' | 'external' | 'both'
    whitelabel_domain: '',
    api_key: '',
    webhook_url: '',
    auto_create_access: true,
    send_welcome_email: true
  });
  
  const [basePlans, setBasePlans] = useState([]);
  const [customPlans, setCustomPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingPlan, setEditingPlan] = useState(null);
  const [showApiDocs, setShowApiDocs] = useState(false);
  const [copiedKey, setCopiedKey] = useState(false);

  useEffect(() => {
    fetchConfig();
    fetchBasePlans();
    fetchCustomPlans();
  }, []);

  const fetchConfig = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/institution/sales-config`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
      }
    } catch (error) {
      console.error('Error fetching config:', error);
    }
  };

  const fetchBasePlans = async () => {
    try {
      const response = await fetch(`${API_URL}/api/oet-packs/base-plans`);
      if (response.ok) {
        const data = await response.json();
        setBasePlans(data.plans || getDefaultBasePlans());
      } else {
        setBasePlans(getDefaultBasePlans());
      }
    } catch (error) {
      setBasePlans(getDefaultBasePlans());
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomPlans = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/institution/custom-plans`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setCustomPlans(data.plans || []);
      }
    } catch (error) {
      console.error('Error fetching custom plans:', error);
    }
  };

  const getDefaultBasePlans = () => [
    {
      id: 'STARTER',
      name: 'Plan Starter',
      mock_exams: 3,
      ai_tutor_minutes: 30,
      speaking_sessions: 2,
      validity_days: 30,
      features_fixed: [
        '3 Mock Exams completos',
        '30 minutos de Tutor IA',
        '2 sesiones de Speaking',
        'Feedback detallado'
      ],
      editable: false
    },
    {
      id: 'STANDARD',
      name: 'Plan Standard',
      mock_exams: 5,
      ai_tutor_minutes: -1, // Unlimited
      speaking_sessions: -1, // Unlimited
      validity_days: 60,
      features_fixed: [
        '5 Mock Exams completos',
        'Tutor IA ilimitado',
        'Speaking ilimitado',
        'Evaluación de Writing',
        'Analytics avanzados'
      ],
      editable: false
    },
    {
      id: 'PREMIUM',
      name: 'Plan Premium',
      mock_exams: 10,
      ai_tutor_minutes: -1,
      speaking_sessions: -1,
      validity_days: 90,
      features_fixed: [
        '10 Mock Exams completos',
        'Tutor IA ilimitado',
        'Speaking ilimitado',
        'Evaluación de Writing con IA',
        'Plan de estudio personalizado',
        'Soporte prioritario'
      ],
      editable: false
    }
  ];

  const saveConfig = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/institution/sales-config`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
      });
      
      if (response.ok) {
        toast.success('Configuración guardada correctamente');
      } else {
        toast.error('Error al guardar la configuración');
      }
    } catch (error) {
      toast.error('Error de conexión');
    } finally {
      setSaving(false);
    }
  };

  const generateApiKey = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/institution/generate-api-key`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setConfig(prev => ({ ...prev, api_key: data.api_key }));
        toast.success('API Key generada correctamente');
      }
    } catch (error) {
      toast.error('Error al generar API Key');
    }
  };

  const copyApiKey = () => {
    navigator.clipboard.writeText(config.api_key);
    setCopiedKey(true);
    toast.success('API Key copiada al portapapeles');
    setTimeout(() => setCopiedKey(false), 2000);
  };

  const saveCustomPlan = async (plan) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/institution/custom-plans`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(plan)
      });
      
      if (response.ok) {
        toast.success('Plan personalizado guardado');
        fetchCustomPlans();
        setEditingPlan(null);
      }
    } catch (error) {
      toast.error('Error al guardar el plan');
    }
  };

  const deleteCustomPlan = async (planId) => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API_URL}/api/institution/custom-plans/${planId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      toast.success('Plan eliminado');
      fetchCustomPlans();
    } catch (error) {
      toast.error('Error al eliminar el plan');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-teal-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400">Cargando configuración...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white flex items-center gap-3">
          <Store className="w-7 h-7 text-teal-400" />
          Configuración de Ventas
        </h2>
        <p className="text-slate-400 mt-1">
          Configura cómo vender tus cursos: a través de ProficientHub o tu propia web
        </p>
      </div>

      {/* Sales Mode Selection */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <ShoppingCart className="w-5 h-5 text-teal-400" />
            Modo de Ventas
          </CardTitle>
          <CardDescription>
            Con un click, decide cómo quieres vender tus cursos
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-3 gap-4">
            {/* Option 1: Sell via ProficientHub */}
            <Card 
              className={`cursor-pointer transition-all ${
                config.sales_mode === 'proficient' 
                  ? 'border-teal-500 bg-teal-500/10' 
                  : 'border-slate-700 hover:border-slate-600'
              }`}
              onClick={() => setConfig(prev => ({ ...prev, sales_mode: 'proficient' }))}
            >
              <CardContent className="p-6 text-center">
                <div className={`w-14 h-14 rounded-xl mx-auto mb-4 flex items-center justify-center ${
                  config.sales_mode === 'proficient' ? 'bg-teal-500' : 'bg-slate-700'
                }`}>
                  <Globe className="w-7 h-7 text-white" />
                </div>
                <h4 className="text-white font-semibold mb-2">Vender vía ProficientHub</h4>
                <p className="text-sm text-slate-400 mb-3">
                  Tus clientes compran directamente en tu whitelabel de ProficientHub
                </p>
                {config.sales_mode === 'proficient' && (
                  <Badge className="bg-teal-500/20 text-teal-300">Seleccionado</Badge>
                )}
              </CardContent>
            </Card>

            {/* Option 2: Sell via Own Website */}
            <Card 
              className={`cursor-pointer transition-all ${
                config.sales_mode === 'external' 
                  ? 'border-orange-500 bg-orange-500/10' 
                  : 'border-slate-700 hover:border-slate-600'
              }`}
              onClick={() => setConfig(prev => ({ ...prev, sales_mode: 'external' }))}
            >
              <CardContent className="p-6 text-center">
                <div className={`w-14 h-14 rounded-xl mx-auto mb-4 flex items-center justify-center ${
                  config.sales_mode === 'external' ? 'bg-orange-500' : 'bg-slate-700'
                }`}>
                  <ExternalLink className="w-7 h-7 text-white" />
                </div>
                <h4 className="text-white font-semibold mb-2">Vender en Tu Web</h4>
                <p className="text-sm text-slate-400 mb-3">
                  Vendes como siempre y usas nuestra API para dar acceso
                </p>
                {config.sales_mode === 'external' && (
                  <Badge className="bg-orange-500/20 text-orange-300">Seleccionado</Badge>
                )}
              </CardContent>
            </Card>

            {/* Option 3: Both */}
            <Card 
              className={`cursor-pointer transition-all ${
                config.sales_mode === 'both' 
                  ? 'border-purple-500 bg-purple-500/10' 
                  : 'border-slate-700 hover:border-slate-600'
              }`}
              onClick={() => setConfig(prev => ({ ...prev, sales_mode: 'both' }))}
            >
              <CardContent className="p-6 text-center">
                <div className={`w-14 h-14 rounded-xl mx-auto mb-4 flex items-center justify-center ${
                  config.sales_mode === 'both' ? 'bg-purple-500' : 'bg-slate-700'
                }`}>
                  <Zap className="w-7 h-7 text-white" />
                </div>
                <h4 className="text-white font-semibold mb-2">Ambos Canales</h4>
                <p className="text-sm text-slate-400 mb-3">
                  Vende en tu web Y en tu whitelabel de ProficientHub
                </p>
                {config.sales_mode === 'both' && (
                  <Badge className="bg-purple-500/20 text-purple-300">Seleccionado</Badge>
                )}
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>

      {/* Base Plans (Fixed by ProficientHub) */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white flex items-center gap-2">
                <Package className="w-5 h-5 text-teal-400" />
                Planes Base de ProficientHub
              </CardTitle>
              <CardDescription>
                Estos planes incluyen IA y Mock Exams. <strong>No son modificables.</strong>
              </CardDescription>
            </div>
            <Badge className="bg-slate-700 text-slate-300">
              <Shield className="w-3 h-3 mr-1" />
              Fijo
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            {basePlans.map((plan) => (
              <Card key={plan.id} className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-white font-semibold">{plan.name}</h4>
                    <Badge className="bg-teal-500/20 text-teal-300 text-xs">Base</Badge>
                  </div>
                  
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">Mock Exams:</span>
                      <span className="text-white font-medium">{plan.mock_exams}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">Tutor IA:</span>
                      <span className="text-white font-medium">
                        {plan.ai_tutor_minutes === -1 ? 'Ilimitado' : `${plan.ai_tutor_minutes} min`}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">Speaking:</span>
                      <span className="text-white font-medium">
                        {plan.speaking_sessions === -1 ? 'Ilimitado' : `${plan.speaking_sessions} sesiones`}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">Validez:</span>
                      <span className="text-white font-medium">{plan.validity_days} días</span>
                    </div>
                  </div>

                  <div className="pt-4 border-t border-slate-700">
                    <p className="text-xs text-slate-500 mb-2">Incluye:</p>
                    <ul className="space-y-1">
                      {plan.features_fixed.map((feature, idx) => (
                        <li key={idx} className="text-xs text-slate-400 flex items-start gap-1">
                          <Check className="w-3 h-3 text-teal-400 mt-0.5 flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Custom Add-ons (Editable by Institution) */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white flex items-center gap-2">
                <Edit className="w-5 h-5 text-orange-400" />
                Tus Añadidos Personalizados
              </CardTitle>
              <CardDescription>
                Añade servicios propios: clases presenciales, libros, tutorías, etc. <strong>Tú pones el precio.</strong>
              </CardDescription>
            </div>
            <Dialog>
              <DialogTrigger asChild>
                <Button size="sm" className="bg-orange-500 hover:bg-orange-600">
                  <Plus className="w-4 h-4 mr-2" />
                  Añadir Servicio
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-slate-900 border-slate-700">
                <DialogHeader>
                  <DialogTitle className="text-white">Añadir Servicio Personalizado</DialogTitle>
                  <DialogDescription>
                    Define un servicio adicional para incluir en tus planes
                  </DialogDescription>
                </DialogHeader>
                <CustomPlanEditor onSave={saveCustomPlan} onCancel={() => {}} />
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          {customPlans.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <Package className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No has añadido servicios personalizados aún</p>
              <p className="text-sm mt-1">Añade clases presenciales, libros, tutorías, etc.</p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 gap-4">
              {customPlans.map((plan) => (
                <Card key={plan.id} className="bg-slate-800/50 border-slate-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-medium">{plan.name}</h4>
                      <div className="flex items-center gap-2">
                        <Button variant="ghost" size="sm" onClick={() => setEditingPlan(plan)}>
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => deleteCustomPlan(plan.id)}>
                          <Trash2 className="w-4 h-4 text-red-400" />
                        </Button>
                      </div>
                    </div>
                    <p className="text-sm text-slate-400">{plan.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* API Integration (for external sales) */}
      {(config.sales_mode === 'external' || config.sales_mode === 'both') && (
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Code className="w-5 h-5 text-blue-400" />
              Integración API
            </CardTitle>
            <CardDescription>
              Conecta tu sistema de ventas con ProficientHub para dar acceso automático
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* API Key */}
            <div className="space-y-2">
              <Label className="text-slate-300">Tu API Key</Label>
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <Input
                    type="password"
                    value={config.api_key || 'No generada aún'}
                    disabled
                    className="bg-slate-800 border-slate-700 text-slate-300 pr-10"
                  />
                  {config.api_key && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="absolute right-1 top-1 h-8"
                      onClick={copyApiKey}
                    >
                      {copiedKey ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                    </Button>
                  )}
                </div>
                <Button onClick={generateApiKey} className="bg-blue-500 hover:bg-blue-600">
                  <Key className="w-4 h-4 mr-2" />
                  {config.api_key ? 'Regenerar' : 'Generar'}
                </Button>
              </div>
            </div>

            {/* Webhook URL */}
            <div className="space-y-2">
              <Label className="text-slate-300">Webhook URL (opcional)</Label>
              <Input
                placeholder="https://tu-web.com/api/webhook/proficient"
                value={config.webhook_url}
                onChange={(e) => setConfig(prev => ({ ...prev, webhook_url: e.target.value }))}
                className="bg-slate-800 border-slate-700 text-white"
              />
              <p className="text-xs text-slate-500">
                Recibirás notificaciones cuando un estudiante complete un examen o cambie de estado
              </p>
            </div>

            {/* Options */}
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <p className="text-white font-medium">Crear acceso automáticamente</p>
                  <p className="text-xs text-slate-400">Al recibir venta por API, crear usuario y dar acceso</p>
                </div>
                <Switch
                  checked={config.auto_create_access}
                  onCheckedChange={(checked) => setConfig(prev => ({ ...prev, auto_create_access: checked }))}
                />
              </div>
              
              <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <p className="text-white font-medium">Enviar email de bienvenida</p>
                  <p className="text-xs text-slate-400">Enviar credenciales y link de acceso al nuevo estudiante</p>
                </div>
                <Switch
                  checked={config.send_welcome_email}
                  onCheckedChange={(checked) => setConfig(prev => ({ ...prev, send_welcome_email: checked }))}
                />
              </div>
            </div>

            {/* API Documentation */}
            <Alert className="bg-blue-500/10 border-blue-500/30">
              <Info className="h-4 w-4 text-blue-400" />
              <AlertTitle className="text-blue-300">Documentación API</AlertTitle>
              <AlertDescription className="text-blue-200/80">
                <Button 
                  variant="link" 
                  className="p-0 h-auto text-blue-300"
                  onClick={() => setShowApiDocs(true)}
                >
                  Ver cómo integrar tu sistema de ventas →
                </Button>
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}

      {/* Whitelabel Domain (for ProficientHub sales) */}
      {(config.sales_mode === 'proficient' || config.sales_mode === 'both') && (
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Globe className="w-5 h-5 text-teal-400" />
              Tu Dominio Whitelabel
            </CardTitle>
            <CardDescription>
              Tus clientes accederán a tu plataforma personalizada
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label className="text-slate-300">Dominio personalizado</Label>
              <div className="flex gap-2">
                <Input
                  placeholder="academia.proficienthub.com"
                  value={config.whitelabel_domain}
                  onChange={(e) => setConfig(prev => ({ ...prev, whitelabel_domain: e.target.value }))}
                  className="bg-slate-800 border-slate-700 text-white"
                />
                <Button variant="outline" className="border-slate-700">
                  Verificar DNS
                </Button>
              </div>
              <p className="text-xs text-slate-500">
                Puedes usar tu propio dominio (ej: cursos.tuacademia.com) o un subdominio de ProficientHub
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Save Button */}
      <div className="flex justify-end">
        <Button 
          className="bg-teal-500 hover:bg-teal-600 px-8"
          onClick={saveConfig}
          disabled={saving}
        >
          {saving ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
              Guardando...
            </>
          ) : (
            <>
              <Save className="w-4 h-4 mr-2" />
              Guardar Configuración
            </>
          )}
        </Button>
      </div>

      {/* API Docs Dialog */}
      <Dialog open={showApiDocs} onOpenChange={setShowApiDocs}>
        <DialogContent className="bg-slate-900 border-slate-700 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">API de Integración</DialogTitle>
            <DialogDescription>
              Conecta tu sistema de ventas para dar acceso automático
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 mt-4 max-h-[60vh] overflow-y-auto">
            <div className="p-4 bg-slate-800 rounded-lg">
              <h4 className="text-white font-medium mb-2">1. Crear acceso para un estudiante</h4>
              <pre className="text-xs text-green-400 bg-slate-950 p-3 rounded overflow-x-auto">
{`POST /api/v1/access/create
Headers:
  Authorization: Bearer YOUR_API_KEY
  Content-Type: application/json

Body:
{
  "email": "estudiante@email.com",
  "name": "Juan Pérez",
  "plan_id": "STANDARD",
  "custom_addons": ["CLASES_PRESENCIALES"]
}`}
              </pre>
            </div>

            <div className="p-4 bg-slate-800 rounded-lg">
              <h4 className="text-white font-medium mb-2">2. Verificar estado de un estudiante</h4>
              <pre className="text-xs text-green-400 bg-slate-950 p-3 rounded overflow-x-auto">
{`GET /api/v1/students/{email}/status
Headers:
  Authorization: Bearer YOUR_API_KEY`}
              </pre>
            </div>

            <div className="p-4 bg-slate-800 rounded-lg">
              <h4 className="text-white font-medium mb-2">3. Webhook de eventos</h4>
              <pre className="text-xs text-blue-400 bg-slate-950 p-3 rounded overflow-x-auto">
{`// ProficientHub enviará a tu webhook:
{
  "event": "exam_completed",
  "student_email": "estudiante@email.com",
  "exam_type": "OET",
  "score": 85,
  "band": "B"
}`}
              </pre>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// Component for editing custom plan/service
function CustomPlanEditor({ plan, onSave, onCancel }) {
  const [formData, setFormData] = useState(plan || {
    name: '',
    description: '',
    type: 'addon' // addon | service | material
  });

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label className="text-slate-300">Nombre del servicio</Label>
        <Input
          placeholder="Ej: Clases presenciales diarias"
          value={formData.name}
          onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
          className="bg-slate-800 border-slate-700 text-white"
        />
      </div>

      <div className="space-y-2">
        <Label className="text-slate-300">Descripción</Label>
        <Textarea
          placeholder="Ej: Clases de 9:00 a 10:00 de lunes a viernes"
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          className="bg-slate-800 border-slate-700 text-white"
          rows={3}
        />
      </div>

      <div className="flex gap-2 pt-4">
        <Button variant="outline" className="flex-1 border-slate-700" onClick={onCancel}>
          Cancelar
        </Button>
        <Button className="flex-1 bg-teal-500 hover:bg-teal-600" onClick={() => onSave(formData)}>
          Guardar
        </Button>
      </div>
    </div>
  );
}
