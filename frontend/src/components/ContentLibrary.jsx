import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Textarea } from '../components/ui/textarea';
import { Switch } from '../components/ui/switch';
import {
  Upload, FileText, Video, BookOpen, Image, Trash2, Download, Eye, 
  Search, Filter, FolderPlus, File, MoreVertical, Cloud, CloudOff,
  Sparkles, BookMarked, Languages, Plus, RefreshCw, Check, X
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

// File type icons and colors
const FILE_TYPES = {
  pdf: { icon: FileText, color: 'text-red-500', bg: 'bg-red-50' },
  video: { icon: Video, color: 'text-blue-500', bg: 'bg-blue-50' },
  image: { icon: Image, color: 'text-green-500', bg: 'bg-green-50' },
  document: { icon: File, color: 'text-purple-500', bg: 'bg-purple-50' },
  book: { icon: BookOpen, color: 'text-amber-500', bg: 'bg-amber-50' },
};

// Material Upload Component
const MaterialUploader = ({ onUploadComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      await uploadFiles(files);
    }
  };

  const handleFileSelect = async (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await uploadFiles(files);
    }
  };

  const uploadFiles = async (files) => {
    setUploading(true);
    setUploadProgress(0);

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const formData = new FormData();
      formData.append('file', file);

      try {
        await axios.post(`${API_URL}/library/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            const progress = ((i + progressEvent.loaded / progressEvent.total) / files.length) * 100;
            setUploadProgress(Math.round(progress));
          }
        });
        toast.success(`Uploaded: ${file.name}`);
      } catch (error) {
        toast.error(`Failed to upload: ${file.name}`);
      }
    }

    setUploading(false);
    setUploadProgress(0);
    onUploadComplete?.();
  };

  return (
    <div
      className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
        dragActive ? 'border-[#58CC02] bg-green-50' : 'border-gray-300 hover:border-gray-400'
      }`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        multiple
        accept=".pdf,.mp4,.mov,.avi,.jpg,.jpeg,.png,.doc,.docx,.epub"
        onChange={handleFileSelect}
        className="hidden"
        id="file-upload"
      />
      
      {uploading ? (
        <div className="space-y-4">
          <div className="w-16 h-16 mx-auto rounded-full bg-[#58CC02]/10 flex items-center justify-center">
            <RefreshCw className="w-8 h-8 text-[#58CC02] animate-spin" />
          </div>
          <div>
            <p className="text-gray-600 font-medium">Uploading...</p>
            <Progress value={uploadProgress} className="mt-2 h-2" />
            <p className="text-sm text-gray-500 mt-1">{uploadProgress}%</p>
          </div>
        </div>
      ) : (
        <>
          <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600 mb-2">Drag and drop files here, or</p>
          <label htmlFor="file-upload">
            <Button className="btn-duo cursor-pointer" asChild>
              <span>Browse Files</span>
            </Button>
          </label>
          <p className="text-xs text-gray-400 mt-3">
            Supported: PDF, Videos (MP4, MOV), Images, Documents, eBooks
          </p>
        </>
      )}
    </div>
  );
};

// Vocabulary Manager Component
const VocabularyManager = () => {
  const [vocabularies, setVocabularies] = useState([]);
  const [createOpen, setCreateOpen] = useState(false);
  const [newVocab, setNewVocab] = useState({
    name: '',
    description: '',
    words: '',
    exam_type: 'all',
    auto_generate_flashcards: true
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchVocabularies();
  }, []);

  const fetchVocabularies = async () => {
    try {
      const response = await axios.get(`${API_URL}/library/vocabularies`);
      setVocabularies(response.data.vocabularies || []);
    } catch (error) {
      console.error('Failed to fetch vocabularies:', error);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Parse words (comma or newline separated)
      const wordList = newVocab.words
        .split(/[,\n]/)
        .map(w => w.trim())
        .filter(w => w.length > 0);

      await axios.post(`${API_URL}/library/vocabularies`, {
        ...newVocab,
        words: wordList
      });
      
      toast.success('Vocabulary list created!');
      if (newVocab.auto_generate_flashcards) {
        toast.info('Generating flashcards...');
      }
      setCreateOpen(false);
      setNewVocab({ name: '', description: '', words: '', exam_type: 'all', auto_generate_flashcards: true });
      fetchVocabularies();
    } catch (error) {
      toast.error('Failed to create vocabulary list');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-bold text-gray-900">Vocabulary Lists</h3>
          <p className="text-sm text-gray-500">Custom vocabulary for your students</p>
        </div>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button className="btn-duo" data-testid="create-vocab-btn">
              <Plus className="w-4 h-4 mr-2" /> New List
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-lg">
            <DialogHeader>
              <DialogTitle className="text-gray-900 font-extrabold">Create Vocabulary List</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <Label>List Name *</Label>
                <Input
                  value={newVocab.name}
                  onChange={(e) => setNewVocab({...newVocab, name: e.target.value})}
                  required
                  className="input-duo"
                  placeholder="e.g., IELTS Academic Words"
                />
              </div>
              <div>
                <Label>Description</Label>
                <Input
                  value={newVocab.description}
                  onChange={(e) => setNewVocab({...newVocab, description: e.target.value})}
                  className="input-duo"
                  placeholder="Brief description..."
                />
              </div>
              <div>
                <Label>Words (one per line or comma-separated) *</Label>
                <Textarea
                  value={newVocab.words}
                  onChange={(e) => setNewVocab({...newVocab, words: e.target.value})}
                  required
                  className="input-duo font-mono"
                  rows={6}
                  placeholder="apple&#10;banana&#10;cherry&#10;or: apple, banana, cherry"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {newVocab.words.split(/[,\n]/).filter(w => w.trim()).length} words
                </p>
              </div>
              <div className="flex items-center justify-between p-3 bg-purple-50 rounded-xl">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-500" />
                  <div>
                    <p className="font-medium text-gray-900 text-sm">Auto-generate Flashcards</p>
                    <p className="text-xs text-gray-500">AI creates definitions and examples</p>
                  </div>
                </div>
                <Switch
                  checked={newVocab.auto_generate_flashcards}
                  onCheckedChange={(checked) => setNewVocab({...newVocab, auto_generate_flashcards: checked})}
                />
              </div>
              <Button type="submit" className="btn-duo w-full" disabled={loading}>
                {loading ? 'Creating...' : 'Create Vocabulary List'}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {vocabularies.map((vocab) => (
          <Card key={vocab.id} className="border-2 border-gray-100 rounded-xl">
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <BookMarked className="w-5 h-5 text-purple-500" />
                  <h4 className="font-bold text-gray-900">{vocab.name}</h4>
                </div>
                <Badge variant="outline">{vocab.word_count} words</Badge>
              </div>
              <p className="text-sm text-gray-500 mb-3">{vocab.description || 'No description'}</p>
              <div className="flex items-center justify-between">
                <div className="flex gap-2">
                  {vocab.has_flashcards && (
                    <Badge className="bg-green-100 text-green-700">Flashcards Ready</Badge>
                  )}
                  {vocab.offline_available && (
                    <Badge className="bg-blue-100 text-blue-700">
                      <CloudOff className="w-3 h-3 mr-1" /> Offline
                    </Badge>
                  )}
                </div>
                <Button size="sm" variant="ghost">
                  <Eye className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
        {vocabularies.length === 0 && (
          <div className="col-span-full text-center py-8">
            <BookMarked className="w-12 h-12 mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">No vocabulary lists yet</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Flashcard Manager Component
const FlashcardManager = () => {
  const [flashcardSets, setFlashcardSets] = useState([]);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchFlashcards();
  }, []);

  const fetchFlashcards = async () => {
    try {
      const response = await axios.get(`${API_URL}/library/flashcards`);
      setFlashcardSets(response.data.flashcard_sets || []);
    } catch (error) {
      console.error('Failed to fetch flashcards:', error);
    }
  };

  const generateFromMaterial = async (materialId) => {
    setGenerating(true);
    try {
      await axios.post(`${API_URL}/library/flashcards/generate`, { material_id: materialId });
      toast.success('Flashcards generated successfully!');
      fetchFlashcards();
    } catch (error) {
      toast.error('Failed to generate flashcards');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-bold text-gray-900">Flashcard Sets</h3>
          <p className="text-sm text-gray-500">Auto-generated or custom flashcards</p>
        </div>
        <Button className="btn-duo" disabled={generating}>
          <Sparkles className="w-4 h-4 mr-2" />
          {generating ? 'Generating...' : 'Generate from Material'}
        </Button>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        {flashcardSets.map((set) => (
          <Card key={set.id} className="border-2 border-gray-100 rounded-xl hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-4 text-center">
              <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 mx-auto mb-3 flex items-center justify-center">
                <BookOpen className="w-7 h-7 text-white" />
              </div>
              <h4 className="font-bold text-gray-900 mb-1">{set.name}</h4>
              <p className="text-sm text-gray-500 mb-3">{set.card_count} cards</p>
              <div className="flex items-center justify-center gap-2">
                {set.offline_available && (
                  <Badge variant="outline" className="text-xs">
                    <CloudOff className="w-3 h-3 mr-1" /> Offline
                  </Badge>
                )}
                <Badge className="bg-purple-100 text-purple-700 text-xs">
                  {set.mastery || 0}% mastered
                </Badge>
              </div>
            </CardContent>
          </Card>
        ))}
        {flashcardSets.length === 0 && (
          <div className="col-span-full text-center py-8">
            <BookOpen className="w-12 h-12 mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">No flashcard sets yet</p>
            <p className="text-xs text-gray-400 mt-1">Create vocabulary lists to auto-generate flashcards</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Main Content Library Component
export default function ContentLibrary() {
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('materials');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    fetchMaterials();
  }, []);

  const fetchMaterials = async () => {
    try {
      const response = await axios.get(`${API_URL}/library/materials`);
      setMaterials(response.data.materials || []);
    } catch (error) {
      console.error('Failed to fetch materials:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleOffline = async (materialId, currentStatus) => {
    try {
      await axios.post(`${API_URL}/library/materials/${materialId}/offline`, {
        enabled: !currentStatus
      });
      toast.success(currentStatus ? 'Removed from offline' : 'Added to offline');
      fetchMaterials();
    } catch (error) {
      toast.error('Failed to update offline status');
    }
  };

  const deleteMaterial = async (materialId) => {
    if (!window.confirm('Are you sure you want to delete this material?')) return;
    try {
      await axios.delete(`${API_URL}/library/materials/${materialId}`);
      toast.success('Material deleted');
      fetchMaterials();
    } catch (error) {
      toast.error('Failed to delete material');
    }
  };

  const getFileType = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    if (['pdf'].includes(ext)) return 'pdf';
    if (['mp4', 'mov', 'avi', 'webm'].includes(ext)) return 'video';
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) return 'image';
    if (['epub', 'mobi'].includes(ext)) return 'book';
    return 'document';
  };

  const filteredMaterials = materials.filter(m => {
    const matchesSearch = m.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterType === 'all' || getFileType(m.filename) === filterType;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6" data-testid="content-library">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-gray-900">Content Library</h2>
          <p className="text-gray-500">Manage materials, vocabulary, and flashcards</p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="materials" className="flex items-center gap-2">
            <FolderPlus className="w-4 h-4" /> Materials
          </TabsTrigger>
          <TabsTrigger value="vocabulary" className="flex items-center gap-2">
            <Languages className="w-4 h-4" /> Vocabulary
          </TabsTrigger>
          <TabsTrigger value="flashcards" className="flex items-center gap-2">
            <BookOpen className="w-4 h-4" /> Flashcards
          </TabsTrigger>
        </TabsList>

        <div className="mt-6">
          <TabsContent value="materials">
            <div className="space-y-6">
              {/* Upload Section */}
              <MaterialUploader onUploadComplete={fetchMaterials} />

              {/* Search and Filter */}
              <div className="flex gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search materials..."
                    className="input-duo pl-10"
                  />
                </div>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="h-10 px-4 border-2 border-gray-200 rounded-xl focus:border-[#58CC02] outline-none"
                >
                  <option value="all">All Types</option>
                  <option value="pdf">PDFs</option>
                  <option value="video">Videos</option>
                  <option value="image">Images</option>
                  <option value="document">Documents</option>
                  <option value="book">eBooks</option>
                </select>
              </div>

              {/* Materials Grid */}
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="w-10 h-10 border-4 border-[#58CC02] border-t-transparent rounded-full animate-spin"></div>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredMaterials.map((material) => {
                    const fileType = getFileType(material.filename);
                    const TypeIcon = FILE_TYPES[fileType]?.icon || File;
                    const typeColor = FILE_TYPES[fileType]?.color || 'text-gray-500';
                    const typeBg = FILE_TYPES[fileType]?.bg || 'bg-gray-50';

                    return (
                      <Card key={material.id} className="border-2 border-gray-100 rounded-xl group hover:shadow-md transition-all">
                        <CardContent className="p-4">
                          <div className="flex items-start gap-3">
                            <div className={`w-12 h-12 rounded-xl ${typeBg} flex items-center justify-center flex-shrink-0`}>
                              <TypeIcon className={`w-6 h-6 ${typeColor}`} />
                            </div>
                            <div className="flex-1 min-w-0">
                              <h4 className="font-semibold text-gray-900 truncate">{material.name}</h4>
                              <p className="text-xs text-gray-500">{material.size_formatted}</p>
                            </div>
                          </div>
                          
                          <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
                            <div className="flex gap-2">
                              <button
                                onClick={() => toggleOffline(material.id, material.offline_enabled)}
                                className={`p-2 rounded-lg transition-colors ${
                                  material.offline_enabled 
                                    ? 'bg-blue-100 text-blue-600' 
                                    : 'bg-gray-100 text-gray-400 hover:text-gray-600'
                                }`}
                                title={material.offline_enabled ? 'Remove from offline' : 'Make available offline'}
                              >
                                {material.offline_enabled ? <CloudOff className="w-4 h-4" /> : <Cloud className="w-4 h-4" />}
                              </button>
                            </div>
                            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                              <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                                <Eye className="w-4 h-4" />
                              </Button>
                              <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                                <Download className="w-4 h-4" />
                              </Button>
                              <Button 
                                size="sm" 
                                variant="ghost" 
                                className="h-8 w-8 p-0 text-red-500 hover:text-red-600"
                                onClick={() => deleteMaterial(material.id)}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                  
                  {filteredMaterials.length === 0 && (
                    <div className="col-span-full text-center py-12">
                      <FolderPlus className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                      <h3 className="text-lg font-semibold text-gray-600 mb-2">No materials yet</h3>
                      <p className="text-gray-400">Upload PDFs, videos, and documents for your students</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="vocabulary">
            <VocabularyManager />
          </TabsContent>

          <TabsContent value="flashcards">
            <FlashcardManager />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}
