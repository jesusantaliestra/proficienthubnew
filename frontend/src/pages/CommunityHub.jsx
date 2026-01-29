import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  ArrowLeft, MessageSquare, Users, BookOpen, HelpCircle, Trophy, Target,
  Plus, Search, Heart, MessageCircle, Eye, Pin, CheckCircle, Clock,
  Filter, TrendingUp, Calendar, UserPlus, Lock, Globe, Send
} from 'lucide-react';
import axios from 'axios';
import { toast, Toaster } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function CommunityHub() {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [activeTab, setActiveTab] = useState('forum');
  const [loading, setLoading] = useState(true);
  
  // Forum State
  const [posts, setPosts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [createPostOpen, setCreatePostOpen] = useState(false);
  const [selectedPost, setSelectedPost] = useState(null);
  const [newPost, setNewPost] = useState({ title: '', content: '', category: 'general', tags: '' });
  const [newReply, setNewReply] = useState('');
  
  // Study Groups State
  const [groups, setGroups] = useState([]);
  const [createGroupOpen, setCreateGroupOpen] = useState(false);
  const [newGroup, setNewGroup] = useState({ name: '', description: '', exam_type: 'IELTS', max_members: 20, is_private: false });

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  useEffect(() => {
    fetchCategories();
    fetchPosts();
    fetchGroups();
  }, [selectedCategory, sortBy]);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API_URL}/community/forum/categories`, axiosConfig);
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (selectedCategory) params.append('category', selectedCategory);
      if (searchQuery) params.append('search', searchQuery);
      params.append('sort_by', sortBy);
      
      const response = await axios.get(`${API_URL}/community/forum/posts?${params}`, axiosConfig);
      setPosts(response.data.posts || []);
    } catch (error) {
      console.error('Failed to fetch posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchGroups = async () => {
    try {
      const response = await axios.get(`${API_URL}/community/groups`, axiosConfig);
      setGroups(response.data.groups || []);
    } catch (error) {
      console.error('Failed to fetch groups:', error);
    }
  };

  const handleCreatePost = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/community/forum/posts`, {
        ...newPost,
        tags: newPost.tags.split(',').map(t => t.trim()).filter(Boolean)
      }, axiosConfig);
      toast.success('Post created successfully!');
      setCreatePostOpen(false);
      setNewPost({ title: '', content: '', category: 'general', tags: '' });
      fetchPosts();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create post');
    }
  };

  const handleLikePost = async (postId) => {
    try {
      await axios.post(`${API_URL}/community/forum/posts/${postId}/like`, {}, axiosConfig);
      fetchPosts();
    } catch (error) {
      toast.error('Failed to like post');
    }
  };

  const handleViewPost = async (post) => {
    try {
      const response = await axios.get(`${API_URL}/community/forum/posts/${post.id}`, axiosConfig);
      setSelectedPost(response.data);
    } catch (error) {
      toast.error('Failed to load post');
    }
  };

  const handleReply = async () => {
    if (!newReply.trim() || !selectedPost) return;
    try {
      await axios.post(`${API_URL}/community/forum/posts/${selectedPost.id}/replies`, {
        content: newReply
      }, axiosConfig);
      toast.success('Reply posted!');
      setNewReply('');
      handleViewPost(selectedPost);
    } catch (error) {
      toast.error('Failed to post reply');
    }
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/community/groups`, newGroup, axiosConfig);
      toast.success('Study group created!');
      setCreateGroupOpen(false);
      setNewGroup({ name: '', description: '', exam_type: 'IELTS', max_members: 20, is_private: false });
      fetchGroups();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create group');
    }
  };

  const handleJoinGroup = async (groupId) => {
    try {
      await axios.post(`${API_URL}/community/groups/${groupId}/join`, {}, axiosConfig);
      toast.success('Joined group!');
      fetchGroups();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to join group');
    }
  };

  const getCategoryIcon = (categoryId) => {
    const icons = {
      general: MessageSquare,
      exam_tips: Target,
      study_partners: Users,
      resources: BookOpen,
      questions: HelpCircle,
      success_stories: Trophy
    };
    return icons[categoryId] || MessageSquare;
  };

  const formatTimeAgo = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="min-h-screen bg-gray-50" data-testid="community-hub">
      <Toaster position="top-right" richColors />
      
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate(-1)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
                  <Users className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">Community Hub</h1>
                  <p className="text-sm text-gray-500">Connect, Learn, Succeed Together</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-white border rounded-xl p-1">
            <TabsTrigger value="forum" className="flex items-center gap-2 data-[state=active]:bg-indigo-600 data-[state=active]:text-white rounded-lg">
              <MessageSquare className="w-4 h-4" /> Forum
            </TabsTrigger>
            <TabsTrigger value="groups" className="flex items-center gap-2 data-[state=active]:bg-indigo-600 data-[state=active]:text-white rounded-lg">
              <Users className="w-4 h-4" /> Study Groups
            </TabsTrigger>
          </TabsList>

          {/* Forum Tab */}
          <TabsContent value="forum" className="space-y-6">
            <div className="flex items-center justify-between gap-4">
              {/* Search */}
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="Search discussions..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && fetchPosts()}
                  className="pl-10 border-2 border-gray-200 rounded-xl"
                />
              </div>
              
              {/* Filters */}
              <div className="flex items-center gap-2">
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger className="w-40 border-2 border-gray-200 rounded-xl">
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="created_at">Latest</SelectItem>
                    <SelectItem value="likes">Most Liked</SelectItem>
                    <SelectItem value="views">Most Viewed</SelectItem>
                    <SelectItem value="reply_count">Most Replies</SelectItem>
                  </SelectContent>
                </Select>
                
                <Dialog open={createPostOpen} onOpenChange={setCreatePostOpen}>
                  <DialogTrigger asChild>
                    <Button className="bg-indigo-600 hover:bg-indigo-700 text-white" data-testid="create-post-btn">
                      <Plus className="w-4 h-4 mr-2" /> New Post
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-lg">
                    <DialogHeader>
                      <DialogTitle className="text-gray-900 font-bold">Create Discussion</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleCreatePost} className="space-y-4">
                      <div>
                        <Label>Title</Label>
                        <Input
                          value={newPost.title}
                          onChange={(e) => setNewPost({...newPost, title: e.target.value})}
                          placeholder="What's your question or topic?"
                          className="border-2 border-gray-200 rounded-xl"
                          required
                        />
                      </div>
                      <div>
                        <Label>Category</Label>
                        <Select value={newPost.category} onValueChange={(v) => setNewPost({...newPost, category: v})}>
                          <SelectTrigger className="border-2 border-gray-200 rounded-xl">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {categories.map((cat) => (
                              <SelectItem key={cat.id} value={cat.id}>{cat.name}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label>Content</Label>
                        <Textarea
                          value={newPost.content}
                          onChange={(e) => setNewPost({...newPost, content: e.target.value})}
                          placeholder="Share your thoughts, questions, or tips..."
                          className="border-2 border-gray-200 rounded-xl"
                          rows={4}
                          required
                        />
                      </div>
                      <div>
                        <Label>Tags (comma-separated)</Label>
                        <Input
                          value={newPost.tags}
                          onChange={(e) => setNewPost({...newPost, tags: e.target.value})}
                          placeholder="ielts, speaking, tips"
                          className="border-2 border-gray-200 rounded-xl"
                        />
                      </div>
                      <Button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700 text-white">
                        Post Discussion
                      </Button>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </div>

            <div className="grid lg:grid-cols-4 gap-6">
              {/* Categories Sidebar */}
              <div className="lg:col-span-1 space-y-3">
                <h3 className="font-bold text-gray-900 mb-3">Categories</h3>
                <button
                  onClick={() => { setSelectedCategory(''); fetchPosts(); }}
                  className={`w-full text-left p-3 rounded-xl transition-all ${
                    !selectedCategory ? 'bg-indigo-100 text-indigo-700' : 'bg-white hover:bg-gray-50'
                  }`}
                >
                  <span className="font-medium">All Discussions</span>
                </button>
                {categories.map((cat) => {
                  const Icon = getCategoryIcon(cat.id);
                  return (
                    <button
                      key={cat.id}
                      onClick={() => { setSelectedCategory(cat.id); }}
                      className={`w-full text-left p-3 rounded-xl flex items-center gap-3 transition-all ${
                        selectedCategory === cat.id ? 'bg-indigo-100 text-indigo-700' : 'bg-white hover:bg-gray-50'
                      }`}
                    >
                      <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: cat.color + '20' }}>
                        <Icon className="w-4 h-4" style={{ color: cat.color }} />
                      </div>
                      <span className="font-medium text-sm">{cat.name}</span>
                    </button>
                  );
                })}
              </div>

              {/* Posts List */}
              <div className="lg:col-span-3 space-y-4">
                {loading ? (
                  <div className="text-center py-12">
                    <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                  </div>
                ) : posts.length === 0 ? (
                  <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                    <CardContent className="p-12 text-center">
                      <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                      <h3 className="font-bold text-gray-700 mb-2">No discussions yet</h3>
                      <p className="text-gray-500 mb-4">Be the first to start a conversation!</p>
                      <Button onClick={() => setCreatePostOpen(true)} className="bg-indigo-600 hover:bg-indigo-700 text-white">
                        <Plus className="w-4 h-4 mr-2" /> Create First Post
                      </Button>
                    </CardContent>
                  </Card>
                ) : (
                  posts.map((post) => {
                    const CategoryIcon = getCategoryIcon(post.category);
                    const category = categories.find(c => c.id === post.category);
                    
                    return (
                      <Card
                        key={post.id}
                        className="bg-white border-2 border-gray-100 hover:border-gray-200 rounded-2xl cursor-pointer transition-all"
                        onClick={() => handleViewPost(post)}
                        data-testid={`post-${post.id}`}
                      >
                        <CardContent className="p-5">
                          <div className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold flex-shrink-0">
                              {post.author_name?.charAt(0) || 'A'}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                {post.is_pinned && <Pin className="w-4 h-4 text-amber-500" />}
                                {post.is_solved && <Badge className="bg-green-100 text-green-700 text-xs">Solved</Badge>}
                                <Badge variant="outline" className="text-xs" style={{ borderColor: category?.color, color: category?.color }}>
                                  {category?.name || post.category}
                                </Badge>
                              </div>
                              <h3 className="font-bold text-gray-900 mb-1 truncate">{post.title}</h3>
                              <p className="text-sm text-gray-500 line-clamp-2 mb-3">{post.content}</p>
                              
                              <div className="flex items-center gap-4 text-sm text-gray-500">
                                <span className="flex items-center gap-1">
                                  <Heart className="w-4 h-4" /> {post.likes}
                                </span>
                                <span className="flex items-center gap-1">
                                  <MessageCircle className="w-4 h-4" /> {post.reply_count}
                                </span>
                                <span className="flex items-center gap-1">
                                  <Eye className="w-4 h-4" /> {post.views}
                                </span>
                                <span className="flex items-center gap-1 ml-auto">
                                  <Clock className="w-4 h-4" /> {formatTimeAgo(post.created_at)}
                                </span>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })
                )}
              </div>
            </div>
          </TabsContent>

          {/* Study Groups Tab */}
          <TabsContent value="groups" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-gray-900">Study Groups</h2>
              <Dialog open={createGroupOpen} onOpenChange={setCreateGroupOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-indigo-600 hover:bg-indigo-700 text-white" data-testid="create-group-btn">
                    <Plus className="w-4 h-4 mr-2" /> Create Group
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-lg">
                  <DialogHeader>
                    <DialogTitle className="text-gray-900 font-bold">Create Study Group</DialogTitle>
                  </DialogHeader>
                  <form onSubmit={handleCreateGroup} className="space-y-4">
                    <div>
                      <Label>Group Name</Label>
                      <Input
                        value={newGroup.name}
                        onChange={(e) => setNewGroup({...newGroup, name: e.target.value})}
                        placeholder="e.g., IELTS Band 7+ Study Group"
                        className="border-2 border-gray-200 rounded-xl"
                        required
                      />
                    </div>
                    <div>
                      <Label>Description</Label>
                      <Textarea
                        value={newGroup.description}
                        onChange={(e) => setNewGroup({...newGroup, description: e.target.value})}
                        placeholder="What's the focus of this group?"
                        className="border-2 border-gray-200 rounded-xl"
                        rows={3}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label>Exam Type</Label>
                        <Select value={newGroup.exam_type} onValueChange={(v) => setNewGroup({...newGroup, exam_type: v})}>
                          <SelectTrigger className="border-2 border-gray-200 rounded-xl">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="IELTS">IELTS</SelectItem>
                            <SelectItem value="TOEFL">TOEFL</SelectItem>
                            <SelectItem value="PTE">PTE</SelectItem>
                            <SelectItem value="Cambridge">Cambridge</SelectItem>
                            <SelectItem value="Other">Other</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label>Max Members</Label>
                        <Input
                          type="number"
                          value={newGroup.max_members}
                          onChange={(e) => setNewGroup({...newGroup, max_members: parseInt(e.target.value)})}
                          min="2"
                          max="100"
                          className="border-2 border-gray-200 rounded-xl"
                        />
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        id="private"
                        checked={newGroup.is_private}
                        onChange={(e) => setNewGroup({...newGroup, is_private: e.target.checked})}
                        className="rounded"
                      />
                      <Label htmlFor="private" className="text-sm">Private group (invite only)</Label>
                    </div>
                    <Button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700 text-white">
                      Create Group
                    </Button>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {groups.length === 0 ? (
                <Card className="md:col-span-2 lg:col-span-3 bg-white border-2 border-gray-100 rounded-2xl">
                  <CardContent className="p-12 text-center">
                    <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <h3 className="font-bold text-gray-700 mb-2">No study groups yet</h3>
                    <p className="text-gray-500 mb-4">Create a group and invite others to study together!</p>
                    <Button onClick={() => setCreateGroupOpen(true)} className="bg-indigo-600 hover:bg-indigo-700 text-white">
                      <Plus className="w-4 h-4 mr-2" /> Create First Group
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                groups.map((group) => (
                  <Card key={group.id} className="bg-white border-2 border-gray-100 rounded-2xl hover:border-indigo-200 transition-all">
                    <CardContent className="p-5">
                      <div className="flex items-start justify-between mb-3">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
                          <Users className="w-6 h-6 text-white" />
                        </div>
                        {group.is_private ? (
                          <Badge variant="outline" className="flex items-center gap-1">
                            <Lock className="w-3 h-3" /> Private
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="flex items-center gap-1 text-green-600 border-green-200">
                            <Globe className="w-3 h-3" /> Public
                          </Badge>
                        )}
                      </div>
                      <h3 className="font-bold text-gray-900 mb-1">{group.name}</h3>
                      <p className="text-sm text-gray-500 mb-3 line-clamp-2">{group.description || 'No description'}</p>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                        <Badge variant="outline">{group.exam_type}</Badge>
                        <span className="flex items-center gap-1">
                          <Users className="w-4 h-4" />
                          {group.member_count}/{group.max_members}
                        </span>
                      </div>
                      
                      {group.members?.includes(user?.id) ? (
                        <Button variant="outline" className="w-full" disabled>
                          <CheckCircle className="w-4 h-4 mr-2" /> Joined
                        </Button>
                      ) : (
                        <Button 
                          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white"
                          onClick={() => handleJoinGroup(group.id)}
                        >
                          <UserPlus className="w-4 h-4 mr-2" /> Join Group
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>
        </Tabs>
      </main>

      {/* Post Detail Dialog */}
      <Dialog open={!!selectedPost} onOpenChange={() => setSelectedPost(null)}>
        <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-2xl max-h-[90vh] overflow-y-auto">
          {selectedPost && (
            <>
              <DialogHeader>
                <div className="flex items-center gap-2 mb-2">
                  {selectedPost.is_solved && <Badge className="bg-green-100 text-green-700">Solved</Badge>}
                  <Badge variant="outline">{selectedPost.category}</Badge>
                </div>
                <DialogTitle className="text-gray-900 font-bold text-xl">{selectedPost.title}</DialogTitle>
              </DialogHeader>
              
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold">
                    {selectedPost.author_name?.charAt(0) || 'A'}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">{selectedPost.author_name}</p>
                    <p className="text-sm text-gray-500">{formatTimeAgo(selectedPost.created_at)}</p>
                  </div>
                </div>
                
                <p className="text-gray-700 whitespace-pre-wrap">{selectedPost.content}</p>
                
                <div className="flex items-center gap-4 pt-4 border-t">
                  <button 
                    onClick={() => handleLikePost(selectedPost.id)}
                    className="flex items-center gap-1 text-gray-500 hover:text-red-500 transition-colors"
                  >
                    <Heart className="w-5 h-5" /> {selectedPost.likes}
                  </button>
                  <span className="flex items-center gap-1 text-gray-500">
                    <Eye className="w-5 h-5" /> {selectedPost.views}
                  </span>
                </div>

                {/* Replies */}
                <div className="pt-4 border-t">
                  <h4 className="font-bold text-gray-900 mb-4">
                    {selectedPost.replies?.length || 0} Replies
                  </h4>
                  
                  <div className="space-y-4">
                    {selectedPost.replies?.map((reply) => (
                      <div key={reply.id} className={`p-4 rounded-xl ${reply.is_solution ? 'bg-green-50 border-2 border-green-200' : 'bg-gray-50'}`}>
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-white text-sm font-bold">
                            {reply.author_name?.charAt(0) || 'A'}
                          </div>
                          <span className="font-semibold text-sm">{reply.author_name}</span>
                          <span className="text-xs text-gray-500">{formatTimeAgo(reply.created_at)}</span>
                          {reply.is_solution && (
                            <Badge className="bg-green-100 text-green-700 ml-auto">
                              <CheckCircle className="w-3 h-3 mr-1" /> Solution
                            </Badge>
                          )}
                        </div>
                        <p className="text-gray-700 text-sm">{reply.content}</p>
                      </div>
                    ))}
                  </div>

                  {/* Reply Form */}
                  <div className="flex gap-2 mt-4">
                    <Input
                      value={newReply}
                      onChange={(e) => setNewReply(e.target.value)}
                      placeholder="Write a reply..."
                      className="border-2 border-gray-200 rounded-xl"
                      onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleReply()}
                    />
                    <Button onClick={handleReply} className="bg-indigo-600 hover:bg-indigo-700 text-white">
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
