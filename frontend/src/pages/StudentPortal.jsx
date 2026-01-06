import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { GraduationCap, Mail, Lock, Eye, EyeOff, BookOpen, ArrowLeft } from 'lucide-react';
import { toast, Toaster } from 'sonner';
import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function StudentPortal() {
  const navigate = useNavigate();
  const location = useLocation();
  const { slug } = useParams(); // For white-label: /student-portal/:institutionSlug
  const { login } = useAuth();
  
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [institutionBranding, setInstitutionBranding] = useState(null);
  const [loadingBranding, setLoadingBranding] = useState(!!slug);
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  // Fetch institution branding if slug is provided (white-label)
  useEffect(() => {
    if (slug) {
      fetchInstitutionBranding();
    }
  }, [slug]);

  const fetchInstitutionBranding = async () => {
    try {
      const response = await axios.get(`${API_URL}/institution/branding/${slug}`);
      setInstitutionBranding(response.data);
    } catch (error) {
      console.error('Branding not found:', error);
      // Use default branding if not found
    } finally {
      setLoadingBranding(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const user = await login(formData.email, formData.password, 'student');
      
      // Check if password change is required (first login with provisional credentials)
      if (user.requires_password_change) {
        toast.info('Please set your new password');
        navigate('/student/change-password', { state: { firstLogin: true, institutionSlug: slug } });
        return;
      }
      
      // Check if student belongs to the right institution (for white-label)
      if (slug && user.institution_slug !== slug) {
        toast.error('Invalid credentials for this institution');
        setLoading(false);
        return;
      }
      
      toast.success(`Welcome, ${user.name}!`);
      navigate('/student/dashboard');
    } catch (error) {
      console.error('Login error:', error);
      toast.error(error.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  // Custom branding from institution or defaults
  const branding = institutionBranding || {
    name: 'Student Portal',
    logo: null,
    primaryColor: '#58CC02',
    secondaryColor: '#46A302',
    tagline: 'Access your exam preparation materials'
  };

  if (loadingBranding) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-gray-200 border-t-[#58CC02] rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-500">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Toaster position="top-right" richColors />
      
      {/* Header - White-label or default */}
      <header 
        className="py-4 px-6"
        style={{ backgroundColor: branding.primaryColor }}
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            {branding.logo ? (
              <img src={branding.logo} alt={branding.name} className="h-10" />
            ) : (
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
            )}
            <span className="text-xl font-bold text-white">{branding.name}</span>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          {!slug && (
            <Button
              variant="ghost"
              className="text-gray-600 hover:text-gray-900 -ml-4 mb-6 font-semibold"
              onClick={() => navigate('/')}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Home
            </Button>
          )}
          
          <Card className="bg-white border-2 border-gray-200 shadow-xl rounded-2xl">
            <CardHeader className="text-center pb-2">
              <div className="w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center"
                style={{ backgroundColor: `${branding.primaryColor}15` }}
              >
                <BookOpen className="w-8 h-8" style={{ color: branding.primaryColor }} />
              </div>
              <CardTitle className="text-2xl text-gray-900 font-extrabold">
                Student Login
              </CardTitle>
              <CardDescription className="text-gray-500">
                {branding.tagline}
              </CardDescription>
            </CardHeader>
            
            <CardContent className="pt-4">
              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="space-y-2">
                  <Label className="text-gray-700 font-semibold">Email</Label>
                  <div className="relative">
                    <div className="absolute left-0 top-0 bottom-0 w-12 flex items-center justify-center pointer-events-none border-r border-gray-200 bg-gray-50 rounded-l-xl">
                      <Mail className="w-5 h-5 text-gray-400" />
                    </div>
                    <Input
                      type="email"
                      placeholder="your.email@example.com"
                      value={formData.email}
                      onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                      className="h-12 pl-14 rounded-xl border-2 border-gray-200 focus:border-[#58CC02] placeholder:text-gray-400"
                      required
                      data-testid="student-email-input"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label className="text-gray-700 font-semibold">Password</Label>
                  <div className="relative">
                    <div className="absolute left-0 top-0 bottom-0 w-12 flex items-center justify-center pointer-events-none border-r border-gray-200 bg-gray-50 rounded-l-xl">
                      <Lock className="w-5 h-5 text-gray-400" />
                    </div>
                    <Input
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Enter your password"
                      value={formData.password}
                      onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                      className="h-12 pl-14 pr-12 rounded-xl border-2 border-gray-200 focus:border-[#58CC02] placeholder:text-gray-400"
                      required
                      data-testid="student-password-input"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-0 top-0 bottom-0 w-12 flex items-center justify-center text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>
                
                <Button
                  type="submit"
                  className="w-full h-12 text-white font-bold text-lg rounded-xl"
                  style={{ backgroundColor: branding.primaryColor }}
                  disabled={loading}
                  data-testid="student-login-btn"
                >
                  {loading ? 'Signing in...' : 'Sign In'}
                </Button>
              </form>
              
              <div className="mt-6 p-4 bg-blue-50 rounded-xl">
                <p className="text-sm text-blue-800">
                  <strong>First time?</strong> Use the provisional credentials sent to your email. 
                  You'll be asked to set a new password on first login.
                </p>
              </div>
              
              <div className="mt-4 text-center">
                <button
                  onClick={() => navigate('/forgot-password')}
                  className="text-gray-500 hover:text-gray-700 text-sm"
                >
                  Forgot your password?
                </button>
              </div>
            </CardContent>
          </Card>
          
          {/* Show "Powered by" only if not white-label or institution allows it */}
          {!institutionBranding?.hide_powered_by && !slug && (
            <p className="text-center text-gray-400 text-sm mt-6">
              Powered by ProficientHub
            </p>
          )}
        </div>
      </main>
    </div>
  );
}
