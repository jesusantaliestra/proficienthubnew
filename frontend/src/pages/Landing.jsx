import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Slider } from '../components/ui/slider';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { 
  GraduationCap, Brain, BarChart3, Mic, 
  Users, TrendingUp, ChevronRight, Star, CheckCircle, Check,
  BookOpen, Target, Clock, ArrowRight, Building,
  Calculator, AlertTriangle, Headphones,
  Video, FolderOpen, Volume2, Coins, Plus
} from 'lucide-react';
import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function Landing() {
  const navigate = useNavigate();
  const [calculatorValues, setCalculatorValues] = useState({
    students: 50,
    teachers: 3,
    passRate: 65,
    noShowRate: 25,
    teacherSalary: 3000
  });
  const [roiResults, setRoiResults] = useState(null);
  const [calculating, setCalculating] = useState(false);
  
  // NEW: Pricing model state
  const [pricingData, setPricingData] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState('plan_10');
  const [numStudents, setNumStudents] = useState(50);
  const [selectedAiOption, setSelectedAiOption] = useState('none');
  const [resalePrice, setResalePrice] = useState(30);
  const [calculatedPrice, setCalculatedPrice] = useState(null);
  const [calculatingPrice, setCalculatingPrice] = useState(false);
  
  // Monetization calculator state
  const [monetizationValues, setMonetizationValues] = useState({
    writingTests: 100,
    speakingTests: 50,
    writingSellPrice: 5.0,
    speakingSellPrice: 7.0
  });
  const [monetizationResult, setMonetizationResult] = useState(null);

  // Fetch pricing data from backend
  const fetchPricingData = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/pricing/platform-plans`);
      setPricingData(response.data);
    } catch (error) {
      console.error('Error fetching pricing:', error);
    }
  }, []);

  // Fetch pricing data on mount
  useEffect(() => {
    fetchPricingData();
  }, [fetchPricingData]);

  // Calculate pricing when inputs change
  const calculatePricing = useCallback(async () => {
    if (!selectedPlan || numStudents < 1) return;
    
    setCalculatingPrice(true);
    try {
      const response = await axios.get(
        `${API_URL}/pricing/calculator?exam_plan=${selectedPlan}&num_students=${numStudents}&ai_tutor_option=${selectedAiOption}&resale_price_per_student=${resalePrice}`
      );
      setCalculatedPrice(response.data);
    } catch (error) {
      console.error('Pricing calculation error:', error);
    } finally {
      setCalculatingPrice(false);
    }
  }, [selectedPlan, numStudents, selectedAiOption, resalePrice]);

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      if (selectedPlan && numStudents > 0) {
        calculatePricing();
      }
    }, 300);
    return () => clearTimeout(debounceTimer);
  }, [selectedPlan, numStudents, selectedAiOption, resalePrice, calculatePricing]);

  const calculateMonetization = async () => {
    try {
      const response = await axios.post(
        `${API_URL}/pricing/monetization-calculator?writing_tests=${monetizationValues.writingTests}&speaking_tests=${monetizationValues.speakingTests}&writing_sell_price=${monetizationValues.writingSellPrice}&speaking_sell_price=${monetizationValues.speakingSellPrice}`
      );
      setMonetizationResult(response.data);
    } catch (error) {
      console.error('Monetization calculation error:', error);
      // Fallback local calculation
      const writingCostPerTest = 0.05;
      const speakingCostPerTest = 0.85;
      const writingCost = monetizationValues.writingTests * writingCostPerTest;
      const speakingCost = monetizationValues.speakingTests * speakingCostPerTest;
      const writingRevenue = monetizationValues.writingTests * monetizationValues.writingSellPrice;
      const speakingRevenue = monetizationValues.speakingTests * monetizationValues.speakingSellPrice;
      
      setMonetizationResult({
        writing: {
          profit: Math.round(writingRevenue - writingCost),
          cost: writingCost.toFixed(2),
          revenue: writingRevenue.toFixed(2)
        },
        speaking: {
          profit: Math.round(speakingRevenue - speakingCost),
          cost: speakingCost.toFixed(2),
          revenue: speakingRevenue.toFixed(2)
        },
        totals: {
          investment: (writingCost + speakingCost).toFixed(2),
          profit: Math.round((writingRevenue - writingCost) + (speakingRevenue - speakingCost)),
          roi_percent: Math.round(((writingRevenue + speakingRevenue) / (writingCost + speakingCost) - 1) * 100)
        },
        subscription_recovery: {
          writing_tests_needed: Math.ceil(500 / (monetizationValues.writingSellPrice - writingCostPerTest)),
          speaking_tests_needed: Math.ceil(500 / (monetizationValues.speakingSellPrice - speakingCostPerTest))
        }
      });
    }
  };

  const calculateROI = async () => {
    setCalculating(true);
    
    // With AI, same teachers can handle 10x students (no need to hire more)
    const aiEnhancedRatio = 100; // 1 teacher can manage 100 students with AI support
    const potentialStudents = calculatorValues.teachers * aiEnhancedRatio;
    const additionalStudents = Math.max(0, potentialStudents - calculatorValues.students);
    const multiplier = Math.round(potentialStudents / calculatorValues.students);
    
    // Pass rate improvement with AI feedback
    const newPassRate = Math.min(95, calculatorValues.passRate + 20);
    
    // No-show reduction with AI engagement
    const newNoShowRate = Math.max(5, calculatorValues.noShowRate * 0.4);
    
    // Revenue calculation
    const avgRevenuePerStudent = 500;
    const currentRevenue = calculatorValues.students * avgRevenuePerStudent * (calculatorValues.passRate / 100);
    const projectedRevenue = potentialStudents * avgRevenuePerStudent * (newPassRate / 100);
    const revenueIncrease = projectedRevenue - currentRevenue;
    
    // Cost AVOIDANCE (not firing teachers, but not needing to hire more)
    const standardRatio = 15; // Traditional ratio without AI
    const teachersNeededWithoutAI = Math.ceil(potentialStudents / standardRatio);
    const teachersYouWouldNeedToHire = Math.max(0, teachersNeededWithoutAI - calculatorValues.teachers);
    const hiringCostAvoided = teachersYouWouldNeedToHire * calculatorValues.teacherSalary * 12;
    
    // Teacher time freed for higher-value tasks
    const timeSavedPerTeacher = 30;
    const totalTimeSaved = timeSavedPerTeacher * calculatorValues.teachers;

    setRoiResults({
      currentStudents: calculatorValues.students,
      potentialStudents: potentialStudents,
      additionalStudents: additionalStudents,
      studentMultiplier: multiplier,
      currentPassRate: calculatorValues.passRate,
      improvedPassRate: newPassRate,
      currentNoShow: calculatorValues.noShowRate,
      reducedNoShow: newNoShowRate,
      revenueIncrease: Math.round(revenueIncrease),
      hiringCostAvoided: Math.round(hiringCostAvoided),
      teachersYouWouldNeedToHire: teachersYouWouldNeedToHire,
      timeSavedWeekly: totalTimeSaved,
      totalAnnualBenefit: Math.round(revenueIncrease + hiringCostAvoided)
    });
    
    setCalculating(false);
  };

  const features = [
    { icon: Brain, title: 'AI Tutoring Agents', description: 'Personal AI tutor for each exam with voice conversations', color: 'feature-icon-green' },
    { icon: Volume2, title: 'Voice-Enabled Practice', description: 'Speaking tests with real-time AI feedback', color: 'feature-icon-blue' },
    { icon: BarChart3, title: 'Risk Analytics', description: 'Predict pass probability, identify at-risk students', color: 'feature-icon-purple' },
    { icon: FolderOpen, title: 'Institution Library', description: 'Upload materials, flashcards, audio, video', color: 'feature-icon-orange' },
    { icon: Video, title: 'Video Classes', description: 'Stream and record classes in the platform', color: 'feature-icon-yellow' },
    { icon: Headphones, title: 'Offline Access', description: 'Students practice anywhere with downloads', color: 'feature-icon-green' }
  ];

  const examTypes = [
    { id: 'toefl', name: 'TOEFL', color: 'bg-blue-500', cost: '$0.92' },
    { id: 'ielts', name: 'IELTS', color: 'bg-red-500', cost: '$0.82' },
    { id: 'cambridge', name: 'Cambridge', color: 'bg-purple-500', cost: '$0.95' },
    { id: 'pte', name: 'PTE', color: 'bg-orange-500', cost: '$0.98' },
    { id: 'oet', name: 'OET', color: 'bg-green-500', cost: '$1.02' }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-[#58CC02] flex items-center justify-center">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-extrabold text-gray-800">ProficientHub</span>
            </div>
            
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900 font-semibold">Features</a>
              <a href="#exams" className="text-gray-600 hover:text-gray-900 font-semibold">Exams</a>
              <a href="#pricing" className="text-gray-600 hover:text-gray-900 font-semibold">Pricing</a>
              <a href="#calculator" className="text-gray-600 hover:text-gray-900 font-semibold">ROI Calculator</a>
            </div>
            
            <div className="flex items-center gap-4">
              <Button variant="ghost" className="text-gray-600 font-semibold" onClick={() => navigate('/login')} data-testid="nav-login-btn">
                Log In
              </Button>
              <button className="btn-duo px-6 py-2.5 text-sm" onClick={() => navigate('/register')} data-testid="nav-get-started-btn">
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-28 pb-20 overflow-hidden">
        <div className="absolute top-20 right-0 w-96 h-96 bg-green-100 rounded-full blur-3xl opacity-50"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-100 rounded-full blur-3xl opacity-50"></div>
        
        <div className="relative max-w-7xl mx-auto px-6">
          <div className="text-center max-w-4xl mx-auto mb-16">
            <Badge className="bg-green-100 text-green-700 border-green-200 px-4 py-2 mb-6 text-sm font-semibold">
              <Building className="w-4 h-4 mr-2" />
              For Language Schools & Institutions
            </Badge>
            
            <h1 className="text-5xl lg:text-6xl font-extrabold text-gray-900 leading-tight mb-6">
              Scale Your Academy{' '}
              <span className="text-[#58CC02]">10x</span>{' '}
              With AI-Powered Learning
            </h1>
            
            <p className="text-xl text-gray-600 leading-relaxed max-w-3xl mx-auto mb-8">
              Your current teachers can handle 10x more students with AI tutors, instant feedback, and premium analytics. 
              No new hires needed. Prepare students for TOEFL, IELTS, Cambridge, PTE, and OET.
            </p>
            
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              <button className="btn-duo px-8 py-4 text-lg flex items-center gap-2" onClick={() => navigate('/register')} data-testid="hero-cta-btn">
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </button>
              <button className="btn-duo-outline px-8 py-4 text-lg" onClick={() => document.getElementById('calculator').scrollIntoView({ behavior: 'smooth' })}>
                Calculate Your ROI
              </button>
            </div>
            
            <div className="flex flex-wrap justify-center gap-12">
              <div className="text-center">
                <div className="text-4xl font-extrabold text-gray-900">10x</div>
                <div className="text-gray-500 font-semibold">Student Capacity</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-extrabold text-[#58CC02]">+23%</div>
                <div className="text-gray-500 font-semibold">Pass Rate Increase</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-extrabold text-gray-900">-60%</div>
                <div className="text-gray-500 font-semibold">No-Show Reduction</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-extrabold text-gray-900">500+</div>
                <div className="text-gray-500 font-semibold">Partner Institutions</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Everything Your Institution Needs</h2>
            <p className="text-xl text-gray-600">Premium features designed for scale and student success</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="card-duo border-2 p-6">
                <div className={`feature-icon ${feature.color} mb-4`}>
                  <feature.icon className="w-7 h-7" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Exams Section */}
      <section id="exams" className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">All Major English Proficiency Exams</h2>
            <p className="text-xl text-gray-600">One platform, complete preparation with real exam conditions</p>
          </div>
          
          <div className="grid md:grid-cols-3 lg:grid-cols-5 gap-6">
            {examTypes.map((exam) => (
              <Card key={exam.id} className="card-duo text-center p-6">
                <div className={`w-16 h-16 mx-auto rounded-2xl ${exam.color} flex items-center justify-center mb-4`}>
                  <GraduationCap className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900">{exam.name}</h3>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Planes por Número de Exámenes</h2>
            <p className="text-xl text-gray-600 mb-8">
              Elige cuántos mock exams necesitas por estudiante. Más estudiantes = Mejor precio. Márgenes saludables garantizados.
            </p>
          </div>
          
          {/* 6 Exam Plan Cards */}
          {pricingData && (
            <div className="grid md:grid-cols-3 lg:grid-cols-6 gap-4 mb-12">
              {pricingData.exam_plans.map((plan, index) => (
                <div 
                  key={plan.id} 
                  onClick={() => {
                    setSelectedPlan(plan.id);
                    document.getElementById('price-calculator').scrollIntoView({ behavior: 'smooth' });
                  }}
                  className={`bg-white rounded-2xl border-2 p-5 cursor-pointer transition-all hover:shadow-lg ${
                    selectedPlan === plan.id 
                      ? 'border-[#58CC02] ring-4 ring-green-100 scale-105' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  data-testid={`plan-${plan.id}`}
                >
                  {plan.id === 'plan_20' && (
                    <Badge className="bg-[#58CC02] text-white border-0 mb-3 text-xs">Popular</Badge>
                  )}
                  <div className="text-center">
                    <div className="w-12 h-12 mx-auto rounded-xl bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center mb-3">
                      <GraduationCap className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-2xl font-extrabold text-gray-900">{plan.exams}</h3>
                    <p className="text-sm text-gray-500 mb-2">Mock Exams</p>
                    <div className="bg-gray-50 rounded-lg p-2">
                      <span className="text-xs text-gray-500">Coste base</span>
                      <p className="font-bold text-[#58CC02]">${plan.base_cost.toFixed(2)}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* Volume Pricing Info */}
          {pricingData && (
            <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 mb-8 max-w-4xl mx-auto">
              <h3 className="text-lg font-bold text-gray-900 mb-4 text-center">
                📊 Descuentos por Volumen de Estudiantes
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {pricingData.volume_pricing.map((tier) => (
                  <div key={tier.id} className="text-center p-3 bg-gray-50 rounded-xl">
                    <p className="text-sm font-semibold text-gray-700">{tier.label}</p>
                    <p className="text-xs text-gray-500">Descuento: <span className="font-bold text-[#58CC02]">{tier.discount}</span></p>
                    <p className="text-xs text-gray-400">Margen: ~{Math.round((1 - 1/tier.price_multiplier) * 100)}%</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* AI Tutor Add-on */}
          {pricingData && (
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-6 max-w-4xl mx-auto mb-8">
              <div className="flex items-center gap-3 mb-4">
                <Brain className="w-8 h-8 text-purple-600" />
                <div>
                  <h3 className="text-xl font-bold text-gray-900">AI Tutor Add-on (Opcional)</h3>
                  <p className="text-gray-600">Añade tutorías con voz a cada licencia</p>
                </div>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {pricingData.ai_tutor_options.filter(opt => opt.minutes > 0).map((option) => (
                  <div 
                    key={option.id}
                    onClick={() => setSelectedAiOption(option.id)}
                    className={`bg-white rounded-xl p-3 text-center cursor-pointer transition-all ${
                      selectedAiOption === option.id 
                        ? 'ring-2 ring-purple-500 bg-purple-50' 
                        : 'hover:bg-purple-50'
                    }`}
                  >
                    <div className="font-bold text-gray-900">{option.minutes} min</div>
                    <div className="text-purple-600 font-bold">+${option.price}/lic</div>
                    <div className="text-xs text-gray-400">Coste: ${option.cost}</div>
                  </div>
                ))}
              </div>
              <button 
                onClick={() => setSelectedAiOption('none')}
                className={`mt-3 text-sm ${selectedAiOption === 'none' ? 'text-purple-700 font-bold' : 'text-gray-500'}`}
              >
                {selectedAiOption === 'none' ? '✓ Sin AI Tutor seleccionado' : 'Sin AI Tutor'}
              </button>
            </div>
          )}
          
          {/* Cost breakdown */}
          <div className="bg-gray-50 rounded-2xl p-6 max-w-4xl mx-auto">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Calculator className="w-5 h-5 text-[#58CC02]" />
              Tu coste interno por tipo de examen
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {examTypes.map((exam) => (
                <div key={exam.id} className="text-center">
                  <div className={`w-12 h-12 ${exam.color} rounded-xl mx-auto mb-2 flex items-center justify-center`}>
                    <GraduationCap className="w-6 h-6 text-white" />
                  </div>
                  <div className="font-bold text-gray-900">{exam.name}</div>
                  <div className="text-sm text-[#58CC02] font-semibold">{exam.cost}</div>
                </div>
              ))}
            </div>
            <p className="text-center text-gray-500 mt-4 text-sm">
              Promedio: <strong>${pricingData?.base_costs?.mock_test || '0.94'}</strong> por mock test
            </p>
          </div>
        </div>
      </section>

      {/* Interactive Price Calculator */}
      <section id="price-calculator" className="py-20">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-12">
            <Badge className="bg-blue-100 text-blue-700 border-blue-200 px-4 py-2 mb-6 text-sm font-semibold">
              <Calculator className="w-4 h-4 mr-2" />
              Calculadora de Precios en Tiempo Real
            </Badge>
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Calcula tu Precio Final</h2>
            <p className="text-xl text-gray-600">Selecciona plan, número de estudiantes y ve tu precio al instante</p>
          </div>
          
          <Card className="bg-white border-2 border-gray-200 rounded-3xl overflow-hidden">
            <div className="grid lg:grid-cols-2">
              {/* Inputs */}
              <div className="p-8 border-r border-gray-200">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Configura tu pedido</h3>
                
                <div className="space-y-6">
                  {/* Plan Selection */}
                  <div>
                    <Label className="text-gray-700 font-semibold block mb-3">Plan de Exámenes</Label>
                    <div className="grid grid-cols-3 gap-2">
                      {pricingData?.exam_plans.map((plan) => (
                        <button
                          key={plan.id}
                          onClick={() => setSelectedPlan(plan.id)}
                          className={`p-3 rounded-xl text-center transition-all ${
                            selectedPlan === plan.id
                              ? 'bg-[#58CC02] text-white'
                              : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                          }`}
                        >
                          <div className="font-bold">{plan.exams}</div>
                          <div className="text-xs">exams</div>
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  {/* Number of Students */}
                  <div>
                    <div className="flex justify-between mb-2">
                      <Label className="text-gray-700 font-semibold">Número de Estudiantes</Label>
                      <span className="text-[#58CC02] font-bold text-lg">{numStudents.toLocaleString()}</span>
                    </div>
                    <Slider
                      value={[numStudents]}
                      onValueChange={([v]) => setNumStudents(v)}
                      max={10000}
                      min={1}
                      step={numStudents < 100 ? 1 : numStudents < 1000 ? 10 : 100}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                      <span>1</span>
                      <span>100</span>
                      <span>500</span>
                      <span>2,000</span>
                      <span>10,000</span>
                    </div>
                  </div>
                  
                  {/* AI Tutor Option */}
                  <div>
                    <Label className="text-gray-700 font-semibold block mb-2">AI Tutor (opcional)</Label>
                    <select
                      value={selectedAiOption}
                      onChange={(e) => setSelectedAiOption(e.target.value)}
                      className="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-[#58CC02] outline-none"
                    >
                      {pricingData?.ai_tutor_options.map((option) => (
                        <option key={option.id} value={option.id}>
                          {option.label} {option.price > 0 ? `(+$${option.price}/estudiante)` : ''}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  {/* Resale Price */}
                  <div>
                    <div className="flex justify-between mb-2">
                      <Label className="text-gray-700 font-semibold">Tu precio de reventa ($/estudiante)</Label>
                      <span className="text-blue-600 font-bold">${resalePrice}</span>
                    </div>
                    <Slider
                      value={[resalePrice]}
                      onValueChange={([v]) => setResalePrice(v)}
                      max={150}
                      min={10}
                      step={5}
                      className="w-full"
                    />
                  </div>
                </div>
              </div>
              
              {/* Results */}
              <div className="p-8 bg-gradient-to-br from-green-50 to-white">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Tu Cotización</h3>
                
                {calculatingPrice ? (
                  <div className="text-center py-12 text-gray-400">
                    <Calculator className="w-12 h-12 mx-auto mb-4 animate-pulse" />
                    <p>Calculando...</p>
                  </div>
                ) : calculatedPrice ? (
                  <div className="space-y-4" data-testid="pricing-results">
                    {/* Summary */}
                    <div className="bg-white rounded-xl p-4 border border-gray-200">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Plan:</span>
                          <span className="font-bold ml-2">{calculatedPrice.plan.label}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Estudiantes:</span>
                          <span className="font-bold ml-2">{calculatedPrice.volume_tier.students.toLocaleString()}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Tier:</span>
                          <span className="font-bold ml-2 text-[#58CC02]">{calculatedPrice.volume_tier.discount} desc.</span>
                        </div>
                        <div>
                          <span className="text-gray-500">AI Tutor:</span>
                          <span className="font-bold ml-2">{calculatedPrice.ai_tutor.label}</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Per Student */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-red-50 rounded-xl p-4 border border-red-200">
                        <div className="text-sm text-gray-500">TU COSTE / Estudiante</div>
                        <div className="text-2xl font-extrabold text-red-600">${calculatedPrice.pricing.cost_per_student}</div>
                      </div>
                      <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
                        <div className="text-sm text-gray-500">PRECIO / Estudiante</div>
                        <div className="text-2xl font-extrabold text-blue-600">${calculatedPrice.pricing.price_per_student}</div>
                      </div>
                    </div>
                    
                    {/* Totals */}
                    <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-5 text-white">
                      <div className="grid grid-cols-3 gap-4 text-center mb-4">
                        <div>
                          <div className="text-green-100 text-xs">Tu Inversión</div>
                          <div className="text-lg font-bold">${calculatedPrice.pricing.total_cost.toLocaleString()}</div>
                        </div>
                        <div>
                          <div className="text-green-100 text-xs">Precio Total</div>
                          <div className="text-lg font-bold">${calculatedPrice.pricing.total_price.toLocaleString()}</div>
                        </div>
                        <div>
                          <div className="text-green-100 text-xs">Tu Ganancia</div>
                          <div className="text-lg font-bold">${calculatedPrice.pricing.profit.toLocaleString()}</div>
                        </div>
                      </div>
                      <div className="flex justify-between items-center pt-3 border-t border-green-400">
                        <span className="text-green-100">Margen ProficientHub</span>
                        <span className="text-2xl font-extrabold">{calculatedPrice.pricing.margin_percentage}%</span>
                      </div>
                    </div>
                    
                    {/* Customer ROI */}
                    <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
                      <div className="flex items-start gap-3">
                        <TrendingUp className="w-5 h-5 text-blue-600 mt-0.5" />
                        <div>
                          <div className="font-bold text-blue-800">Tu ROI si revendes a ${resalePrice}/estudiante</div>
                          <div className="text-sm text-blue-600">
                            Ingresos: ${calculatedPrice.customer_roi.customer_revenue.toLocaleString()} · 
                            Ganancia: ${calculatedPrice.customer_roi.customer_profit.toLocaleString()} · 
                            ROI: <strong>{calculatedPrice.customer_roi.customer_roi_percentage}%</strong>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Recommendation */}
                    <div className="bg-yellow-50 rounded-xl p-4 border border-yellow-200">
                      <div className="text-sm text-yellow-800">{calculatedPrice.recommendation}</div>
                    </div>
                    
                    <button className="btn-duo w-full py-4 text-lg" onClick={() => navigate('/register')}>
                      Comenzar Ahora
                    </button>
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-400">
                    <Calculator className="w-16 h-16 mx-auto mb-4 opacity-30" />
                    <p className="font-semibold">Selecciona un plan para ver precios</p>
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* Writing & Speaking Test Packages Section */}
      <section id="test-packages" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <Badge className="bg-orange-100 text-orange-700 border-orange-200 px-4 py-2 mb-6 text-sm font-semibold">
              <Coins className="w-4 h-4 mr-2" />
              Servicios Extra para Monetización
            </Badge>
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Paquetes de Writing & Speaking</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Compra tests individuales a precio mayorista y revéndelos a tus estudiantes.
              <strong className="text-[#58CC02]"> Genera ingresos adicionales con márgenes excelentes.</strong>
            </p>
          </div>
          
          {/* Package Tables */}
          <div className="grid lg:grid-cols-2 gap-8 mb-12">
            {/* Writing Tests */}
            <Card className="border-2 border-blue-200 rounded-2xl overflow-hidden">
              <div className="bg-blue-50 p-4 border-b border-blue-200">
                <h3 className="text-xl font-bold text-blue-800 flex items-center gap-2">
                  <BookOpen className="w-5 h-5" />
                  Writing Test Packages
                </h3>
                <p className="text-sm text-blue-600">AI-graded essays con feedback detallado</p>
              </div>
              <div className="p-4">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-gray-500 border-b">
                      <th className="pb-2">Tests</th>
                      <th className="pb-2 text-center">Tu Coste</th>
                      <th className="pb-2 text-center">Reventa Sugerida</th>
                      <th className="pb-2 text-center">Tu Ganancia</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {[
                      { tests: 100, cost: 5, resale: 3, profit: 295 },
                      { tests: 500, cost: 22.50, resale: 3, profit: 1477.50, popular: true },
                      { tests: 1000, cost: 40, resale: 3, profit: 2960 },
                      { tests: 5000, cost: 175, resale: 2.50, profit: 12325 },
                      { tests: 10000, cost: 300, resale: 2.50, profit: 24700 }
                    ].map((pkg) => (
                      <tr key={pkg.tests} className={`border-b ${pkg.popular ? 'bg-blue-50' : ''}`}>
                        <td className="py-3 font-semibold">
                          {pkg.tests.toLocaleString()} tests 
                          {pkg.popular && <Badge className="ml-2 bg-blue-500 text-white border-0 text-xs">Best Value</Badge>}
                        </td>
                        <td className="py-3 text-center text-red-600 font-bold">${pkg.cost}</td>
                        <td className="py-3 text-center text-gray-600">${pkg.resale}/test</td>
                        <td className="py-3 text-center text-green-600 font-bold">${pkg.profit.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p className="text-xs text-gray-500 mt-2 text-center">Coste interno: ~$0.05/test</p>
              </div>
            </Card>
            
            {/* Speaking Tests */}
            <Card className="border-2 border-purple-200 rounded-2xl overflow-hidden">
              <div className="bg-purple-50 p-4 border-b border-purple-200">
                <h3 className="text-xl font-bold text-purple-800 flex items-center gap-2">
                  <Mic className="w-5 h-5" />
                  Speaking Test Packages
                </h3>
                <p className="text-sm text-purple-600">AI-powered con feedback de pronunciación</p>
              </div>
              <div className="p-4">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-gray-500 border-b">
                      <th className="pb-2">Tests</th>
                      <th className="pb-2 text-center">Tu Coste</th>
                      <th className="pb-2 text-center">Reventa Sugerida</th>
                      <th className="pb-2 text-center">Tu Ganancia</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {[
                      { tests: 100, cost: 85, resale: 5, profit: 415 },
                      { tests: 500, cost: 382.50, resale: 5, profit: 2117.50, popular: true },
                      { tests: 1000, cost: 680, resale: 4, profit: 3320 },
                      { tests: 5000, cost: 2975, resale: 3.50, profit: 14525 },
                      { tests: 10000, cost: 5100, resale: 3, profit: 24900 }
                    ].map((pkg) => (
                      <tr key={pkg.tests} className={`border-b ${pkg.popular ? 'bg-purple-50' : ''}`}>
                        <td className="py-3 font-semibold">
                          {pkg.tests.toLocaleString()} tests 
                          {pkg.popular && <Badge className="ml-2 bg-purple-500 text-white border-0 text-xs">Best Value</Badge>}
                        </td>
                        <td className="py-3 text-center text-red-600 font-bold">${pkg.cost}</td>
                        <td className="py-3 text-center text-gray-600">${pkg.resale}/test</td>
                        <td className="py-3 text-center text-green-600 font-bold">${pkg.profit.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p className="text-xs text-gray-500 mt-2 text-center">Coste interno: ~$0.85/test (incluye STT + TTS + AI eval)</p>
              </div>
            </Card>
          </div>
          
          {/* Monetization Calculator */}
          <Card className="border-2 border-[#58CC02] rounded-2xl overflow-hidden" data-testid="monetization-calculator">
            <div className="bg-green-50 p-6 border-b border-green-200">
              <h3 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                <TrendingUp className="w-7 h-7 text-[#58CC02]" />
                Calculadora de Monetización
              </h3>
              <p className="text-gray-600 mt-1">Calcula cuánto puedes ganar revendiendo tests a tus estudiantes</p>
            </div>
            
            <div className="grid lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-gray-200">
              {/* Inputs */}
              <div className="p-6 space-y-6">
                <div>
                  <Label className="text-gray-700 font-semibold block mb-2">Writing Tests a Vender (mensual)</Label>
                  <div className="flex items-center gap-4">
                    <Slider
                      value={[monetizationValues.writingTests]}
                      onValueChange={([v]) => setMonetizationValues(prev => ({ ...prev, writingTests: v }))}
                      max={1000}
                      min={0}
                      step={10}
                      className="flex-1"
                    />
                    <span className="text-lg font-bold text-blue-600 w-16 text-right">{monetizationValues.writingTests}</span>
                  </div>
                </div>
                
                <div>
                  <Label className="text-gray-700 font-semibold block mb-2">Speaking Tests a Vender (mensual)</Label>
                  <div className="flex items-center gap-4">
                    <Slider
                      value={[monetizationValues.speakingTests]}
                      onValueChange={([v]) => setMonetizationValues(prev => ({ ...prev, speakingTests: v }))}
                      max={500}
                      min={0}
                      step={10}
                      className="flex-1"
                    />
                    <span className="text-lg font-bold text-purple-600 w-16 text-right">{monetizationValues.speakingTests}</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-gray-700 font-semibold block mb-2">Tu Precio Writing ($)</Label>
                    <Input
                      type="number"
                      step="0.5"
                      value={monetizationValues.writingSellPrice}
                      onChange={(e) => setMonetizationValues(prev => ({ ...prev, writingSellPrice: parseFloat(e.target.value) || 0 }))}
                      className="input-duo"
                    />
                  </div>
                  <div>
                    <Label className="text-gray-700 font-semibold block mb-2">Tu Precio Speaking ($)</Label>
                    <Input
                      type="number"
                      step="0.5"
                      value={monetizationValues.speakingSellPrice}
                      onChange={(e) => setMonetizationValues(prev => ({ ...prev, speakingSellPrice: parseFloat(e.target.value) || 0 }))}
                      className="input-duo"
                    />
                  </div>
                </div>
                
                <button 
                  className="btn-duo w-full py-3" 
                  onClick={calculateMonetization}
                  data-testid="calculate-monetization-btn"
                >
                  Calcular Ganancia
                </button>
              </div>
              
              {/* Results */}
              <div className="p-6 bg-gradient-to-br from-green-50 to-white">
                {monetizationResult ? (
                  <div className="space-y-4" data-testid="monetization-results">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-white rounded-xl p-4 border border-blue-200">
                        <div className="text-sm text-gray-500 mb-1">Ganancia Writing</div>
                        <div className="text-2xl font-extrabold text-blue-600">${monetizationResult.writing.profit}</div>
                        <div className="text-xs text-gray-400">
                          Coste: ${monetizationResult.writing.cost} | Ingreso: ${monetizationResult.writing.revenue}
                        </div>
                      </div>
                      <div className="bg-white rounded-xl p-4 border border-purple-200">
                        <div className="text-sm text-gray-500 mb-1">Ganancia Speaking</div>
                        <div className="text-2xl font-extrabold text-purple-600">${monetizationResult.speaking.profit}</div>
                        <div className="text-xs text-gray-400">
                          Coste: ${monetizationResult.speaking.cost} | Ingreso: ${monetizationResult.speaking.revenue}
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-5 text-white">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-green-100">Ganancia Mensual Total</span>
                        <span className="text-3xl font-extrabold">${monetizationResult.totals.profit}</span>
                      </div>
                      <div className="flex justify-between text-sm text-green-100">
                        <span>Inversión: ${monetizationResult.totals.investment}</span>
                        <span>ROI: {monetizationResult.totals.roi_percent}%</span>
                      </div>
                    </div>
                    
                    {monetizationResult.subscription_recovery && (
                      <div className="bg-orange-50 rounded-xl p-4 border border-orange-200">
                        <div className="flex items-start gap-3">
                          <Coins className="w-5 h-5 text-orange-600 mt-0.5" />
                          <div>
                            <div className="font-bold text-orange-800">Recuperación de Suscripción</div>
                            <div className="text-sm text-orange-600">
                              Vende solo <strong>{monetizationResult.subscription_recovery.writing_tests_needed} writing tests</strong> o{' '}
                              <strong>{monetizationResult.subscription_recovery.speaking_tests_needed} speaking tests</strong> para recuperar una suscripción de $500/mes
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-gray-400 py-8">
                    <TrendingUp className="w-12 h-12 mb-3 opacity-30" />
                    <p className="font-semibold">Ajusta valores y calcula</p>
                    <p className="text-sm">para ver tus ganancias potenciales</p>
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* Package ROI Calculator Section */}
      <section id="calculator" className="py-20 bg-gray-50">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-12">
            <Badge className="bg-blue-100 text-blue-700 border-blue-200 px-4 py-2 mb-6 text-sm font-semibold">
              <Calculator className="w-4 h-4 mr-2" />
              Calculadora ROI por Licencias
            </Badge>
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Calcula tu ROI</h2>
            <p className="text-xl text-gray-600">Ve cuánto puedes ganar vendiendo licencias a tus estudiantes</p>
          </div>
          
          <Card className="bg-white border-2 border-gray-200 rounded-3xl overflow-hidden">
            <div className="grid lg:grid-cols-2">
              {/* Inputs */}
              <div className="p-8 border-r border-gray-200">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Configura tu escenario</h3>
                
                <div className="space-y-6">
                  <div>
                    <div className="flex justify-between mb-2">
                      <Label className="text-gray-700 font-semibold">Número de Licencias (Estudiantes)</Label>
                      <span className="text-[#58CC02] font-bold text-lg">{numLicenses}</span>
                    </div>
                    <Slider
                      value={[numLicenses]}
                      onValueChange={([v]) => setNumLicenses(v)}
                      max={600}
                      min={1}
                      step={1}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                      <span>1</span>
                      <span>20</span>
                      <span>100</span>
                      <span>500</span>
                      <span>600</span>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <Label className="text-gray-700 font-semibold">Precio que cobras por licencia ($)</Label>
                      <span className="text-[#58CC02] font-bold text-lg">${pricePerStudent}</span>
                    </div>
                    <Slider
                      value={[pricePerStudent]}
                      onValueChange={([v]) => setPricePerStudent(v)}
                      max={100}
                      min={15}
                      step={5}
                      className="w-full"
                    />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <Label className="text-gray-700 font-semibold flex items-center gap-2">
                        <Brain className="w-4 h-4 text-purple-600" />
                        AI Tutor por licencia (min)
                      </Label>
                      <span className="text-purple-600 font-bold text-lg">{aiTutorMinutes} min</span>
                    </div>
                    <Slider
                      value={[aiTutorMinutes]}
                      onValueChange={([v]) => setAiTutorMinutes(v)}
                      max={120}
                      min={0}
                      step={30}
                      className="w-full"
                    />
                    {aiTutorMinutes > 0 && (
                      <p className="text-sm text-purple-600 mt-1">
                        + ${(aiTutorMinutes * 0.20).toFixed(2)} por licencia (AI Tutor)
                      </p>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Results */}
              <div className="p-8 bg-gradient-to-br from-green-50 to-white">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Tu Proyección de ROI</h3>
                
                {packageRoiResult ? (
                  <div className="space-y-4" data-testid="package-roi-results">
                    <div className="bg-white rounded-xl p-4 border border-gray-200">
                      <div className="text-sm text-gray-500 mb-1">Tier Aplicado</div>
                      <div className="font-bold text-gray-900">{packageRoiResult.tier.description}</div>
                      <div className="text-sm text-[#58CC02]">
                        ${packageRoiResult.tier.price_per_license}/licencia · ${packageRoiResult.tier.price_per_exam}/examen · {packageRoiResult.tier.discount} descuento
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Tu margen base: <span className="font-bold text-green-600">{packageRoiResult.tier.your_margin}</span>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-red-50 rounded-xl p-4 border border-red-200">
                        <div className="text-sm text-gray-500">TU COSTE / Licencia</div>
                        <div className="text-2xl font-extrabold text-red-600">${packageRoiResult.per_license.your_cost}</div>
                      </div>
                      <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
                        <div className="text-sm text-gray-500">TU PRECIO / Licencia</div>
                        <div className="text-2xl font-extrabold text-blue-600">${packageRoiResult.per_license.your_price}</div>
                      </div>
                    </div>
                    
                    <div className="bg-white rounded-xl p-4 border border-gray-200">
                      <div className="text-sm text-gray-500 mb-2">Por Licencia Incluye</div>
                      <div className="flex gap-4 flex-wrap">
                        <Badge className="bg-purple-100 text-purple-700 border-0">
                          {packageRoiResult.per_license.mock_tests} mock tests
                        </Badge>
                        {packageRoiResult.per_license.ai_tutor_minutes > 0 && (
                          <Badge className="bg-orange-100 text-orange-700 border-0">
                            {packageRoiResult.per_license.ai_tutor_minutes} min AI tutor
                          </Badge>
                        )}
                      </div>
                    </div>
                    
                    <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-5 text-white">
                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                          <div className="text-green-100 text-sm">Tu Inversión</div>
                          <div className="text-xl font-bold">${packageRoiResult.totals.your_investment}</div>
                        </div>
                        <div>
                          <div className="text-green-100 text-sm">Tus Ingresos</div>
                          <div className="text-xl font-bold">${packageRoiResult.totals.your_revenue}</div>
                        </div>
                        <div>
                          <div className="text-green-100 text-sm">Tu Ganancia</div>
                          <div className="text-xl font-bold">${packageRoiResult.totals.your_profit}</div>
                        </div>
                      </div>
                      <div className="mt-4 pt-4 border-t border-green-400 flex justify-between items-center">
                        <div className="text-green-100">Tu Margen: {packageRoiResult.per_license.your_margin}%</div>
                        <div className="text-3xl font-extrabold">{packageRoiResult.totals.roi_percentage}% ROI</div>
                      </div>
                    </div>
                    
                    <div className="bg-yellow-50 rounded-xl p-4 border border-yellow-200">
                      <div className="flex items-start gap-3">
                        <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                        <div className="text-sm text-yellow-800">{packageRoiResult.recommendation}</div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-400">
                    <Calculator className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Ajusta los parámetros para ver tu proyección de ROI</p>
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* ROI Calculator Section - Operations */}
      <section id="calculator-ops" className="py-20">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Calculate Your ROI</h2>
            <p className="text-xl text-gray-600">See how AI can multiply your capacity without hiring more teachers</p>
          </div>
          
          <Card className="bg-white border-2 border-gray-200 rounded-3xl overflow-hidden" data-testid="roi-calculator">
            <div className="grid lg:grid-cols-2">
              {/* Calculator Inputs */}
              <div className="p-8 lg:p-12 border-r border-gray-200">
                <h3 className="text-2xl font-bold text-gray-900 mb-8 flex items-center gap-3">
                  <Calculator className="w-7 h-7 text-[#58CC02]" />
                  Your Current Numbers
                </h3>
                
                <div className="space-y-8">
                  <div>
                    <div className="flex justify-between mb-3">
                      <Label className="text-gray-700 font-semibold">Current Students</Label>
                      <span className="text-[#58CC02] font-bold text-lg">{calculatorValues.students}</span>
                    </div>
                    <Slider
                      value={[calculatorValues.students]}
                      onValueChange={([v]) => setCalculatorValues(prev => ({ ...prev, students: v }))}
                      max={200}
                      min={10}
                      step={10}
                      className="w-full"
                    />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-3">
                      <Label className="text-gray-700 font-semibold">Current Teachers</Label>
                      <span className="text-[#58CC02] font-bold text-lg">{calculatorValues.teachers}</span>
                    </div>
                    <Slider
                      value={[calculatorValues.teachers]}
                      onValueChange={([v]) => setCalculatorValues(prev => ({ ...prev, teachers: v }))}
                      max={20}
                      min={1}
                      step={1}
                      className="w-full"
                    />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-3">
                      <Label className="text-gray-700 font-semibold">Current Pass Rate</Label>
                      <span className="text-[#58CC02] font-bold text-lg">{calculatorValues.passRate}%</span>
                    </div>
                    <Slider
                      value={[calculatorValues.passRate]}
                      onValueChange={([v]) => setCalculatorValues(prev => ({ ...prev, passRate: v }))}
                      max={90}
                      min={40}
                      step={5}
                      className="w-full"
                    />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-3">
                      <Label className="text-gray-700 font-semibold">No-Show Rate</Label>
                      <span className="text-orange-500 font-bold text-lg">{calculatorValues.noShowRate}%</span>
                    </div>
                    <Slider
                      value={[calculatorValues.noShowRate]}
                      onValueChange={([v]) => setCalculatorValues(prev => ({ ...prev, noShowRate: v }))}
                      max={40}
                      min={5}
                      step={5}
                      className="w-full"
                    />
                  </div>
                  
                  <div>
                    <Label className="text-gray-700 font-semibold block mb-3">Average Teacher Salary ($/month)</Label>
                    <Input
                      type="number"
                      value={calculatorValues.teacherSalary}
                      onChange={(e) => setCalculatorValues(prev => ({ ...prev, teacherSalary: parseInt(e.target.value) || 0 }))}
                      className="input-duo"
                      placeholder="3000"
                    />
                  </div>
                </div>
                
                <button className="btn-duo w-full py-4 mt-8 text-lg" onClick={calculateROI} disabled={calculating} data-testid="calculate-roi-btn">
                  {calculating ? 'Calculating...' : 'Calculate My ROI'}
                </button>
              </div>
              
              {/* Results */}
              <div className="p-8 lg:p-12 bg-gradient-to-br from-green-50 to-white">
                <h3 className="text-2xl font-bold text-gray-900 mb-8 flex items-center gap-3">
                  <TrendingUp className="w-7 h-7 text-[#58CC02]" />
                  Your Projected Results
                </h3>
                
                {roiResults ? (
                  <div className="space-y-6 animate-fade-in" data-testid="roi-results">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-white rounded-2xl p-5 border-2 border-green-100">
                        <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
                          <Users className="w-4 h-4" />
                          Student Capacity
                        </div>
                        <div className="text-3xl font-extrabold text-[#58CC02]">{roiResults.studentMultiplier}x</div>
                        <div className="text-sm text-gray-500">{roiResults.currentStudents} → {roiResults.potentialStudents}</div>
                      </div>
                      
                      <div className="bg-white rounded-2xl p-5 border-2 border-blue-100">
                        <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
                          <Target className="w-4 h-4" />
                          Pass Rate
                        </div>
                        <div className="text-3xl font-extrabold text-blue-500">{roiResults.improvedPassRate}%</div>
                        <div className="text-sm text-gray-500">From {roiResults.currentPassRate}%</div>
                      </div>
                      
                      <div className="bg-white rounded-2xl p-5 border-2 border-orange-100">
                        <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
                          <AlertTriangle className="w-4 h-4" />
                          No-Show Rate
                        </div>
                        <div className="text-3xl font-extrabold text-orange-500">{roiResults.reducedNoShow.toFixed(0)}%</div>
                        <div className="text-sm text-gray-500">From {roiResults.currentNoShow}%</div>
                      </div>
                      
                      <div className="bg-white rounded-2xl p-5 border-2 border-purple-100">
                        <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
                          <Clock className="w-4 h-4" />
                          Time Saved
                        </div>
                        <div className="text-3xl font-extrabold text-purple-500">{roiResults.timeSavedWeekly}h</div>
                        <div className="text-sm text-gray-500">Per week</div>
                      </div>
                    </div>
                    
                    {/* Key insight - No hiring needed */}
                    <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
                      <div className="flex items-start gap-3">
                        <Users className="w-5 h-5 text-blue-600 mt-0.5" />
                        <div>
                          <div className="font-bold text-blue-800">No New Hires Needed</div>
                          <div className="text-sm text-blue-600">
                            Your {calculatorValues.teachers} teachers can handle {roiResults.potentialStudents} students with AI support.
                            Without AI, you&apos;d need to hire <strong>{roiResults.teachersYouWouldNeedToHire} additional teachers</strong>.
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-2xl p-6 text-white">
                      <div className="text-green-100 text-sm font-semibold mb-2">Total Annual Benefit</div>
                      <div className="text-4xl font-extrabold">${roiResults.totalAnnualBenefit.toLocaleString()}</div>
                      <div className="text-green-100 text-sm mt-2">
                        Revenue increase: ${roiResults.revenueIncrease.toLocaleString()} + Hiring cost avoided: ${roiResults.hiringCostAvoided.toLocaleString()}
                      </div>
                    </div>
                    
                    <button className="btn-duo w-full py-4 text-lg" onClick={() => navigate('/register')}>
                      Start Your Free Trial
                    </button>
                  </div>
                ) : (
                  <div className="text-center py-16 text-gray-400">
                    <Calculator className="w-16 h-16 mx-auto mb-4 opacity-30" />
                    <p className="font-semibold">Enter your numbers and click Calculate</p>
                    <p className="text-sm">to see your projected ROI</p>
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-[#58CC02]">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl font-extrabold text-white mb-6">Ready to Transform Your Institution?</h2>
          <p className="text-xl text-green-100 mb-8">Join 500+ institutions already scaling with AI-powered learning</p>
          <div className="flex justify-center gap-4">
            <button className="bg-white text-[#58CC02] px-8 py-4 rounded-2xl font-bold text-lg hover:bg-gray-100 transition-all shadow-lg" onClick={() => navigate('/register')}>
              Start Free Trial
              <ArrowRight className="w-5 h-5 ml-2 inline" />
            </button>
            <button className="border-2 border-white text-white px-8 py-4 rounded-2xl font-bold text-lg hover:bg-white/10 transition-all">
              Schedule Demo
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-12">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-xl bg-[#58CC02] flex items-center justify-center">
                  <GraduationCap className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold">ProficientHub</span>
              </div>
              <p className="text-gray-400">The leading AI-powered platform for English proficiency exam preparation.</p>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#features" className="hover:text-white">Features</a></li>
                <li><a href="#exams" className="hover:text-white">Exams</a></li>
                <li><a href="#pricing" className="hover:text-white">Pricing</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Careers</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white">Terms of Service</a></li>
              </ul>
            </div>
          </div>
          
          <div className="mt-12 pt-8 border-t border-gray-800 text-center text-gray-400">
            © 2024 ProficientHub. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
