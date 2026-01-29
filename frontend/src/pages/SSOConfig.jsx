import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Switch } from '../components/ui/switch';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import {
  ArrowLeft, Shield, Key, Plus, Settings, Trash2, Copy, ExternalLink,
  CheckCircle, XCircle, AlertCircle, Building2, Users, Activity,
  Globe, Lock, RefreshCw, Download, Upload, Eye, EyeOff, GraduationCap
} from 'lucide-react';
import axios from 'axios';
import { toast, Toaster } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function SSOConfig() {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [configs, setConfigs] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [addConfigOpen, setAddConfigOpen] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState(null);
  const [showCertificate, setShowCertificate] = useState(false);
  
  const [newConfig, setNewConfig] = useState({
    name: '',
    idp_entity_id: '',
    idp_sso_url: '',
    idp_slo_url: '',
    idp_certificate: '',
    auto_create_users: true,
    default_role: 'student',
    allowed_domains: '',
    is_active: true
  });

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  };

  useEffect(() => {
    fetchConfigs();
    fetchAnalytics();
  }, []);

  const fetchConfigs = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/sso/saml/configs`, axiosConfig);
      setConfigs(response.data.configs || []);
    } catch (error) {
      console.error('Failed to fetch SSO configs:', error);
      toast.error('Failed to load SSO configurations');
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API_URL}/sso/analytics?days=30`, axiosConfig);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch SSO analytics:', error);
    }
  };

  const handleCreateConfig = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...newConfig,
        allowed_domains: newConfig.allowed_domains 
          ? newConfig.allowed_domains.split(',').map(d => d.trim()).filter(Boolean)
          : []
      };
      
      const response = await axios.post(`${API_URL}/sso/saml/config`, payload, axiosConfig);
      toast.success('SSO configuration created successfully!');
      setAddConfigOpen(false);
      setNewConfig({
        name: '',
        idp_entity_id: '',
        idp_sso_url: '',
        idp_slo_url: '',
        idp_certificate: '',
        auto_create_users: true,
        default_role: 'student',
        allowed_domains: '',
        is_active: true
      });
      fetchConfigs();
      
      // Show SP metadata info
      setSelectedConfig({
        ...response.data,
        showMetadataInfo: true
      });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create SSO configuration');
    }
  };

  const handleDeleteConfig = async (configId) => {
    if (!window.confirm('Are you sure you want to delete this SSO configuration? Users will no longer be able to login via this SSO.')) {
      return;
    }
    
    try {
      await axios.delete(`${API_URL}/sso/saml/config/${configId}`, axiosConfig);
      toast.success('SSO configuration deleted');
      fetchConfigs();
      if (selectedConfig?.id === configId) {
        setSelectedConfig(null);
      }
    } catch (error) {
      toast.error('Failed to delete SSO configuration');
    }
  };

  const handleToggleActive = async (configId, currentStatus) => {
    try {
      await axios.patch(`${API_URL}/sso/saml/config/${configId}`, 
        { is_active: !currentStatus }, 
        axiosConfig
      );
      toast.success(`SSO ${!currentStatus ? 'enabled' : 'disabled'}`);
      fetchConfigs();
    } catch (error) {
      toast.error('Failed to update SSO status');
    }
  };

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied to clipboard`);
  };

  const downloadMetadata = async (configId) => {
    try {
      const response = await axios.get(`${API_URL}/sso/metadata/${configId}`);
      const blob = new Blob([response.data], { type: 'application/xml' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sp-metadata-${configId}.xml`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success('Metadata downloaded');
    } catch (error) {
      toast.error('Failed to download metadata');
    }
  };

  const idpPresets = [
    { name: 'Azure AD', icon: '🔷', entityIdHint: 'https://sts.windows.net/{tenant-id}/', ssoUrlHint: 'https://login.microsoftonline.com/{tenant-id}/saml2' },
    { name: 'Okta', icon: '🟢', entityIdHint: 'http://www.okta.com/{app-id}', ssoUrlHint: 'https://{your-domain}.okta.com/app/{app-id}/sso/saml' },
    { name: 'Google Workspace', icon: '🔴', entityIdHint: 'https://accounts.google.com/o/saml2?idpid={idp-id}', ssoUrlHint: 'https://accounts.google.com/o/saml2/idp?idpid={idp-id}' },
    { name: 'OneLogin', icon: '🟣', entityIdHint: 'https://app.onelogin.com/saml/metadata/{app-id}', ssoUrlHint: 'https://{subdomain}.onelogin.com/trust/saml2/http-post/sso/{app-id}' },
    { name: 'Other SAML 2.0', icon: '🔐', entityIdHint: '', ssoUrlHint: '' }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-gray-500 font-semibold">Loading SSO configurations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="sso-config-page">
      <Toaster position="top-right" richColors />
      
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/institution/dashboard')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                data-testid="back-to-dashboard"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center">
                  <Shield className="w-5 h-5 text-indigo-600" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">Single Sign-On (SSO)</h1>
                  <p className="text-sm text-gray-500">SAML 2.0 Configuration</p>
                </div>
              </div>
            </div>
            
            <Dialog open={addConfigOpen} onOpenChange={setAddConfigOpen}>
              <DialogTrigger asChild>
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white" data-testid="add-sso-config-btn">
                  <Plus className="w-4 h-4 mr-2" />
                  Add SSO Provider
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-white border-2 border-gray-200 rounded-2xl max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle className="text-gray-900 font-bold text-xl">Configure SAML SSO</DialogTitle>
                </DialogHeader>
                
                <form onSubmit={handleCreateConfig} className="space-y-6">
                  {/* IdP Presets */}
                  <div>
                    <Label className="text-gray-700 font-semibold mb-3 block">Identity Provider</Label>
                    <div className="grid grid-cols-5 gap-2">
                      {idpPresets.map((preset) => (
                        <button
                          key={preset.name}
                          type="button"
                          onClick={() => setNewConfig(prev => ({
                            ...prev,
                            name: preset.name !== 'Other SAML 2.0' ? `${preset.name} SSO` : prev.name,
                            idp_entity_id: preset.entityIdHint,
                            idp_sso_url: preset.ssoUrlHint
                          }))}
                          className="p-3 rounded-xl border-2 border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-all text-center"
                        >
                          <span className="text-2xl block mb-1">{preset.icon}</span>
                          <span className="text-xs text-gray-600 font-medium">{preset.name}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label className="text-gray-700 font-semibold">Display Name *</Label>
                      <Input
                        value={newConfig.name}
                        onChange={(e) => setNewConfig(prev => ({ ...prev, name: e.target.value }))}
                        className="border-2 border-gray-200 rounded-xl"
                        placeholder="e.g., Company SSO, University Login"
                        required
                        data-testid="sso-name-input"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label className="text-gray-700 font-semibold">Default Role</Label>
                      <Select
                        value={newConfig.default_role}
                        onValueChange={(v) => setNewConfig(prev => ({ ...prev, default_role: v }))}
                      >
                        <SelectTrigger className="border-2 border-gray-200 rounded-xl" data-testid="sso-role-select">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="student">Student</SelectItem>
                          <SelectItem value="teacher">Teacher</SelectItem>
                          <SelectItem value="admin">Admin</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label className="text-gray-700 font-semibold">IdP Entity ID (Issuer) *</Label>
                    <Input
                      value={newConfig.idp_entity_id}
                      onChange={(e) => setNewConfig(prev => ({ ...prev, idp_entity_id: e.target.value }))}
                      className="border-2 border-gray-200 rounded-xl font-mono text-sm"
                      placeholder="https://idp.example.com/entity-id"
                      required
                      data-testid="sso-entity-id-input"
                    />
                    <p className="text-xs text-gray-500">The unique identifier of your Identity Provider</p>
                  </div>
                  
                  <div className="space-y-2">
                    <Label className="text-gray-700 font-semibold">IdP SSO URL *</Label>
                    <Input
                      value={newConfig.idp_sso_url}
                      onChange={(e) => setNewConfig(prev => ({ ...prev, idp_sso_url: e.target.value }))}
                      className="border-2 border-gray-200 rounded-xl font-mono text-sm"
                      placeholder="https://idp.example.com/sso/saml"
                      required
                      data-testid="sso-sso-url-input"
                    />
                    <p className="text-xs text-gray-500">The URL where SAML authentication requests are sent</p>
                  </div>
                  
                  <div className="space-y-2">
                    <Label className="text-gray-700 font-semibold">IdP Single Logout URL (Optional)</Label>
                    <Input
                      value={newConfig.idp_slo_url}
                      onChange={(e) => setNewConfig(prev => ({ ...prev, idp_slo_url: e.target.value }))}
                      className="border-2 border-gray-200 rounded-xl font-mono text-sm"
                      placeholder="https://idp.example.com/slo/saml"
                      data-testid="sso-slo-url-input"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label className="text-gray-700 font-semibold">IdP X.509 Certificate (PEM) *</Label>
                    <Textarea
                      value={newConfig.idp_certificate}
                      onChange={(e) => setNewConfig(prev => ({ ...prev, idp_certificate: e.target.value }))}
                      className="border-2 border-gray-200 rounded-xl font-mono text-xs"
                      rows={6}
                      placeholder="-----BEGIN CERTIFICATE-----&#10;MIIDpDCCAoygAwIBAgIGAX...&#10;-----END CERTIFICATE-----"
                      required
                      data-testid="sso-certificate-input"
                    />
                    <p className="text-xs text-gray-500">The public certificate used to verify SAML responses from your IdP</p>
                  </div>
                  
                  <div className="space-y-2">
                    <Label className="text-gray-700 font-semibold">Allowed Email Domains (Optional)</Label>
                    <Input
                      value={newConfig.allowed_domains}
                      onChange={(e) => setNewConfig(prev => ({ ...prev, allowed_domains: e.target.value }))}
                      className="border-2 border-gray-200 rounded-xl"
                      placeholder="company.com, university.edu (comma-separated)"
                      data-testid="sso-domains-input"
                    />
                    <p className="text-xs text-gray-500">Leave empty to allow all domains</p>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                    <div>
                      <Label className="text-gray-700 font-semibold">Auto-create Users</Label>
                      <p className="text-xs text-gray-500">Automatically create accounts for new SSO users</p>
                    </div>
                    <Switch
                      checked={newConfig.auto_create_users}
                      onCheckedChange={(checked) => setNewConfig(prev => ({ ...prev, auto_create_users: checked }))}
                      data-testid="sso-auto-create-toggle"
                    />
                  </div>
                  
                  <div className="flex gap-3 pt-4">
                    <Button
                      type="button"
                      variant="outline"
                      className="flex-1"
                      onClick={() => setAddConfigOpen(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white"
                      data-testid="sso-submit-btn"
                    >
                      Create SSO Configuration
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Analytics Overview */}
        {analytics && (
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <Card className="bg-white border-2 border-gray-100 rounded-2xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-500 text-sm font-medium">SSO Logins (30 days)</p>
                    <p className="text-3xl font-bold text-gray-900 mt-1">
                      {analytics.by_provider?.reduce((acc, p) => acc + p.login_count, 0) || 0}
                    </p>
                  </div>
                  <div className="w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center">
                    <Activity className="w-6 h-6 text-indigo-600" />
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white border-2 border-gray-100 rounded-2xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-500 text-sm font-medium">Unique SSO Users</p>
                    <p className="text-3xl font-bold text-gray-900 mt-1">
                      {analytics.by_provider?.reduce((acc, p) => acc + p.unique_users, 0) || 0}
                    </p>
                  </div>
                  <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
                    <Users className="w-6 h-6 text-green-600" />
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white border-2 border-gray-100 rounded-2xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-500 text-sm font-medium">Total SSO Users</p>
                    <p className="text-3xl font-bold text-gray-900 mt-1">{analytics.total_sso_users || 0}</p>
                  </div>
                  <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center">
                    <Shield className="w-6 h-6 text-purple-600" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
        
        <div className="grid lg:grid-cols-3 gap-8">
          {/* SSO Configurations List */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-lg font-bold text-gray-900">SSO Configurations</h2>
            
            {configs.length === 0 ? (
              <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                <CardContent className="p-12 text-center">
                  <Shield className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-bold text-gray-700 mb-2">No SSO Configured</h3>
                  <p className="text-gray-500 mb-6">
                    Set up Single Sign-On to allow your users to login with their existing corporate credentials.
                  </p>
                  <Button
                    onClick={() => setAddConfigOpen(true)}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Configure SSO
                  </Button>
                </CardContent>
              </Card>
            ) : (
              configs.map((config) => (
                <Card 
                  key={config.id} 
                  className={`bg-white border-2 rounded-2xl cursor-pointer transition-all ${
                    selectedConfig?.id === config.id 
                      ? 'border-indigo-300 ring-2 ring-indigo-100' 
                      : 'border-gray-100 hover:border-gray-200'
                  }`}
                  onClick={() => setSelectedConfig(config)}
                  data-testid={`sso-config-${config.id}`}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                          config.is_active ? 'bg-green-100' : 'bg-gray-100'
                        }`}>
                          <Shield className={`w-6 h-6 ${config.is_active ? 'text-green-600' : 'text-gray-400'}`} />
                        </div>
                        <div>
                          <h3 className="font-bold text-gray-900">{config.name}</h3>
                          <p className="text-sm text-gray-500 font-mono truncate max-w-md">
                            {config.idp_entity_id}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Badge className={config.is_active 
                          ? 'bg-green-100 text-green-700 border-green-200' 
                          : 'bg-gray-100 text-gray-600 border-gray-200'
                        }>
                          {config.is_active ? 'Active' : 'Disabled'}
                        </Badge>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleToggleActive(config.id, config.is_active);
                          }}
                          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                          title={config.is_active ? 'Disable SSO' : 'Enable SSO'}
                        >
                          {config.is_active ? (
                            <CheckCircle className="w-5 h-5 text-green-500" />
                          ) : (
                            <XCircle className="w-5 h-5 text-gray-400" />
                          )}
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteConfig(config.id);
                          }}
                          className="p-2 hover:bg-red-50 rounded-lg transition-colors text-red-500"
                          title="Delete SSO Configuration"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                    
                    <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Users className="w-4 h-4" />
                        {config.default_role}
                      </span>
                      <span className="flex items-center gap-1">
                        <Globe className="w-4 h-4" />
                        {config.allowed_domains?.length > 0 
                          ? config.allowed_domains.join(', ')
                          : 'All domains'
                        }
                      </span>
                      {config.auto_create_users && (
                        <span className="flex items-center gap-1 text-green-600">
                          <CheckCircle className="w-4 h-4" />
                          Auto-create
                        </span>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
          
          {/* Configuration Details / Setup Guide */}
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-gray-900">
              {selectedConfig ? 'Configuration Details' : 'Setup Guide'}
            </h2>
            
            {selectedConfig ? (
              <Card className="bg-white border-2 border-gray-100 rounded-2xl">
                <CardHeader className="pb-2">
                  <CardTitle className="text-gray-900 font-bold">{selectedConfig.name}</CardTitle>
                  <CardDescription>Service Provider (SP) Details</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* SP Entity ID */}
                  <div>
                    <Label className="text-xs text-gray-500 uppercase font-bold">SP Entity ID</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <code className="flex-1 text-xs bg-gray-100 p-2 rounded-lg truncate">
                        {selectedConfig.sp_entity_id}
                      </code>
                      <button
                        onClick={() => copyToClipboard(selectedConfig.sp_entity_id, 'SP Entity ID')}
                        className="p-2 hover:bg-gray-100 rounded-lg"
                      >
                        <Copy className="w-4 h-4 text-gray-500" />
                      </button>
                    </div>
                  </div>
                  
                  {/* ACS URL */}
                  <div>
                    <Label className="text-xs text-gray-500 uppercase font-bold">ACS URL (Reply URL)</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <code className="flex-1 text-xs bg-gray-100 p-2 rounded-lg truncate">
                        {selectedConfig.sp_acs_url}
                      </code>
                      <button
                        onClick={() => copyToClipboard(selectedConfig.sp_acs_url, 'ACS URL')}
                        className="p-2 hover:bg-gray-100 rounded-lg"
                      >
                        <Copy className="w-4 h-4 text-gray-500" />
                      </button>
                    </div>
                  </div>
                  
                  {/* SLO URL */}
                  <div>
                    <Label className="text-xs text-gray-500 uppercase font-bold">Single Logout URL</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <code className="flex-1 text-xs bg-gray-100 p-2 rounded-lg truncate">
                        {selectedConfig.sp_slo_url}
                      </code>
                      <button
                        onClick={() => copyToClipboard(selectedConfig.sp_slo_url, 'SLO URL')}
                        className="p-2 hover:bg-gray-100 rounded-lg"
                      >
                        <Copy className="w-4 h-4 text-gray-500" />
                      </button>
                    </div>
                  </div>
                  
                  {/* Metadata Download */}
                  <div className="pt-4 border-t border-gray-100">
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => downloadMetadata(selectedConfig.id)}
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Download SP Metadata XML
                    </Button>
                  </div>
                  
                  {/* Login URL */}
                  <div className="pt-4 border-t border-gray-100">
                    <Label className="text-xs text-gray-500 uppercase font-bold">SSO Login URL</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <code className="flex-1 text-xs bg-indigo-50 text-indigo-700 p-2 rounded-lg truncate">
                        {`${process.env.REACT_APP_BACKEND_URL}/api/sso/saml/login/${selectedConfig.id}`}
                      </code>
                      <button
                        onClick={() => copyToClipboard(
                          `${process.env.REACT_APP_BACKEND_URL}/api/sso/saml/login/${selectedConfig.id}`,
                          'SSO Login URL'
                        )}
                        className="p-2 hover:bg-gray-100 rounded-lg"
                      >
                        <Copy className="w-4 h-4 text-gray-500" />
                      </button>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      Users can bookmark this URL or use it to initiate SSO login directly.
                    </p>
                  </div>
                  
                  {/* Test Login */}
                  <div className="pt-4">
                    <a
                      href={`${process.env.REACT_APP_BACKEND_URL}/api/sso/saml/login/${selectedConfig.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full inline-flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl font-medium transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                      Test SSO Login
                    </a>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="bg-gradient-to-br from-indigo-50 to-purple-50 border-2 border-indigo-100 rounded-2xl">
                <CardHeader>
                  <CardTitle className="text-gray-900 font-bold flex items-center gap-2">
                    <Key className="w-5 h-5 text-indigo-600" />
                    SAML 2.0 Setup Guide
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0">1</div>
                      <div>
                        <p className="font-semibold text-gray-900">Create SAML App in your IdP</p>
                        <p className="text-sm text-gray-600">Azure AD, Okta, Google Workspace, etc.</p>
                      </div>
                    </div>
                    
                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0">2</div>
                      <div>
                        <p className="font-semibold text-gray-900">Get IdP Metadata</p>
                        <p className="text-sm text-gray-600">Entity ID, SSO URL, and X.509 Certificate</p>
                      </div>
                    </div>
                    
                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0">3</div>
                      <div>
                        <p className="font-semibold text-gray-900">Add SSO Provider Here</p>
                        <p className="text-sm text-gray-600">Click "Add SSO Provider" to configure</p>
                      </div>
                    </div>
                    
                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0">4</div>
                      <div>
                        <p className="font-semibold text-gray-900">Configure IdP with SP Details</p>
                        <p className="text-sm text-gray-600">Add our ACS URL and Entity ID to your IdP</p>
                      </div>
                    </div>
                    
                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 rounded-full bg-green-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0">5</div>
                      <div>
                        <p className="font-semibold text-gray-900">Test & Go Live</p>
                        <p className="text-sm text-gray-600">Use the test login button to verify</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t border-indigo-100">
                    <h4 className="font-semibold text-gray-900 mb-2">Supported Identity Providers</h4>
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="outline" className="bg-white">🔷 Azure AD</Badge>
                      <Badge variant="outline" className="bg-white">🟢 Okta</Badge>
                      <Badge variant="outline" className="bg-white">🔴 Google</Badge>
                      <Badge variant="outline" className="bg-white">🟣 OneLogin</Badge>
                      <Badge variant="outline" className="bg-white">🔐 Any SAML 2.0</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
