import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { 
  ArrowLeft, Check, X, AlertTriangle, Eye, Edit2, 
  BookOpen, Headphones, Mic, FileText, 
  ChevronDown, ChevronUp, Search, Filter,
  CheckCircle, XCircle, Clock, RefreshCw
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function ExamBankAdmin() {
  const navigate = useNavigate();
  const [exams, setExams] = useState([]);
  const [selectedExam, setSelectedExam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ type: 'all', status: 'all' });
  const [expandedSections, setExpandedSections] = useState({});
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchExams();
  }, [filter]);

  const fetchExams = async () => {
    try {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams();
      if (filter.type !== 'all') params.append('exam_type', filter.type);
      if (filter.status !== 'all') params.append('status', filter.status);
      
      const response = await axios.get(`${API_URL}/api/admin/exam-bank?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setExams(response.data.exams || []);
    } catch (error) {
      console.error('Error fetching exams:', error);
    } finally {
      setLoading(false);
    }
  };

  const initializeOET = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/api/admin/exam-bank/initialize-oet`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchExams();
    } catch (error) {
      console.error('Error initializing OET:', error);
    }
  };

  const validateExam = async (examId, action, notes = '') => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/api/admin/exam-bank/validate/${examId}?action=${action}&notes=${notes}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchExams();
      if (selectedExam?.exam_id === examId) {
        setSelectedExam(prev => ({ ...prev, validation_status: action === 'approve' ? 'approved' : action === 'reject' ? 'rejected' : 'needs_revision' }));
      }
    } catch (error) {
      console.error('Error validating exam:', error);
    }
  };

  const toggleSection = (sectionKey) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionKey]: !prev[sectionKey]
    }));
  };

  const getStatusBadge = (status) => {
    const styles = {
      draft: 'bg-gray-100 text-gray-700',
      pending_human_review: 'bg-yellow-100 text-yellow-700',
      approved: 'bg-green-100 text-green-700',
      rejected: 'bg-red-100 text-red-700',
      needs_revision: 'bg-orange-100 text-orange-700'
    };
    return <Badge className={styles[status] || styles.draft}>{status?.replace(/_/g, ' ')}</Badge>;
  };

  const getSectionIcon = (section) => {
    const icons = {
      listening: <Headphones className="w-5 h-5" />,
      reading: <BookOpen className="w-5 h-5" />,
      writing: <FileText className="w-5 h-5" />,
      speaking: <Mic className="w-5 h-5" />
    };
    return icons[section] || <BookOpen className="w-5 h-5" />;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-4 border-green-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" onClick={() => navigate('/admin')}>
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Admin
              </Button>
              <h1 className="text-2xl font-bold text-gray-900">Exam Bank Management</h1>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" onClick={initializeOET}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Initialize OET Exams
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Panel - Exam List */}
          <div className="lg:col-span-1 space-y-4">
            {/* Filters */}
            <Card>
              <CardContent className="p-4 space-y-4">
                <div className="flex items-center gap-2">
                  <Filter className="w-5 h-5 text-gray-500" />
                  <span className="font-semibold">Filters</span>
                </div>
                
                <div className="grid grid-cols-2 gap-2">
                  <select
                    className="border rounded-lg px-3 py-2 text-sm"
                    value={filter.type}
                    onChange={(e) => setFilter(prev => ({ ...prev, type: e.target.value }))}
                  >
                    <option value="all">All Types</option>
                    <option value="oet">OET</option>
                    <option value="ielts">IELTS</option>
                    <option value="toefl">TOEFL</option>
                    <option value="toeic">TOEIC</option>
                    <option value="celpip">CELPIP</option>
                    <option value="pte">PTE</option>
                  </select>
                  
                  <select
                    className="border rounded-lg px-3 py-2 text-sm"
                    value={filter.status}
                    onChange={(e) => setFilter(prev => ({ ...prev, status: e.target.value }))}
                  >
                    <option value="all">All Status</option>
                    <option value="draft">Draft</option>
                    <option value="pending_human_review">Pending Review</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </div>
                
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <Input
                    placeholder="Search exams..."
                    className="pl-9"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Exam List */}
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {exams.length === 0 ? (
                <Card>
                  <CardContent className="p-8 text-center">
                    <BookOpen className="w-12 h-12 mx-auto text-gray-300 mb-4" />
                    <p className="text-gray-500">No exams found</p>
                    <Button className="mt-4" onClick={initializeOET}>
                      Initialize OET Exams
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                exams.filter(e => 
                  e.exam_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  e.topics_covered?.some(t => t.toLowerCase().includes(searchTerm.toLowerCase()))
                ).map((exam) => (
                  <Card 
                    key={exam.exam_id}
                    className={`cursor-pointer transition-all hover:shadow-md ${
                      selectedExam?.exam_id === exam.exam_id ? 'ring-2 ring-green-500' : ''
                    }`}
                    onClick={() => setSelectedExam(exam)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="font-semibold text-gray-900">{exam.exam_id}</h3>
                          <p className="text-sm text-gray-500">{exam.profession || 'General'}</p>
                        </div>
                        {getStatusBadge(exam.validation_status)}
                      </div>
                      
                      <div className="flex flex-wrap gap-1 mt-2">
                        {exam.topics_covered?.slice(0, 3).map((topic, i) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            {topic.replace(/_/g, ' ')}
                          </Badge>
                        ))}
                        {exam.topics_covered?.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{exam.topics_covered.length - 3} more
                          </Badge>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </div>

          {/* Right Panel - Exam Details */}
          <div className="lg:col-span-2">
            {selectedExam ? (
              <div className="space-y-6">
                {/* Exam Header */}
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h2 className="text-2xl font-bold text-gray-900">{selectedExam.exam_id}</h2>
                        <p className="text-gray-500">
                          {selectedExam.exam_type?.toUpperCase()} - {selectedExam.profession}
                        </p>
                      </div>
                      {getStatusBadge(selectedExam.validation_status)}
                    </div>

                    {/* Quick Stats */}
                    <div className="grid grid-cols-4 gap-4 mb-6">
                      <div className="bg-blue-50 rounded-lg p-3 text-center">
                        <Headphones className="w-6 h-6 mx-auto text-blue-600 mb-1" />
                        <p className="text-xs text-gray-500">Listening</p>
                        <p className="font-bold text-blue-600">42 Q</p>
                      </div>
                      <div className="bg-green-50 rounded-lg p-3 text-center">
                        <BookOpen className="w-6 h-6 mx-auto text-green-600 mb-1" />
                        <p className="text-xs text-gray-500">Reading</p>
                        <p className="font-bold text-green-600">42 Q</p>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-3 text-center">
                        <FileText className="w-6 h-6 mx-auto text-purple-600 mb-1" />
                        <p className="text-xs text-gray-500">Writing</p>
                        <p className="font-bold text-purple-600">1 Task</p>
                      </div>
                      <div className="bg-orange-50 rounded-lg p-3 text-center">
                        <Mic className="w-6 h-6 mx-auto text-orange-600 mb-1" />
                        <p className="text-xs text-gray-500">Speaking</p>
                        <p className="font-bold text-orange-600">2 RP</p>
                      </div>
                    </div>

                    {/* Topics at a glance */}
                    <div className="mb-6">
                      <h3 className="font-semibold text-gray-700 mb-2">Topics Covered</h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedExam.topics_covered?.map((topic, i) => (
                          <Badge key={i} className="bg-gray-100 text-gray-700">
                            {topic.replace(/_/g, ' ')}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Validation Actions */}
                    {selectedExam.validation_status !== 'approved' && (
                      <div className="flex gap-3 pt-4 border-t">
                        <Button 
                          className="bg-green-600 hover:bg-green-700 flex-1"
                          onClick={() => validateExam(selectedExam.exam_id, 'approve')}
                        >
                          <CheckCircle className="w-4 h-4 mr-2" />
                          Approve
                        </Button>
                        <Button 
                          variant="outline"
                          className="border-orange-300 text-orange-600 hover:bg-orange-50 flex-1"
                          onClick={() => validateExam(selectedExam.exam_id, 'request_changes')}
                        >
                          <Edit2 className="w-4 h-4 mr-2" />
                          Request Changes
                        </Button>
                        <Button 
                          variant="outline"
                          className="border-red-300 text-red-600 hover:bg-red-50 flex-1"
                          onClick={() => validateExam(selectedExam.exam_id, 'reject')}
                        >
                          <XCircle className="w-4 h-4 mr-2" />
                          Reject
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Listening Section */}
                <Card>
                  <CardHeader 
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => toggleSection('listening')}
                  >
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <Headphones className="w-5 h-5 text-blue-600" />
                        Listening Section
                      </CardTitle>
                      {expandedSections.listening ? <ChevronUp /> : <ChevronDown />}
                    </div>
                  </CardHeader>
                  {expandedSections.listening && selectedExam.listening && (
                    <CardContent className="space-y-4">
                      {/* Part A */}
                      <div className="border rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 mb-2">Part A - Consultation Extracts</h4>
                        {selectedExam.listening.part_a && (
                          <>
                            <div className="bg-blue-50 rounded-lg p-3 mb-3">
                              <p className="text-sm text-gray-700">
                                <strong>Consultation 1:</strong> {selectedExam.listening.part_a.consultation_1?.scenario}
                              </p>
                            </div>
                            <div className="space-y-2">
                              {selectedExam.listening.part_a.consultation_1?.questions?.slice(0, 5).map((q, i) => (
                                <div key={i} className="flex items-start gap-3 text-sm bg-white p-2 rounded border">
                                  <span className="bg-blue-100 text-blue-700 rounded px-2 py-0.5 text-xs font-medium">
                                    Q{q.number}
                                  </span>
                                  <div className="flex-1">
                                    <p className="text-gray-700">{q.blank}</p>
                                    <p className="text-green-600 font-medium">Answer: {q.answer}</p>
                                  </div>
                                </div>
                              ))}
                              {selectedExam.listening.part_a.consultation_1?.questions?.length > 5 && (
                                <p className="text-sm text-gray-500 text-center">
                                  + {selectedExam.listening.part_a.consultation_1.questions.length - 5} more questions
                                </p>
                              )}
                            </div>
                          </>
                        )}
                      </div>

                      {/* Part B */}
                      <div className="border rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 mb-2">Part B - Workplace Extracts</h4>
                        {selectedExam.listening.part_b?.extracts?.slice(0, 2).map((ext, i) => (
                          <div key={i} className="bg-gray-50 rounded-lg p-3 mb-2">
                            <p className="text-sm text-gray-700 mb-1"><strong>{ext.context}</strong></p>
                            <p className="text-sm text-gray-600">{ext.question}</p>
                            <p className="text-sm text-green-600 font-medium">Answer: {ext.answer}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  )}
                </Card>

                {/* Reading Section */}
                <Card>
                  <CardHeader 
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => toggleSection('reading')}
                  >
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <BookOpen className="w-5 h-5 text-green-600" />
                        Reading Section
                      </CardTitle>
                      {expandedSections.reading ? <ChevronUp /> : <ChevronDown />}
                    </div>
                  </CardHeader>
                  {expandedSections.reading && selectedExam.reading && (
                    <CardContent className="space-y-4">
                      {/* Part A */}
                      <div className="border rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 mb-2">
                          Part A - {selectedExam.reading.part_a?.theme?.replace(/_/g, ' ')}
                        </h4>
                        <div className="grid md:grid-cols-2 gap-3">
                          {selectedExam.reading.part_a?.texts && Object.entries(selectedExam.reading.part_a.texts).map(([key, text]) => (
                            <div key={key} className="bg-gray-50 rounded-lg p-3">
                              <Badge className="mb-2">{key}</Badge>
                              <h5 className="font-medium text-sm mb-1">{text.title}</h5>
                              <p className="text-xs text-gray-500 line-clamp-3">{text.content}</p>
                            </div>
                          ))}
                        </div>
                        <div className="mt-3 space-y-1">
                          {selectedExam.reading.part_a?.questions?.slice(0, 5).map((q, i) => (
                            <div key={i} className="flex items-center gap-2 text-sm">
                              <Badge variant="outline" className="text-xs">Q{q.number}</Badge>
                              <span className="text-gray-600 flex-1 truncate">{q.question}</span>
                              <span className="text-green-600 font-medium">{q.answer}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  )}
                </Card>

                {/* Writing Section */}
                <Card>
                  <CardHeader 
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => toggleSection('writing')}
                  >
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <FileText className="w-5 h-5 text-purple-600" />
                        Writing Section
                      </CardTitle>
                      {expandedSections.writing ? <ChevronUp /> : <ChevronDown />}
                    </div>
                  </CardHeader>
                  {expandedSections.writing && selectedExam.writing && (
                    <CardContent className="space-y-4">
                      <div className="bg-purple-50 rounded-lg p-4">
                        <Badge className="mb-2">{selectedExam.writing.letter_type} Letter</Badge>
                        <p className="text-sm text-gray-700 mb-3">{selectedExam.writing.task_instructions}</p>
                        
                        <h5 className="font-semibold text-sm mb-2">Case Notes Summary:</h5>
                        <div className="bg-white rounded p-3 text-sm">
                          <p><strong>Patient:</strong> {selectedExam.writing.case_notes?.patient_name}</p>
                          <p><strong>DOB:</strong> {selectedExam.writing.case_notes?.dob}</p>
                          <p><strong>Presenting Complaint:</strong> {selectedExam.writing.case_notes?.presenting_complaint}</p>
                        </div>
                      </div>
                      
                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="border rounded-lg p-3">
                          <h5 className="font-semibold text-green-700 mb-2 flex items-center gap-1">
                            <Check className="w-4 h-4" /> Key Points to Include
                          </h5>
                          <ul className="text-sm space-y-1">
                            {selectedExam.writing.key_points_to_include?.map((point, i) => (
                              <li key={i} className="text-gray-600">• {point}</li>
                            ))}
                          </ul>
                        </div>
                        <div className="border rounded-lg p-3">
                          <h5 className="font-semibold text-red-700 mb-2 flex items-center gap-1">
                            <X className="w-4 h-4" /> Points to Omit
                          </h5>
                          <ul className="text-sm space-y-1">
                            {selectedExam.writing.points_to_omit?.map((point, i) => (
                              <li key={i} className="text-gray-600">• {point}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </CardContent>
                  )}
                </Card>

                {/* Speaking Section */}
                <Card>
                  <CardHeader 
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => toggleSection('speaking')}
                  >
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <Mic className="w-5 h-5 text-orange-600" />
                        Speaking Section
                      </CardTitle>
                      {expandedSections.speaking ? <ChevronUp /> : <ChevronDown />}
                    </div>
                  </CardHeader>
                  {expandedSections.speaking && selectedExam.speaking && (
                    <CardContent className="space-y-4">
                      {[selectedExam.speaking.role_play_1, selectedExam.speaking.role_play_2].map((rp, i) => rp && (
                        <div key={i} className="border rounded-lg p-4">
                          <Badge className="mb-2">Role Play {i + 1}</Badge>
                          <h4 className="font-semibold text-gray-900">{rp.scenario_title}</h4>
                          <p className="text-sm text-gray-500 mb-3">{rp.setting}</p>
                          
                          <div className="grid md:grid-cols-2 gap-4">
                            <div className="bg-blue-50 rounded-lg p-3">
                              <h5 className="font-medium text-sm mb-2">Candidate Card</h5>
                              <p className="text-xs text-gray-600 mb-2">{rp.candidate_card?.situation}</p>
                              <ul className="text-xs space-y-1">
                                {rp.candidate_card?.tasks?.map((task, j) => (
                                  <li key={j}>• {task}</li>
                                ))}
                              </ul>
                            </div>
                            <div className="bg-orange-50 rounded-lg p-3">
                              <h5 className="font-medium text-sm mb-2">Interlocutor Card</h5>
                              <p className="text-xs text-gray-600 mb-2">{rp.interlocutor_card?.background}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  )}
                </Card>
              </div>
            ) : (
              <Card className="h-full flex items-center justify-center">
                <CardContent className="text-center py-16">
                  <Eye className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">Select an Exam</h3>
                  <p className="text-gray-500">Click on an exam from the list to view details and validate</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
