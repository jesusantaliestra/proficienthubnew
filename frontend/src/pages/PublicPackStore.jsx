import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Store,
  Package,
  Search,
  Filter,
  ShoppingCart,
  Star,
  BookOpen,
  Sparkles,
  Mic,
  PenTool,
  Clock,
  Building2,
  CreditCard,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  GraduationCap,
  Globe,
  Users,
  Award,
  Loader2
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function PublicPackStore() {
  const { t } = useTranslation();
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  // State
  const [packs, setPacks] = useState([]);
  const [institutions, setInstitutions] = useState([]);
  const [examTypes, setExamTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPack, setSelectedPack] = useState(null);
  const [showCheckout, setShowCheckout] = useState(false);
  const [processingPayment, setProcessingPayment] = useState(false);
  
  // Filters
  const [filters, setFilters] = useState({
    institution_id: searchParams.get('institution') || '',
    exam_type: searchParams.get('exam') || '',
    search: ''
  });
  
  // Load data
  useEffect(() => {
    fetchData();
  }, [filters.institution_id, filters.exam_type]);
  
  const fetchData = async () => {
    setLoading(true);
    try {
      // Build query params
      const params = new URLSearchParams();
      if (filters.institution_id) params.append('institution_id', filters.institution_id);
      if (filters.exam_type) params.append('exam_type', filters.exam_type);
      
      const [packsRes, institutionsRes, examTypesRes] = await Promise.all([
        fetch(`${API_URL}/api/store/packs?${params}`),
        fetch(`${API_URL}/api/store/institutions`),
        fetch(`${API_URL}/api/store/exam-types`)
      ]);
      
      if (packsRes.ok) {
        const data = await packsRes.json();
        setPacks(data.packs || []);
      }
      
      if (institutionsRes.ok) {
        const data = await institutionsRes.json();
        setInstitutions(data.institutions || []);
      }
      
      if (examTypesRes.ok) {
        const data = await examTypesRes.json();
        setExamTypes(data.exam_types || []);
      }
    } catch (error) {
      console.error('Error fetching store data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleBuyPack = (pack) => {
    if (!isAuthenticated) {
      toast.info('Inicia sesión para comprar');
      navigate('/login?redirect=/store');
      return;
    }
    setSelectedPack(pack);
    setShowCheckout(true);
  };
  
  const processCheckout = async () => {
    if (!selectedPack) return;
    
    setProcessingPayment(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/store/checkout/create-session`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          pack_id: selectedPack.id
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        // Redirect to Stripe checkout
        if (data.checkout_url) {
          window.location.href = data.checkout_url;
        }
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Error al procesar el pago');
      }
    } catch (error) {
      toast.error('Error de conexión');
    } finally {
      setProcessingPayment(false);
    }
  };
  
  const filteredPacks = packs.filter(pack => {
    if (filters.search) {
      const search = filters.search.toLowerCase();
      return pack.name.toLowerCase().includes(search) ||
             pack.institution_name?.toLowerCase().includes(search) ||
             pack.exam_type?.toLowerCase().includes(search);
    }
    return true;
  });

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/')}
                className="text-slate-400 hover:text-white"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div>
                <h1 className="text-xl font-bold text-white flex items-center gap-2">
                  <Store className="w-6 h-6 text-teal-400" />
                  Tienda de Packs
                </h1>
                <p className="text-sm text-slate-400">
                  Encuentra el pack perfecto para tu preparación
                </p>
              </div>
            </div>
            
            {isAuthenticated ? (
              <Button 
                onClick={() => navigate('/student/dashboard')}
                className="bg-teal-500 hover:bg-teal-600"
              >
                Mi Dashboard
              </Button>
            ) : (
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  onClick={() => navigate('/login')}
                  className="border-slate-700"
                >
                  Iniciar Sesión
                </Button>
                <Button 
                  onClick={() => navigate('/register')}
                  className="bg-teal-500 hover:bg-teal-600"
                >
                  Registrarse
                </Button>
              </div>
            )}
          </div>
        </div>
      </header>
      
      {/* Filters */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              placeholder="Buscar packs..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="pl-10 bg-slate-800 border-slate-700 text-white"
            />
          </div>
          
          <Select 
            value={filters.exam_type} 
            onValueChange={(value) => setFilters(prev => ({ ...prev, exam_type: value }))}
          >
            <SelectTrigger className="w-[200px] bg-slate-800 border-slate-700 text-white">
              <SelectValue placeholder="Tipo de Examen" />
            </SelectTrigger>
            <SelectContent className="bg-slate-800 border-slate-700">
              <SelectItem value="" className="text-white">Todos los exámenes</SelectItem>
              {examTypes.map(exam => (
                <SelectItem key={exam.id} value={exam.id} className="text-white">
                  {exam.name} ({exam.pack_count})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Select 
            value={filters.institution_id} 
            onValueChange={(value) => setFilters(prev => ({ ...prev, institution_id: value }))}
          >
            <SelectTrigger className="w-[200px] bg-slate-800 border-slate-700 text-white">
              <SelectValue placeholder="Institución" />
            </SelectTrigger>
            <SelectContent className="bg-slate-800 border-slate-700">
              <SelectItem value="" className="text-white">Todas las instituciones</SelectItem>
              {institutions.map(inst => (
                <SelectItem key={inst.id} value={inst.id} className="text-white">
                  {inst.name} ({inst.pack_count})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 pb-12">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-teal-400 animate-spin" />
          </div>
        ) : filteredPacks.length === 0 ? (
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="py-20 text-center">
              <Package className="w-16 h-16 mx-auto mb-4 text-slate-600" />
              <h3 className="text-xl font-semibold text-white mb-2">
                No hay packs disponibles
              </h3>
              <p className="text-slate-400 max-w-md mx-auto">
                {filters.exam_type || filters.institution_id || filters.search
                  ? 'No se encontraron packs con los filtros seleccionados. Prueba con otros criterios.'
                  : 'Actualmente no hay instituciones vendiendo packs a través de la plataforma.'
                }
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPacks.map(pack => (
              <PackCard 
                key={pack.id}
                pack={pack}
                onBuy={() => handleBuyPack(pack)}
              />
            ))}
          </div>
        )}
      </main>
      
      {/* Checkout Dialog */}
      <Dialog open={showCheckout} onOpenChange={setShowCheckout}>
        <DialogContent className="bg-slate-900 border-slate-700 max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <ShoppingCart className="w-5 h-5 text-teal-400" />
              Confirmar Compra
            </DialogTitle>
            <DialogDescription>
              Revisa los detalles antes de proceder al pago
            </DialogDescription>
          </DialogHeader>
          
          {selectedPack && (
            <div className="space-y-4 py-4">
              {/* Pack Summary */}
              <div className="p-4 bg-slate-800/50 rounded-lg">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="text-white font-semibold">{selectedPack.name}</h4>
                    <p className="text-sm text-slate-400">{selectedPack.institution_name}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-teal-400">
                      {selectedPack.price} {selectedPack.currency}
                    </p>
                  </div>
                </div>
                
                {/* Features */}
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {selectedPack.num_mocks > 0 && (
                    <div className="flex items-center gap-2 text-slate-300">
                      <BookOpen className="w-4 h-4 text-blue-400" />
                      <span>{selectedPack.num_mocks} Mocks</span>
                    </div>
                  )}
                  {selectedPack.include_ai_tutor && (
                    <div className="flex items-center gap-2 text-slate-300">
                      <Sparkles className="w-4 h-4 text-purple-400" />
                      <span>Tutor IA</span>
                    </div>
                  )}
                  {selectedPack.include_speaking && (
                    <div className="flex items-center gap-2 text-slate-300">
                      <Mic className="w-4 h-4 text-green-400" />
                      <span>Speaking</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2 text-slate-300">
                    <Clock className="w-4 h-4 text-orange-400" />
                    <span>{selectedPack.validity_days} días</span>
                  </div>
                </div>
              </div>
              
              {/* Payment Info */}
              <div className="flex items-center gap-3 p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <CreditCard className="w-5 h-5 text-blue-400" />
                <div>
                  <p className="text-sm text-white">Pago seguro con Stripe</p>
                  <p className="text-xs text-slate-400">Acepta tarjetas de crédito y débito</p>
                </div>
              </div>
            </div>
          )}
          
          <DialogFooter className="gap-2">
            <Button 
              variant="outline" 
              onClick={() => setShowCheckout(false)}
              className="border-slate-700"
            >
              Cancelar
            </Button>
            <Button 
              onClick={processCheckout}
              disabled={processingPayment}
              className="bg-teal-500 hover:bg-teal-600"
            >
              {processingPayment ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Procesando...
                </>
              ) : (
                <>
                  <CreditCard className="w-4 h-4 mr-2" />
                  Pagar {selectedPack?.price} {selectedPack?.currency}
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// Pack Card Component
function PackCard({ pack, onBuy }) {
  const examTypeShort = {
    'OET': 'OET',
    'IELTS_ACADEMIC': 'IELTS Ac.',
    'IELTS_GENERAL': 'IELTS Gen.',
    'TOEFL': 'TOEFL',
    'PTE': 'PTE',
    'CAMBRIDGE_FCE': 'FCE',
    'CAMBRIDGE_CAE': 'CAE',
    'CAMBRIDGE_CPE': 'CPE',
    'CELPIP': 'CELPIP',
    'TOEIC': 'TOEIC'
  };
  
  return (
    <Card className="bg-slate-900/50 border-slate-800 hover:border-slate-700 transition-all group">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge className="bg-blue-500/20 text-blue-300 text-xs">
                {examTypeShort[pack.exam_type] || pack.exam_type}
              </Badge>
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
            <CardTitle className="text-white text-lg group-hover:text-teal-400 transition-colors">
              {pack.name}
            </CardTitle>
          </div>
        </div>
        
        {pack.institution_name && (
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Building2 className="w-4 h-4" />
            {pack.institution_name}
          </div>
        )}
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
              <span>Tutor IA</span>
            </div>
          )}
          {pack.include_speaking && (
            <div className="flex items-center gap-2 text-slate-300">
              <Mic className="w-4 h-4 text-green-400" />
              <span>Speaking</span>
            </div>
          )}
          {pack.include_writing_evaluation && (
            <div className="flex items-center gap-2 text-slate-300">
              <PenTool className="w-4 h-4 text-orange-400" />
              <span>Writing</span>
            </div>
          )}
        </div>
        
        {/* Custom Services */}
        {pack.custom_services?.length > 0 && (
          <div className="pt-2 border-t border-slate-800">
            <p className="text-xs text-slate-500 mb-2">Incluye:</p>
            <div className="flex flex-wrap gap-1">
              {pack.custom_services.slice(0, 3).map((service, idx) => (
                <Badge key={idx} variant="outline" className="text-xs border-slate-700 text-slate-400">
                  {service.name}
                </Badge>
              ))}
              {pack.custom_services.length > 3 && (
                <Badge variant="outline" className="text-xs border-slate-700 text-slate-400">
                  +{pack.custom_services.length - 3} más
                </Badge>
              )}
            </div>
          </div>
        )}
        
        {/* Validity */}
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <Clock className="w-4 h-4" />
          <span>Válido por {pack.validity_days} días</span>
        </div>
      </CardContent>
      
      <CardFooter className="flex items-center justify-between pt-4 border-t border-slate-800">
        <div>
          <p className="text-2xl font-bold text-teal-400">
            {pack.price} <span className="text-sm font-normal">{pack.currency}</span>
          </p>
        </div>
        <Button 
          onClick={onBuy}
          className="bg-teal-500 hover:bg-teal-600"
          data-testid={`buy-pack-${pack.id}`}
        >
          Comprar
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </CardFooter>
    </Card>
  );
}

// Success Page Component
export function StoreSuccessPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const orderId = searchParams.get('order_id');
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    if (orderId) {
      completeAndFetchOrder();
    }
  }, [orderId]);
  
  const completeAndFetchOrder = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Complete the order (for testing without webhook)
      await fetch(`${API_URL}/api/store/orders/${orderId}/complete`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      // Fetch order status
      const response = await fetch(`${API_URL}/api/store/orders/${orderId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setOrder(data.order);
      }
    } catch (error) {
      console.error('Error fetching order:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-teal-400 animate-spin" />
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
      <Card className="bg-slate-900/50 border-slate-800 max-w-md w-full">
        <CardContent className="py-8 text-center">
          <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-8 h-8 text-green-400" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">¡Compra Exitosa!</h1>
          <p className="text-slate-400 mb-6">
            Tu pack ha sido activado y está listo para usar.
          </p>
          
          {order && (
            <div className="p-4 bg-slate-800/50 rounded-lg mb-6 text-left">
              <p className="text-white font-medium">{order.pack_name}</p>
              <p className="text-sm text-slate-400">
                Orden #{order.id?.slice(0, 8)}
              </p>
              <p className="text-sm text-teal-400 mt-2">
                {order.amount} {order.currency}
              </p>
            </div>
          )}
          
          <div className="flex gap-3 justify-center">
            <Button 
              variant="outline" 
              onClick={() => navigate('/store')}
              className="border-slate-700"
            >
              Ver más Packs
            </Button>
            <Button 
              onClick={() => navigate('/student/dashboard')}
              className="bg-teal-500 hover:bg-teal-600"
            >
              Ir a Mi Dashboard
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Cancel Page Component
export function StoreCancelPage() {
  const navigate = useNavigate();
  
  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
      <Card className="bg-slate-900/50 border-slate-800 max-w-md w-full">
        <CardContent className="py-8 text-center">
          <div className="w-16 h-16 bg-orange-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <ShoppingCart className="w-8 h-8 text-orange-400" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Compra Cancelada</h1>
          <p className="text-slate-400 mb-6">
            No se realizó ningún cargo. Puedes volver a intentarlo cuando quieras.
          </p>
          
          <div className="flex gap-3 justify-center">
            <Button 
              onClick={() => navigate('/store')}
              className="bg-teal-500 hover:bg-teal-600"
            >
              Volver a la Tienda
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
