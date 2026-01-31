import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Package,
  Plus,
  Edit,
  Trash2,
  Copy,
  GripVertical,
  Save,
  X,
  Check,
  Star,
  BookOpen,
  MessageSquare,
  Mic,
  PenTool,
  Clock,
  DollarSign,
  Users,
  TrendingUp,
  ArrowLeft,
  Sparkles,
  Settings,
  BarChart3,
  Eye,
  EyeOff
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Exam types
const EXAM_TYPES = [
  { id: 'OET', name: 'OET - Occupational English Test', hasProfessions: true },
  { id: 'IELTS_ACADEMIC', name: 'IELTS Academic', hasProfessions: false },
  { id: 'IELTS_GENERAL', name: 'IELTS General Training', hasProfessions: false },
  { id: 'TOEFL', name: 'TOEFL iBT', hasProfessions: false },
  { id: 'PTE', name: 'PTE Academic', hasProfessions: false },
  { id: 'CAMBRIDGE_FCE', name: 'Cambridge B2 First (FCE)', hasProfessions: false },
  { id: 'CAMBRIDGE_CAE', name: 'Cambridge C1 Advanced (CAE)', hasProfessions: false },
  { id: 'CAMBRIDGE_CPE', name: 'Cambridge C2 Proficiency (CPE)', hasProfessions: false },
  { id: 'CELPIP', name: 'CELPIP', hasProfessions: false },
  { id: 'TOEIC', name: 'TOEIC', hasProfessions: false },
];

const OET_PROFESSIONS = [
  { id: 'nursing', name: 'Enfermería' },
  { id: 'medicine', name: 'Medicina' },
  { id: 'dentistry', name: 'Odontología' },
  { id: 'pharmacy', name: 'Farmacia' },
  { id: 'physiotherapy', name: 'Fisioterapia' },
  { id: 'radiography', name: 'Radiografía' },
  { id: 'optometry', name: 'Optometría' },
  { id: 'dietetics', name: 'Dietética' },
  { id: 'occupational_therapy', name: 'Terapia Ocupacional' },
  { id: 'speech_pathology', name: 'Logopedia' },
  { id: 'veterinary_science', name: 'Veterinaria' },
  { id: 'podiatry', name: 'Podología' },
];

const CURRENCIES = ['EUR', 'USD', 'GBP', 'MXN', 'COP', 'ARS', 'CLP', 'PEN'];

export default function InstitutionPacksManager() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [packs, setPacks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showEditor, setShowEditor] = useState(false);
  const [editingPack, setEditingPack] = useState(null);
  const [salesData, setSalesData] = useState(null);
  const [activeTab, setActiveTab] = useState('packs');

  useEffect(() => {
    fetchPacks();
    fetchSalesData();
  }, []);

  const fetchPacks = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/institution-packs/packs`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setPacks(data.packs || []);
      }
    } catch (error) {
      console.error('Error fetching packs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSalesData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/institution-packs/institution-sales?days=30`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setSalesData(data);
      }
    } catch (error) {
      console.error('Error fetching sales:', error);
    }
  };

  const handleSavePack = async (packData) => {
    try {
      const token = localStorage.getItem('token');
      const method = editingPack ? 'PUT' : 'POST';
      const url = editingPack 
        ? `${API_URL}/api/institution-packs/packs/${editingPack.id}`
        : `${API_URL}/api/institution-packs/packs`;
      
      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(packData)
      });
      
      if (response.ok) {
        toast.success(editingPack ? 'Pack actualizado' : 'Pack creado');
        setShowEditor(false);
        setEditingPack(null);
        fetchPacks();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Error al guardar');
      }
    } catch (error) {
      toast.error('Error de conexión');
    }
  };

  const handleDeletePack = async (packId) => {
    if (!window.confirm('¿Seguro que quieres eliminar este pack?')) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/institution-packs/packs/${packId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        toast.success('Pack eliminado');
        fetchPacks();
      }
    } catch (error) {
      toast.error('Error al eliminar');
    }
  };

  const handleDuplicatePack = async (packId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/institution-packs/packs/${packId}/duplicate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        toast.success('Pack duplicado');
        fetchPacks();
      }
    } catch (error) {
      toast.error('Error al duplicar');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-teal-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400">Cargando packs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Link to="/institution/dashboard">
              <Button variant="ghost" size="icon" className="text-slate-400 hover:text-white">
                <ArrowLeft className="w-5 h-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                <Package className="w-7 h-7 text-teal-400" />
                Mis Packs de Examen
              </h1>
              <p className="text-slate-400 mt-1">
                Crea packs personalizados con mocks, tutor IA y tus servicios propios
              </p>
            </div>
          </div>
          
          <Button 
            onClick={() => { setEditingPack(null); setShowEditor(true); }}
            className="bg-teal-500 hover:bg-teal-600"
            data-testid="create-pack-btn"
          >
            <Plus className="w-4 h-4 mr-2" />
            Crear Pack
          </Button>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-slate-800/50 border border-slate-700">
            <TabsTrigger value="packs" className="data-[state=active]:bg-teal-500">
              <Package className="w-4 h-4 mr-2" />
              Mis Packs ({packs.length})
            </TabsTrigger>
            <TabsTrigger value="sales" className="data-[state=active]:bg-teal-500">
              <BarChart3 className="w-4 h-4 mr-2" />
              Ventas
            </TabsTrigger>
          </TabsList>

          {/* Packs Tab */}
          <TabsContent value="packs" className="space-y-4">
            {packs.length === 0 ? (
              <Card className="bg-slate-900/50 border-slate-800">
                <CardContent className="py-16 text-center">
                  <Package className="w-16 h-16 mx-auto mb-4 text-slate-600" />
                  <h3 className="text-xl font-semibold text-white mb-2">
                    No tienes packs creados
                  </h3>
                  <p className="text-slate-400 mb-6 max-w-md mx-auto">
                    Crea tu primer pack de examen combinando mocks, tutor IA y tus servicios propios.
                    Tú decides qué incluir y a qué precio.
                  </p>
                  <Button 
                    onClick={() => setShowEditor(true)}
                    className="bg-teal-500 hover:bg-teal-600"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Crear mi primer Pack
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {packs.map((pack) => (
                  <PackCard 
                    key={pack.id}
                    pack={pack}
                    onEdit={() => { setEditingPack(pack); setShowEditor(true); }}
                    onDelete={() => handleDeletePack(pack.id)}
                    onDuplicate={() => handleDuplicatePack(pack.id)}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          {/* Sales Tab */}
          <TabsContent value="sales">
            <SalesOverview data={salesData} />
          </TabsContent>
        </Tabs>

        {/* Pack Editor Dialog */}
        <Dialog open={showEditor} onOpenChange={setShowEditor}>
          <DialogContent className="bg-slate-900 border-slate-700 max-w-3xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-white">
                {editingPack ? 'Editar Pack' : 'Crear Nuevo Pack'}
              </DialogTitle>
              <DialogDescription>
                Configura todos los detalles de tu pack de examen
              </DialogDescription>
            </DialogHeader>
            <PackEditor 
              pack={editingPack}
              onSave={handleSavePack}
              onCancel={() => setShowEditor(false)}
            />
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}

// Pack Card Component
function PackCard({ pack, onEdit, onDelete, onDuplicate }) {
  const examType = EXAM_TYPES.find(e => e.id === pack.exam_type);
  const profession = OET_PROFESSIONS.find(p => p.id === pack.profession);
  
  return (
    <Card className="bg-slate-900/50 border-slate-800 hover:border-slate-700 transition-all">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              {pack.is_popular && (
                <Badge className="bg-yellow-500/20 text-yellow-300 text-xs">
                  <Star className="w-3 h-3 mr-1" />
                  Popular
                </Badge>
              )}
              {pack.badge_text && (
                <Badge className="bg-teal-500/20 text-teal-300 text-xs">
                  {pack.badge_text}
                </Badge>
              )}
            </div>
            <CardTitle className="text-white text-lg">{pack.name}</CardTitle>
            <CardDescription className="text-slate-400 text-sm mt-1">
              {examType?.name || pack.exam_type}
              {profession && ` - ${profession.name}`}
            </CardDescription>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-teal-400">
              {pack.price} {pack.currency}
            </p>
            <p className="text-xs text-slate-500">{pack.validity_days} días</p>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Features */}
        <div className="grid grid-cols-2 gap-2 text-sm">
          {pack.num_mocks > 0 && (
            <div className="flex items-center gap-2 text-slate-300">
              <BookOpen className="w-4 h-4 text-blue-400" />
              <span>{pack.num_mocks} Mocks</span>
            </div>
          )}
          {pack.include_ai_tutor && (
            <div className="flex items-center gap-2 text-slate-300">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <span>Tutor IA {pack.ai_tutor_minutes === -1 ? '∞' : `${pack.ai_tutor_minutes}m`}</span>
            </div>
          )}
          {pack.include_speaking && (
            <div className="flex items-center gap-2 text-slate-300">
              <Mic className="w-4 h-4 text-green-400" />
              <span>Speaking {pack.speaking_sessions === -1 ? '∞' : pack.speaking_sessions}</span>
            </div>
          )}
          {pack.include_writing_evaluation && (
            <div className="flex items-center gap-2 text-slate-300">
              <PenTool className="w-4 h-4 text-orange-400" />
              <span>Writing {pack.writing_evaluations === -1 ? '∞' : pack.writing_evaluations}</span>
            </div>
          )}
        </div>

        {/* Custom Services */}
        {pack.custom_services?.length > 0 && (
          <div className="pt-2 border-t border-slate-800">
            <p className="text-xs text-slate-500 mb-2">Servicios propios:</p>
            <div className="flex flex-wrap gap-1">
              {pack.custom_services.map((service, idx) => (
                <Badge key={idx} variant="outline" className="text-xs border-slate-700 text-slate-400">
                  {service.name}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-800">
          <span className="text-xs text-slate-500">
            <Users className="w-3 h-3 inline mr-1" />
            {pack.total_sold || 0} vendidos
          </span>
          
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="sm" onClick={onEdit} className="h-8 px-2 text-slate-400 hover:text-white">
              <Edit className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={onDuplicate} className="h-8 px-2 text-slate-400 hover:text-white">
              <Copy className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={onDelete} className="h-8 px-2 text-slate-400 hover:text-red-400">
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Pack Editor Component
function PackEditor({ pack, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    name: pack?.name || '',
    description: pack?.description || '',
    exam_type: pack?.exam_type || 'OET',
    profession: pack?.profession || '',
    num_mocks: pack?.num_mocks || 5,
    include_ai_tutor: pack?.include_ai_tutor ?? true,
    ai_tutor_minutes: pack?.ai_tutor_minutes ?? -1,
    include_speaking: pack?.include_speaking ?? true,
    speaking_sessions: pack?.speaking_sessions ?? -1,
    include_writing_evaluation: pack?.include_writing_evaluation ?? true,
    writing_evaluations: pack?.writing_evaluations ?? -1,
    validity_days: pack?.validity_days || 60,
    custom_services: pack?.custom_services || [],
    price: pack?.price || 99,
    currency: pack?.currency || 'EUR',
    is_popular: pack?.is_popular || false,
    badge_text: pack?.badge_text || '',
    sort_order: pack?.sort_order || 0
  });

  const [newService, setNewService] = useState({ name: '', description: '' });
  const [saving, setSaving] = useState(false);

  const selectedExamType = EXAM_TYPES.find(e => e.id === formData.exam_type);

  const addCustomService = () => {
    if (!newService.name.trim()) return;
    setFormData(prev => ({
      ...prev,
      custom_services: [...prev.custom_services, { ...newService, type: 'service' }]
    }));
    setNewService({ name: '', description: '' });
  };

  const removeCustomService = (index) => {
    setFormData(prev => ({
      ...prev,
      custom_services: prev.custom_services.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async () => {
    if (!formData.name.trim()) {
      toast.error('El nombre es obligatorio');
      return;
    }
    if (formData.price <= 0) {
      toast.error('El precio debe ser mayor a 0');
      return;
    }
    
    setSaving(true);
    await onSave(formData);
    setSaving(false);
  };

  return (
    <div className="space-y-6">
      {/* Basic Info */}
      <div className="space-y-4">
        <h4 className="text-white font-medium flex items-center gap-2">
          <Package className="w-4 h-4 text-teal-400" />
          Información Básica
        </h4>
        
        <div className="grid md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label className="text-slate-300">Nombre del Pack *</Label>
            <Input
              placeholder="Ej: Pack Premium OET Nursing"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="bg-slate-800 border-slate-700 text-white"
              data-testid="pack-name-input"
            />
          </div>
          
          <div className="space-y-2">
            <Label className="text-slate-300">Tipo de Examen *</Label>
            <Select 
              value={formData.exam_type} 
              onValueChange={(value) => setFormData(prev => ({ ...prev, exam_type: value, profession: '' }))}
            >
              <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                <SelectValue placeholder="Seleccionar examen" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                {EXAM_TYPES.map((exam) => (
                  <SelectItem key={exam.id} value={exam.id} className="text-white">
                    {exam.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* OET Profession */}
        {selectedExamType?.hasProfessions && (
          <div className="space-y-2">
            <Label className="text-slate-300">Profesión OET</Label>
            <Select 
              value={formData.profession || "all"} 
              onValueChange={(value) => setFormData(prev => ({ ...prev, profession: value === "all" ? "" : value }))}
            >
              <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                <SelectValue placeholder="Seleccionar profesión" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                <SelectItem value="all" className="text-white">Todas las profesiones</SelectItem>
                {OET_PROFESSIONS.map((prof) => (
                  <SelectItem key={prof.id} value={prof.id} className="text-white">
                    {prof.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        <div className="space-y-2">
          <Label className="text-slate-300">Descripción</Label>
          <Textarea
            placeholder="Descripción del pack..."
            value={formData.description}
            onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
            className="bg-slate-800 border-slate-700 text-white"
            rows={2}
          />
        </div>
      </div>

      {/* Features */}
      <div className="space-y-4">
        <h4 className="text-white font-medium flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-purple-400" />
          Características del Pack
        </h4>
        
        <div className="grid md:grid-cols-2 gap-4">
          {/* Mocks */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-blue-400" />
                  <span className="text-white font-medium">Mock Exams</span>
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-slate-400 text-sm">Número de mocks</Label>
                <Input
                  type="number"
                  min="0"
                  value={formData.num_mocks}
                  onChange={(e) => setFormData(prev => ({ ...prev, num_mocks: parseInt(e.target.value) || 0 }))}
                  className="bg-slate-900 border-slate-600 text-white"
                />
              </div>
            </CardContent>
          </Card>

          {/* AI Tutor */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-400" />
                  <span className="text-white font-medium">Tutor IA</span>
                </div>
                <Switch
                  checked={formData.include_ai_tutor}
                  onCheckedChange={(checked) => setFormData(prev => ({ ...prev, include_ai_tutor: checked }))}
                />
              </div>
              {formData.include_ai_tutor && (
                <div className="space-y-2">
                  <Label className="text-slate-400 text-sm">Minutos (-1 = ilimitado)</Label>
                  <Input
                    type="number"
                    min="-1"
                    value={formData.ai_tutor_minutes}
                    onChange={(e) => setFormData(prev => ({ ...prev, ai_tutor_minutes: parseInt(e.target.value) || 0 }))}
                    className="bg-slate-900 border-slate-600 text-white"
                  />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Speaking */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Mic className="w-5 h-5 text-green-400" />
                  <span className="text-white font-medium">Speaking Dinámico</span>
                </div>
                <Switch
                  checked={formData.include_speaking}
                  onCheckedChange={(checked) => setFormData(prev => ({ ...prev, include_speaking: checked }))}
                />
              </div>
              {formData.include_speaking && (
                <div className="space-y-2">
                  <Label className="text-slate-400 text-sm">Sesiones (-1 = ilimitado)</Label>
                  <Input
                    type="number"
                    min="-1"
                    value={formData.speaking_sessions}
                    onChange={(e) => setFormData(prev => ({ ...prev, speaking_sessions: parseInt(e.target.value) || 0 }))}
                    className="bg-slate-900 border-slate-600 text-white"
                  />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Writing */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <PenTool className="w-5 h-5 text-orange-400" />
                  <span className="text-white font-medium">Evaluación Writing</span>
                </div>
                <Switch
                  checked={formData.include_writing_evaluation}
                  onCheckedChange={(checked) => setFormData(prev => ({ ...prev, include_writing_evaluation: checked }))}
                />
              </div>
              {formData.include_writing_evaluation && (
                <div className="space-y-2">
                  <Label className="text-slate-400 text-sm">Evaluaciones (-1 = ilimitado)</Label>
                  <Input
                    type="number"
                    min="-1"
                    value={formData.writing_evaluations}
                    onChange={(e) => setFormData(prev => ({ ...prev, writing_evaluations: parseInt(e.target.value) || 0 }))}
                    className="bg-slate-900 border-slate-600 text-white"
                  />
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Custom Services */}
      <div className="space-y-4">
        <h4 className="text-white font-medium flex items-center gap-2">
          <Settings className="w-4 h-4 text-orange-400" />
          Tus Servicios Propios
          <span className="text-xs text-slate-500 font-normal">(clases, libros, tutorías...)</span>
        </h4>
        
        {/* Add new service */}
        <div className="flex gap-2">
          <Input
            placeholder="Nombre del servicio"
            value={newService.name}
            onChange={(e) => setNewService(prev => ({ ...prev, name: e.target.value }))}
            className="bg-slate-800 border-slate-700 text-white"
          />
          <Input
            placeholder="Descripción (opcional)"
            value={newService.description}
            onChange={(e) => setNewService(prev => ({ ...prev, description: e.target.value }))}
            className="bg-slate-800 border-slate-700 text-white"
          />
          <Button 
            onClick={addCustomService}
            className="bg-orange-500 hover:bg-orange-600 shrink-0"
          >
            <Plus className="w-4 h-4" />
          </Button>
        </div>

        {/* Services list */}
        {formData.custom_services.length > 0 && (
          <div className="space-y-2">
            {formData.custom_services.map((service, idx) => (
              <div 
                key={idx}
                className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700"
              >
                <div>
                  <p className="text-white font-medium">{service.name}</p>
                  {service.description && (
                    <p className="text-sm text-slate-400">{service.description}</p>
                  )}
                </div>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => removeCustomService(idx)}
                  className="text-slate-400 hover:text-red-400"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Pricing & Validity */}
      <div className="space-y-4">
        <h4 className="text-white font-medium flex items-center gap-2">
          <DollarSign className="w-4 h-4 text-green-400" />
          Precio y Validez
        </h4>
        
        <div className="grid md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label className="text-slate-300">Precio *</Label>
            <Input
              type="number"
              min="0"
              step="0.01"
              value={formData.price}
              onChange={(e) => setFormData(prev => ({ ...prev, price: parseFloat(e.target.value) || 0 }))}
              className="bg-slate-800 border-slate-700 text-white text-lg font-bold"
              data-testid="pack-price-input"
            />
          </div>
          
          <div className="space-y-2">
            <Label className="text-slate-300">Moneda</Label>
            <Select 
              value={formData.currency} 
              onValueChange={(value) => setFormData(prev => ({ ...prev, currency: value }))}
            >
              <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                {CURRENCIES.map((currency) => (
                  <SelectItem key={currency} value={currency} className="text-white">
                    {currency}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label className="text-slate-300">Validez (días)</Label>
            <Input
              type="number"
              min="1"
              value={formData.validity_days}
              onChange={(e) => setFormData(prev => ({ ...prev, validity_days: parseInt(e.target.value) || 30 }))}
              className="bg-slate-800 border-slate-700 text-white"
            />
          </div>
        </div>
      </div>

      {/* Display Options */}
      <div className="space-y-4">
        <h4 className="text-white font-medium">Opciones de Visualización</h4>
        
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <Switch
              checked={formData.is_popular}
              onCheckedChange={(checked) => setFormData(prev => ({ ...prev, is_popular: checked }))}
            />
            <Label className="text-slate-300">Marcar como Popular</Label>
          </div>
          
          <div className="flex-1">
            <Input
              placeholder="Texto de badge (ej: Mejor Valor)"
              value={formData.badge_text}
              onChange={(e) => setFormData(prev => ({ ...prev, badge_text: e.target.value }))}
              className="bg-slate-800 border-slate-700 text-white"
            />
          </div>
        </div>
      </div>

      {/* Actions */}
      <DialogFooter className="gap-2">
        <Button variant="outline" onClick={onCancel} className="border-slate-700">
          Cancelar
        </Button>
        <Button 
          onClick={handleSubmit}
          disabled={saving}
          className="bg-teal-500 hover:bg-teal-600"
          data-testid="save-pack-btn"
        >
          {saving ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
              Guardando...
            </>
          ) : (
            <>
              <Save className="w-4 h-4 mr-2" />
              {pack ? 'Guardar Cambios' : 'Crear Pack'}
            </>
          )}
        </Button>
      </DialogFooter>
    </div>
  );
}

// Sales Overview Component
function SalesOverview({ data }) {
  if (!data) {
    return (
      <Card className="bg-slate-900/50 border-slate-800">
        <CardContent className="py-12 text-center text-slate-500">
          Cargando datos de ventas...
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid md:grid-cols-3 gap-4">
        <Card className="bg-slate-900/50 border-slate-800">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-green-400" />
              </div>
              <div>
                <p className="text-slate-400 text-sm">Ingresos (30 días)</p>
                <p className="text-2xl font-bold text-white">
                  {data.total_revenue?.toFixed(2)} EUR
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-slate-900/50 border-slate-800">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                <Users className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <p className="text-slate-400 text-sm">Ventas Totales</p>
                <p className="text-2xl font-bold text-white">{data.total_sales}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-slate-900/50 border-slate-800">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <p className="text-slate-400 text-sm">Ticket Promedio</p>
                <p className="text-2xl font-bold text-white">
                  {data.total_sales > 0 
                    ? (data.total_revenue / data.total_sales).toFixed(2)
                    : '0.00'
                  } EUR
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* By Pack */}
      {Object.keys(data.by_pack || {}).length > 0 && (
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">Ventas por Pack</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(data.by_pack).map(([packName, stats]) => (
                <div 
                  key={packName}
                  className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <Package className="w-5 h-5 text-teal-400" />
                    <span className="text-white">{packName}</span>
                  </div>
                  <div className="text-right">
                    <p className="text-white font-medium">{stats.revenue.toFixed(2)} EUR</p>
                    <p className="text-xs text-slate-400">{stats.count} ventas</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Sales */}
      {data.recent_sales?.length > 0 && (
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">Ventas Recientes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.recent_sales.slice(0, 10).map((sale) => (
                <div 
                  key={sale.id}
                  className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg"
                >
                  <div>
                    <p className="text-white">{sale.pack_name}</p>
                    <p className="text-xs text-slate-400">
                      {new Date(sale.purchased_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Badge className="bg-green-500/20 text-green-300">
                    +{sale.price_paid} {sale.currency}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
