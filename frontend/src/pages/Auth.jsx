import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { GraduationCap, Mail, Lock, User, Building, ArrowLeft, Eye, EyeOff, CheckCircle } from 'lucide-react';
import { toast, Toaster } from 'sonner';

export default function Auth() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, register } = useAuth();
  const isLogin = location.pathname === '/login';
  
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    userType: 'institution',
    institutionName: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      if (isLogin) {
        const user = await login(formData.email, formData.password);
        toast.success('Welcome back!');
        navigateByUserType(user.user_type);
      } else {
        const user = await register({
          email: formData.email,
          password: formData.password,
          name: formData.name,
          user_type: formData.userType,
          institution_name: formData.userType === 'institution' ? formData.institutionName : null
        });
        toast.success('Account created successfully!');
        navigateByUserType(user.user_type);
      }
    } catch (error) {
      console.error('Auth error:', error);
      toast.error(error.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const navigateByUserType = (userType) => {
    switch (userType) {
      case 'institution':
        navigate('/institution/dashboard');
        break;
      case 'admin':
        navigate('/admin');
        break;
      case 'student':
      case 'individual':
      default:
        navigate('/student/dashboard');
    }
  };

  const benefits = [
    '10x student capacity with AI tutoring',
    'Premium risk analytics & pass prediction',
    'Voice-enabled speaking practice',
    'Institution library & video classes'
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Toaster position="top-right" richColors />
      
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-[#58CC02] relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#58CC02] to-[#46A302]"></div>
        <div className="absolute top-20 right-20 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 left-20 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        
        <div className="relative z-10 flex flex-col justify-between p-12 text-white">
          <div 
            className="flex items-center gap-3 cursor-pointer" 
            onClick={() => navigate('/')}
            data-testid="auth-logo"
          >
            <div className="w-12 h-12 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center">
              <GraduationCap className="w-7 h-7" />
            </div>
            <span className="text-2xl font-extrabold">ProficientHub</span>
          </div>
          
          <div className="space-y-8">
            <h1 className="text-4xl font-extrabold leading-tight">
              Scale Your Institution With{' '}
              <span className="text-[#FFC800]">AI-Powered</span>{' '}
              Learning
            </h1>
            
            <div className="space-y-4">
              {benefits.map((benefit, index) => (
                <div key={index} className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center">
                    <CheckCircle className="w-4 h-4" />
                  </div>
                  <span className="text-lg">{benefit}</span>
                </div>
              ))}
            </div>
            
            <div className="flex gap-8 pt-4">
              <div>
                <div className="text-4xl font-extrabold">10x</div>
                <div className="text-green-100">Student Capacity</div>
              </div>
              <div>
                <div className="text-4xl font-extrabold">+23%</div>
                <div className="text-green-100">Pass Rate</div>
              </div>
            </div>
          </div>
          
          <div className="text-green-100 text-sm">
            © 2024 ProficientHub. All rights reserved.
          </div>
        </div>
      </div>
      
      {/* Right Panel - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md space-y-8">
          <Button
            variant="ghost"
            className="text-gray-600 hover:text-gray-900 -ml-4 font-semibold"
            onClick={() => navigate('/')}
            data-testid="back-to-home-btn"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
          
          <Card className="bg-white border-2 border-gray-200 shadow-xl rounded-2xl">
            <CardHeader className="text-center pb-2">
              <div className="lg:hidden flex items-center justify-center gap-2 mb-4">
                <div className="w-10 h-10 rounded-xl bg-[#58CC02] flex items-center justify-center">
                  <GraduationCap className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-extrabold text-gray-800">ProficientHub</span>
              </div>
              <CardTitle className="text-2xl text-gray-900 font-extrabold">
                {isLogin ? 'Welcome Back' : 'Create Account'}
              </CardTitle>
              <CardDescription className="text-gray-500">
                {isLogin 
                  ? 'Sign in to access your dashboard' 
                  : 'Start your journey to scale with AI'}
              </CardDescription>
            </CardHeader>
            
            <CardContent className="pt-4">
              <form onSubmit={handleSubmit} className="space-y-5">
                {!isLogin && (
                  <>
                    <div className="space-y-2">
                      <Label className="text-gray-700 font-semibold">Account Type</Label>
                      <Select
                        value={formData.userType}
                        onValueChange={(value) => setFormData(prev => ({ ...prev, userType: value }))}
                      >
                        <SelectTrigger 
                          className="input-duo"
                          data-testid="user-type-select"
                        >
                          <SelectValue placeholder="Select account type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="institution">Institution / Academy</SelectItem>
                          <SelectItem value="individual">Individual Learner</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label className="text-gray-700 font-semibold">Full Name</Label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <Input
                          type="text"
                          placeholder="John Smith"
                          value={formData.name}
                          onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                          className="input-duo pl-10"
                          required
                          data-testid="name-input"
                        />
                      </div>
                    </div>
                    
                    {formData.userType === 'institution' && (
                      <div className="space-y-2">
                        <Label className="text-gray-700 font-semibold">Institution Name</Label>
                        <div className="relative">
                          <Building className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                          <Input
                            type="text"
                            placeholder="Cambridge Academy"
                            value={formData.institutionName}
                            onChange={(e) => setFormData(prev => ({ ...prev, institutionName: e.target.value }))}
                            className="input-duo pl-10"
                            data-testid="institution-name-input"
                          />
                        </div>
                      </div>
                    )}
                  </>
                )}
                
                <div className="space-y-2">
                  <Label className="text-gray-700 font-semibold">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <Input
                      type="email"
                      placeholder="you@example.com"
                      value={formData.email}
                      onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                      className="input-duo pl-10"
                      required
                      data-testid="email-input"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label className="text-gray-700 font-semibold">Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <Input
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                      className="input-duo pl-10 pr-10"
                      required
                      data-testid="password-input"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>
                
                <button
                  type="submit"
                  className="btn-duo w-full py-4 text-lg"
                  disabled={loading}
                  data-testid="auth-submit-btn"
                >
                  {loading ? 'Please wait...' : isLogin ? 'Sign In' : 'Create Account'}
                </button>
              </form>
              
              <div className="mt-6 text-center">
                <p className="text-gray-500">
                  {isLogin ? "Don't have an account? " : "Already have an account? "}
                  <button
                    onClick={() => navigate(isLogin ? '/register' : '/login')}
                    className="text-[#58CC02] hover:underline font-bold"
                    data-testid="toggle-auth-mode-btn"
                  >
                    {isLogin ? 'Sign Up' : 'Sign In'}
                  </button>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
