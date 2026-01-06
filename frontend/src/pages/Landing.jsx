import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Slider } from '../components/ui/slider';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { 
  GraduationCap, Brain, BarChart3, Mic, Globe, Shield, 
  Zap, Users, TrendingUp, ChevronRight, Star, CheckCircle,
  BookOpen, Target, Award, Clock, ArrowRight, Building,
  DollarSign, Calculator, UserCheck, AlertTriangle, Headphones,
  Video, FolderOpen, Volume2
} from 'lucide-react';
import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function Landing() {
  const { t } = useTranslation();
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
  const [selectedExams, setSelectedExams] = useState(1);

  // Realistic ROI calculation based on AI capabilities
  const calculateROI = async () => {
    setCalculating(true);
    
    // Industry standard: 1 teacher per 15-20 students in language academies
    const currentRatio = calculatorValues.students / calculatorValues.teachers;
    const standardRatio = 15;
    
    // With AI (unlimited feedback, AI tutors, automated practice), ratio can be 10x
    // AI handles: grading, feedback, practice sessions, Q&A, speaking practice
    const aiEnhancedRatio = 100; // 1 teacher can now handle 100 students with AI
    
    // Calculate potential students with same teachers
    const potentialStudents = calculatorValues.teachers * aiEnhancedRatio;
    const additionalStudents = Math.max(0, potentialStudents - calculatorValues.students);
    const multiplier = Math.round(potentialStudents / calculatorValues.students);
    
    // Pass rate improvement: AI provides personalized practice, instant feedback
    // Typical improvement: 15-25% with consistent AI practice
    const passRateImprovement = 0.20;
    const newPassRate = Math.min(95, calculatorValues.passRate + (passRateImprovement * 100));
    
    // No-show reduction: AI engagement, reminders, progress tracking
    // Dashboard metrics help identify at-risk students early
    const noShowReduction = 0.60; // 60% reduction typical with engagement tools
    const newNoShowRate = Math.max(5, calculatorValues.noShowRate * (1 - noShowReduction));
    
    // Revenue calculation
    // Assuming average exam prep course: $500/student
    const avgRevenuePerStudent = 500;
    const currentRevenue = calculatorValues.students * avgRevenuePerStudent * (calculatorValues.passRate / 100);
    const projectedRevenue = potentialStudents * avgRevenuePerStudent * (newPassRate / 100);
    const revenueIncrease = projectedRevenue - currentRevenue;
    
    // Teacher cost savings
    // Without AI: would need more teachers to scale
    const teachersNeededWithoutAI = Math.ceil(potentialStudents / standardRatio);
    const additionalTeachersNeeded = teachersNeededWithoutAI - calculatorValues.teachers;
    const teacherCostSavings = additionalTeachersNeeded * calculatorValues.teacherSalary * 12; // Annual
    
    // Time saved per teacher (hours/week)
    // AI handles: grading (10h), feedback (15h), basic Q&A (5h), practice supervision (10h)
    const timeSavedPerTeacher = 30; // hours per week
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
      teacherCostSavings: Math.round(teacherCostSavings),
      timeSavedWeekly: totalTimeSaved,
      totalAnnualBenefit: Math.round(revenueIncrease + teacherCostSavings)
    });
    
    setCalculating(false);
  };

  const features = [
    { icon: Brain, title: 'AI Tutoring Agents', description: 'Personal AI tutor for each exam type with voice conversations', color: 'feature-icon-green' },
    { icon: Volume2, title: 'Voice-Enabled Practice', description: 'Speaking tests with real-time AI feedback using advanced voice technology', color: 'feature-icon-blue' },
    { icon: BarChart3, title: 'Risk Analytics Dashboard', description: 'Predict pass probability, identify at-risk students, track engagement', color: 'feature-icon-purple' },
    { icon: FolderOpen, title: 'Institution Library', description: 'Upload materials, create flashcards, audio summaries, video classes', color: 'feature-icon-orange' },
    { icon: Video, title: 'Live Video Classes', description: 'Stream and record classes directly in the platform', color: 'feature-icon-yellow' },
    { icon: Headphones, title: 'Offline Access', description: 'Students can practice anywhere with downloaded content', color: 'feature-icon-green' }
  ];

  const examTypes = [
    { id: 'toefl', name: 'TOEFL', color: 'bg-blue-500', students: '50K+' },
    { id: 'ielts', name: 'IELTS', color: 'bg-red-500', students: '80K+' },
    { id: 'cambridge', name: 'Cambridge', color: 'bg-purple-500', students: '30K+' },
    { id: 'pte', name: 'PTE', color: 'bg-orange-500', students: '25K+' },
    { id: 'oet', name: 'OET', color: 'bg-green-500', students: '15K+' }
  ];

  // Pricing based on student tiers and number of exams
  // Calculated for 85-95% margins considering ElevenLabs + OpenAI costs
  const getPricingPlans = () => {
    const examMultiplier = selectedExams === 1 ? 1 : selectedExams === 2 ? 1.6 : 2.2;
    const basePrices = {
      starter: { monthly: 149, yearly: 1490, students: '1-10', label: 'Starter' },
      growth: { monthly: 349, yearly: 3490, students: '11-50', label: 'Growth' },
      professional: { monthly: 699, yearly: 6990, students: '51-100', label: 'Professional' },
      enterprise: { monthly: 1299, yearly: 12990, students: '101-200', label: 'Enterprise', extra: '+$8/student' }
    };

    return Object.entries(basePrices).map(([key, plan]) => ({
      id: key,
      name: plan.label,
      students: plan.students,
      price: Math.round(plan.monthly * examMultiplier),
      yearly: Math.round(plan.yearly * examMultiplier),
      extra: plan.extra,
      features: key === 'starter' 
        ? ['Up to 10 students', `${selectedExams} exam type${selectedExams > 1 ? 's' : ''}`, 'AI Tutoring', 'Basic Analytics', 'Email Support']
        : key === 'growth'
        ? ['Up to 50 students', `${selectedExams} exam type${selectedExams > 1 ? 's' : ''}`, 'AI Tutoring + Voice', 'Advanced Analytics', 'Library (5GB)', 'Priority Support']
        : key === 'professional'
        ? ['Up to 100 students', `${selectedExams} exam type${selectedExams > 1 ? 's' : ''}`, 'AI Tutoring + Voice', 'Premium Analytics', 'Library (25GB)', 'Video Classes', 'Dedicated Support']
        : ['101-200 students', 'All exam types', 'Unlimited AI + Voice', 'Full Analytics Suite', 'Unlimited Library', 'Video Classes + Recording', 'White-label Option', 'Dedicated Account Manager'],
      popular: key === 'professional'
    }));
  };

  const pricingPlans = getPricingPlans();

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
              <a href="#features" className="text-gray-600 hover:text-gray-900 font-semibold transition-colors">Features</a>
              <a href="#exams" className="text-gray-600 hover:text-gray-900 font-semibold transition-colors">Exams</a>
              <a href="#pricing" className="text-gray-600 hover:text-gray-900 font-semibold transition-colors">Pricing</a>
              <a href="#calculator" className="text-gray-600 hover:text-gray-900 font-semibold transition-colors">ROI Calculator</a>
            </div>
            
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                className="text-gray-600 hover:text-gray-900 font-semibold"
                onClick={() => navigate('/login')}
                data-testid="nav-login-btn"
              >
                Log In
              </Button>
              <button 
                className="btn-duo px-6 py-2.5 text-sm"
                onClick={() => navigate('/register')}
                data-testid="nav-get-started-btn"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section - B2B Focused */}
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
              Enable your teachers to handle 10x more students with AI tutors, instant feedback, and premium analytics. 
              Prepare students for TOEFL, IELTS, Cambridge, PTE, and OET with real exam simulations.
            </p>
            
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              <button 
                className="btn-duo px-8 py-4 text-lg flex items-center gap-2"
                onClick={() => navigate('/register')}
                data-testid="hero-cta-btn"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </button>
              <button 
                className="btn-duo-outline px-8 py-4 text-lg"
                onClick={() => document.getElementById('calculator').scrollIntoView({ behavior: 'smooth' })}
                data-testid="hero-calculator-btn"
              >
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
              <Card 
                key={index} 
                className="card-duo border-2 p-6"
                data-testid={`feature-card-${index}`}
              >
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
              <Card 
                key={exam.id}
                className="card-duo text-center p-6"
                data-testid={`exam-card-${exam.id}`}
              >
                <div className={`w-16 h-16 mx-auto rounded-2xl ${exam.color} flex items-center justify-center mb-4`}>
                  <GraduationCap className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900">{exam.name}</h3>
                <p className="text-gray-500 text-sm mt-1">{exam.students} students trained</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* ROI Calculator Section */}
      <section id="calculator" className="py-20 bg-gray-50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Calculate Your ROI</h2>
            <p className="text-xl text-gray-600">See how AI can transform your institution's capacity and revenue</p>
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
                      data-testid="calculator-students-slider"
                    />
                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                      <span>10</span>
                      <span>200</span>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-3">
                      <Label className="text-gray-700 font-semibold">Number of Teachers</Label>
                      <span className="text-[#58CC02] font-bold text-lg">{calculatorValues.teachers}</span>
                    </div>
                    <Slider
                      value={[calculatorValues.teachers]}
                      onValueChange={([v]) => setCalculatorValues(prev => ({ ...prev, teachers: v }))}
                      max={20}
                      min={1}
                      step={1}
                      className="w-full"
                      data-testid="calculator-teachers-slider"
                    />
                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                      <span>1</span>
                      <span>20</span>
                    </div>
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
                      data-testid="calculator-passrate-slider"
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
                      data-testid="calculator-noshow-slider"
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
                      data-testid="calculator-salary-input"
                    />
                  </div>
                </div>
                
                <button 
                  className="btn-duo w-full py-4 mt-8 text-lg"
                  onClick={calculateROI}
                  disabled={calculating}
                  data-testid="calculate-roi-btn"
                >
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
                    
                    <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-2xl p-6 text-white">
                      <div className="text-green-100 text-sm font-semibold mb-2">Total Annual Benefit</div>
                      <div className="text-4xl font-extrabold">${roiResults.totalAnnualBenefit.toLocaleString()}</div>
                      <div className="text-green-100 text-sm mt-2">
                        Revenue increase: ${roiResults.revenueIncrease.toLocaleString()} + 
                        Teacher cost savings: ${roiResults.teacherCostSavings.toLocaleString()}
                      </div>
                    </div>
                    
                    <button 
                      className="btn-duo w-full py-4 text-lg"
                      onClick={() => navigate('/register')}
                    >
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

      {/* Pricing Section */}
      <section id="pricing" className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Simple, Transparent Pricing</h2>
            <p className="text-xl text-gray-600 mb-8">Choose the plan that fits your institution size</p>
            
            {/* Exam selector */}
            <div className="flex justify-center gap-4 mb-8">
              <Label className="text-gray-600 font-semibold self-center">Exam types:</Label>
              <div className="inline-flex bg-gray-100 rounded-xl p-1">
                {[1, 2, 3].map((num) => (
                  <button
                    key={num}
                    className={`px-6 py-2 rounded-lg font-bold transition-all ${selectedExams === num ? 'bg-white shadow text-[#58CC02]' : 'text-gray-500'}`}
                    onClick={() => setSelectedExams(num)}
                    data-testid={`exam-count-${num}`}
                  >
                    {num === 3 ? '3+ Exams' : `${num} Exam${num > 1 ? 's' : ''}`}
                  </button>
                ))}
              </div>
            </div>
            
            {/* Billing toggle */}
            <div className="inline-flex bg-gray-100 rounded-xl p-1">
              <button
                className={`px-6 py-2 rounded-lg font-bold transition-all ${billingCycle === 'monthly' ? 'bg-white shadow text-gray-800' : 'text-gray-500'}`}
                onClick={() => setBillingCycle('monthly')}
                data-testid="billing-monthly-btn"
              >
                Monthly
              </button>
              <button
                className={`px-6 py-2 rounded-lg font-bold transition-all ${billingCycle === 'yearly' ? 'bg-white shadow text-gray-800' : 'text-gray-500'}`}
                onClick={() => setBillingCycle('yearly')}
                data-testid="billing-yearly-btn"
              >
                Yearly
                <Badge className="ml-2 bg-green-100 text-green-700 border-0">Save 17%</Badge>
              </button>
            </div>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {pricingPlans.map((plan) => (
              <Card 
                key={plan.id}
                className={`relative border-2 rounded-2xl ${plan.popular ? 'pricing-popular border-[#58CC02]' : 'border-gray-200'}`}
                data-testid={`pricing-card-${plan.id}`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <Badge className="bg-[#58CC02] text-white border-0 px-4 py-1 font-bold">
                      <Star className="w-3 h-3 mr-1" />
                      Most Popular
                    </Badge>
                  </div>
                )}
                <CardContent className="p-6">
                  <div className="mb-4">
                    <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                    <p className="text-gray-500 text-sm">{plan.students} students</p>
                  </div>
                  
                  <div className="mb-6">
                    <span className="text-4xl font-extrabold text-gray-900">
                      ${billingCycle === 'monthly' ? plan.price : plan.yearly}
                    </span>
                    <span className="text-gray-500">
                      /{billingCycle === 'monthly' ? 'mo' : 'yr'}
                    </span>
                    {plan.extra && (
                      <p className="text-sm text-gray-500 mt-1">{plan.extra}</p>
                    )}
                  </div>
                  
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-2 text-gray-700 text-sm">
                        <CheckCircle className="w-5 h-5 text-[#58CC02] flex-shrink-0 mt-0.5" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  
                  <button 
                    className={`w-full py-3 rounded-xl font-bold transition-all ${plan.popular ? 'btn-duo' : 'btn-duo-outline'}`}
                    onClick={() => navigate('/register')}
                    data-testid={`pricing-cta-${plan.id}`}
                  >
                    Get Started
                  </button>
                </CardContent>
              </Card>
            ))}
          </div>
          
          <p className="text-center text-gray-500 mt-8">
            Need more than 200 students? <a href="#" className="text-[#58CC02] font-semibold hover:underline">Contact us for custom enterprise pricing</a>
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-[#58CC02]">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl font-extrabold text-white mb-6">Ready to Transform Your Institution?</h2>
          <p className="text-xl text-green-100 mb-8">Join 500+ institutions already scaling with AI-powered learning</p>
          <div className="flex justify-center gap-4">
            <button 
              className="bg-white text-[#58CC02] px-8 py-4 rounded-2xl font-bold text-lg hover:bg-gray-100 transition-all shadow-lg"
              onClick={() => navigate('/register')}
              data-testid="cta-get-started-btn"
            >
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
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#exams" className="hover:text-white transition-colors">Exams</a></li>
                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#calculator" className="hover:text-white transition-colors">ROI Calculator</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
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
