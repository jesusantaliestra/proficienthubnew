import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Slider } from '../components/ui/slider';
import { Badge } from '../components/ui/badge';
import { 
  GraduationCap, Brain, BarChart3, Mic, Globe, Shield, 
  Zap, Users, TrendingUp, ChevronRight, Star, CheckCircle,
  BookOpen, Target, Award, Clock, ArrowRight
} from 'lucide-react';
import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function Landing() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [calculatorValues, setCalculatorValues] = useState({
    students: 100,
    teachers: 5,
    passRate: 65,
    noShowRate: 20
  });
  const [roiResults, setRoiResults] = useState(null);
  const [calculating, setCalculating] = useState(false);

  const calculateROI = async () => {
    setCalculating(true);
    try {
      const response = await axios.post(`${API_URL}/pricing/calculate-roi`, {
        current_students: calculatorValues.students,
        current_teachers: calculatorValues.teachers,
        current_pass_rate: calculatorValues.passRate / 100,
        current_no_show_rate: calculatorValues.noShowRate / 100
      });
      setRoiResults(response.data);
    } catch (error) {
      console.error('ROI calculation error:', error);
    } finally {
      setCalculating(false);
    }
  };

  const features = [
    { icon: Brain, title: t('features.ai.title'), description: t('features.ai.description'), color: 'text-blue-400' },
    { icon: BookOpen, title: t('features.exams.title'), description: t('features.exams.description'), color: 'text-amber-400' },
    { icon: BarChart3, title: t('features.analytics.title'), description: t('features.analytics.description'), color: 'text-emerald-400' },
    { icon: Mic, title: t('features.speaking.title'), description: t('features.speaking.description'), color: 'text-purple-400' }
  ];

  const examTypes = [
    { id: 'toefl', name: 'TOEFL', color: 'from-blue-500 to-blue-700', students: '50K+' },
    { id: 'ielts', name: 'IELTS', color: 'from-red-500 to-red-700', students: '80K+' },
    { id: 'cambridge', name: 'Cambridge', color: 'from-purple-500 to-purple-700', students: '30K+' },
    { id: 'pte', name: 'PTE', color: 'from-amber-500 to-amber-700', students: '25K+' },
    { id: 'oet', name: 'OET', color: 'from-emerald-500 to-emerald-700', students: '15K+' }
  ];

  const pricingPlans = [
    {
      id: 'starter',
      name: 'Starter',
      price: 49,
      yearly: 470,
      features: ['1 exam type', 'Up to 50 students', 'Basic analytics', 'Email support'],
      popular: false
    },
    {
      id: 'professional',
      name: 'Professional',
      price: 149,
      yearly: 1430,
      features: ['3 exam types', 'Up to 200 students', 'Advanced analytics', 'AI tutoring', 'Priority support'],
      popular: true
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 399,
      yearly: 3830,
      features: ['All exam types', 'Unlimited students', 'Premium analytics', 'AI tutoring', 'Dedicated support', 'Custom branding'],
      popular: false
    }
  ];

  const [billingCycle, setBillingCycle] = useState('monthly');

  return (
    <div className="min-h-screen bg-slate-950 noise">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-heavy">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-white font-outfit">ProficientHub</span>
            </div>
            
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-slate-400 hover:text-white transition-colors">{t('nav.features')}</a>
              <a href="#exams" className="text-slate-400 hover:text-white transition-colors">{t('nav.exams')}</a>
              <a href="#pricing" className="text-slate-400 hover:text-white transition-colors">{t('nav.pricing')}</a>
            </div>
            
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                className="text-slate-300 hover:text-white"
                onClick={() => navigate('/login')}
                data-testid="nav-login-btn"
              >
                {t('nav.login')}
              </Button>
              <Button 
                className="bg-blue-500 hover:bg-blue-600 text-white rounded-full px-6"
                onClick={() => navigate('/register')}
                data-testid="nav-get-started-btn"
              >
                {t('nav.getStarted')}
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center pt-20">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-6 py-20 grid lg:grid-cols-2 gap-16 items-center">
          <div className="space-y-8 animate-fade-in">
            <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20 px-4 py-2">
              <Zap className="w-4 h-4 mr-2" />
              AI-Powered Learning Platform
            </Badge>
            
            <h1 className="text-5xl lg:text-6xl font-bold text-white leading-tight font-outfit">
              {t('hero.title')}{' '}
              <span className="text-gradient">{t('hero.titleHighlight')}</span>
            </h1>
            
            <p className="text-xl text-slate-400 leading-relaxed max-w-xl">
              {t('hero.subtitle')}
            </p>
            
            <div className="flex flex-wrap gap-4">
              <Button 
                size="lg" 
                className="bg-blue-500 hover:bg-blue-600 text-white rounded-full px-8 py-6 text-lg glow-blue"
                onClick={() => navigate('/register')}
                data-testid="hero-cta-btn"
              >
                {t('hero.cta')}
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="border-slate-700 text-slate-300 hover:bg-slate-800 rounded-full px-8 py-6 text-lg"
                data-testid="hero-demo-btn"
              >
                {t('hero.ctaSecondary')}
              </Button>
            </div>
            
            <div className="flex gap-8 pt-4">
              <div>
                <div className="text-3xl font-bold text-white font-outfit">200K+</div>
                <div className="text-slate-500">{t('hero.statsStudents')}</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-white font-outfit">500+</div>
                <div className="text-slate-500">{t('hero.statsInstitutions')}</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-emerald-400 font-outfit">+23%</div>
                <div className="text-slate-500">{t('hero.statsPassRate')}</div>
              </div>
            </div>
          </div>
          
          {/* ROI Calculator */}
          <div className="animate-slide-up stagger-2">
            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-xl" data-testid="roi-calculator">
              <CardHeader>
                <CardTitle className="text-2xl text-white font-outfit flex items-center gap-2">
                  <Target className="w-6 h-6 text-amber-400" />
                  {t('calculator.title')}
                </CardTitle>
                <p className="text-slate-400">{t('calculator.subtitle')}</p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <label className="text-sm text-slate-400">{t('calculator.students')}</label>
                      <span className="text-white font-semibold">{calculatorValues.students}</span>
                    </div>
                    <Slider
                      value={[calculatorValues.students]}
                      onValueChange={([v]) => setCalculatorValues(prev => ({ ...prev, students: v }))}
                      max={1000}
                      min={10}
                      step={10}
                      className="w-full"
                      data-testid="calculator-students-slider"
                    />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <label className="text-sm text-slate-400">{t('calculator.teachers')}</label>
                      <span className="text-white font-semibold">{calculatorValues.teachers}</span>
                    </div>
                    <Slider
                      value={[calculatorValues.teachers]}
                      onValueChange={([v]) => setCalculatorValues(prev => ({ ...prev, teachers: v }))}
                      max={50}
                      min={1}
                      step={1}
                      className="w-full"
                      data-testid="calculator-teachers-slider"
                    />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <label className="text-sm text-slate-400">{t('calculator.passRate')}</label>
                      <span className="text-white font-semibold">{calculatorValues.passRate}%</span>
                    </div>
                    <Slider
                      value={[calculatorValues.passRate]}
                      onValueChange={([v]) => setCalculatorValues(prev => ({ ...prev, passRate: v }))}
                      max={95}
                      min={30}
                      step={5}
                      className="w-full"
                      data-testid="calculator-passrate-slider"
                    />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <label className="text-sm text-slate-400">{t('calculator.noShowRate')}</label>
                      <span className="text-white font-semibold">{calculatorValues.noShowRate}%</span>
                    </div>
                    <Slider
                      value={[calculatorValues.noShowRate]}
                      onValueChange={([v]) => setCalculatorValues(prev => ({ ...prev, noShowRate: v }))}
                      max={50}
                      min={0}
                      step={5}
                      className="w-full"
                      data-testid="calculator-noshow-slider"
                    />
                  </div>
                </div>
                
                <Button 
                  className="w-full bg-amber-500 hover:bg-amber-600 text-white rounded-full py-6"
                  onClick={calculateROI}
                  disabled={calculating}
                  data-testid="calculate-roi-btn"
                >
                  {calculating ? 'Calculating...' : t('calculator.calculate')}
                </Button>
                
                {roiResults && (
                  <div className="grid grid-cols-2 gap-4 pt-4 animate-fade-in" data-testid="roi-results">
                    <div className="bg-slate-800/50 rounded-xl p-4">
                      <div className="text-2xl font-bold text-emerald-400">+{roiResults.additional_students}</div>
                      <div className="text-xs text-slate-500">{t('calculator.results.additionalStudents')}</div>
                    </div>
                    <div className="bg-slate-800/50 rounded-xl p-4">
                      <div className="text-2xl font-bold text-blue-400">{roiResults.improved_pass_rate}%</div>
                      <div className="text-xs text-slate-500">{t('calculator.results.improvedPassRate')}</div>
                    </div>
                    <div className="bg-slate-800/50 rounded-xl p-4">
                      <div className="text-2xl font-bold text-amber-400">{roiResults.reduced_no_show_rate}%</div>
                      <div className="text-xs text-slate-500">{t('calculator.results.reducedNoShow')}</div>
                    </div>
                    <div className="bg-slate-800/50 rounded-xl p-4">
                      <div className="text-2xl font-bold text-purple-400">${Math.round(roiResults.estimated_revenue_increase).toLocaleString()}</div>
                      <div className="text-xs text-slate-500">{t('calculator.results.revenueIncrease')}</div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-32 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white font-outfit mb-4">{t('features.title')}</h2>
            <p className="text-xl text-slate-400">{t('features.subtitle')}</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card 
                key={index} 
                className="bg-slate-900/30 border-slate-800 hover:border-slate-700 transition-all duration-300 card-hover group"
                data-testid={`feature-card-${index}`}
              >
                <CardContent className="p-6 space-y-4">
                  <div className={`w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center ${feature.color} group-hover:scale-110 transition-transform duration-300`}>
                    <feature.icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-semibold text-white">{feature.title}</h3>
                  <p className="text-slate-400 text-sm leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Exams Section */}
      <section id="exams" className="py-32 relative bg-slate-900/30">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white font-outfit mb-4">All Major English Proficiency Exams</h2>
            <p className="text-xl text-slate-400">One platform, complete preparation</p>
          </div>
          
          <div className="grid md:grid-cols-3 lg:grid-cols-5 gap-6">
            {examTypes.map((exam) => (
              <Card 
                key={exam.id}
                className="bg-slate-900/50 border-slate-800 hover:border-slate-600 transition-all duration-300 card-hover cursor-pointer group"
                data-testid={`exam-card-${exam.id}`}
              >
                <CardContent className="p-6 text-center space-y-4">
                  <div className={`w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br ${exam.color} flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                    <GraduationCap className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-white">{exam.name}</h3>
                  <p className="text-slate-500 text-sm">{exam.students} students trained</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-32 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white font-outfit mb-4">{t('pricing.title')}</h2>
            <p className="text-xl text-slate-400 mb-8">{t('pricing.subtitle')}</p>
            
            <div className="inline-flex items-center gap-2 bg-slate-900 rounded-full p-1">
              <button
                className={`px-6 py-2 rounded-full transition-all ${billingCycle === 'monthly' ? 'bg-blue-500 text-white' : 'text-slate-400'}`}
                onClick={() => setBillingCycle('monthly')}
                data-testid="billing-monthly-btn"
              >
                {t('pricing.monthly')}
              </button>
              <button
                className={`px-6 py-2 rounded-full transition-all ${billingCycle === 'yearly' ? 'bg-blue-500 text-white' : 'text-slate-400'}`}
                onClick={() => setBillingCycle('yearly')}
                data-testid="billing-yearly-btn"
              >
                {t('pricing.yearly')}
                <Badge className="ml-2 bg-emerald-500/20 text-emerald-400 border-0">-20%</Badge>
              </button>
            </div>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {pricingPlans.map((plan) => (
              <Card 
                key={plan.id}
                className={`relative bg-slate-900/50 border-slate-800 ${plan.popular ? 'border-blue-500 ring-2 ring-blue-500/20' : ''} transition-all duration-300 card-hover`}
                data-testid={`pricing-card-${plan.id}`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <Badge className="bg-blue-500 text-white border-0 px-4 py-1">
                      <Star className="w-3 h-3 mr-1" />
                      {t('pricing.popular')}
                    </Badge>
                  </div>
                )}
                <CardContent className="p-8 space-y-6">
                  <div>
                    <h3 className="text-2xl font-bold text-white font-outfit">{plan.name}</h3>
                    <div className="mt-4">
                      <span className="text-4xl font-bold text-white">
                        ${billingCycle === 'monthly' ? plan.price : plan.yearly}
                      </span>
                      <span className="text-slate-500">
                        {billingCycle === 'monthly' ? t('pricing.perMonth') : t('pricing.perYear')}
                      </span>
                    </div>
                  </div>
                  
                  <ul className="space-y-3">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-center gap-3 text-slate-300">
                        <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  
                  <Button 
                    className={`w-full rounded-full py-6 ${plan.popular ? 'bg-blue-500 hover:bg-blue-600' : 'bg-slate-800 hover:bg-slate-700'}`}
                    onClick={() => navigate('/register')}
                    data-testid={`pricing-cta-${plan.id}`}
                  >
                    {plan.id === 'enterprise' ? t('pricing.contactSales') : t('pricing.getStarted')}
                    <ChevronRight className="w-4 h-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 relative">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <div className="glass-heavy rounded-3xl p-12 space-y-8">
            <h2 className="text-4xl font-bold text-white font-outfit">Ready to Transform Your Institution?</h2>
            <p className="text-xl text-slate-400">Join 500+ institutions already using ProficientHub to improve student outcomes.</p>
            <div className="flex justify-center gap-4">
              <Button 
                size="lg" 
                className="bg-blue-500 hover:bg-blue-600 text-white rounded-full px-8 py-6 text-lg"
                onClick={() => navigate('/register')}
                data-testid="cta-get-started-btn"
              >
                Get Started Free
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="border-slate-700 text-slate-300 hover:bg-slate-800 rounded-full px-8 py-6 text-lg"
              >
                Schedule Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-12">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                  <GraduationCap className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold text-white font-outfit">ProficientHub</span>
              </div>
              <p className="text-slate-500">{t('footer.description')}</p>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4">{t('footer.product')}</h4>
              <ul className="space-y-2 text-slate-500">
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#exams" className="hover:text-white transition-colors">Exams</a></li>
                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4">{t('footer.company')}</h4>
              <ul className="space-y-2 text-slate-500">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-white mb-4">{t('footer.legal')}</h4>
              <ul className="space-y-2 text-slate-500">
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
              </ul>
            </div>
          </div>
          
          <div className="mt-12 pt-8 border-t border-slate-800 text-center text-slate-500">
            {t('footer.copyright')}
          </div>
        </div>
      </footer>
    </div>
  );
}
