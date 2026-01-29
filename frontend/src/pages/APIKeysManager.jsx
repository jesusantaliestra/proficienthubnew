import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
  Key, Plus, Trash2, RefreshCw, Copy, Eye, EyeOff, 
  ArrowLeft, Shield, Activity, Clock, CheckCircle, XCircle
} from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function APIKeysManager() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newKey, setNewKey] = useState(null);
  const [showKeyId, setShowKeyId] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    scopes: ['read'],
    rate_limit: 1000,
    expires_in_days: 365
  });

  useEffect(() => {
    fetchApiKeys();
  }, []);

  const fetchApiKeys = async () => {
    try {
      const response = await fetch(`${API_URL}/api/api-keys`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setApiKeys(data || []);
    } catch (error) {
      console.error('Error fetching API keys:', error);
    } finally {
      setLoading(false);
    }
  };

  const createApiKey = async () => {
    try {
      const response = await fetch(`${API_URL}/api/api-keys`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        const data = await response.json();
        setNewKey(data);
        toast.success('API Key created successfully');
        fetchApiKeys();
        setFormData({ name: '', description: '', scopes: ['read'], rate_limit: 1000, expires_in_days: 365 });
      } else {
        toast.error('Failed to create API key');
      }
    } catch (error) {
      toast.error('Error creating API key');
    }
  };

  const revokeApiKey = async (keyId) => {
    if (!window.confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) return;
    
    try {
      const response = await fetch(`${API_URL}/api/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        toast.success('API Key revoked');
        fetchApiKeys();
      }
    } catch (error) {
      toast.error('Error revoking API key');
    }
  };

  const rotateApiKey = async (keyId) => {
    if (!window.confirm('Rotate this API key? The old key will stop working immediately.')) return;
    
    try {
      const response = await fetch(`${API_URL}/api/api-keys/${keyId}/rotate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setNewKey({ api_key: data.api_key, key_prefix: data.key_prefix, name: 'Rotated Key' });
        toast.success('API Key rotated successfully');
        fetchApiKeys();
      }
    } catch (error) {
      toast.error('Error rotating API key');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const toggleScope = (scope) => {
    setFormData(prev => ({
      ...prev,
      scopes: prev.scopes.includes(scope)
        ? prev.scopes.filter(s => s !== scope)
        : [...prev.scopes, scope]
    }));
  };

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => navigate(-1)} className="text-slate-400">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                <Key className="w-6 h-6 text-blue-400" />
                API Keys Management
              </h1>
              <p className="text-slate-400 text-sm mt-1">Manage API access for external integrations</p>
            </div>
          </div>
          <Button onClick={() => setShowCreate(true)} className="bg-blue-600 hover:bg-blue-700">
            <Plus className="w-4 h-4 mr-2" /> Create API Key
          </Button>
        </div>

        {/* New Key Alert */}
        {newKey && (
          <Card className="bg-green-900/30 border-green-500 mb-6">
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <CheckCircle className="w-6 h-6 text-green-400 mt-1" />
                <div className="flex-1">
                  <h3 className="text-green-400 font-semibold mb-2">API Key Created Successfully</h3>
                  <p className="text-slate-300 text-sm mb-3">
                    Copy this key now. You won't be able to see it again!
                  </p>
                  <div className="bg-slate-900 rounded-lg p-3 flex items-center justify-between">
                    <code className="text-green-400 font-mono text-sm break-all">{newKey.api_key}</code>
                    <Button 
                      size="sm" 
                      variant="ghost" 
                      onClick={() => copyToClipboard(newKey.api_key)}
                      className="text-green-400 ml-2"
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    onClick={() => setNewKey(null)}
                    className="text-slate-400 mt-3"
                  >
                    I've saved this key
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Create Form Modal */}
        {showCreate && (
          <Card className="bg-slate-900 border-slate-800 mb-6">
            <CardHeader>
              <CardTitle className="text-white">Create New API Key</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-slate-300 text-sm mb-1 block">Key Name *</label>
                <Input
                  placeholder="e.g., Production API, Staging Integration"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              
              <div>
                <label className="text-slate-300 text-sm mb-1 block">Description</label>
                <Input
                  placeholder="What will this key be used for?"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>

              <div>
                <label className="text-slate-300 text-sm mb-2 block">Permissions</label>
                <div className="flex gap-3">
                  {['read', 'write', 'admin'].map(scope => (
                    <button
                      key={scope}
                      onClick={() => toggleScope(scope)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        formData.scopes.includes(scope)
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                      }`}
                    >
                      {scope.charAt(0).toUpperCase() + scope.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-slate-300 text-sm mb-1 block">Rate Limit (req/hour)</label>
                  <Input
                    type="number"
                    value={formData.rate_limit}
                    onChange={(e) => setFormData({ ...formData, rate_limit: parseInt(e.target.value) })}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
                <div>
                  <label className="text-slate-300 text-sm mb-1 block">Expires In (days)</label>
                  <Input
                    type="number"
                    value={formData.expires_in_days}
                    onChange={(e) => setFormData({ ...formData, expires_in_days: parseInt(e.target.value) })}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <Button variant="ghost" onClick={() => setShowCreate(false)} className="text-slate-400">
                  Cancel
                </Button>
                <Button 
                  onClick={createApiKey} 
                  disabled={!formData.name}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Create Key
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* API Keys List */}
        <div className="space-y-4">
          {loading ? (
            <div className="text-center py-12">
              <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
            </div>
          ) : apiKeys.length === 0 ? (
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-12 text-center">
                <Key className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <h3 className="text-white text-lg mb-2">No API Keys Yet</h3>
                <p className="text-slate-400 mb-4">Create your first API key to start integrating</p>
                <Button onClick={() => setShowCreate(true)} className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="w-4 h-4 mr-2" /> Create API Key
                </Button>
              </CardContent>
            </Card>
          ) : (
            apiKeys.map(key => (
              <Card key={key.id} className="bg-slate-900 border-slate-800">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        key.is_active ? 'bg-green-500/20' : 'bg-red-500/20'
                      }`}>
                        {key.is_active ? (
                          <Shield className="w-5 h-5 text-green-400" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-400" />
                        )}
                      </div>
                      <div>
                        <h3 className="text-white font-medium">{key.name}</h3>
                        <div className="flex items-center gap-3 mt-1">
                          <code className="text-slate-400 text-sm font-mono">{key.key_prefix}...</code>
                          <span className="text-slate-500 text-xs">•</span>
                          <span className="text-slate-400 text-xs flex items-center gap-1">
                            <Activity className="w-3 h-3" /> {key.usage_count} requests
                          </span>
                          {key.last_used_at && (
                            <>
                              <span className="text-slate-500 text-xs">•</span>
                              <span className="text-slate-400 text-xs flex items-center gap-1">
                                <Clock className="w-3 h-3" /> Last used {new Date(key.last_used_at).toLocaleDateString()}
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1 mr-4">
                        {key.scopes.map(scope => (
                          <span 
                            key={scope}
                            className={`px-2 py-1 text-xs rounded ${
                              scope === 'admin' ? 'bg-purple-500/20 text-purple-400' :
                              scope === 'write' ? 'bg-orange-500/20 text-orange-400' :
                              'bg-blue-500/20 text-blue-400'
                            }`}
                          >
                            {scope}
                          </span>
                        ))}
                      </div>
                      
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => rotateApiKey(key.id)}
                        className="text-slate-400 hover:text-white"
                        title="Rotate Key"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </Button>
                      
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => revokeApiKey(key.id)}
                        className="text-red-400 hover:text-red-300"
                        title="Revoke Key"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Documentation Link */}
        <Card className="bg-slate-900/50 border-slate-800 mt-8">
          <CardContent className="p-6">
            <h3 className="text-white font-medium mb-2">API Documentation</h3>
            <p className="text-slate-400 text-sm mb-4">
              Use your API key in the <code className="bg-slate-800 px-2 py-1 rounded text-blue-400">X-API-Key</code> header
              to authenticate requests to the Public API v1.
            </p>
            <div className="bg-slate-800 rounded-lg p-4">
              <code className="text-green-400 text-sm">
                curl -X GET "{API_URL}/api/v1/students" \<br/>
                &nbsp;&nbsp;-H "X-API-Key: ph_live_your_api_key_here"
              </code>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
