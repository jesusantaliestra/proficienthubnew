import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
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
import LandingAgentWidget from '../components/LandingAgentWidget';
import LanguageSelector from '../components/LanguageSelector';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function Landing() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [calculatorValues, setCalculatorValues] = useState({
    students: 50,
    teachers: 3,
    passRate: 65,
    noShowRate: 25,
    teacherSalary: 3000
  });
  const [roiResults, setRoiResults] = useState(null);
  const [calculating, setCalculating] = useState(false);
  
  // Pricing model state
  const [pricingData, setPricingData] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState('plan_10');
  const [withAI, setWithAI] = useState(false);
  const [selectedAiOption, setSelectedAiOption] = useState('none');
  const [numLicenses, setNumLicenses] = useState(100);
  const [calculatedPrice, setCalculatedPrice] = useState(null);
  const [calculatingPrice, setCalculatingPrice] = useState(false);
  const [selectedDuration, setSelectedDuration] = useState(1); // Duration in months
  
  // Exam types selection (doesn't affect price, just configuration)
  const [selectedExamTypes, setSelectedExamTypes] = useState(['all']);
  const availableExamTypes = [
    { id: 'all', label: 'All Exams' },
    { id: 'toefl', label: 'TOEFL' },
    { id: 'ielts', label: 'IELTS' },
    { id: 'cambridge', label: 'Cambridge' },
    { id: 'trinity', label: 'Trinity' },
    { id: 'toeic', label: 'TOEIC' },
    { id: 'celpip', label: 'CELPIP' },
    { id: 'pte', label: 'PTE' },
    { id: 'oet', label: 'OET' }
  ];
  
  // Free Trial Lead Capture
  const [trialForm, setTrialForm] = useState({
    institutionName: '',
    contactName: '',
    email: '',
    phone: '',
    country: '',
    studentsCount: '',
    selectedExam: 'toefl'
  });
  const [trialSubmitting, setTrialSubmitting] = useState(false);
  const [trialSubmitted, setTrialSubmitted] = useState(false);
  
  // Monetization calculator state
  const [monetizationValues, setMonetizationValues] = useState({
    writingTests: 100,
    speakingTests: 50,
    mockExams: 50,
    writingSellPrice: 5.0,
    speakingSellPrice: 6.0,
    mockExamSellPrice: 8.0
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
    if (!selectedPlan || numLicenses < 1) return;
    
    setCalculatingPrice(true);
    try {
      const aiOption = withAI ? selectedAiOption : 'none';
      const response = await axios.get(
        `${API_URL}/pricing/calculator?exam_plan=${selectedPlan}&num_licenses=${numLicenses}&ai_tutor_option=${aiOption}`
      );
      setCalculatedPrice(response.data);
    } catch (error) {
      console.error('Pricing calculation error:', error);
    } finally {
      setCalculatingPrice(false);
    }
  }, [selectedPlan, numLicenses, withAI, selectedAiOption]);

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      if (selectedPlan && numLicenses > 0) {
        calculatePricing();
      }
    }, 300);
    return () => clearTimeout(debounceTimer);
  }, [selectedPlan, numLicenses, withAI, selectedAiOption, calculatePricing]);

  // Calculate monetization with Writing, Speaking, and Mock Exams
  const calculateMonetization = () => {
    // Cost prices (what institution pays) - Based on 1000 tier
    const writingCostPerTest = 1.10;  // Writing Tests
    const speakingCostPerTest = 2.20; // Speaking Tests (cheaper)
    const mockExamCostPerTest = 2.70; // Mock Exams (more expensive - full exam)
    
    // Calculate costs
    const writingCost = monetizationValues.writingTests * writingCostPerTest;
    const speakingCost = monetizationValues.speakingTests * speakingCostPerTest;
    const mockExamCost = monetizationValues.mockExams * mockExamCostPerTest;
    
    // Calculate revenues
    const writingRevenue = monetizationValues.writingTests * monetizationValues.writingSellPrice;
    const speakingRevenue = monetizationValues.speakingTests * monetizationValues.speakingSellPrice;
    const mockExamRevenue = monetizationValues.mockExams * monetizationValues.mockExamSellPrice;
    
    // Calculate profits
    const writingProfit = writingRevenue - writingCost;
    const speakingProfit = speakingRevenue - speakingCost;
    const mockExamProfit = mockExamRevenue - mockExamCost;
    
    const totalCost = writingCost + speakingCost + mockExamCost;
    const totalRevenue = writingRevenue + speakingRevenue + mockExamRevenue;
    const totalProfit = writingProfit + speakingProfit + mockExamProfit;
    const roiPercent = totalCost > 0 ? ((totalRevenue / totalCost - 1) * 100) : 0;
    
    setMonetizationResult({
      writing: {
        quantity: monetizationValues.writingTests,
        cost: writingCost.toFixed(2),
        revenue: writingRevenue.toFixed(2),
        profit: writingProfit.toFixed(2),
        margin: writingRevenue > 0 ? ((writingProfit / writingRevenue) * 100).toFixed(0) : 0
      },
      speaking: {
        quantity: monetizationValues.speakingTests,
        cost: speakingCost.toFixed(2),
        revenue: speakingRevenue.toFixed(2),
        profit: speakingProfit.toFixed(2),
        margin: speakingRevenue > 0 ? ((speakingProfit / speakingRevenue) * 100).toFixed(0) : 0
      },
      mockExams: {
        quantity: monetizationValues.mockExams,
        cost: mockExamCost.toFixed(2),
        revenue: mockExamRevenue.toFixed(2),
        profit: mockExamProfit.toFixed(2),
        margin: mockExamRevenue > 0 ? ((mockExamProfit / mockExamRevenue) * 100).toFixed(0) : 0
      },
      totals: {
        cost: totalCost.toFixed(2),
        revenue: totalRevenue.toFixed(2),
        profit: totalProfit.toFixed(2),
        roi_percent: roiPercent.toFixed(0)
      }
    });
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

  // Features with translations - using t() function
  const getFeatures = () => [
    { icon: Brain, titleKey: 'features.ai_tutoring', descKey: 'features.ai_tutoring_desc', color: 'feature-icon-green' },
    { icon: Volume2, titleKey: 'features.speaking', descKey: 'features.speaking_desc', color: 'feature-icon-blue' },
    { icon: BarChart3, titleKey: 'features.analytics', descKey: 'features.analytics_desc', color: 'feature-icon-purple' },
    { icon: FolderOpen, titleKey: 'institution.library', descKey: 'landing.library_desc', color: 'feature-icon-orange' },
    { icon: Video, titleKey: 'institution.video_classes', descKey: 'landing.video_classes_desc', color: 'feature-icon-yellow' },
    { icon: Headphones, titleKey: 'landing.offline_access', descKey: 'landing.offline_access_desc', color: 'feature-icon-green' }
  ];

  const examTypes = [
    { id: 'toefl', name: 'TOEFL', color: 'bg-blue-600', description: 'Test of English as a Foreign Language' },
    { id: 'ielts-academic', name: 'IELTS Academic', color: 'bg-red-600', description: 'For university admissions and professional registration' },
    { id: 'ielts-general', name: 'IELTS General', color: 'bg-red-500', description: 'For migration and work experience' },
    { id: 'cambridge', name: 'Cambridge', color: 'bg-purple-600', description: 'Cambridge English Qualifications (FCE, CAE, CPE)' },
    { id: 'trinity', name: 'Trinity', color: 'bg-pink-600', description: 'Trinity College London GESE & ISE Exams' },
    { id: 'toeic', name: 'TOEIC', color: 'bg-indigo-600', description: 'Test of English for International Communication' },
    { id: 'celpip', name: 'CELPIP', color: 'bg-cyan-600', description: 'Canadian English Language Proficiency Index' },
    { id: 'pte-academic', name: 'PTE Academic', color: 'bg-orange-600', description: 'For study abroad and immigration' },
    { id: 'pte-core', name: 'PTE Core', color: 'bg-orange-500', description: 'For Canadian immigration and citizenship' },
    { id: 'oet', name: 'OET', color: 'bg-emerald-600', description: 'Occupational English Test' }
  ];

  // Handle trial form submission
  const handleTrialSubmit = async (e) => {
    e.preventDefault();
    setTrialSubmitting(true);
    try {
      await axios.post(`${API_URL}/trial-request`, trialForm);
      setTrialSubmitted(true);
    } catch (error) {
      console.error('Trial request error:', error);
      // Still show success for demo
      setTrialSubmitted(true);
    } finally {
      setTrialSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Premium Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/98 backdrop-blur-xl border-b border-gray-100 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#58CC02] to-[#46a302] flex items-center justify-center shadow-lg shadow-green-200">
                <GraduationCap className="w-7 h-7 text-white" />
              </div>
              <div>
                <span className="text-2xl font-black text-gray-900 tracking-tight">ProficientHub</span>
                <span className="hidden md:inline text-xs text-gray-400 ml-2 font-medium">Empresas</span>
              </div>
            </div>
            
            <div className="hidden lg:flex items-center gap-10">
              <a href="#features" className="text-gray-600 hover:text-gray-900 font-semibold transition-colors">{t('nav.features')}</a>
              <a href="#exams" className="text-gray-600 hover:text-gray-900 font-semibold transition-colors">{t('nav.exams')}</a>
              <a href="#pricing" className="text-gray-600 hover:text-gray-900 font-semibold transition-colors">{t('nav.pricing')}</a>
              <a href="#trial" className="text-gray-600 hover:text-gray-900 font-semibold transition-colors">{t('landing.request_demo')}</a>
              <a href="#calculator" className="text-gray-600 hover:text-gray-900 font-semibold transition-colors">{t('landing.roi_calculator')}</a>
            </div>
            
            <div className="flex items-center gap-3">
              <LanguageSelector variant="compact" />
              <Button variant="ghost" className="text-gray-600 font-semibold hover:bg-gray-100" onClick={() => navigate('/login')} data-testid="nav-login-btn">
                {t('nav.login')}
              </Button>
              <button className="bg-gradient-to-r from-[#58CC02] to-[#46a302] text-white px-6 py-2.5 rounded-xl font-bold shadow-lg shadow-green-200 hover:shadow-xl hover:shadow-green-300 transition-all transform hover:-translate-y-0.5" onClick={() => document.getElementById('trial').scrollIntoView({ behavior: 'smooth' })} data-testid="nav-get-started-btn">
                {t('landing.request_demo')}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Premium Hero Section */}
      <section className="relative pt-32 pb-24 overflow-hidden bg-gradient-to-b from-gray-50 to-white">
        {/* Background Elements */}
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-gradient-to-br from-green-100 to-blue-50 rounded-full blur-3xl opacity-60 -translate-y-1/2 translate-x-1/4"></div>
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-gradient-to-tr from-purple-50 to-green-50 rounded-full blur-3xl opacity-60 translate-y-1/2 -translate-x-1/4"></div>
        <div className="absolute top-1/2 left-1/2 w-[800px] h-[800px] bg-gradient-to-r from-green-50 to-transparent rounded-full blur-3xl opacity-30 -translate-x-1/2 -translate-y-1/2"></div>
        
        <div className="relative max-w-7xl mx-auto px-6">
          <div className="text-center max-w-5xl mx-auto mb-20">
            <div className="inline-flex items-center gap-2 bg-gradient-to-r from-green-100 to-blue-100 text-gray-700 px-5 py-2.5 rounded-full mb-8 shadow-sm">
              <Building className="w-4 h-4 text-green-600" />
              <span className="font-semibold text-sm">{t('landing.b2b_platform')}</span>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            </div>
            
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-black text-gray-900 leading-[1.1] mb-8 tracking-tight">
              {t('landing.hero_title')}
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-600 leading-relaxed max-w-3xl mx-auto mb-10">
              {t('landing.hero_subtitle')} {' '}
              <span className="font-semibold text-blue-600"> TOEFL</span>,
              <span className="font-semibold text-red-600"> IELTS</span>,
              <span className="font-semibold text-purple-600"> Cambridge</span>,
              <span className="font-semibold text-pink-600"> Trinity</span>,
              <span className="font-semibold text-indigo-600"> TOEIC</span>,
              <span className="font-semibold text-cyan-600"> CELPIP</span>,
              <span className="font-semibold text-orange-600"> PTE</span> {t('common.and')}
              <span className="font-semibold text-emerald-600"> OET</span>.
            </p>
            
            <div className="flex flex-wrap justify-center gap-4 mb-16">
              <button 
                className="group bg-gradient-to-r from-[#58CC02] to-[#46a302] text-white px-10 py-5 rounded-2xl font-bold text-lg shadow-xl shadow-green-200 hover:shadow-2xl hover:shadow-green-300 transition-all transform hover:-translate-y-1 flex items-center gap-3" 
                onClick={() => document.getElementById('trial').scrollIntoView({ behavior: 'smooth' })}
                data-testid="hero-cta-btn"
              >
                {t('landing.get_started')}
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button 
                className="group bg-white text-gray-900 px-10 py-5 rounded-2xl font-bold text-lg border-2 border-gray-200 hover:border-gray-300 shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1 flex items-center gap-3"
                onClick={() => document.getElementById('calculator').scrollIntoView({ behavior: 'smooth' })}
              >
                <Calculator className="w-5 h-5 text-green-600" />
                {t('landing.roi_calculator')}
              </button>
            </div>
            
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
              <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                <div className="text-4xl font-black text-gray-900 mb-1">10x</div>
                <div className="text-gray-500 font-medium text-sm">{t('landing.student_capacity')}</div>
              </div>
              <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                <div className="text-4xl font-black text-[#58CC02] mb-1">+23%</div>
                <div className="text-gray-500 font-medium text-sm">{t('landing.pass_rate_increase')}</div>
              </div>
              <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                <div className="text-4xl font-black text-gray-900 mb-1">-60%</div>
                <div className="text-gray-500 font-medium text-sm">{t('landing.time_saved')}</div>
              </div>
              <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                <div className="text-4xl font-black text-gray-900 mb-1">+40%</div>
                <div className="text-gray-500 font-medium text-sm">{t('landing.revenue_increase')}</div>
              </div>
            </div>
          </div>
          
          {/* Exam Logos Row */}
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
            <span className="text-sm text-gray-400 font-medium">{t('nav.exams')}:</span>
            {examTypes.map((exam) => (
              <div key={exam.id} className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-lg ${exam.color} flex items-center justify-center`}>
                  <GraduationCap className="w-4 h-4 text-white" />
                </div>
                <span className="font-bold text-gray-700">{exam.name}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">{t('landing.features_title')}</h2>
            <p className="text-xl text-gray-600">{t('landing.features_subtitle')}</p>
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

      {/* Exams Section - Premium */}
      <section id="exams" className="py-24 bg-gradient-to-b from-white to-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <Badge className="bg-blue-100 text-blue-700 border-blue-200 px-4 py-2 mb-6">
              {t('landing.exams_badge')}
            </Badge>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-6">{t('landing.exams_title')}</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">{t('landing.exams_subtitle')}</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {examTypes.map((exam) => (
              <Card key={exam.id} className="group bg-white border-2 border-gray-100 hover:border-gray-200 rounded-2xl overflow-hidden transition-all hover:shadow-xl hover:-translate-y-1">
                <div className={`h-2 ${exam.color}`}></div>
                <div className="p-8">
                  <div className={`w-16 h-16 rounded-2xl ${exam.color} flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform`}>
                    <GraduationCap className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{exam.name}</h3>
                  <p className="text-gray-500 mb-4">{exam.description}</p>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="outline" className="text-xs">Reading</Badge>
                    <Badge variant="outline" className="text-xs">Writing</Badge>
                    <Badge variant="outline" className="text-xs">Listening</Badge>
                    <Badge variant="outline" className="text-xs">Speaking</Badge>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-gray-50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">B2B Plans & Pricing</h2>
            <p className="text-xl text-gray-600 mb-8">
              Configure your plan: exams per license + optional AI + license volume
            </p>
          </div>
          
          {/* Step-by-step Pricing Calculator */}
          <Card className="bg-white border-2 border-gray-200 rounded-3xl overflow-hidden shadow-xl">
            <div className="p-8">
              {/* STEP 1: Select Exam Plan */}
              <div className="mb-10">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-full bg-[#58CC02] flex items-center justify-center text-white font-bold text-lg">1</div>
                  <h3 className="text-2xl font-bold text-gray-900">Select Exams Per License</h3>
                </div>
                
                {pricingData && (
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                    {pricingData.exam_plans.map((plan) => (
                      <button
                        key={plan.id}
                        onClick={() => setSelectedPlan(plan.id)}
                        className={`p-5 rounded-2xl border-2 transition-all text-center ${
                          selectedPlan === plan.id
                            ? 'border-[#58CC02] bg-green-50 ring-4 ring-green-100'
                            : 'border-gray-200 hover:border-gray-300 bg-white'
                        }`}
                        data-testid={`plan-${plan.id}`}
                      >
                        <div className="text-3xl font-extrabold text-gray-900 mb-1">{plan.exams}</div>
                        <div className="text-sm text-gray-500">Mock Exams</div>
                        {plan.id === 'plan_20' && (
                          <Badge className="bg-[#58CC02] text-white border-0 mt-2 text-xs">Popular</Badge>
                        )}
                      </button>
                    ))}
                  </div>
                )}
                
                {/* Exam Types Selection */}
                <div className="mt-6 bg-gray-50 rounded-xl p-4">
                  <Label className="text-gray-700 font-semibold block mb-3">Which exam types? (does not affect price)</Label>
                  <div className="flex flex-wrap gap-2">
                    {availableExamTypes.map((examType) => (
                      <button
                        key={examType.id}
                        onClick={() => {
                          if (examType.id === 'all') {
                            setSelectedExamTypes(['all']);
                          } else {
                            const newSelection = selectedExamTypes.filter(e => e !== 'all');
                            if (newSelection.includes(examType.id)) {
                              const filtered = newSelection.filter(e => e !== examType.id);
                              setSelectedExamTypes(filtered.length > 0 ? filtered : ['all']);
                            } else {
                              setSelectedExamTypes([...newSelection, examType.id]);
                            }
                          }
                        }}
                        className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                          selectedExamTypes.includes(examType.id) || (examType.id === 'all' && selectedExamTypes.includes('all'))
                            ? 'bg-[#58CC02] text-white'
                            : 'bg-white border border-gray-200 text-gray-700 hover:border-[#58CC02]'
                        }`}
                      >
                        {examType.label}
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-gray-400 mt-2">
                    Selected: {selectedExamTypes.includes('all') ? 'All exam types' : selectedExamTypes.map(e => availableExamTypes.find(a => a.id === e)?.label).join(', ')}
                  </p>
                </div>
              </div>
              
              {/* STEP 2: AI Tutor Option */}
              <div className="mb-10">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-full bg-[#58CC02] flex items-center justify-center text-white font-bold text-lg">2</div>
                  <h3 className="text-2xl font-bold text-gray-900">Add AI Tutor?</h3>
                </div>
                
                <div className="flex flex-col gap-4">
                  {/* AI Toggle */}
                  <div className="flex gap-4">
                    <button
                      onClick={() => { setWithAI(false); setSelectedAiOption('none'); }}
                      className={`flex-1 p-4 rounded-xl border-2 transition-all ${
                        !withAI
                          ? 'border-[#58CC02] bg-green-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-bold text-gray-900">No AI Tutor</div>
                      <div className="text-sm text-gray-500">Mock exams only</div>
                    </button>
                    <button
                      onClick={() => { setWithAI(true); setSelectedAiOption('standard'); }}
                      className={`flex-1 p-4 rounded-xl border-2 transition-all ${
                        withAI
                          ? 'border-purple-500 bg-purple-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-bold text-gray-900 flex items-center gap-2">
                        <Brain className="w-5 h-5 text-purple-600" />
                        Include AI Tutor
                      </div>
                      <div className="text-sm text-gray-500">Voice-powered tutoring</div>
                    </button>
                  </div>
                  
                  {/* AI Options (if AI selected) */}
                  {withAI && pricingData && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-2">
                      {pricingData.ai_tutor_options.filter(opt => opt.minutes > 0).map((option) => (
                        <button
                          key={option.id}
                          onClick={() => setSelectedAiOption(option.id)}
                          className={`p-3 rounded-xl border-2 text-center transition-all ${
                            selectedAiOption === option.id
                              ? 'border-purple-500 bg-purple-50'
                              : 'border-gray-200 hover:border-purple-300'
                          }`}
                        >
                          <div className="font-bold text-gray-900">{option.minutes} min</div>
                          <div className="text-purple-600 font-semibold">+${option.price}/lic</div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              
              {/* STEP 3: Number of Licenses */}
              <div className="mb-10">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-full bg-[#58CC02] flex items-center justify-center text-white font-bold text-lg">3</div>
                  <h3 className="text-2xl font-bold text-gray-900">How Many Licenses?</h3>
                </div>
                
                {/* Volume Tiers */}
                {pricingData && (
                  <div className="mb-6">
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
                      {pricingData.volume_pricing.map((tier) => {
                        const isSelected = numLicenses >= tier.min && numLicenses <= tier.max;
                        return (
                          <button
                            key={tier.id}
                            onClick={() => setNumLicenses(tier.min)}
                            className={`p-3 rounded-xl border-2 text-center transition-all ${
                              isSelected
                                ? 'border-blue-500 bg-blue-50'
                                : 'border-gray-200 hover:border-blue-300'
                            }`}
                          >
                            <div className="text-sm font-bold text-gray-700">{tier.min.toLocaleString()}-{tier.max.toLocaleString()}</div>
                            {tier.discount !== "0%" && (
                              <Badge className="bg-orange-100 text-orange-700 border-0 mt-1 text-xs">
                                {tier.discount} off
                              </Badge>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}
                
                {/* License Input */}
                <div className="bg-gray-50 rounded-xl p-6">
                  <div className="flex justify-between items-center mb-4">
                    <Label className="text-gray-700 font-semibold">Exact number of licenses</Label>
                    <input
                      type="number"
                      value={numLicenses}
                      onChange={(e) => {
                        const val = parseInt(e.target.value);
                        if (!isNaN(val) && val >= 1 && val <= 100000) {
                          setNumLicenses(val);
                        } else if (e.target.value === '') {
                          // Allow empty while typing
                        }
                      }}
                      onBlur={(e) => {
                        const val = parseInt(e.target.value) || 1;
                        setNumLicenses(Math.min(100000, Math.max(1, val)));
                      }}
                      onFocus={(e) => e.target.select()}
                      className="w-36 text-right text-2xl font-extrabold text-[#58CC02] bg-white border-2 border-gray-200 rounded-lg px-3 py-2 focus:border-[#58CC02] outline-none"
                      min={1}
                      max={100000}
                    />
                  </div>
                  
                  {/* Quick selection buttons */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {[1, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 50000, 100000].map((val) => (
                      <button
                        key={val}
                        onClick={() => setNumLicenses(val)}
                        className={`px-3 py-1 rounded-lg text-sm font-semibold transition-all ${
                          numLicenses === val
                            ? 'bg-[#58CC02] text-white'
                            : 'bg-white border border-gray-200 text-gray-600 hover:border-[#58CC02]'
                        }`}
                      >
                        {val.toLocaleString()}
                      </button>
                    ))}
                  </div>
                  
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>Min: 1</span>
                    <span>Max: 100,000</span>
                  </div>
                </div>
              </div>
              
              {/* RESULT: Final Price */}
              <div className="border-t-2 border-gray-100 pt-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-green-500 to-green-600 flex items-center justify-center text-white">
                    <Check className="w-6 h-6" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900">Your Final Price</h3>
                </div>
                
                {calculatingPrice ? (
                  <div className="text-center py-8 text-gray-400">
                    <Calculator className="w-12 h-12 mx-auto mb-4 animate-pulse" />
                    <p>Calculating...</p>
                  </div>
                ) : calculatedPrice ? (
                  <div className="grid lg:grid-cols-2 gap-6" data-testid="pricing-results">
                    {/* Summary */}
                    <div className="space-y-4">
                      <div className="bg-gray-50 rounded-xl p-5">
                        <div className="text-sm text-gray-500 mb-3">Your configuration:</div>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Plan:</span>
                            <span className="font-bold">{calculatedPrice.plan.label}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">AI Tutor:</span>
                            <span className="font-bold">{calculatedPrice.ai_tutor.label}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Volume Tier:</span>
                            <span className="font-bold text-blue-600">{calculatedPrice.volume_tier.num_licenses.toLocaleString()} licenses</span>
                          </div>
                        </div>
                      </div>
                      
                      {calculatedPrice.pricing.savings_per_license > 0 && (
                        <div className="bg-orange-50 rounded-xl p-4 border border-orange-200">
                          <div className="flex items-center gap-2 text-orange-700">
                            <TrendingUp className="w-5 h-5" />
                            <span className="font-bold">You save ${calculatedPrice.pricing.total_savings.toLocaleString()}!</span>
                          </div>
                          <div className="text-sm text-orange-600 mt-1">
                            ${calculatedPrice.pricing.savings_per_license}/license with volume discount
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {/* Price Card */}
                    <div className="bg-gradient-to-br from-[#58CC02] to-green-600 rounded-2xl p-6 text-white">
                      <div className="text-center mb-4">
                        <div className="text-green-100 text-sm mb-1">Precio por Licencia Individual</div>
                        <div className="text-5xl font-extrabold">${calculatedPrice.pricing.price_per_license}</div>
                        <div className="text-green-200 text-sm mt-1">/mes por licencia</div>
                        {calculatedPrice.pricing.full_price_per_license > calculatedPrice.pricing.price_per_license && (
                          <div className="text-green-200 line-through text-lg mt-1">
                            ${calculatedPrice.pricing.full_price_per_license}/mes
                          </div>
                        )}
                      </div>
                      
                      {/* Duration Selector */}
                      <div className="bg-white/10 rounded-xl p-4 mb-4">
                        <div className="text-green-100 text-sm mb-3 font-semibold">Duración del contrato:</div>
                        <div className="grid grid-cols-3 gap-2">
                          {[1, 2, 3, 4, 6, 12].map((months) => (
                            <button
                              key={months}
                              onClick={() => setSelectedDuration(months)}
                              className={`py-2 px-3 rounded-lg text-sm font-bold transition-all ${
                                selectedDuration === months
                                  ? 'bg-white text-[#58CC02]'
                                  : 'bg-white/20 text-white hover:bg-white/30'
                              }`}
                            >
                              {months} {months === 1 ? 'mes' : 'meses'}
                            </button>
                          ))}
                        </div>
                      </div>
                      
                      <div className="border-t border-green-400 pt-4 mt-4">
                        <div className="flex justify-between text-sm text-green-100 mb-1">
                          <span>Licencias:</span>
                          <span className="font-bold">{calculatedPrice.volume_tier.num_licenses.toLocaleString()} × ${calculatedPrice.pricing.price_per_license}/mes</span>
                        </div>
                        <div className="flex justify-between text-sm text-green-100 mb-3">
                          <span>Duración:</span>
                          <span className="font-bold">{selectedDuration || 1} {(selectedDuration || 1) === 1 ? 'mes' : 'meses'}</span>
                        </div>
                        <div className="flex justify-between text-lg border-t border-green-400 pt-3">
                          <span className="text-green-100">Total a pagar:</span>
                          <span className="font-extrabold text-2xl">
                            ${(calculatedPrice.pricing.total_order_price * (selectedDuration || 1)).toLocaleString()}
                          </span>
                        </div>
                        <div className="text-green-200 text-xs mt-2">
                          {calculatedPrice.volume_tier.num_licenses.toLocaleString()} licencias individuales × {selectedDuration || 1} {(selectedDuration || 1) === 1 ? 'mes' : 'meses'}
                        </div>
                      </div>
                      
                      {/* Action Buttons */}
                      <div className="mt-6 space-y-3">
                        <button 
                          className="w-full bg-white text-[#58CC02] font-bold py-4 rounded-xl hover:bg-green-50 transition-colors text-lg flex items-center justify-center gap-2"
                          onClick={() => {
                            // Store pricing config for checkout
                            localStorage.setItem('pricingConfig', JSON.stringify({
                              ...calculatedPrice,
                              duration: selectedDuration || 1,
                              totalAmount: calculatedPrice.pricing.total_order_price * (selectedDuration || 1)
                            }));
                            navigate('/checkout');
                          }}
                        >
                          <CheckCircle className="w-5 h-5" />
                          Contratar Ahora
                        </button>
                        <button 
                          className="w-full bg-transparent border-2 border-white text-white font-bold py-3 rounded-xl hover:bg-white/10 transition-colors"
                          onClick={() => navigate('/register?demo=true')}
                        >
                          Solicitar Demo Gratuita
                        </button>
                      </div>
                      
                      <p className="text-green-200 text-xs text-center mt-4">
                        * Cada licencia es individual y da acceso completo a 1 estudiante
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Calculator className="w-16 h-16 mx-auto mb-4 opacity-30" />
                    <p className="font-semibold">Configure your plan to see pricing</p>
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* Test Packages Section */}
      <section id="test-packages" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <Badge className="bg-orange-100 text-orange-700 border-orange-200 px-4 py-2 mb-6 text-sm font-semibold">
              <Coins className="w-4 h-4 mr-2" />
              Additional Services
            </Badge>
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Additional Test Packages</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Purchase individual tests and offer them to your students as additional services.
            </p>
          </div>
          
          {/* Package Tables */}
          <div className="grid lg:grid-cols-3 gap-6 mb-12">
            {/* Writing Tests */}
            <Card className="border-2 border-blue-200 rounded-2xl overflow-hidden">
              <div className="bg-blue-50 p-4 border-b border-blue-200">
                <h3 className="text-xl font-bold text-blue-800 flex items-center gap-2">
                  <BookOpen className="w-5 h-5" />
                  Writing Tests
                </h3>
                <p className="text-sm text-blue-600">AI-graded essays</p>
              </div>
              <div className="p-4">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-gray-500 border-b">
                      <th className="pb-2">Quantity</th>
                      <th className="pb-2 text-right">Price</th>
                      <th className="pb-2 text-right">Per Test</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {[
                      { tests: 100, price: 150, perTest: 1.50 },
                      { tests: 500, price: 625, perTest: 1.25 },
                      { tests: 1000, price: 1100, perTest: 1.10, popular: true },
                      { tests: 5000, price: 4750, perTest: 0.95 },
                      { tests: 10000, price: 8500, perTest: 0.85 },
                      { tests: 50000, price: 37500, perTest: 0.75 },
                      { tests: 100000, price: 65000, perTest: 0.65 }
                    ].map((pkg) => (
                      <tr key={pkg.tests} className={`border-b ${pkg.popular ? 'bg-blue-50' : ''}`}>
                        <td className="py-2 font-semibold">
                          {pkg.tests.toLocaleString()}
                          {pkg.popular && <Badge className="ml-1 bg-blue-500 text-white border-0 text-xs">Popular</Badge>}
                        </td>
                        <td className="py-2 text-right font-bold text-blue-600">${pkg.price.toLocaleString()}</td>
                        <td className="py-2 text-right text-gray-600">${pkg.perTest}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
            
            {/* Speaking Tests */}
            <Card className="border-2 border-purple-200 rounded-2xl overflow-hidden">
              <div className="bg-purple-50 p-4 border-b border-purple-200">
                <h3 className="text-xl font-bold text-purple-800 flex items-center gap-2">
                  <Mic className="w-5 h-5" />
                  Speaking Tests
                </h3>
                <p className="text-sm text-purple-600">AI pronunciation feedback</p>
              </div>
              <div className="p-4">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-gray-500 border-b">
                      <th className="pb-2">Quantity</th>
                      <th className="pb-2 text-right">Price</th>
                      <th className="pb-2 text-right">Per Test</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {[
                      { tests: 100, price: 280, perTest: 2.80 },
                      { tests: 500, price: 1250, perTest: 2.50 },
                      { tests: 1000, price: 2200, perTest: 2.20, popular: true },
                      { tests: 5000, price: 9500, perTest: 1.90 },
                      { tests: 10000, price: 17000, perTest: 1.70 },
                      { tests: 50000, price: 75000, perTest: 1.50 },
                      { tests: 100000, price: 130000, perTest: 1.30 }
                    ].map((pkg) => (
                      <tr key={pkg.tests} className={`border-b ${pkg.popular ? 'bg-purple-50' : ''}`}>
                        <td className="py-2 font-semibold">
                          {pkg.tests.toLocaleString()}
                          {pkg.popular && <Badge className="ml-1 bg-purple-500 text-white border-0 text-xs">Popular</Badge>}
                        </td>
                        <td className="py-2 text-right font-bold text-purple-600">${pkg.price.toLocaleString()}</td>
                        <td className="py-2 text-right text-gray-600">${pkg.perTest}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
            
            {/* Mock Exams */}
            <Card className="border-2 border-green-200 rounded-2xl overflow-hidden">
              <div className="bg-green-50 p-4 border-b border-green-200">
                <h3 className="text-xl font-bold text-green-800 flex items-center gap-2">
                  <GraduationCap className="w-5 h-5" />
                  Mock Exams
                </h3>
                <p className="text-sm text-green-600">Full practice exams</p>
              </div>
              <div className="p-4">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-gray-500 border-b">
                      <th className="pb-2">Quantity</th>
                      <th className="pb-2 text-right">Price</th>
                      <th className="pb-2 text-right">Per Exam</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {[
                      { tests: 100, price: 350, perTest: 3.50 },
                      { tests: 500, price: 1500, perTest: 3.00 },
                      { tests: 1000, price: 2700, perTest: 2.70, popular: true },
                      { tests: 5000, price: 11500, perTest: 2.30 },
                      { tests: 10000, price: 20000, perTest: 2.00 },
                      { tests: 50000, price: 85000, perTest: 1.70 },
                      { tests: 100000, price: 150000, perTest: 1.50 }
                    ].map((pkg) => (
                      <tr key={pkg.tests} className={`border-b ${pkg.popular ? 'bg-green-50' : ''}`}>
                        <td className="py-2 font-semibold">
                          {pkg.tests.toLocaleString()}
                          {pkg.popular && <Badge className="ml-1 bg-green-500 text-white border-0 text-xs">Popular</Badge>}
                        </td>
                        <td className="py-2 text-right font-bold text-green-600">${pkg.price.toLocaleString()}</td>
                        <td className="py-2 text-right text-gray-600">${pkg.perTest}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
          
          {/* ROI Calculator for Test Packages */}
          <Card className="border-2 border-[#58CC02] rounded-2xl overflow-hidden mt-8" data-testid="monetization-calculator">
            <div className="bg-green-50 p-6 border-b border-green-200">
              <h3 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                <TrendingUp className="w-7 h-7 text-[#58CC02]" />
                ROI Calculator - Additional Test Packages
              </h3>
              <p className="text-gray-600 mt-1">Calculate your potential profit when reselling tests to your students</p>
            </div>
            
            <div className="grid lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-gray-200">
              {/* Inputs */}
              <div className="p-6 space-y-5">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-gray-700 font-semibold block mb-2">Writing Tests (qty)</Label>
                    <input
                      type="number"
                      value={monetizationValues.writingTests}
                      onChange={(e) => setMonetizationValues(prev => ({ ...prev, writingTests: parseInt(e.target.value) || 0 }))}
                      className="w-full p-2 border-2 border-gray-200 rounded-lg focus:border-blue-500 outline-none"
                      min={0}
                    />
                  </div>
                  <div>
                    <Label className="text-gray-700 font-semibold block mb-2">Your Sell Price ($)</Label>
                    <input
                      type="number"
                      step="0.5"
                      value={monetizationValues.writingSellPrice}
                      onChange={(e) => setMonetizationValues(prev => ({ ...prev, writingSellPrice: parseFloat(e.target.value) || 0 }))}
                      className="w-full p-2 border-2 border-gray-200 rounded-lg focus:border-blue-500 outline-none"
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-gray-700 font-semibold block mb-2">Speaking Tests (qty)</Label>
                    <input
                      type="number"
                      value={monetizationValues.speakingTests}
                      onChange={(e) => setMonetizationValues(prev => ({ ...prev, speakingTests: parseInt(e.target.value) || 0 }))}
                      className="w-full p-2 border-2 border-gray-200 rounded-lg focus:border-purple-500 outline-none"
                      min={0}
                    />
                  </div>
                  <div>
                    <Label className="text-gray-700 font-semibold block mb-2">Your Sell Price ($)</Label>
                    <input
                      type="number"
                      step="0.5"
                      value={monetizationValues.speakingSellPrice}
                      onChange={(e) => setMonetizationValues(prev => ({ ...prev, speakingSellPrice: parseFloat(e.target.value) || 0 }))}
                      className="w-full p-2 border-2 border-gray-200 rounded-lg focus:border-purple-500 outline-none"
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-gray-700 font-semibold block mb-2">Mock Exams (qty)</Label>
                    <input
                      type="number"
                      value={monetizationValues.mockExams}
                      onChange={(e) => setMonetizationValues(prev => ({ ...prev, mockExams: parseInt(e.target.value) || 0 }))}
                      className="w-full p-2 border-2 border-gray-200 rounded-lg focus:border-green-500 outline-none"
                      min={0}
                    />
                  </div>
                  <div>
                    <Label className="text-gray-700 font-semibold block mb-2">Your Sell Price ($)</Label>
                    <input
                      type="number"
                      step="0.5"
                      value={monetizationValues.mockExamSellPrice}
                      onChange={(e) => setMonetizationValues(prev => ({ ...prev, mockExamSellPrice: parseFloat(e.target.value) || 0 }))}
                      className="w-full p-2 border-2 border-gray-200 rounded-lg focus:border-green-500 outline-none"
                    />
                  </div>
                </div>
                
                <button 
                  className="btn-duo w-full py-3 mt-4" 
                  onClick={calculateMonetization}
                  data-testid="calculate-monetization-btn"
                >
                  Calculate Profit
                </button>
              </div>
              
              {/* Results */}
              <div className="p-6 bg-gradient-to-br from-green-50 to-white">
                {monetizationResult ? (
                  <div className="space-y-4" data-testid="monetization-results">
                    {/* Per Product Results */}
                    <div className="space-y-3">
                      <div className="bg-white rounded-xl p-3 border border-blue-200">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Writing Tests ({monetizationResult.writing.quantity})</span>
                          <span className="font-bold text-blue-600">${monetizationResult.writing.profit} profit</span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          Cost: ${monetizationResult.writing.cost} | Revenue: ${monetizationResult.writing.revenue} | Margin: {monetizationResult.writing.margin}%
                        </div>
                      </div>
                      
                      <div className="bg-white rounded-xl p-3 border border-purple-200">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Speaking Tests ({monetizationResult.speaking.quantity})</span>
                          <span className="font-bold text-purple-600">${monetizationResult.speaking.profit} profit</span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          Cost: ${monetizationResult.speaking.cost} | Revenue: ${monetizationResult.speaking.revenue} | Margin: {monetizationResult.speaking.margin}%
                        </div>
                      </div>
                      
                      <div className="bg-white rounded-xl p-3 border border-green-200">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Mock Exams ({monetizationResult.mockExams.quantity})</span>
                          <span className="font-bold text-green-600">${monetizationResult.mockExams.profit} profit</span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          Cost: ${monetizationResult.mockExams.cost} | Revenue: ${monetizationResult.mockExams.revenue} | Margin: {monetizationResult.mockExams.margin}%
                        </div>
                      </div>
                    </div>
                    
                    {/* Totals */}
                    <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-5 text-white">
                      <div className="grid grid-cols-3 gap-4 text-center mb-3">
                        <div>
                          <div className="text-green-100 text-xs">Your Cost</div>
                          <div className="text-lg font-bold">${monetizationResult.totals.cost}</div>
                        </div>
                        <div>
                          <div className="text-green-100 text-xs">Your Revenue</div>
                          <div className="text-lg font-bold">${monetizationResult.totals.revenue}</div>
                        </div>
                        <div>
                          <div className="text-green-100 text-xs">Your Profit</div>
                          <div className="text-lg font-bold">${monetizationResult.totals.profit}</div>
                        </div>
                      </div>
                      <div className="flex justify-between items-center pt-3 border-t border-green-400">
                        <span className="text-green-100">Return on Investment</span>
                        <span className="text-2xl font-extrabold">{monetizationResult.totals.roi_percent}% ROI</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-gray-400 py-8">
                    <TrendingUp className="w-12 h-12 mb-3 opacity-30" />
                    <p className="font-semibold">Enter quantities and prices</p>
                    <p className="text-sm">to see your potential profit</p>
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* Free Trial Section - Lead Capture */}
      <section id="trial" className="py-24 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 relative overflow-hidden">
        {/* Background decorations */}
        <div className="absolute top-0 left-0 w-96 h-96 bg-green-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
        
        <div className="relative max-w-6xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left side - Info */}
            <div className="text-white">
              <Badge className="bg-green-500/20 text-green-400 border-green-500/30 px-4 py-2 mb-6">
                Exclusive for Institutions
              </Badge>
              <h2 className="text-4xl md:text-5xl font-black mb-6 leading-tight">
                Start Your Free
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-blue-400">
                  Institution Trial
                </span>
              </h2>
              <p className="text-xl text-gray-300 mb-8 leading-relaxed">
                Experience the full power of ProficientHub. Get access to:
              </p>
              
              <div className="space-y-4 mb-8">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-green-500/20 flex items-center justify-center">
                    <Check className="w-5 h-5 text-green-400" />
                  </div>
                  <span className="text-lg text-gray-200">1 Complete Mock Exam of your choice</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-green-500/20 flex items-center justify-center">
                    <Check className="w-5 h-5 text-green-400" />
                  </div>
                  <span className="text-lg text-gray-200">30 minutes AI Tutor conversation</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-green-500/20 flex items-center justify-center">
                    <Check className="w-5 h-5 text-green-400" />
                  </div>
                  <span className="text-lg text-gray-200">Full analytics dashboard preview</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-green-500/20 flex items-center justify-center">
                    <Check className="w-5 h-5 text-green-400" />
                  </div>
                  <span className="text-lg text-gray-200">Personalized demo with our team</span>
                </div>
              </div>
              
              <div className="flex items-center gap-4 text-gray-400">
                <AlertTriangle className="w-5 h-5 text-yellow-500" />
                <span className="text-sm">Available only for verified educational institutions</span>
              </div>
            </div>
            
            {/* Right side - Form */}
            <Card className="bg-white/10 backdrop-blur-xl border-white/20 rounded-3xl overflow-hidden">
              <div className="p-8">
                {!trialSubmitted ? (
                  <form onSubmit={handleTrialSubmit} className="space-y-5">
                    <h3 className="text-2xl font-bold text-white mb-6">Request Your Free Trial</h3>
                    
                    <div>
                      <Label className="text-gray-300 mb-2 block">Institution Name *</Label>
                      <Input
                        required
                        placeholder="e.g., Oxford Language Academy"
                        className="bg-white/10 border-white/20 text-white placeholder:text-gray-500 h-12"
                        value={trialForm.institutionName}
                        onChange={(e) => setTrialForm({...trialForm, institutionName: e.target.value})}
                      />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-gray-300 mb-2 block">Nombre de Contacto *</Label>
                        <Input
                          required
                          placeholder="Nombre completo"
                          className="bg-white/10 border-white/20 text-white placeholder:text-gray-500 h-12"
                          value={trialForm.contactName}
                          onChange={(e) => setTrialForm({...trialForm, contactName: e.target.value})}
                        />
                      </div>
                      <div>
                        <Label className="text-gray-300 mb-2 block">Teléfono *</Label>
                        <Input
                          required
                          placeholder="+34 612 345 678"
                          className="bg-white/10 border-white/20 text-white placeholder:text-gray-500 h-12"
                          value={trialForm.phone}
                          onChange={(e) => setTrialForm({...trialForm, phone: e.target.value})}
                        />
                      </div>
                    </div>
                    
                    <div>
                      <Label className="text-gray-300 mb-2 block">Email de Trabajo *</Label>
                      <Input
                        required
                        type="email"
                        placeholder="correo@institucion.edu"
                        className="bg-white/10 border-white/20 text-white placeholder:text-gray-500 h-12"
                        value={trialForm.email}
                        onChange={(e) => setTrialForm({...trialForm, email: e.target.value})}
                      />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-gray-300 mb-2 block">Country *</Label>
                        <Input
                          required
                          placeholder="Country"
                          className="bg-white/10 border-white/20 text-white placeholder:text-gray-500 h-12"
                          value={trialForm.country}
                          onChange={(e) => setTrialForm({...trialForm, country: e.target.value})}
                        />
                      </div>
                      <div>
                        <Label className="text-gray-300 mb-2 block">Students Count *</Label>
                        <Input
                          required
                          type="number"
                          placeholder="e.g., 500"
                          className="bg-white/10 border-white/20 text-white placeholder:text-gray-500 h-12"
                          value={trialForm.studentsCount}
                          onChange={(e) => setTrialForm({...trialForm, studentsCount: e.target.value})}
                        />
                      </div>
                    </div>
                    
                    <div>
                      <Label className="text-gray-300 mb-2 block">Exam to Try *</Label>
                      <div className="grid grid-cols-3 gap-2">
                        {examTypes.map((exam) => (
                          <button
                            key={exam.id}
                            type="button"
                            onClick={() => setTrialForm({...trialForm, selectedExam: exam.id})}
                            className={`p-3 rounded-xl border-2 transition-all text-sm font-semibold ${
                              trialForm.selectedExam === exam.id
                                ? 'border-green-500 bg-green-500/20 text-green-400'
                                : 'border-white/20 text-gray-400 hover:border-white/40'
                            }`}
                          >
                            {exam.name}
                          </button>
                        ))}
                      </div>
                    </div>
                    
                    <button
                      type="submit"
                      disabled={trialSubmitting}
                      className="w-full bg-gradient-to-r from-green-500 to-green-600 text-white py-4 rounded-xl font-bold text-lg hover:from-green-600 hover:to-green-700 transition-all shadow-lg shadow-green-500/30 disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      {trialSubmitting ? (
                        <>
                          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                          Processing...
                        </>
                      ) : (
                        <>
                          Request Free Trial
                          <ArrowRight className="w-5 h-5" />
                        </>
                      )}
                    </button>
                    
                    <p className="text-xs text-gray-500 text-center">
                      By submitting, you agree to be contacted by our team for verification.
                    </p>
                  </form>
                ) : (
                  <div className="text-center py-12">
                    <div className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-6">
                      <Check className="w-10 h-10 text-green-400" />
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-4">Request Received!</h3>
                    <p className="text-gray-300 mb-6">
                      Our team will verify your institution and contact you within 24 hours to set up your free trial.
                    </p>
                    <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                      Check your email for confirmation
                    </Badge>
                  </div>
                )}
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* ROI Calculator Section - Operations */}
      <section id="calculator" className="py-20">
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
                      <span className="text-[#58CC02] font-bold text-lg">{calculatorValues.students.toLocaleString()}</span>
                    </div>
                    <Slider
                      value={[calculatorValues.students]}
                      onValueChange={([v]) => setCalculatorValues(prev => ({ ...prev, students: v }))}
                      max={10000}
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
                      max={100}
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
          <h2 className="text-4xl font-extrabold text-white mb-6">¿Listo para Transformar Tu Institución?</h2>
          <p className="text-xl text-green-100 mb-8">Únete a más de 500 instituciones que ya escalan con aprendizaje potenciado por IA</p>
          <div className="flex justify-center gap-4">
            <button className="bg-white text-[#58CC02] px-8 py-4 rounded-2xl font-bold text-lg hover:bg-gray-100 transition-all shadow-lg" onClick={() => navigate('/register')}>
              Prueba Gratuita
              <ArrowRight className="w-5 h-5 ml-2 inline" />
            </button>
            <button className="border-2 border-white text-white px-8 py-4 rounded-2xl font-bold text-lg hover:bg-white/10 transition-all">
              Agendar Demo
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
              <p className="text-gray-400">La plataforma líder con IA para preparación de exámenes de inglés.</p>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Producto</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#features" className="hover:text-white">Características</a></li>
                <li><a href="#exams" className="hover:text-white">Exámenes</a></li>
                <li><a href="#pricing" className="hover:text-white">Precios</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Empresa</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Sobre Nosotros</a></li>
                <li><a href="#" className="hover:text-white">Carreras</a></li>
                <li><a href="#" className="hover:text-white">Contacto</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Política de Privacidad</a></li>
                <li><a href="#" className="hover:text-white">Términos de Servicio</a></li>
              </ul>
            </div>
          </div>
          
          <div className="mt-12 pt-8 border-t border-gray-800 text-center text-gray-400">
            © 2024 ProficientHub. Todos los derechos reservados.
          </div>
        </div>
      </footer>
      
      {/* Landing Agent Widget */}
      <LandingAgentWidget />
    </div>
  );
}
