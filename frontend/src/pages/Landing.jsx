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
  
  // Pricing model state
  const [pricingData, setPricingData] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState('plan_10');
  const [withAI, setWithAI] = useState(false);
  const [selectedAiOption, setSelectedAiOption] = useState('none');
  const [numLicenses, setNumLicenses] = useState(100);
  const [calculatedPrice, setCalculatedPrice] = useState(null);
  const [calculatingPrice, setCalculatingPrice] = useState(false);
  
  // Exam types selection (doesn't affect price, just configuration)
  const [selectedExamTypes, setSelectedExamTypes] = useState(['all']);
  const availableExamTypes = [
    { id: 'all', label: 'All Exams' },
    { id: 'toefl', label: 'TOEFL' },
    { id: 'ielts', label: 'IELTS' },
    { id: 'cambridge', label: 'Cambridge' },
    { id: 'pte', label: 'PTE' },
    { id: 'oet', label: 'OET' }
  ];
  
  // Monetization calculator state
  const [monetizationValues, setMonetizationValues] = useState({
    writingTests: 100,
    speakingTests: 50,
    mockExams: 50,
    writingSellPrice: 5.0,
    speakingSellPrice: 7.0,
    mockExamSellPrice: 10.0
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
    // Cost prices (what institution pays)
    const writingCostPerTest = 1.10;  // Based on 1000 tier
    const speakingCostPerTest = 2.70; // Based on 1000 tier
    const mockExamCostPerTest = 2.20; // Based on 1000 tier
    
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

  const features = [
    { icon: Brain, title: 'AI Tutoring Agents', description: 'Personal AI tutor for each exam with voice conversations', color: 'feature-icon-green' },
    { icon: Volume2, title: 'Voice-Enabled Practice', description: 'Speaking tests with real-time AI feedback', color: 'feature-icon-blue' },
    { icon: BarChart3, title: 'Risk Analytics', description: 'Predict pass probability, identify at-risk students', color: 'feature-icon-purple' },
    { icon: FolderOpen, title: 'Institution Library', description: 'Upload materials, flashcards, audio, video', color: 'feature-icon-orange' },
    { icon: Video, title: 'Video Classes', description: 'Stream and record classes in the platform', color: 'feature-icon-yellow' },
    { icon: Headphones, title: 'Offline Access', description: 'Students practice anywhere with downloads', color: 'feature-icon-green' }
  ];

  const examTypes = [
    { id: 'toefl', name: 'TOEFL', color: 'bg-blue-500' },
    { id: 'ielts', name: 'IELTS', color: 'bg-red-500' },
    { id: 'cambridge', name: 'Cambridge', color: 'bg-purple-500' },
    { id: 'pte', name: 'PTE', color: 'bg-orange-500' },
    { id: 'oet', name: 'OET', color: 'bg-green-500' }
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
                  <Label className="text-gray-700 font-semibold block mb-3">Which exam types? (doesn't affect price)</Label>
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
                        const val = parseInt(e.target.value) || 1;
                        setNumLicenses(Math.min(100000, Math.max(1, val)));
                      }}
                      className="w-32 text-right text-2xl font-extrabold text-[#58CC02] bg-white border-2 border-gray-200 rounded-lg px-3 py-1 focus:border-[#58CC02] outline-none"
                      min={1}
                      max={100000}
                    />
                  </div>
                  <input
                    type="range"
                    value={numLicenses}
                    onChange={(e) => setNumLicenses(parseInt(e.target.value))}
                    min={1}
                    max={100000}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#58CC02]"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-2">
                    <span>1</span>
                    <span>100</span>
                    <span>500</span>
                    <span>1,000</span>
                    <span>5,000</span>
                    <span>10,000</span>
                    <span>100,000</span>
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
                        <div className="text-green-100 text-sm mb-1">Price Per License</div>
                        <div className="text-5xl font-extrabold">${calculatedPrice.pricing.price_per_license}</div>
                        {calculatedPrice.pricing.full_price_per_license > calculatedPrice.pricing.price_per_license && (
                          <div className="text-green-200 line-through text-lg mt-1">
                            ${calculatedPrice.pricing.full_price_per_license}
                          </div>
                        )}
                      </div>
                      
                      <div className="border-t border-green-400 pt-4 mt-4">
                        <div className="flex justify-between text-lg">
                          <span className="text-green-100">Order Total:</span>
                          <span className="font-extrabold text-2xl">${calculatedPrice.pricing.total_order_price.toLocaleString()}</span>
                        </div>
                        <div className="text-green-200 text-sm mt-2">
                          {calculatedPrice.summary}
                        </div>
                      </div>
                      
                      <button 
                        className="w-full mt-6 bg-white text-[#58CC02] font-bold py-4 rounded-xl hover:bg-green-50 transition-colors text-lg"
                        onClick={() => navigate('/register')}
                      >
                        Request Demo
                      </button>
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
                      { tests: 100, price: 350, perTest: 3.50 },
                      { tests: 500, price: 1500, perTest: 3.00 },
                      { tests: 1000, price: 2700, perTest: 2.70, popular: true },
                      { tests: 5000, price: 11500, perTest: 2.30 },
                      { tests: 10000, price: 20000, perTest: 2.00 },
                      { tests: 50000, price: 85000, perTest: 1.70 },
                      { tests: 100000, price: 150000, perTest: 1.50 }
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
                      { tests: 100, price: 280, perTest: 2.80 },
                      { tests: 500, price: 1250, perTest: 2.50 },
                      { tests: 1000, price: 2200, perTest: 2.20, popular: true },
                      { tests: 5000, price: 9500, perTest: 1.90 },
                      { tests: 10000, price: 17000, perTest: 1.70 },
                      { tests: 50000, price: 75000, perTest: 1.50 },
                      { tests: 100000, price: 130000, perTest: 1.30 }
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
