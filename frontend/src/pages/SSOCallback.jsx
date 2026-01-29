import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Shield, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { toast, Toaster } from 'sonner';

export default function SSOCallback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { loginWithToken } = useAuth();
  const [status, setStatus] = useState('processing'); // processing, success, error
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      const token = searchParams.get('token');
      const relayState = searchParams.get('relay_state') || '/';
      const error = searchParams.get('error');

      if (error) {
        setStatus('error');
        setErrorMessage(decodeURIComponent(error));
        return;
      }

      if (!token) {
        setStatus('error');
        setErrorMessage('No authentication token received from SSO provider.');
        return;
      }

      try {
        // Use the token to authenticate
        await loginWithToken(token);
        setStatus('success');
        toast.success('SSO login successful!');
        
        // Redirect after a short delay
        setTimeout(() => {
          // Navigate to the relay state or default dashboard
          if (relayState && relayState !== '/') {
            navigate(relayState, { replace: true });
          } else {
            navigate('/student/dashboard', { replace: true });
          }
        }, 1500);
      } catch (error) {
        console.error('SSO callback error:', error);
        setStatus('error');
        setErrorMessage(error.message || 'Failed to complete SSO authentication.');
      }
    };

    handleCallback();
  }, [searchParams, loginWithToken, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 flex items-center justify-center p-6">
      <Toaster position="top-right" richColors />
      
      <div className="max-w-md w-full">
        <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8 text-center">
          {/* Logo */}
          <div className="w-16 h-16 rounded-2xl bg-indigo-100 flex items-center justify-center mx-auto mb-6">
            <Shield className="w-8 h-8 text-indigo-600" />
          </div>
          
          {status === 'processing' && (
            <>
              <Loader2 className="w-12 h-12 text-indigo-500 animate-spin mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Completing SSO Login</h1>
              <p className="text-gray-500">Please wait while we verify your identity...</p>
            </>
          )}
          
          {status === 'success' && (
            <>
              <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Login Successful!</h1>
              <p className="text-gray-500">Redirecting you to your dashboard...</p>
              
              <div className="mt-6">
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div className="bg-green-500 h-1.5 rounded-full animate-pulse" style={{ width: '100%' }}></div>
                </div>
              </div>
            </>
          )}
          
          {status === 'error' && (
            <>
              <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
                <XCircle className="w-8 h-8 text-red-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Login Failed</h1>
              <p className="text-gray-500 mb-4">{errorMessage}</p>
              
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/login')}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-6 rounded-xl transition-colors"
                >
                  Back to Login
                </button>
                <button
                  onClick={() => window.location.reload()}
                  className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-6 rounded-xl transition-colors"
                >
                  Try Again
                </button>
              </div>
              
              <p className="text-xs text-gray-400 mt-6">
                If this problem persists, please contact your administrator.
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
