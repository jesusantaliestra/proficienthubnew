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
import StudentExamDashboard from './pages/StudentExamDashboard';
import SequentialExamDashboard from './pages/SequentialExamDashboard';
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
import LandingAgentAdmin from './pages/LandingAgentAdmin';
import DemoManagement from './pages/DemoManagement';
import PricingConfig from './pages/PricingConfig';

// Enterprise Pages
import APIKeysManager from './pages/APIKeysManager';
import IntegrationsHub from './pages/IntegrationsHub';
import ERPDashboard from './pages/ERPDashboard';
import CRMEducation from './pages/CRMEducation';
import SSOConfig from './pages/SSOConfig';
import SSOCallback from './pages/SSOCallback';
import ABTestingDashboard from './pages/ABTestingDashboard';
import CommunityHub from './pages/CommunityHub';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import AlertsAutomation from './pages/AlertsAutomation';
import AIAgentsConfig from './pages/AIAgentsConfig';
import ConversionAnalyticsDashboard from './pages/ConversionAnalyticsDashboard';

// OET Pages
import OETNurseDashboard from './pages/OETNurseDashboard';
import OETExamSession from './pages/OETExamSession';
import OETSpeakingMock from './pages/OETSpeakingMock';
import OETProfessionDashboard from './pages/OETProfessionDashboard';
import OETExamPacksStore from './pages/OETExamPacksStore';

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
      
      {/* SSO Callback - handles SSO login response */}
      <Route path="/sso/callback" element={<SSOCallback />} />
      
      {/* Admin Routes */}
      <Route 
        path="/admin" 
        element={
          <ProtectedRoute allowedTypes={['admin']}>
            <AdminPanel />
          </ProtectedRoute>
        } 
      />
      
      {/* Superadmin Dashboard - Platform Overview */}
      <Route 
        path="/superadmin" 
        element={
          <ProtectedRoute allowedTypes={['admin']}>
            <SuperadminDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Pricing Configuration - Superadmin only */}
      <Route 
        path="/superadmin/pricing" 
        element={
          <ProtectedRoute allowedTypes={['admin']}>
            <PricingConfig />
          </ProtectedRoute>
        } 
      />
      
      {/* Landing Agent Admin */}
      <Route 
        path="/superadmin/landing-agent" 
        element={
          <ProtectedRoute allowedTypes={['admin']}>
            <LandingAgentAdmin />
          </ProtectedRoute>
        } 
      />
      
      {/* Demo & HeyGen Management */}
      <Route 
        path="/superadmin/demo-management" 
        element={
          <ProtectedRoute allowedTypes={['admin']}>
            <DemoManagement />
          </ProtectedRoute>
        } 
      />

      {/* Conversion Analytics Dashboard */}
      <Route 
        path="/superadmin/conversion-analytics" 
        element={
          <ProtectedRoute allowedTypes={['admin']}>
            <ConversionAnalyticsDashboard />
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
      
      {/* Student Premium Exam Dashboard - Integrated Academy + ProficientHub */}
      <Route 
        path="/student/exam-dashboard" 
        element={
          <ProtectedRoute allowedTypes={['student', 'individual']}>
            <StudentExamDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Sequential Exam Dashboard - Shows unlocked exams */}
      <Route 
        path="/my-exams/:examType" 
        element={
          <ProtectedRoute allowedTypes={['student', 'individual']}>
            <SequentialExamDashboard />
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
      
      {/* Enterprise Routes - API Keys */}
      <Route 
        path="/institution/api-keys" 
        element={
          <ProtectedRoute allowedTypes={['institution', 'admin']}>
            <APIKeysManager />
          </ProtectedRoute>
        } 
      />
      
      {/* Enterprise Routes - Integrations Hub */}
      <Route 
        path="/institution/integrations" 
        element={
          <ProtectedRoute allowedTypes={['institution', 'admin']}>
            <IntegrationsHub />
          </ProtectedRoute>
        } 
      />
      
      {/* Enterprise Routes - ERP Dashboard */}
      <Route 
        path="/institution/erp" 
        element={
          <ProtectedRoute allowedTypes={['institution', 'admin']}>
            <ERPDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Enterprise Routes - CRM Education */}
      <Route 
        path="/institution/crm" 
        element={
          <ProtectedRoute allowedTypes={['institution', 'admin']}>
            <CRMEducation />
          </ProtectedRoute>
        } 
      />
      
      {/* Enterprise Routes - SSO Configuration */}
      <Route 
        path="/institution/sso" 
        element={
          <ProtectedRoute allowedTypes={['institution', 'admin']}>
            <SSOConfig />
          </ProtectedRoute>
        } 
      />
      
      {/* Enterprise Routes - A/B Testing Dashboard */}
      <Route 
        path="/institution/ab-testing" 
        element={
          <ProtectedRoute allowedTypes={['institution', 'admin']}>
            <ABTestingDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Community Hub - Forums and Study Groups */}
      <Route 
        path="/community" 
        element={
          <ProtectedRoute allowedTypes={['institution', 'admin', 'student', 'teacher']}>
            <CommunityHub />
          </ProtectedRoute>
        } 
      />
      
      {/* Analytics Dashboard - Advanced Metrics */}
      <Route 
        path="/institution/analytics" 
        element={
          <ProtectedRoute allowedTypes={['institution', 'admin']}>
            <AnalyticsDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Alerts Automation - Monetizable Feature */}
      <Route 
        path="/institution/alerts" 
        element={
          <ProtectedRoute allowedTypes={['institution', 'admin']}>
            <AlertsAutomation />
          </ProtectedRoute>
        } 
      />
      
      {/* AI Agents Configuration */}
      <Route 
        path="/institution/ai-agents" 
        element={
          <ProtectedRoute allowedTypes={['institution', 'admin']}>
            <AIAgentsConfig />
          </ProtectedRoute>
        } 
      />
      
      {/* OET Routes */}
      <Route 
        path="/oet/nurse" 
        element={
          <ProtectedRoute allowedTypes={['student', 'individual', 'institution', 'admin']}>
            <OETNurseDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/oet/nursing" 
        element={
          <ProtectedRoute allowedTypes={['student', 'individual', 'institution', 'admin']}>
            <OETNurseDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/oet/exam/:sessionId" 
        element={
          <ProtectedRoute allowedTypes={['student', 'individual', 'institution', 'admin']}>
            <OETExamSession />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/oet/mock/:mockId" 
        element={
          <ProtectedRoute allowedTypes={['student', 'individual', 'institution', 'admin']}>
            <OETExamSession />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/oet/speaking-practice" 
        element={
          <ProtectedRoute allowedTypes={['student', 'individual', 'institution', 'admin']}>
            <OETSpeakingMock />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/oet/speaking/:rolePlayId" 
        element={
          <ProtectedRoute allowedTypes={['student', 'individual', 'institution', 'admin']}>
            <OETSpeakingMock />
          </ProtectedRoute>
        } 
      />
      
      {/* Generic OET Profession Dashboard */}
      <Route 
        path="/oet/:profession" 
        element={
          <ProtectedRoute allowedTypes={['student', 'individual', 'institution', 'admin']}>
            <OETProfessionDashboard />
          </ProtectedRoute>
        } 
      />
      
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
