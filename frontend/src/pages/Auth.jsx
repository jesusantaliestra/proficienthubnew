import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { GraduationCap, Mail, Lock, User, Building, ArrowLeft, Eye, EyeOff } from 'lucide-react';
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

  return (
    <div className="min-h-screen bg-slate-950 flex">
      <Toaster position="top-right" richColors />
      
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-blue-700 to-slate-900"></div>
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1758413351776-cea82eed2176')] bg-cover bg-center opacity-20"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent"></div>
        
        <div className="relative z-10 flex flex-col justify-between p-12 text-white">
          <div 
            className="flex items-center gap-2 cursor-pointer" 
            onClick={() => navigate('/')}
            data-testid="auth-logo"
          >
            <div className="w-10 h-10 rounded-xl bg-white/10 backdrop-blur flex items-center justify-center">
              <GraduationCap className="w-6 h-6" />
            </div>
            <span className="text-xl font-bold font-outfit">ProficientHub</span>
          </div>
          
          <div className="space-y-6">
            <h1 className="text-4xl font-bold font-outfit leading-tight">
              Empower Your Students to{' '}
              <span className="text-amber-400">Succeed</span>
            </h1>
            <p className="text-lg text-blue-100/80 max-w-md">
              Join 500+ institutions using AI-powered exam preparation to improve pass rates and student engagement.
            </p>
            
            <div className="flex gap-8">
              <div>
                <div className="text-3xl font-bold">+23%</div>
                <div className="text-blue-200/70 text-sm">Pass Rate Improvement</div>
              </div>
              <div>
                <div className="text-3xl font-bold">-12%</div>
                <div className="text-blue-200/70 text-sm">No-Show Reduction</div>
              </div>
            </div>
          </div>
          
          <div className="text-blue-200/50 text-sm">
            © 2024 ProficientHub. All rights reserved.
          </div>
        </div>
      </div>
      
      {/* Right Panel - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md space-y-8">
          <Button
            variant="ghost"
            className="text-slate-400 hover:text-white -ml-4"
            onClick={() => navigate('/')}
            data-testid="back-to-home-btn"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
          
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-xl">
            <CardHeader className="text-center">
              <div className="lg:hidden flex items-center justify-center gap-2 mb-4">
                <div className="w-10 h-10 rounded-xl bg-blue-500 flex items-center justify-center">
                  <GraduationCap className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold text-white font-outfit">ProficientHub</span>
              </div>
              <CardTitle className="text-2xl text-white font-outfit">
                {isLogin ? 'Welcome Back' : 'Create Account'}
              </CardTitle>
              <CardDescription className="text-slate-400">
                {isLogin 
                  ? 'Sign in to access your dashboard' 
                  : 'Start your journey to exam success'}
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {!isLogin && (
                  <>
                    <div className="space-y-2">
                      <Label className="text-slate-300">Account Type</Label>
                      <Select
                        value={formData.userType}
                        onValueChange={(value) => setFormData(prev => ({ ...prev, userType: value }))}
                      >
                        <SelectTrigger 
                          className="bg-slate-800 border-slate-700 text-white"
                          data-testid="user-type-select"
                        >
                          <SelectValue placeholder="Select account type" />
                        </SelectTrigger>
                        <SelectContent className="bg-slate-800 border-slate-700">
                          <SelectItem value="institution">Institution</SelectItem>
                          <SelectItem value="individual">Individual Learner</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label className="text-slate-300">Full Name</Label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <Input
                          type="text"
                          placeholder="John Smith"
                          value={formData.name}
                          onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                          className="pl-10 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
                          required
                          data-testid="name-input"
                        />
                      </div>
                    </div>
                    
                    {formData.userType === 'institution' && (
                      <div className="space-y-2">
                        <Label className="text-slate-300">Institution Name</Label>
                        <div className="relative">
                          <Building className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                          <Input
                            type="text"
                            placeholder="Cambridge Academy"
                            value={formData.institutionName}
                            onChange={(e) => setFormData(prev => ({ ...prev, institutionName: e.target.value }))}
                            className="pl-10 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
                            data-testid="institution-name-input"
                          />
                        </div>
                      </div>
                    )}
                  </>
                )}
                
                <div className="space-y-2">
                  <Label className="text-slate-300">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <Input
                      type="email"
                      placeholder="you@example.com"
                      value={formData.email}
                      onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                      className="pl-10 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
                      required
                      data-testid="email-input"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label className="text-slate-300">Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <Input
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                      className="pl-10 pr-10 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
                      required
                      data-testid="password-input"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                
                <Button
                  type="submit"
                  className="w-full bg-blue-500 hover:bg-blue-600 text-white rounded-full py-6"
                  disabled={loading}
                  data-testid="auth-submit-btn"
                >
                  {loading ? 'Please wait...' : isLogin ? 'Sign In' : 'Create Account'}
                </Button>
              </form>
              
              <div className="mt-6 text-center">
                <p className="text-slate-500">
                  {isLogin ? "Don't have an account? " : "Already have an account? "}
                  <button
                    onClick={() => navigate(isLogin ? '/register' : '/login')}
                    className="text-blue-400 hover:text-blue-300 font-medium"
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
