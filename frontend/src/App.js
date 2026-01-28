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
import StudentDashboardRestricted from './pages/StudentDashboardRestricted';
import AITutor from './pages/AITutor';
import AITutorMultiAgent from './pages/AITutorMultiAgent';
import ExamSimulator from './pages/ExamSimulator';
import PaymentSuccess from './pages/PaymentSuccess';
import AdminPanel from './pages/AdminPanel';
import StudentPortal from './pages/StudentPortal';
import ChangePassword from './pages/ChangePassword';
import IncomeCalculator from './pages/IncomeCalculator';
import ExamBankAdmin from './pages/ExamBankAdmin';
import WhiteLabelSettings from './pages/WhiteLabelSettings';
import SuperadminDashboard from './pages/SuperadminDashboard';

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

// Student Dashboard Router - shows restricted dashboard for institutional students
const StudentDashboardRouter = () => {
  const { user } = useAuth();
  
  // If student has an institution_id, they should see the restricted dashboard
  if (user?.institution_id && user?.user_type === 'student') {
    return <StudentDashboardRestricted />;
  }
  
  // Individual users see the full dashboard
  return <StudentDashboard />;
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
      
      {/* Student Portal - White-label access */}
      <Route path="/student-portal" element={<StudentPortal />} />
      <Route path="/student-portal/:slug" element={<StudentPortal />} />
      
      {/* Password Change - Required for first login */}
      <Route path="/change-password" element={<ChangePassword />} />
      <Route path="/student/change-password" element={<ChangePassword />} />
      
      {/* Admin Routes */}
      <Route 
        path="/admin" 
        element={
          <ProtectedRoute allowedTypes={['admin']}>
            <AdminPanel />
          </ProtectedRoute>
        } 
      />
      
      {/* Income Calculator - Dedicated page */}
      <Route 
        path="/income-calculator" 
        element={<IncomeCalculator />} 
      />
      
      {/* Exam Bank Admin - Dedicated page */}
      <Route 
        path="/admin/exam-bank" 
        element={
          <ProtectedRoute allowedTypes={['admin']}>
            <ExamBankAdmin />
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
      
      {/* White-Label Settings */}
      <Route 
        path="/institution/whitelabel" 
        element={
          <ProtectedRoute allowedTypes={['institution', 'admin']}>
            <WhiteLabelSettings />
          </ProtectedRoute>
        } 
      />
      
      {/* Student/Individual Routes */}
      <Route 
        path="/student/dashboard" 
        element={
          <ProtectedRoute allowedTypes={['student', 'individual', 'admin']}>
            <StudentDashboardRouter />
          </ProtectedRoute>
        } 
      />
      
      {/* AI Tutor - Multi-Agent System */}
      <Route 
        path="/tutor/:examType" 
        element={
          <ProtectedRoute>
            <AITutorMultiAgent />
          </ProtectedRoute>
        } 
      />
      
      {/* AI Tutor - Legacy (fallback) */}
      <Route 
        path="/tutor-legacy/:examType" 
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
