import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Toaster } from 'sonner';
import { OfflineIndicator } from './hooks/useOffline';
import './i18n';

// Pages
import Landing from './pages/Landing';
import Auth from './pages/Auth';
import InstitutionDashboard from './pages/InstitutionDashboard';
import StudentDashboard from './pages/StudentDashboard';
import AITutor from './pages/AITutor';
import ExamSimulator from './pages/ExamSimulator';
import PaymentSuccess from './pages/PaymentSuccess';
import AdminPanel from './pages/AdminPanel';
import StudentPortal from './pages/StudentPortal';
import ChangePassword from './pages/ChangePassword';

// Protected Route Component
const ProtectedRoute = ({ children, allowedTypes = [] }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  if (allowedTypes.length > 0 && !allowedTypes.includes(user.user_type)) {
    // Redirect based on user type
    switch (user.user_type) {
      case 'institution':
        return <Navigate to="/institution/dashboard" replace />;
      case 'admin':
        return <Navigate to="/admin" replace />;
      default:
        return <Navigate to="/student/dashboard" replace />;
    }
  }
  
  return children;
};

// Public Route (redirects authenticated users)
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }
  
  if (user) {
    switch (user.user_type) {
      case 'institution':
        return <Navigate to="/institution/dashboard" replace />;
      case 'admin':
        return <Navigate to="/admin" replace />;
      default:
        return <Navigate to="/student/dashboard" replace />;
    }
  }
  
  return children;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<PublicRoute><Auth /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><Auth /></PublicRoute>} />
      <Route path="/payment-success" element={<PaymentSuccess />} />
      <Route path="/pricing" element={<Landing />} />
      
      {/* Admin Routes */}
      <Route 
        path="/admin" 
        element={
          <ProtectedRoute allowedTypes={['admin']}>
            <AdminPanel />
          </ProtectedRoute>
        } 
      />
      
      {/* Institution Routes */}
      <Route 
        path="/institution/dashboard" 
        element={
          <ProtectedRoute allowedTypes={['institution', 'admin']}>
            <InstitutionDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Student/Individual Routes */}
      <Route 
        path="/student/dashboard" 
        element={
          <ProtectedRoute allowedTypes={['student', 'individual', 'admin']}>
            <StudentDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* AI Tutor */}
      <Route 
        path="/tutor/:examType" 
        element={
          <ProtectedRoute>
            <AITutor />
          </ProtectedRoute>
        } 
      />
      
      {/* Exam Simulator */}
      <Route 
        path="/exam/:examType/:section" 
        element={
          <ProtectedRoute>
            <ExamSimulator />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/exam/:examType" 
        element={
          <ProtectedRoute>
            <ExamSimulator />
          </ProtectedRoute>
        } 
      />
      
      {/* Dashboard redirect */}
      <Route path="/dashboard" element={<Navigate to="/student/dashboard" replace />} />
      
      {/* Catch all - redirect to landing */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" richColors />
        <OfflineIndicator />
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
