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
  const [billingCycle, setBillingCycle] = useState('monthly');
  
  // New exam package pricing state - 4 simple plans
  const [selectedPackage, setSelectedPackage] = useState('plan_40');
  const [numStudents, setNumStudents] = useState(20);
  const [pricePerStudent, setPricePerStudent] = useState(30);
  const [aiTutorMinutes, setAiTutorMinutes] = useState(0);
  const [examPackages, setExamPackages] = useState([]);
  const [packageRoiResult, setPackageRoiResult] = useState(null);
  
  // Monetization calculator state
  const [monetizationValues, setMonetizationValues] = useState({
    writingTests: 100,
    speakingTests: 50,
    writingSellPrice: 5.0,
    speakingSellPrice: 7.0
  });
  const [monetizationResult, setMonetizationResult] = useState(null);

  // Fetch exam packages function
  const fetchExamPackages = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/pricing/exam-packages`);
      setExamPackages(response.data.packages);
    } catch (error) {
      console.error('Error fetching packages:', error);
    }
  }, []);

  // Fetch exam packages on mount
  useEffect(() => {
    fetchExamPackages();
  }, [fetchExamPackages]);

  const calculatePackageROI = useCallback(async () => {
    try {
      const response = await axios.get(
        `${API_URL}/pricing/roi-calculator?package_id=${selectedPackage}&num_students=${numStudents}&price_per_student=${pricePerStudent}&ai_tutor_minutes=${aiTutorMinutes}`
      );
      setPackageRoiResult(response.data);
    } catch (error) {
      console.error('ROI calculation error:', error);
    }
  }, [selectedPackage, numStudents, pricePerStudent, aiTutorMinutes]);

  useEffect(() => {
    if (selectedPackage && numStudents > 0) {
      calculatePackageROI();
    }
  }, [selectedPackage, numStudents, pricePerStudent, calculatePackageROI]);

  const calculateMonetization = async () => {
    try {
      const response = await axios.post(
        `${API_URL}/pricing/monetization-calculator?writing_tests=${monetizationValues.writingTests}&speaking_tests=${monetizationValues.speakingTests}&writing_sell_price=${monetizationValues.writingSellPrice}&speaking_sell_price=${monetizationValues.speakingSellPrice}`
      );
      setMonetizationResult(response.data);
    } catch (error) {
      console.error('Monetization calculation error:', error);
      // Fallback local calculation with new costs
      const writingCost = monetizationValues.writingTests * 1.05;  // $1.05 per test from package
      const speakingCost = monetizationValues.speakingTests * 5.55; // $5.55 per test from package
      const writingRevenue = monetizationValues.writingTests * monetizationValues.writingSellPrice;
      const speakingRevenue = monetizationValues.speakingTests * monetizationValues.speakingSellPrice;
      
      setMonetizationResult({
        writing: {
          profit: Math.round(writingRevenue - writingCost),
          cost: writingCost,
          revenue: writingRevenue
        },
        speaking: {
          profit: Math.round(speakingRevenue - speakingCost),
          cost: speakingCost,
          revenue: speakingRevenue
        },
        totals: {
          investment: writingCost + speakingCost,
          profit: Math.round((writingRevenue - writingCost) + (speakingRevenue - speakingCost)),
          roi_percent: Math.round(((writingRevenue + speakingRevenue) / (writingCost + speakingCost) - 1) * 100)
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
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Paquetes de Exámenes B2B</h2>
            <p className="text-xl text-gray-600 mb-8">4 planes simples. Más volumen = menos precio por examen. AI Tutor opcional.</p>
          </div>
          
          {/* 4 Package Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {examPackages.map((pkg, index) => (
              <div 
                key={pkg.id} 
                className={`bg-white rounded-2xl border-2 p-6 ${pkg.id === 'plan_40' ? 'border-[#58CC02] ring-4 ring-green-100' : 'border-gray-200'}`}
                data-testid={`package-${pkg.id}`}
              >
                {pkg.id === 'plan_40' && (
                  <Badge className="bg-[#58CC02] text-white border-0 mb-4">Más Popular</Badge>
                )}
                {pkg.volume_discount !== "0%" && (
                  <Badge className="bg-orange-100 text-orange-700 border-0 mb-4">-{pkg.volume_discount}</Badge>
                )}
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{pkg.mock_tests} Tests</h3>
                <div className="mb-4">
                  <span className="text-4xl font-extrabold text-gray-900">${pkg.price}</span>
                </div>
                
                <div className="bg-green-50 rounded-lg p-3 mb-4">
                  <div className="text-sm text-gray-600">Precio por examen</div>
                  <div className="text-2xl font-bold text-[#58CC02]">${pkg.price_per_exam}</div>
                </div>
                
                <div className="space-y-2 mb-6 text-sm">
                  {pkg.features.slice(0, 4).map((feature, i) => (
                    <div key={i} className="flex items-center gap-2 text-gray-600">
                      <Check className="w-4 h-4 text-[#58CC02]" />
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>
                
                <button 
                  className={`w-full py-3 rounded-xl font-bold transition-all ${pkg.id === 'plan_40' ? 'btn-duo' : 'btn-duo-outline'}`}
                  onClick={() => {
                    setSelectedPackage(pkg.id);
                    document.getElementById('calculator').scrollIntoView({ behavior: 'smooth' });
                  }}
                >
                  Calcular ROI
                </button>
              </div>
            ))}
          </div>
          
          {/* AI Tutor Add-on */}
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-6 max-w-4xl mx-auto mb-8">
            <div className="flex items-center gap-3 mb-4">
              <Brain className="w-8 h-8 text-purple-600" />
              <div>
                <h3 className="text-xl font-bold text-gray-900">AI Tutor Add-on</h3>
                <p className="text-gray-600">Añade tutorías con voz a cualquier plan</p>
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-xl p-3 text-center">
                <div className="font-bold text-gray-900">30 min</div>
                <div className="text-purple-600 font-bold">+$4.50</div>
              </div>
              <div className="bg-white rounded-xl p-3 text-center">
                <div className="font-bold text-gray-900">60 min</div>
                <div className="text-purple-600 font-bold">+$8.00</div>
              </div>
              <div className="bg-white rounded-xl p-3 text-center">
                <div className="font-bold text-gray-900">120 min</div>
                <div className="text-purple-600 font-bold">+$14.00</div>
              </div>
              <div className="bg-white rounded-xl p-3 text-center">
                <div className="font-bold text-gray-900">300 min</div>
                <div className="text-purple-600 font-bold">+$30.00</div>
              </div>
            </div>
            <p className="text-center text-gray-500 mt-4 text-sm">
              $0.15/min - Conversación con voz, feedback personalizado, práctica de pronunciación
            </p>
          </div>
          
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
              Promedio: <strong>$0.94</strong> por mock test (Speaking AI + Writing AI + Corrección)
            </p>
          </div>
        </div>
      </section>

      {/* Writing & Speaking Test Packages Section */}
      <section id="test-packages" className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <Badge className="bg-orange-100 text-orange-700 border-orange-200 px-4 py-2 mb-6 text-sm font-semibold">
              <Coins className="w-4 h-4 mr-2" />
              Additional Revenue Stream
            </Badge>
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Writing & Speaking Test Packages</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Buy test packages at wholesale prices and resell them to your students. 
              <strong className="text-[#58CC02]"> Recover your subscription cost and generate extra profit.</strong>
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
                <p className="text-sm text-blue-600">AI-graded essays with detailed feedback</p>
              </div>
              <div className="p-4">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-gray-500 border-b">
                      <th className="pb-2">Tests</th>
                      <th className="pb-2 text-center">Price</th>
                      <th className="pb-2 text-center">Per Test</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {[
                      { tests: 10, price: 15, perTest: 1.50 },
                      { tests: 50, price: 60, perTest: 1.20 },
                      { tests: 100, price: 100, perTest: 1.00, popular: true },
                      { tests: 250, price: 200, perTest: 0.80 },
                      { tests: 500, price: 350, perTest: 0.70 },
                      { tests: 1000, price: 600, perTest: 0.60 }
                    ].map((pkg) => (
                      <tr key={pkg.tests} className={`border-b ${pkg.popular ? 'bg-blue-50' : ''}`}>
                        <td className="py-3 font-semibold">{pkg.tests} tests {pkg.popular && <Badge className="ml-2 bg-blue-500 text-white border-0 text-xs">Best Value</Badge>}</td>
                        <td className="py-3 text-center font-bold">${pkg.price}</td>
                        <td className="py-3 text-center text-blue-600 font-bold">${pkg.perTest}</td>
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
                  Speaking Test Packages
                </h3>
                <p className="text-sm text-purple-600">AI-powered with pronunciation feedback</p>
              </div>
              <div className="p-4">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-gray-500 border-b">
                      <th className="pb-2">Tests</th>
                      <th className="pb-2 text-center">Price</th>
                      <th className="pb-2 text-center">Per Test</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {[
                      { tests: 10, price: 20, perTest: 2.00 },
                      { tests: 50, price: 85, perTest: 1.70 },
                      { tests: 100, price: 150, perTest: 1.50, popular: true },
                      { tests: 250, price: 325, perTest: 1.30 },
                      { tests: 500, price: 550, perTest: 1.10 },
                      { tests: 1000, price: 900, perTest: 0.90 }
                    ].map((pkg) => (
                      <tr key={pkg.tests} className={`border-b ${pkg.popular ? 'bg-purple-50' : ''}`}>
                        <td className="py-3 font-semibold">{pkg.tests} tests {pkg.popular && <Badge className="ml-2 bg-purple-500 text-white border-0 text-xs">Best Value</Badge>}</td>
                        <td className="py-3 text-center font-bold">${pkg.price}</td>
                        <td className="py-3 text-center text-purple-600 font-bold">${pkg.perTest}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
          
          {/* Monetization Calculator */}
          <Card className="border-2 border-[#58CC02] rounded-2xl overflow-hidden" data-testid="monetization-calculator">
            <div className="bg-green-50 p-6 border-b border-green-200">
              <h3 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                <TrendingUp className="w-7 h-7 text-[#58CC02]" />
                Monetization Calculator
              </h3>
              <p className="text-gray-600 mt-1">See how much you can earn by reselling tests to your students</p>
            </div>
            
            <div className="grid lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-gray-200">
              {/* Inputs */}
              <div className="p-6 space-y-6">
                <div>
                  <Label className="text-gray-700 font-semibold block mb-2">Writing Tests to Sell Monthly</Label>
                  <div className="flex items-center gap-4">
                    <Slider
                      value={[monetizationValues.writingTests]}
                      onValueChange={([v]) => setMonetizationValues(prev => ({ ...prev, writingTests: v }))}
                      max={500}
                      min={0}
                      step={10}
                      className="flex-1"
                    />
                    <span className="text-lg font-bold text-blue-600 w-16 text-right">{monetizationValues.writingTests}</span>
                  </div>
                </div>
                
                <div>
                  <Label className="text-gray-700 font-semibold block mb-2">Speaking Tests to Sell Monthly</Label>
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
                    <Label className="text-gray-700 font-semibold block mb-2">Your Writing Price ($)</Label>
                    <Input
                      type="number"
                      step="0.5"
                      value={monetizationValues.writingSellPrice}
                      onChange={(e) => setMonetizationValues(prev => ({ ...prev, writingSellPrice: parseFloat(e.target.value) || 0 }))}
                      className="input-duo"
                    />
                  </div>
                  <div>
                    <Label className="text-gray-700 font-semibold block mb-2">Your Speaking Price ($)</Label>
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
                  Calculate Profit
                </button>
              </div>
              
              {/* Results */}
              <div className="p-6 bg-gradient-to-br from-green-50 to-white">
                {monetizationResult ? (
                  <div className="space-y-4" data-testid="monetization-results">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-white rounded-xl p-4 border border-blue-200">
                        <div className="text-sm text-gray-500 mb-1">Writing Profit</div>
                        <div className="text-2xl font-extrabold text-blue-600">${monetizationResult.writing.profit}</div>
                        <div className="text-xs text-gray-400">
                          Cost: ${monetizationResult.writing.cost} | Revenue: ${monetizationResult.writing.revenue}
                        </div>
                      </div>
                      <div className="bg-white rounded-xl p-4 border border-purple-200">
                        <div className="text-sm text-gray-500 mb-1">Speaking Profit</div>
                        <div className="text-2xl font-extrabold text-purple-600">${monetizationResult.speaking.profit}</div>
                        <div className="text-xs text-gray-400">
                          Cost: ${monetizationResult.speaking.cost} | Revenue: ${monetizationResult.speaking.revenue}
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-5 text-white">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-green-100">Total Monthly Profit</span>
                        <span className="text-3xl font-extrabold">${monetizationResult.totals.profit}</span>
                      </div>
                      <div className="flex justify-between text-sm text-green-100">
                        <span>Investment: ${monetizationResult.totals.investment}</span>
                        <span>ROI: {monetizationResult.totals.roi_percent}%</span>
                      </div>
                    </div>
                    
                    <div className="bg-orange-50 rounded-xl p-4 border border-orange-200">
                      <div className="flex items-start gap-3">
                        <Coins className="w-5 h-5 text-orange-600 mt-0.5" />
                        <div>
                          <div className="font-bold text-orange-800">Subscription Recovery</div>
                          <div className="text-sm text-orange-600">
                            Sell just <strong>{monetizationResult.subscription_recovery.writing_tests_needed} writing tests</strong> or{' '}
                            <strong>{monetizationResult.subscription_recovery.speaking_tests_needed} speaking tests</strong> to recover a $500/mo subscription!
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-gray-400 py-8">
                    <TrendingUp className="w-12 h-12 mb-3 opacity-30" />
                    <p className="font-semibold">Adjust values and calculate</p>
                    <p className="text-sm">to see your potential profits</p>
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
              Calculadora ROI de Paquetes
            </Badge>
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Calcula tu ROI por Paquete</h2>
            <p className="text-xl text-gray-600">Ve cuánto puedes ganar distribuyendo un paquete entre tus estudiantes</p>
          </div>
          
          <Card className="bg-white border-2 border-gray-200 rounded-3xl overflow-hidden">
            <div className="grid lg:grid-cols-2">
              {/* Inputs */}
              <div className="p-8 border-r border-gray-200">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Configura tu escenario</h3>
                
                <div className="space-y-6">
                  <div>
                    <Label className="text-gray-700 font-semibold block mb-2">Selecciona Paquete</Label>
                    <select 
                      value={selectedPackage}
                      onChange={(e) => setSelectedPackage(e.target.value)}
                      className="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-[#58CC02] outline-none"
                      data-testid="package-selector"
                    >
                      {examPackages.map(pkg => (
                        <option key={pkg.id} value={pkg.id}>
                          {pkg.description} - ${pkg.price}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <Label className="text-gray-700 font-semibold">Número de Estudiantes</Label>
                      <span className="text-[#58CC02] font-bold text-lg">{numStudents}</span>
                    </div>
                    <Slider
                      value={[numStudents]}
                      onValueChange={([v]) => setNumStudents(v)}
                      max={100}
                      min={1}
                      step={1}
                      className="w-full"
                    />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <Label className="text-gray-700 font-semibold">Precio que cobras por estudiante ($)</Label>
                      <span className="text-[#58CC02] font-bold text-lg">${pricePerStudent}</span>
                    </div>
                    <Slider
                      value={[pricePerStudent]}
                      onValueChange={([v]) => setPricePerStudent(v)}
                      max={200}
                      min={20}
                      step={5}
                      className="w-full"
                    />
                  </div>
                </div>
              </div>
              
              {/* Results */}
              <div className="p-8 bg-gradient-to-br from-green-50 to-white">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Tu Proyección de ROI</h3>
                
                {packageRoiResult ? (
                  <div className="space-y-4" data-testid="package-roi-results">
                    <div className="bg-white rounded-xl p-4 border border-gray-200">
                      <div className="text-sm text-gray-500 mb-1">Paquete Seleccionado</div>
                      <div className="font-bold text-gray-900">{packageRoiResult.package.description}</div>
                      <div className="text-sm text-gray-500">
                        {packageRoiResult.package.mock_tests} tests + {packageRoiResult.package.ai_tutor_minutes} min AI
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
                        <div className="text-sm text-gray-500">Tu Costo por Estudiante</div>
                        <div className="text-2xl font-extrabold text-blue-600">${packageRoiResult.per_student.your_cost}</div>
                      </div>
                      <div className="bg-green-50 rounded-xl p-4 border border-green-200">
                        <div className="text-sm text-gray-500">Tu Margen</div>
                        <div className="text-2xl font-extrabold text-green-600">{packageRoiResult.per_student.your_margin}%</div>
                      </div>
                    </div>
                    
                    <div className="bg-white rounded-xl p-4 border border-gray-200">
                      <div className="text-sm text-gray-500 mb-2">Por Estudiante Recibe</div>
                      <div className="flex gap-4">
                        <Badge className="bg-purple-100 text-purple-700 border-0">
                          {packageRoiResult.per_student.mock_tests} mock tests
                        </Badge>
                        <Badge className="bg-orange-100 text-orange-700 border-0">
                          {packageRoiResult.per_student.ai_tutor_minutes} min AI tutor
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-5 text-white">
                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                          <div className="text-green-100 text-sm">Inversión</div>
                          <div className="text-xl font-bold">${packageRoiResult.totals.your_investment}</div>
                        </div>
                        <div>
                          <div className="text-green-100 text-sm">Ingresos</div>
                          <div className="text-xl font-bold">${packageRoiResult.totals.your_revenue}</div>
                        </div>
                        <div>
                          <div className="text-green-100 text-sm">Ganancia</div>
                          <div className="text-xl font-bold">${packageRoiResult.totals.your_profit}</div>
                        </div>
                      </div>
                      <div className="mt-4 pt-4 border-t border-green-400 text-center">
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
