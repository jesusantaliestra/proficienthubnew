import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Slider } from '../components/ui/slider';
import { 
  Settings, Users, DollarSign, Key, BarChart3, 
  LogOut, Save, Eye, EyeOff, Database, Activity,
  TrendingUp, AlertTriangle, CheckCircle, RefreshCw, Brain,
  Calculator, Percent, BookOpen, Mic, GraduationCap
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AdminPanel() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showKeys, setShowKeys] = useState({});
  const [pricingAnalysis, setPricingAnalysis] = useState(null);
  
  const [apiKeys, setApiKeys] = useState({
    openai_key: '',
    elevenlabs_key: '',
    stripe_key: ''
  });

  // ROI Calculator State - Editable prices
  const [licensePricing, setLicensePricing] = useState({
    // Base costs (internal)
    baseCostPerExam: 0.94,
    aiTutorCostPerMin: 0.06,
    writingTestCost: 0.05,
    speakingTestCost: 0.85,
    // Selling prices (editable)
    volumeMultipliers: {
      tier_100: 2.00,
      tier_500: 1.85,
      tier_1000: 1.72,
      tier_2000: 1.60,
      tier_5000: 1.50,
      tier_10000: 1.42,
      tier_100000: 1.35,
    },
    aiTutorPrices: {
      basic: 5.00,
      standard: 9.00,
      premium: 15.00,
      unlimited: 35.00,
    },
    // Test packages sell prices
    writingTestPrice: 1.10,
    speakingTestPrice: 2.70,
    mockExamPrice: 2.20,
  });

  const [roiResults, setRoiResults] = useState(null);

  useEffect(() => {
    if (user?.user_type !== 'admin') {
      toast.error('Acceso denegado: Solo administradores');
      navigate('/');
      return;
    }
    fetchStats();
    fetchSettings();
    fetchPricingAnalysis();
  }, [user, navigate]);

  const fetchPricingAnalysis = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/admin/pricing-analysis`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPricingAnalysis(response.data);
    } catch (error) {
      console.error('Error fetching pricing analysis:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/admin/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSettings = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/admin/settings`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data) {
        setApiKeys({
          openai_key: response.data.openai_key || '',
          elevenlabs_key: response.data.elevenlabs_key || '',
          stripe_key: response.data.stripe_key || ''
        });
      }
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
  };

  const saveSettings = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/admin/settings`, apiKeys, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Configuración guardada');
    } catch (error) {
      toast.error('Error al guardar configuración');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const toggleKeyVisibility = (key) => {
    setShowKeys(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'roi', label: 'ROI Calculator', icon: Calculator },
    { id: 'costs', label: 'Costs Analysis', icon: DollarSign },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'revenue', label: 'Revenue', icon: TrendingUp },
    { id: 'settings', label: 'API Keys', icon: Key },
  ];

  // Calculate ROI for all products
  const calculateAllROI = () => {
    const results = {
      licenses: {},
      aiTutor: {},
      writingTests: {},
      speakingTests: {},
      mockExams: {},
    };

    // License ROI by tier (for 10 exams plan)
    const baseExamCost = licensePricing.baseCostPerExam * 10;
    Object.entries(licensePricing.volumeMultipliers).forEach(([tier, multiplier]) => {
      const sellPrice = baseExamCost * multiplier;
      const profit = sellPrice - baseExamCost;
      const margin = (profit / sellPrice) * 100;
      results.licenses[tier] = {
        cost: baseExamCost.toFixed(2),
        price: sellPrice.toFixed(2),
        profit: profit.toFixed(2),
        margin: margin.toFixed(1),
      };
    });

    // AI Tutor ROI
    const aiCosts = { basic: 1.80, standard: 3.60, premium: 7.20, unlimited: 18.00 };
    Object.entries(licensePricing.aiTutorPrices).forEach(([option, price]) => {
      const cost = aiCosts[option];
      const profit = price - cost;
      const margin = (profit / price) * 100;
      results.aiTutor[option] = {
        cost: cost.toFixed(2),
        price: price.toFixed(2),
        profit: profit.toFixed(2),
        margin: margin.toFixed(1),
      };
    });

    // Writing Tests ROI (per 1000)
    const writingCost = licensePricing.writingTestCost * 1000;
    const writingRevenue = licensePricing.writingTestPrice * 1000;
    const writingProfit = writingRevenue - writingCost;
    results.writingTests = {
      costPer1000: writingCost.toFixed(2),
      pricePer1000: writingRevenue.toFixed(2),
      profitPer1000: writingProfit.toFixed(2),
      margin: ((writingProfit / writingRevenue) * 100).toFixed(1),
    };

    // Speaking Tests ROI (per 1000)
    const speakingCost = licensePricing.speakingTestCost * 1000;
    const speakingRevenue = licensePricing.speakingTestPrice * 1000;
    const speakingProfit = speakingRevenue - speakingCost;
    results.speakingTests = {
      costPer1000: speakingCost.toFixed(2),
      pricePer1000: speakingRevenue.toFixed(2),
      profitPer1000: speakingProfit.toFixed(2),
      margin: ((speakingProfit / speakingRevenue) * 100).toFixed(1),
    };

    // Mock Exams ROI (per 1000)
    const mockCost = licensePricing.baseCostPerExam * 1000;
    const mockRevenue = licensePricing.mockExamPrice * 1000;
    const mockProfit = mockRevenue - mockCost;
    results.mockExams = {
      costPer1000: mockCost.toFixed(2),
      pricePer1000: mockRevenue.toFixed(2),
      profitPer1000: mockProfit.toFixed(2),
      margin: ((mockProfit / mockRevenue) * 100).toFixed(1),
    };

    setRoiResults(results);
  };

  useEffect(() => {
    calculateAllROI();
  }, [licensePricing]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gray-900 flex items-center justify-center">
                <Settings className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Panel de Administración</h1>
                <p className="text-sm text-gray-500">ProficientHub</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <Badge className="bg-red-100 text-red-700 border-red-200">
                Admin
              </Badge>
              <span className="text-sm text-gray-600">{user?.email}</span>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="w-4 h-4 mr-2" />
                Salir
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="flex gap-2 mb-8 border-b border-gray-200 pb-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all ${
                activeTab === tab.id 
                  ? 'bg-gray-900 text-white' 
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Resumen General</h2>
              <Button variant="outline" size="sm" onClick={fetchStats}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Actualizar
              </Button>
            </div>
            
            {loading ? (
              <div className="text-center py-12">
                <RefreshCw className="w-8 h-8 mx-auto text-gray-400 animate-spin" />
              </div>
            ) : (
              <>
                <div className="grid md:grid-cols-4 gap-6">
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
                          <Users className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Total Usuarios</p>
                          <p className="text-2xl font-bold text-gray-900">{stats?.total_users || 0}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
                          <Database className="w-6 h-6 text-green-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Instituciones</p>
                          <p className="text-2xl font-bold text-gray-900">{stats?.total_institutions || 0}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center">
                          <Activity className="w-6 h-6 text-purple-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Exámenes Hoy</p>
                          <p className="text-2xl font-bold text-gray-900">{stats?.exams_today || 0}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center">
                          <TrendingUp className="w-6 h-6 text-orange-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Conversaciones AI</p>
                          <p className="text-2xl font-bold text-gray-900">{stats?.ai_conversations || 0}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* System Status */}
                <Card>
                  <CardHeader>
                    <CardTitle>Estado del Sistema</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-3 gap-4">
                      <div className="flex items-center gap-3 p-4 bg-green-50 rounded-xl">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        <div>
                          <p className="font-semibold text-green-800">API Backend</p>
                          <p className="text-sm text-green-600">Operativo</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-4 bg-green-50 rounded-xl">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        <div>
                          <p className="font-semibold text-green-800">Base de Datos</p>
                          <p className="text-sm text-green-600">Conectada</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-4 bg-green-50 rounded-xl">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        <div>
                          <p className="font-semibold text-green-800">Stripe</p>
                          <p className="text-sm text-green-600">Configurado</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        )}

        {/* Costs Tab - Internal Pricing Analysis */}
        {activeTab === 'costs' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Análisis de Costes Internos</h2>
            <p className="text-gray-500">Vista de costes para administrador - NO compartir con clientes</p>
            
            {pricingAnalysis ? (
              <>
                {/* Costes por Tipo de Examen */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Database className="w-5 h-5 text-blue-600" />
                      Coste por Tipo de Examen (Mock Test Completo)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-gray-200">
                            <th className="text-left py-3 px-4 font-semibold text-gray-600">Examen</th>
                            <th className="text-center py-3 px-4 font-semibold text-gray-600">Speaking (min)</th>
                            <th className="text-center py-3 px-4 font-semibold text-gray-600">Writing Tasks</th>
                            <th className="text-right py-3 px-4 font-semibold text-gray-600">Coste Interno</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(pricingAnalysis.exam_costs).map(([key, exam]) => (
                            <tr key={key} className="border-b border-gray-100 hover:bg-gray-50">
                              <td className="py-3 px-4">
                                <span className="font-semibold text-gray-900">{key.toUpperCase()}</span>
                                <span className="block text-sm text-gray-500">{exam.description}</span>
                              </td>
                              <td className="text-center py-3 px-4">{exam.speaking_minutes} min</td>
                              <td className="text-center py-3 px-4">{exam.writing_tasks}</td>
                              <td className="text-right py-3 px-4">
                                <span className="font-bold text-red-600">${exam.internal_cost.toFixed(2)}</span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                        <tfoot>
                          <tr className="bg-gray-50">
                            <td colSpan="3" className="py-3 px-4 font-bold text-gray-900">PROMEDIO POR MOCK TEST</td>
                            <td className="text-right py-3 px-4">
                              <span className="font-bold text-red-600 text-lg">${pricingAnalysis.avg_mock_test_cost}</span>
                            </td>
                          </tr>
                        </tfoot>
                      </table>
                    </div>
                  </CardContent>
                </Card>

                {/* Costes Individuales */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="w-5 h-5 text-purple-600" />
                      Costes Individuales (Desglose)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="p-4 bg-blue-50 rounded-xl text-center">
                        <p className="text-sm text-gray-600 mb-1">Writing Test</p>
                        <p className="text-2xl font-bold text-blue-600">${pricingAnalysis.individual_test_costs.writing}</p>
                      </div>
                      <div className="p-4 bg-purple-50 rounded-xl text-center">
                        <p className="text-sm text-gray-600 mb-1">Speaking Test</p>
                        <p className="text-2xl font-bold text-purple-600">${pricingAnalysis.individual_test_costs.speaking}</p>
                      </div>
                      <div className="p-4 bg-orange-50 rounded-xl text-center">
                        <p className="text-sm text-gray-600 mb-1">AI Tutor (voz/min)</p>
                        <p className="text-2xl font-bold text-orange-600">${pricingAnalysis.individual_test_costs.ai_tutor_per_min_voice}</p>
                      </div>
                      <div className="p-4 bg-green-50 rounded-xl text-center">
                        <p className="text-sm text-gray-600 mb-1">AI Tutor (mixto/min)</p>
                        <p className="text-2xl font-bold text-green-600">${pricingAnalysis.individual_test_costs.ai_tutor_per_min_mixed}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Análisis de Tiers por Licencias */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-green-600" />
                      Tiers por Volumen de Licencias - Costes vs Precios vs Márgenes
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b-2 border-gray-200 bg-gray-50">
                            <th className="text-left py-3 px-4 font-bold text-gray-700">Tier</th>
                            <th className="text-center py-3 px-4 font-bold text-gray-700">Licencias</th>
                            <th className="text-center py-3 px-4 font-bold text-gray-700">€/Licencia</th>
                            <th className="text-center py-3 px-4 font-bold text-gray-700">€/Examen</th>
                            <th className="text-center py-3 px-4 font-bold text-gray-700">Descuento</th>
                            <th className="text-right py-3 px-4 font-bold text-red-600">TU COSTE</th>
                            <th className="text-right py-3 px-4 font-bold text-green-600">GANANCIA</th>
                            <th className="text-center py-3 px-4 font-bold text-gray-700">MARGEN</th>
                          </tr>
                        </thead>
                        <tbody>
                          {pricingAnalysis.tier_analysis && pricingAnalysis.tier_analysis.map((tier, index) => (
                            <tr key={tier.tier_id} className={`border-b border-gray-100 ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                              <td className="py-4 px-4">
                                <span className="font-semibold text-gray-900">{tier.tier_id.replace(/_/g, ' ')}</span>
                              </td>
                              <td className="text-center py-4 px-4 font-bold">{tier.licenses_range}</td>
                              <td className="text-center py-4 px-4 text-blue-600 font-bold">${tier.price_per_license}</td>
                              <td className="text-center py-4 px-4 text-[#58CC02] font-bold">${tier.price_per_exam}</td>
                              <td className="text-center py-4 px-4">
                                <Badge className="bg-orange-100 text-orange-700 border-0">{tier.discount}</Badge>
                              </td>
                              <td className="text-right py-4 px-4">
                                <span className="font-bold text-red-600 bg-red-50 px-3 py-1 rounded-lg">
                                  ${tier.internal_cost.toFixed(2)}
                                </span>
                              </td>
                              <td className="text-right py-4 px-4">
                                <span className="font-bold text-green-600 bg-green-50 px-3 py-1 rounded-lg">
                                  ${tier.profit_per_license.toFixed(2)}
                                </span>
                              </td>
                              <td className="text-center py-4 px-4">
                                <Badge className={`${
                                  parseInt(tier.margin_percentage) >= 40 ? 'bg-green-100 text-green-700' :
                                  parseInt(tier.margin_percentage) >= 30 ? 'bg-blue-100 text-blue-700' :
                                  'bg-orange-100 text-orange-700'
                                }`}>
                                  {tier.margin_percentage}
                                </Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <p className="text-sm text-gray-500 mt-4 text-center">
                      Cada licencia incluye 10 mock tests. Coste base por licencia: $9.40
                    </p>
                  </CardContent>
                </Card>

                {/* AI Tutor Add-on Analysis */}
                {pricingAnalysis.ai_tutor_addon_analysis && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Brain className="w-5 h-5 text-purple-600" />
                        AI Tutor Add-on - Análisis de Costes
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b-2 border-gray-200 bg-gray-50">
                              <th className="text-left py-3 px-4 font-bold text-gray-700">Add-on</th>
                              <th className="text-center py-3 px-4 font-bold text-gray-700">Minutos</th>
                              <th className="text-right py-3 px-4 font-bold text-red-600">TU COSTE</th>
                              <th className="text-right py-3 px-4 font-bold text-blue-600">PRECIO</th>
                              <th className="text-right py-3 px-4 font-bold text-green-600">GANANCIA</th>
                              <th className="text-center py-3 px-4 font-bold text-gray-700">MARGEN</th>
                            </tr>
                          </thead>
                          <tbody>
                            {pricingAnalysis.ai_tutor_addon_analysis.map((addon, index) => (
                              <tr key={addon.addon_id} className={`border-b border-gray-100 ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                                <td className="py-3 px-4 font-semibold text-gray-900">{addon.minutes} min AI Tutor</td>
                                <td className="text-center py-3 px-4">{addon.minutes}</td>
                                <td className="text-right py-3 px-4">
                                  <span className="font-bold text-red-600">${addon.internal_cost.toFixed(2)}</span>
                                </td>
                                <td className="text-right py-3 px-4">
                                  <span className="font-bold text-blue-600">${addon.price.toFixed(2)}</span>
                                </td>
                                <td className="text-right py-3 px-4">
                                  <span className="font-bold text-green-600">${addon.profit.toFixed(2)}</span>
                                </td>
                                <td className="text-center py-3 px-4">
                                  <Badge className="bg-purple-100 text-purple-700">{addon.margin}</Badge>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Resumen de Fórmulas */}
                <Card className="bg-yellow-50 border-yellow-200">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-yellow-800">
                      <AlertTriangle className="w-5 h-5" />
                      Fórmulas de Cálculo
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm text-yellow-900 space-y-2">
                    <p><strong>Speaking Test:</strong> STT ($0.06/min × 15min) + AI Eval ($0.01) + TTS Feedback ($0.48) = $1.39</p>
                    <p><strong>Writing Test:</strong> AI Grading ($0.02) + TTS básico ($0.24) = $0.26</p>
                    <p><strong>Mock Test:</strong> Speaking + Writing + Corrección automática ≈ $1.77 promedio</p>
                    <p><strong>AI Tutor/min:</strong> STT ($0.06) + GPT ($0.004) + TTS ($0.12) = $0.18 (voz completo)</p>
                  </CardContent>
                </Card>
              </>
            ) : (
              <div className="text-center py-12">
                <RefreshCw className="w-12 h-12 text-gray-300 mx-auto mb-4 animate-spin" />
                <p className="text-gray-500">Cargando análisis de costes...</p>
              </div>
            )}
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Gestión de Usuarios</h2>
            
            <Card>
              <CardContent className="p-6">
                <div className="grid md:grid-cols-3 gap-6 mb-6">
                  <div className="text-center p-4 bg-blue-50 rounded-xl">
                    <p className="text-3xl font-bold text-blue-600">{stats?.total_users || 0}</p>
                    <p className="text-sm text-gray-600">Total Usuarios</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-xl">
                    <p className="text-3xl font-bold text-green-600">{stats?.total_institutions || 0}</p>
                    <p className="text-sm text-gray-600">Instituciones</p>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-xl">
                    <p className="text-3xl font-bold text-purple-600">{stats?.total_students || 0}</p>
                    <p className="text-sm text-gray-600">Estudiantes</p>
                  </div>
                </div>
                
                <p className="text-gray-500 text-center py-8">
                  Funcionalidad de gestión detallada de usuarios próximamente...
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Revenue Tab */}
        {activeTab === 'revenue' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Análisis de Ingresos</h2>
            
            <div className="grid md:grid-cols-3 gap-6">
              <Card>
                <CardContent className="p-6">
                  <DollarSign className="w-8 h-8 text-green-600 mb-4" />
                  <p className="text-sm text-gray-500">Ingresos Este Mes</p>
                  <p className="text-3xl font-bold text-gray-900">$0</p>
                  <p className="text-sm text-green-600">+0% vs mes anterior</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6">
                  <TrendingUp className="w-8 h-8 text-blue-600 mb-4" />
                  <p className="text-sm text-gray-500">Transacciones</p>
                  <p className="text-3xl font-bold text-gray-900">{stats?.total_transactions || 0}</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6">
                  <Activity className="w-8 h-8 text-purple-600 mb-4" />
                  <p className="text-sm text-gray-500">Tasa de Conversión</p>
                  <p className="text-3xl font-bold text-gray-900">0%</p>
                </CardContent>
              </Card>
            </div>
            
            <Card>
              <CardHeader>
                <CardTitle>Análisis de Márgenes por Tier</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-500 text-center py-8">
                  Gráficos de análisis de márgenes próximamente...
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Configuración de API Keys</h2>
            
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Key className="w-5 h-5" />
                  Claves de API
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                    <div>
                      <p className="font-semibold text-yellow-800">Información Sensible</p>
                      <p className="text-sm text-yellow-700">
                        Las claves de API son información sensible. Nunca las compartas públicamente.
                      </p>
                    </div>
                  </div>
                </div>
                
                {/* OpenAI Key */}
                <div>
                  <Label className="text-gray-700 font-semibold">OpenAI API Key</Label>
                  <p className="text-sm text-gray-500 mb-2">Para AI Tutor y feedback de escritura</p>
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <Input
                        type={showKeys.openai ? 'text' : 'password'}
                        value={apiKeys.openai_key}
                        onChange={(e) => setApiKeys(prev => ({ ...prev, openai_key: e.target.value }))}
                        placeholder="sk-..."
                        className="pr-10"
                      />
                      <button
                        type="button"
                        onClick={() => toggleKeyVisibility('openai')}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showKeys.openai ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>
                
                {/* ElevenLabs Key */}
                <div>
                  <Label className="text-gray-700 font-semibold">ElevenLabs API Key</Label>
                  <p className="text-sm text-gray-500 mb-2">Para voz en AI Tutor y tests de speaking</p>
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <Input
                        type={showKeys.elevenlabs ? 'text' : 'password'}
                        value={apiKeys.elevenlabs_key}
                        onChange={(e) => setApiKeys(prev => ({ ...prev, elevenlabs_key: e.target.value }))}
                        placeholder="..."
                      />
                      <button
                        type="button"
                        onClick={() => toggleKeyVisibility('elevenlabs')}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showKeys.elevenlabs ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>
                
                {/* Stripe Key */}
                <div>
                  <Label className="text-gray-700 font-semibold">Stripe Secret Key</Label>
                  <p className="text-sm text-gray-500 mb-2">Para procesamiento de pagos</p>
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <Input
                        type={showKeys.stripe ? 'text' : 'password'}
                        value={apiKeys.stripe_key}
                        onChange={(e) => setApiKeys(prev => ({ ...prev, stripe_key: e.target.value }))}
                        placeholder="sk_..."
                      />
                      <button
                        type="button"
                        onClick={() => toggleKeyVisibility('stripe')}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showKeys.stripe ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>
                
                <div className="pt-4 border-t">
                  <Button onClick={saveSettings} className="bg-[#58CC02] hover:bg-[#46A302]">
                    <Save className="w-4 h-4 mr-2" />
                    Guardar Configuración
                  </Button>
                </div>
              </CardContent>
            </Card>
            
            {/* Current Status */}
            <Card>
              <CardHeader>
                <CardTitle>Estado Actual de Integraciones</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">OpenAI (Emergent Key)</span>
                    <Badge className="bg-green-100 text-green-700">Configurado</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">Stripe</span>
                    <Badge className="bg-green-100 text-green-700">Modo Test</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">ElevenLabs</span>
                    <Badge className="bg-yellow-100 text-yellow-700">Pendiente</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
