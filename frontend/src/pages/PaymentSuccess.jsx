import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { CheckCircle, XCircle, Loader2, ArrowRight, Home } from 'lucide-react';
import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function PaymentSuccess() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');
  
  const [status, setStatus] = useState('loading'); // loading, success, failed
  const [paymentData, setPaymentData] = useState(null);
  const [pollCount, setPollCount] = useState(0);

  useEffect(() => {
    if (sessionId) {
      pollPaymentStatus();
    } else {
      setStatus('failed');
    }
  }, [sessionId]);

  const pollPaymentStatus = async () => {
    const maxAttempts = 5;
    const pollInterval = 2000;

    if (pollCount >= maxAttempts) {
      setStatus('pending');
      return;
    }

    try {
      const response = await axios.get(`${API_URL}/checkout/status/${sessionId}`);
      const data = response.data;
      
      if (data.payment_status === 'paid') {
        setStatus('success');
        setPaymentData(data);
        return;
      } else if (data.status === 'expired') {
        setStatus('failed');
        return;
      }

      // Continue polling
      setPollCount(prev => prev + 1);
      setTimeout(pollPaymentStatus, pollInterval);
    } catch (error) {
      console.error('Error checking payment status:', error);
      setStatus('failed');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="max-w-md w-full p-8 text-center" data-testid="payment-result">
        {status === 'loading' && (
          <>
            <Loader2 className="w-16 h-16 mx-auto text-[#58CC02] animate-spin mb-6" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Processing Payment...</h1>
            <p className="text-gray-600">Please wait while we confirm your payment.</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="w-20 h-20 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-6">
              <CheckCircle className="w-12 h-12 text-[#58CC02]" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Successful!</h1>
            <p className="text-gray-600 mb-6">
              Thank you for your purchase. Your account has been activated.
            </p>
            
            {paymentData && (
              <div className="bg-gray-50 rounded-xl p-4 mb-6 text-left">
                <div className="text-sm text-gray-500 mb-2">Order Details</div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Amount:</span>
                  <span className="font-bold">${(paymentData.amount_total / 100).toFixed(2)} {paymentData.currency?.toUpperCase()}</span>
                </div>
                {paymentData.metadata?.type && (
                  <div className="flex justify-between text-sm">
                    <span>Type:</span>
                    <span className="font-semibold capitalize">{paymentData.metadata.type.replace('_', ' ')}</span>
                  </div>
                )}
              </div>
            )}
            
            <div className="flex flex-col gap-3">
              <Button 
                className="w-full bg-[#58CC02] hover:bg-[#46A302]"
                onClick={() => navigate('/dashboard')}
                data-testid="go-to-dashboard-btn"
              >
                Go to Dashboard
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
              <Button 
                variant="outline"
                className="w-full"
                onClick={() => navigate('/')}
              >
                <Home className="w-4 h-4 mr-2" />
                Back to Home
              </Button>
            </div>
          </>
        )}

        {status === 'pending' && (
          <>
            <div className="w-20 h-20 mx-auto bg-yellow-100 rounded-full flex items-center justify-center mb-6">
              <Loader2 className="w-12 h-12 text-yellow-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Processing</h1>
            <p className="text-gray-600 mb-6">
              Your payment is being processed. You'll receive a confirmation email shortly.
            </p>
            <Button 
              variant="outline"
              className="w-full"
              onClick={() => navigate('/')}
            >
              <Home className="w-4 h-4 mr-2" />
              Back to Home
            </Button>
          </>
        )}

        {status === 'failed' && (
          <>
            <div className="w-20 h-20 mx-auto bg-red-100 rounded-full flex items-center justify-center mb-6">
              <XCircle className="w-12 h-12 text-red-500" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Failed</h1>
            <p className="text-gray-600 mb-6">
              There was an issue processing your payment. Please try again.
            </p>
            <div className="flex flex-col gap-3">
              <Button 
                className="w-full bg-[#58CC02] hover:bg-[#46A302]"
                onClick={() => navigate('/#pricing')}
              >
                Try Again
              </Button>
              <Button 
                variant="outline"
                className="w-full"
                onClick={() => navigate('/')}
              >
                <Home className="w-4 h-4 mr-2" />
                Back to Home
              </Button>
            </div>
          </>
        )}
      </Card>
    </div>
  );
}
