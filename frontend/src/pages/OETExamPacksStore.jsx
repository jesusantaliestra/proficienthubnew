import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../components/ui/dialog';
import LanguageSelector from '../components/LanguageSelector';
import {
  Stethoscope,
  Check,
  Star,
  CreditCard,
  ShoppingCart,
  ArrowLeft,
  Sparkles,
  Clock,
  FileText,
  Mic,
  BookOpen,
  Brain,
  Shield,
  Zap
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function OETExamPacksStore() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { profession } = useParams();
  const navigate = useNavigate();
  
  const [packs, setPacks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPack, setSelectedPack] = useState(null);
  const [showCheckout, setShowCheckout] = useState(false);
  const [purchasing, setPurchasing] = useState(false);

  // Profession display names
  const professionNames = {
    nursing: { en: 'Nursing', es: 'Enfermería' },
    medicine: { en: 'Medicine', es: 'Medicina' },
    dentistry: { en: 'Dentistry', es: 'Odontología' },
    pharmacy: { en: 'Pharmacy', es: 'Farmacia' },
    physiotherapy: { en: 'Physiotherapy', es: 'Fisioterapia' },
    radiography: { en: 'Radiography', es: 'Radiografía' },
    optometry: { en: 'Optometry', es: 'Optometría' },
    dietetics: { en: 'Dietetics', es: 'Dietética' },
    occupational_therapy: { en: 'Occupational Therapy', es: 'Terapia Ocupacional' },
    speech_pathology: { en: 'Speech Pathology', es: 'Logopedia' },
    veterinary_science: { en: 'Veterinary Science', es: 'Veterinaria' },
    podiatry: { en: 'Podiatry', es: 'Podología' }
  };

  const currentProfession = profession || 'nursing';
  const professionName = professionNames[currentProfession]?.es || currentProfession;

  useEffect(() => {
    fetchPacks();
  }, [currentProfession]);

  const fetchPacks = async () => {
    try {
      const response = await fetch(`${API_URL}/api/oet-packs/packs/${currentProfession}`);
      if (response.ok) {
        const data = await response.json();
        setPacks(data.packs);
      }
    } catch (error) {
      console.error('Error fetching packs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async () => {
    if (!selectedPack) return;
    
    setPurchasing(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/oet-packs/purchase`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          pack_id: selectedPack.id,
          profession: currentProfession,
          payment_method: 'stripe'
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        toast.success(`¡${selectedPack.name} comprado exitosamente!`);
        setShowCheckout(false);
        navigate(`/oet/${currentProfession}`);
      } else {
        toast.error('Error al procesar la compra');
      }
    } catch (error) {
      toast.error('Error de conexión');
    } finally {
      setPurchasing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-teal-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400">Cargando paquetes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur-lg border-b border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => navigate(`/oet/${currentProfession}`)}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Volver
              </Button>
              <div className="h-6 w-px bg-slate-700"></div>
              <div className="flex items-center gap-2">
                <ShoppingCart className="w-5 h-5 text-teal-400" />
                <span className="text-white font-medium">Tienda OET</span>
              </div>
            </div>
            <LanguageSelector variant="compact" />
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header Section */}
        <div className="text-center mb-12">
          <Badge className="bg-teal-500/20 text-teal-300 border-teal-500/30 mb-4">
            <Stethoscope className="w-3 h-3 mr-1" />
            OET {professionName}
          </Badge>
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Elige tu Pack de Preparación
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto">
            Accede a exámenes mock completos, práctica de speaking con IA, y feedback detallado 
            para alcanzar tu banda objetivo en el OET.
          </p>
        </div>

        {/* Profession Selector */}
        <div className="flex justify-center mb-8">
          <div className="flex flex-wrap gap-2 justify-center">
            {Object.entries(professionNames).slice(0, 6).map(([key, names]) => (
              <Button
                key={key}
                variant={key === currentProfession ? 'default' : 'outline'}
                size="sm"
                className={key === currentProfession 
                  ? 'bg-teal-500' 
                  : 'border-slate-700 text-slate-400'}
                onClick={() => navigate(`/oet/packs/${key}`)}
              >
                {names.es}
              </Button>
            ))}
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {packs.map((pack, idx) => (
            <Card 
              key={pack.id}
              className={`bg-slate-900/50 border relative overflow-hidden transition-all hover:border-teal-500/50 ${
                pack.popular 
                  ? 'border-teal-500/50 ring-2 ring-teal-500/20' 
                  : 'border-slate-800'
              }`}
            >
              {pack.popular && (
                <div className="absolute top-0 right-0">
                  <Badge className="bg-teal-500 text-white rounded-none rounded-bl-lg">
                    <Star className="w-3 h-3 mr-1" />
                    Más Popular
                  </Badge>
                </div>
              )}
              
              <CardHeader className="pb-4">
                <CardTitle className="text-white">{pack.name}</CardTitle>
                <CardDescription>
                  {pack.num_mocks} exámenes mock completos
                </CardDescription>
              </CardHeader>
              
              <CardContent className="space-y-6">
                {/* Price */}
                <div className="text-center py-4">
                  <span className="text-4xl font-bold text-white">${pack.price_usd}</span>
                  <span className="text-slate-400 ml-2">USD</span>
                </div>

                {/* Features */}
                <ul className="space-y-3">
                  {pack.features.map((feature, fidx) => (
                    <li key={fidx} className="flex items-start gap-3 text-sm">
                      <Check className="w-4 h-4 text-teal-400 mt-0.5 flex-shrink-0" />
                      <span className="text-slate-300">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
              
              <CardFooter>
                <Button 
                  className={`w-full ${pack.popular ? 'bg-teal-500 hover:bg-teal-600' : 'bg-slate-700 hover:bg-slate-600'}`}
                  onClick={() => {
                    setSelectedPack(pack);
                    setShowCheckout(true);
                  }}
                >
                  <CreditCard className="w-4 h-4 mr-2" />
                  Comprar Pack
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>

        {/* Features Section */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <div className="text-center p-6">
            <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center mx-auto mb-4">
              <FileText className="w-6 h-6 text-blue-400" />
            </div>
            <h4 className="text-white font-medium mb-2">Exámenes Auténticos</h4>
            <p className="text-sm text-slate-400">Formato idéntico al OET oficial</p>
          </div>
          <div className="text-center p-6">
            <div className="w-12 h-12 bg-orange-500/20 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Mic className="w-6 h-6 text-orange-400" />
            </div>
            <h4 className="text-white font-medium mb-2">Speaking con IA</h4>
            <p className="text-sm text-slate-400">Práctica dinámica con avatar</p>
          </div>
          <div className="text-center p-6">
            <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Brain className="w-6 h-6 text-purple-400" />
            </div>
            <h4 className="text-white font-medium mb-2">Feedback IA</h4>
            <p className="text-sm text-slate-400">Análisis detallado de respuestas</p>
          </div>
          <div className="text-center p-6">
            <div className="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Zap className="w-6 h-6 text-emerald-400" />
            </div>
            <h4 className="text-white font-medium mb-2">Resultados Rápidos</h4>
            <p className="text-sm text-slate-400">Banda estimada instantánea</p>
          </div>
        </div>

        {/* Trust Badges */}
        <div className="text-center">
          <div className="inline-flex items-center gap-6 text-sm text-slate-500">
            <span className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              Pago Seguro
            </span>
            <span className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Acceso Inmediato
            </span>
            <span className="flex items-center gap-2">
              <Check className="w-4 h-4" />
              Garantía de Satisfacción
            </span>
          </div>
        </div>
      </main>

      {/* Checkout Dialog */}
      <Dialog open={showCheckout} onOpenChange={setShowCheckout}>
        <DialogContent className="bg-slate-900 border-slate-700 max-w-md">
          <DialogHeader>
            <DialogTitle className="text-white">Confirmar Compra</DialogTitle>
            <DialogDescription>
              Estás a punto de comprar el siguiente paquete:
            </DialogDescription>
          </DialogHeader>
          
          {selectedPack && (
            <div className="space-y-4 mt-4">
              <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                <h4 className="text-white font-semibold">{selectedPack.name}</h4>
                <p className="text-sm text-slate-400">{selectedPack.num_mocks} exámenes mock</p>
                <div className="mt-3 pt-3 border-t border-slate-700">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Total:</span>
                    <span className="text-2xl font-bold text-teal-400">${selectedPack.price_usd}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Button 
                  className="w-full bg-teal-500 hover:bg-teal-600"
                  onClick={handlePurchase}
                  disabled={purchasing}
                >
                  {purchasing ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      Procesando...
                    </>
                  ) : (
                    <>
                      <CreditCard className="w-4 h-4 mr-2" />
                      Pagar ${selectedPack.price_usd}
                    </>
                  )}
                </Button>
                <Button 
                  variant="outline"
                  className="w-full border-slate-700 text-slate-300"
                  onClick={() => setShowCheckout(false)}
                >
                  Cancelar
                </Button>
              </div>

              <p className="text-xs text-slate-500 text-center">
                Al completar la compra, aceptas nuestros términos y condiciones.
              </p>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
