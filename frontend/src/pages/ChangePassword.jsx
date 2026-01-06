import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Lock, Eye, EyeOff, CheckCircle, AlertCircle, Shield } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function ChangePassword() {
  const navigate = useNavigate();
  const location = useLocation();
  const isFirstLogin = location.state?.firstLogin;
  const institutionSlug = location.state?.institutionSlug;
  
  const [loading, setLoading] = useState(false);
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const passwordRequirements = [
    { label: 'At least 8 characters', check: (p) => p.length >= 8 },
    { label: 'Contains uppercase letter', check: (p) => /[A-Z]/.test(p) },
    { label: 'Contains lowercase letter', check: (p) => /[a-z]/.test(p) },
    { label: 'Contains a number', check: (p) => /[0-9]/.test(p) },
    { label: 'Contains special character', check: (p) => /[!@#$%^&*(),.?":{}|<>]/.test(p) }
  ];

  const isPasswordValid = passwordRequirements.every(req => req.check(formData.newPassword));
  const doPasswordsMatch = formData.newPassword === formData.confirmPassword && formData.confirmPassword.length > 0;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!isPasswordValid) {
      toast.error('Password does not meet requirements');
      return;
    }
    
    if (!doPasswordsMatch) {
      toast.error('Passwords do not match');
      return;
    }
    
    setLoading(true);
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/auth/change-password`,
        {
          current_password: formData.currentPassword,
          new_password: formData.newPassword
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success('Password changed successfully!');
      
      // Redirect based on context
      if (institutionSlug) {
        navigate('/student/dashboard');
      } else {
        navigate('/student/dashboard');
      }
    } catch (error) {
      console.error('Password change error:', error);
      toast.error(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({ ...prev, [field]: !prev[field] }));
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <Card className="bg-white border-2 border-gray-200 shadow-xl rounded-2xl">
          <CardHeader className="text-center pb-2">
            <div className="w-16 h-16 rounded-2xl bg-orange-100 mx-auto mb-4 flex items-center justify-center">
              <Shield className="w-8 h-8 text-orange-600" />
            </div>
            <CardTitle className="text-2xl text-gray-900 font-extrabold">
              {isFirstLogin ? 'Set Your Password' : 'Change Password'}
            </CardTitle>
            <CardDescription className="text-gray-500">
              {isFirstLogin 
                ? 'Please create a secure password for your account' 
                : 'Enter your current password and choose a new one'}
            </CardDescription>
          </CardHeader>
          
          <CardContent className="pt-4">
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Current/Provisional Password */}
              <div className="space-y-2">
                <Label className="text-gray-700 font-semibold">
                  {isFirstLogin ? 'Provisional Password' : 'Current Password'}
                </Label>
                <div className="relative">
                  <div className="absolute left-0 top-0 bottom-0 w-12 flex items-center justify-center pointer-events-none border-r border-gray-200 bg-gray-50 rounded-l-xl">
                    <Lock className="w-5 h-5 text-gray-400" />
                  </div>
                  <Input
                    type={showPasswords.current ? 'text' : 'password'}
                    placeholder="Enter current password"
                    value={formData.currentPassword}
                    onChange={(e) => setFormData(prev => ({ ...prev, currentPassword: e.target.value }))}
                    className="h-12 pl-14 pr-12 rounded-xl border-2 border-gray-200 focus:border-[#58CC02] placeholder:text-gray-400"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('current')}
                    className="absolute right-0 top-0 bottom-0 w-12 flex items-center justify-center text-gray-400 hover:text-gray-600"
                  >
                    {showPasswords.current ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>
              
              {/* New Password */}
              <div className="space-y-2">
                <Label className="text-gray-700 font-semibold">New Password</Label>
                <div className="relative">
                  <div className="absolute left-0 top-0 bottom-0 w-12 flex items-center justify-center pointer-events-none border-r border-gray-200 bg-gray-50 rounded-l-xl">
                    <Lock className="w-5 h-5 text-gray-400" />
                  </div>
                  <Input
                    type={showPasswords.new ? 'text' : 'password'}
                    placeholder="Create new password"
                    value={formData.newPassword}
                    onChange={(e) => setFormData(prev => ({ ...prev, newPassword: e.target.value }))}
                    className="h-12 pl-14 pr-12 rounded-xl border-2 border-gray-200 focus:border-[#58CC02] placeholder:text-gray-400"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('new')}
                    className="absolute right-0 top-0 bottom-0 w-12 flex items-center justify-center text-gray-400 hover:text-gray-600"
                  >
                    {showPasswords.new ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                
                {/* Password Requirements */}
                {formData.newPassword.length > 0 && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg space-y-2">
                    {passwordRequirements.map((req, index) => (
                      <div key={index} className="flex items-center gap-2 text-sm">
                        {req.check(formData.newPassword) ? (
                          <CheckCircle className="w-4 h-4 text-green-500" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-gray-300" />
                        )}
                        <span className={req.check(formData.newPassword) ? 'text-green-600' : 'text-gray-500'}>
                          {req.label}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Confirm Password */}
              <div className="space-y-2">
                <Label className="text-gray-700 font-semibold">Confirm New Password</Label>
                <div className="relative">
                  <div className="absolute left-0 top-0 bottom-0 w-12 flex items-center justify-center pointer-events-none border-r border-gray-200 bg-gray-50 rounded-l-xl">
                    <Lock className="w-5 h-5 text-gray-400" />
                  </div>
                  <Input
                    type={showPasswords.confirm ? 'text' : 'password'}
                    placeholder="Confirm new password"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    className={`h-12 pl-14 pr-12 rounded-xl border-2 placeholder:text-gray-400 ${
                      formData.confirmPassword.length > 0
                        ? doPasswordsMatch 
                          ? 'border-green-300 focus:border-green-500' 
                          : 'border-red-300 focus:border-red-500'
                        : 'border-gray-200 focus:border-[#58CC02]'
                    }`}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('confirm')}
                    className="absolute right-0 top-0 bottom-0 w-12 flex items-center justify-center text-gray-400 hover:text-gray-600"
                  >
                    {showPasswords.confirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {formData.confirmPassword.length > 0 && !doPasswordsMatch && (
                  <p className="text-sm text-red-500 mt-1">Passwords do not match</p>
                )}
              </div>
              
              <Button
                type="submit"
                className="w-full h-12 bg-[#58CC02] hover:bg-[#46A302] text-white font-bold text-lg rounded-xl"
                disabled={loading || !isPasswordValid || !doPasswordsMatch}
              >
                {loading ? 'Updating...' : 'Set New Password'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
