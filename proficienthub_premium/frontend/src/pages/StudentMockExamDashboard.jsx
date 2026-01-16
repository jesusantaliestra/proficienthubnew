/**
 * ProficientHub - Student Mock Exam Dashboard
 * 
 * Dashboard para estudiantes que acceden a través de su academia
 * Muestra:
 * - Créditos disponibles
 * - Lista de mock exams con progreso
 * - Estadísticas de rendimiento
 * - Opción de crear nuevo mock exam
 */

import React, { useState, useEffect } from 'react';

// =============================================================================
// TYPES
// =============================================================================

/**
 * @typedef {'full_mock' | 'section'} MockExamMode
 * @typedef {'not_started' | 'in_progress' | 'paused' | 'completed' | 'expired'} MockExamStatus
 * @typedef {'locked' | 'available' | 'in_progress' | 'completed' | 'skipped'} SectionStatus
 */

// =============================================================================
// UI COMPONENTS
// =============================================================================

const Badge = ({ children, variant = 'default', className = '' }) => {
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
    purple: 'bg-purple-100 text-purple-800',
    green: 'bg-green-100 text-green-800',
    blue: 'bg-blue-100 text-blue-800',
    yellow: 'bg-yellow-100 text-yellow-800',
    red: 'bg-red-100 text-red-800',
    gray: 'bg-gray-100 text-gray-800',
  };
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
};

const Card = ({ children, className = '', onClick }) => (
  <div 
    className={`bg-white rounded-xl shadow-sm border border-gray-200 ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''} ${className}`}
    onClick={onClick}
  >
    {children}
  </div>
);

const Button = ({ children, variant = 'primary', size = 'md', disabled = false, onClick, className = '' }) => {
  const variants = {
    primary: 'bg-purple-600 text-white hover:bg-purple-700 disabled:bg-purple-300',
    secondary: 'bg-gray-100 text-gray-700 hover:bg-gray-200',
    outline: 'border-2 border-purple-600 text-purple-600 hover:bg-purple-50',
    ghost: 'text-gray-600 hover:bg-gray-100',
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg',
  };
  
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`rounded-lg font-medium transition-colors ${variants[variant]} ${sizes[size]} ${disabled ? 'cursor-not-allowed' : ''} ${className}`}
    >
      {children}
    </button>
  );
};

const ProgressBar = ({ value, max = 100, color = 'purple', showLabel = true }) => {
  const percentage = Math.min((value / max) * 100, 100);
  const colors = {
    purple: 'bg-purple-600',
    green: 'bg-green-500',
    blue: 'bg-blue-500',
    yellow: 'bg-yellow-500',
  };
  
  return (
    <div className="w-full">
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className={`h-full ${colors[color]} transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <p className="text-xs text-gray-500 mt-1">{Math.round(percentage)}% complete</p>
      )}
    </div>
  );
};

// =============================================================================
// ICONS
// =============================================================================

const Icons = {
  Book: () => <span className="text-xl">📖</span>,
  Headphones: () => <span className="text-xl">🎧</span>,
  Mic: () => <span className="text-xl">🎤</span>,
  Pen: () => <span className="text-xl">✍️</span>,
  Clock: () => <span className="text-xl">⏱️</span>,
  Check: () => <span className="text-xl">✅</span>,
  Lock: () => <span className="text-xl">🔒</span>,
  Play: () => <span className="text-xl">▶️</span>,
  Pause: () => <span className="text-xl">⏸️</span>,
  Trophy: () => <span className="text-xl">🏆</span>,
  TrendUp: () => <span className="text-xl">📈</span>,
  Credit: () => <span className="text-xl">🎫</span>,
};

const SectionIcon = ({ type }) => {
  const icons = {
    reading: <Icons.Book />,
    writing: <Icons.Pen />,
    listening: <Icons.Headphones />,
    speaking: <Icons.Mic />,
  };
  return icons[type] || null;
};

// =============================================================================
// CREDIT STATUS COMPONENT
// =============================================================================

const CreditStatus = ({ credits }) => {
  if (!credits) return null;
  
  const { remaining_credits, total_credits, remaining_full_mocks, remaining_sections, plan_name, academy_name } = credits;
  
  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{plan_name}</h3>
          <p className="text-sm text-gray-500">{academy_name}</p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-purple-600">{remaining_credits}</div>
          <div className="text-sm text-gray-500">credits left</div>
        </div>
      </div>
      
      <ProgressBar value={total_credits - remaining_credits} max={total_credits} showLabel={false} />
      <p className="text-xs text-gray-500 mt-1">
        {total_credits - remaining_credits} of {total_credits} credits used
      </p>
      
      <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">{remaining_full_mocks}</div>
          <div className="text-sm text-gray-500">Full Mocks</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">{remaining_sections}</div>
          <div className="text-sm text-gray-500">Sections</div>
        </div>
      </div>
    </Card>
  );
};

// =============================================================================
// STATISTICS COMPONENT
// =============================================================================

const Statistics = ({ stats, sectionAverages }) => {
  if (!stats) return null;
  
  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Progress</h3>
      
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">{stats.average_band || '-'}</div>
          <div className="text-sm text-gray-500">Avg Band</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{stats.best_band || '-'}</div>
          <div className="text-sm text-gray-500">Best Band</div>
        </div>
        <div className="text-center">
          <div className={`text-2xl font-bold ${stats.improvement_trend > 0 ? 'text-green-600' : stats.improvement_trend < 0 ? 'text-red-600' : 'text-gray-600'}`}>
            {stats.improvement_trend !== null ? (stats.improvement_trend > 0 ? '+' : '') + stats.improvement_trend : '-'}
          </div>
          <div className="text-sm text-gray-500">Trend</div>
        </div>
      </div>
      
      {sectionAverages && Object.keys(sectionAverages).length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-gray-700">Section Averages</h4>
          {['reading', 'writing', 'listening', 'speaking'].map(section => {
            const data = sectionAverages[section];
            if (!data) return null;
            
            return (
              <div key={section} className="flex items-center gap-3">
                <SectionIcon type={section} />
                <div className="flex-1">
                  <div className="flex justify-between text-sm">
                    <span className="capitalize">{section}</span>
                    <span className="font-medium">{data.average}</span>
                  </div>
                  <ProgressBar 
                    value={data.average} 
                    max={9} 
                    showLabel={false}
                    color={data.average >= 7 ? 'green' : data.average >= 6 ? 'yellow' : 'purple'}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
};

// =============================================================================
// MOCK EXAM CARD COMPONENT
// =============================================================================

const MockExamCard = ({ exam, onStart, onContinue, onView }) => {
  const statusColors = {
    not_started: 'gray',
    in_progress: 'blue',
    paused: 'yellow',
    completed: 'green',
    expired: 'red',
  };
  
  const statusLabels = {
    not_started: 'Not Started',
    in_progress: 'In Progress',
    paused: 'Paused',
    completed: 'Completed',
    expired: 'Expired',
  };
  
  return (
    <Card className="p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <h4 className="font-semibold text-gray-900">Mock Exam #{exam.exam_number}</h4>
            <Badge variant={statusColors[exam.status]}>
              {statusLabels[exam.status]}
            </Badge>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            {exam.mode === 'full_mock' ? '🎯 Full Mock' : '📝 Section Mode'}
            {exam.topic && ` • ${exam.topic}`}
          </p>
        </div>
        
        {exam.overall_band && (
          <div className="text-right">
            <div className="text-2xl font-bold text-purple-600">{exam.overall_band}</div>
            <div className="text-xs text-gray-500">Overall Band</div>
          </div>
        )}
      </div>
      
      {/* Section Progress */}
      <div className="grid grid-cols-4 gap-2 mb-3">
        {exam.sections?.map(section => (
          <div 
            key={section.section_type}
            className={`p-2 rounded-lg text-center ${
              section.status === 'completed' ? 'bg-green-50' :
              section.status === 'in_progress' ? 'bg-blue-50' :
              section.status === 'available' ? 'bg-purple-50' :
              'bg-gray-50'
            }`}
          >
            <SectionIcon type={section.section_type} />
            <div className="text-xs mt-1 capitalize">{section.section_type}</div>
            {section.band_score && (
              <div className="text-sm font-semibold text-purple-600">{section.band_score}</div>
            )}
            {section.status === 'locked' && <Icons.Lock />}
          </div>
        ))}
      </div>
      
      {/* Progress Bar */}
      <ProgressBar 
        value={exam.progress?.percentage || 0} 
        max={100}
        color={exam.status === 'completed' ? 'green' : 'purple'}
      />
      
      {/* Actions */}
      <div className="flex gap-2 mt-4">
        {exam.status === 'not_started' && (
          <Button variant="primary" size="sm" onClick={() => onStart(exam.id)}>
            Start Exam
          </Button>
        )}
        {(exam.status === 'in_progress' || exam.status === 'paused') && (
          <Button variant="primary" size="sm" onClick={() => onContinue(exam.id)}>
            Continue
          </Button>
        )}
        {exam.status === 'completed' && (
          <Button variant="secondary" size="sm" onClick={() => onView(exam.id)}>
            View Results
          </Button>
        )}
      </div>
    </Card>
  );
};

// =============================================================================
// CREATE MOCK EXAM MODAL
// =============================================================================

const CreateMockExamModal = ({ isOpen, onClose, onSubmit, examType, remainingCredits }) => {
  const [mode, setMode] = useState('full_mock');
  const [topic, setTopic] = useState('');
  
  if (!isOpen) return null;
  
  const handleSubmit = () => {
    onSubmit({ mode, topic: topic || null });
    onClose();
  };
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Create New Mock Exam</h2>
        
        {/* Mode Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Choose Mode
          </label>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => setMode('full_mock')}
              className={`p-4 rounded-lg border-2 text-left transition-all ${
                mode === 'full_mock' 
                  ? 'border-purple-600 bg-purple-50' 
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-2xl mb-1">🎯</div>
              <div className="font-semibold">Full Mock</div>
              <div className="text-sm text-gray-500">All 4 sections in sequence</div>
              <div className="text-xs text-purple-600 mt-1">Uses 1 credit</div>
            </button>
            
            <button
              onClick={() => setMode('section')}
              className={`p-4 rounded-lg border-2 text-left transition-all ${
                mode === 'section' 
                  ? 'border-purple-600 bg-purple-50' 
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-2xl mb-1">📝</div>
              <div className="font-semibold">Section Mode</div>
              <div className="text-sm text-gray-500">Practice any section</div>
              <div className="text-xs text-purple-600 mt-1">0.25 credit per section</div>
            </button>
          </div>
        </div>
        
        {/* Topic (Optional) */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Topic (Optional)
          </label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Climate change, Technology..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">
            Leave empty for random topics
          </p>
        </div>
        
        {/* Credit Warning */}
        {remainingCredits < 1 && mode === 'full_mock' && (
          <div className="p-3 bg-yellow-50 rounded-lg mb-4">
            <p className="text-sm text-yellow-800">
              ⚠️ You have {remainingCredits} credits. A full mock requires 1 credit.
            </p>
          </div>
        )}
        
        {/* Actions */}
        <div className="flex gap-3">
          <Button variant="secondary" className="flex-1" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            className="flex-1" 
            onClick={handleSubmit}
            disabled={remainingCredits < (mode === 'full_mock' ? 1 : 0.25)}
          >
            Create Exam
          </Button>
        </div>
      </Card>
    </div>
  );
};

// =============================================================================
// MAIN DASHBOARD COMPONENT
// =============================================================================

const StudentMockExamDashboard = ({ examType = 'ielts_academic' }) => {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  
  // Fetch dashboard data
  useEffect(() => {
    fetchDashboard();
  }, [examType]);
  
  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/mock-exams/dashboard/${examType}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to load dashboard');
      
      const data = await response.json();
      setDashboard(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCreateExam = async ({ mode, topic }) => {
    try {
      const response = await fetch('/api/v1/mock-exams/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ exam_type: examType, mode, topic })
      });
      
      if (!response.ok) throw new Error('Failed to create exam');
      
      await fetchDashboard();
    } catch (err) {
      alert(err.message);
    }
  };
  
  const handleStartExam = async (examId) => {
    window.location.href = `/mock-exam/${examId}`;
  };
  
  const handleContinueExam = async (examId) => {
    window.location.href = `/mock-exam/${examId}`;
  };
  
  const handleViewResults = async (examId) => {
    window.location.href = `/mock-exam/${examId}/results`;
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="p-6 max-w-md text-center">
          <div className="text-4xl mb-4">😞</div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Error Loading Dashboard</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={fetchDashboard}>Try Again</Button>
        </Card>
      </div>
    );
  }
  
  const { credits, mock_exams, statistics, section_averages, time_config } = dashboard || {};
  
  // Separate exams by status
  const inProgressExams = mock_exams?.filter(e => ['in_progress', 'paused'].includes(e.status)) || [];
  const notStartedExams = mock_exams?.filter(e => e.status === 'not_started') || [];
  const completedExams = mock_exams?.filter(e => e.status === 'completed') || [];
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {examType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} Practice
              </h1>
              <p className="text-gray-500">
                {credits?.academy_name && `${credits.academy_name} • `}
                {credits?.plan_name}
              </p>
            </div>
            
            <Button 
              variant="primary" 
              onClick={() => setShowCreateModal(true)}
              disabled={credits?.remaining_credits < 0.25}
            >
              + New Mock Exam
            </Button>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Credits & Stats */}
          <div className="space-y-6">
            <CreditStatus credits={credits} />
            <Statistics stats={statistics} sectionAverages={section_averages} />
            
            {/* Time Info Card */}
            <Card className="p-4">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Icons.Clock /> Exam Timing
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Time</span>
                  <span className="font-medium">{time_config?.total_time_minutes} min</span>
                </div>
                {time_config?.sections && Object.entries(time_config.sections)
                  .sort((a, b) => a[1].order - b[1].order)
                  .map(([section, config]) => (
                    <div key={section} className="flex justify-between">
                      <span className="text-gray-600 capitalize">{section}</span>
                      <span>{config.time_minutes} min</span>
                    </div>
                  ))
                }
              </div>
            </Card>
          </div>
          
          {/* Right Column - Mock Exams */}
          <div className="lg:col-span-2 space-y-6">
            {/* In Progress Section */}
            {inProgressExams.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Icons.Play /> Continue Your Exams
                </h2>
                <div className="grid gap-4">
                  {inProgressExams.map(exam => (
                    <MockExamCard
                      key={exam.id}
                      exam={exam}
                      onStart={handleStartExam}
                      onContinue={handleContinueExam}
                      onView={handleViewResults}
                    />
                  ))}
                </div>
              </section>
            )}
            
            {/* Not Started Section */}
            {notStartedExams.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Ready to Start
                </h2>
                <div className="grid gap-4">
                  {notStartedExams.map(exam => (
                    <MockExamCard
                      key={exam.id}
                      exam={exam}
                      onStart={handleStartExam}
                      onContinue={handleContinueExam}
                      onView={handleViewResults}
                    />
                  ))}
                </div>
              </section>
            )}
            
            {/* Completed Section */}
            {completedExams.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Icons.Check /> Completed Exams
                </h2>
                <div className="grid gap-4">
                  {completedExams.map(exam => (
                    <MockExamCard
                      key={exam.id}
                      exam={exam}
                      onStart={handleStartExam}
                      onContinue={handleContinueExam}
                      onView={handleViewResults}
                    />
                  ))}
                </div>
              </section>
            )}
            
            {/* Empty State */}
            {mock_exams?.length === 0 && (
              <Card className="p-12 text-center">
                <div className="text-6xl mb-4">🎓</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Ready to Start Practicing?
                </h3>
                <p className="text-gray-600 mb-6 max-w-md mx-auto">
                  You have {credits?.remaining_credits} credits available. 
                  Create your first mock exam to begin your preparation journey!
                </p>
                <Button variant="primary" size="lg" onClick={() => setShowCreateModal(true)}>
                  Create Your First Mock Exam
                </Button>
              </Card>
            )}
          </div>
        </div>
      </main>
      
      {/* Create Modal */}
      <CreateMockExamModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateExam}
        examType={examType}
        remainingCredits={credits?.remaining_credits || 0}
      />
    </div>
  );
};

export default StudentMockExamDashboard;
