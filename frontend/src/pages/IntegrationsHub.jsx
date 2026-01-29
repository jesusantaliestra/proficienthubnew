import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
  ArrowLeft, Link2, Unlink, CheckCircle, XCircle, RefreshCw,
  Settings, Database, Users, FileText, Zap, Globe, 
  Building2, ShoppingCart, Calculator, Briefcase
} from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Integration icons mapping
const integrationIcons = {
  salesforce: '🔵',
  hubspot: '🟠',
  zoho_crm: '🔴',
  pipedrive: '🟢',
  freshsales: '🟣',
  monday: '🟡',
  sap_business_one: '💙',
  dynamics_365: '🔷',
  netsuite: '🔶',
  odoo: '💜',
  quickbooks: '💚',
  xero: '💎',
  sage: '🌿'
};

export default function IntegrationsHub() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [availableIntegrations, setAvailableIntegrations] = useState({});
  const [connectedIntegrations, setConnectedIntegrations] = useState([]);
  const [categories, setCategories] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedIntegration, setSelectedIntegration] = useState(null);
  const [connectForm, setConnectForm] = useState({});
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Fetch available integrations
      const availableRes = await fetch(`${API_URL}/api/integrations/available`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const availableData = await availableRes.json();
      setAvailableIntegrations(availableData.integrations || {});
      setCategories(availableData.categories || {});

      // Fetch connected integrations
      const connectedRes = await fetch(`${API_URL}/api/integrations`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const connectedData = await connectedRes.json();
      setConnectedIntegrations(connectedData.integrations || []);
    } catch (error) {
      console.error('Error fetching integrations:', error);
    } finally {
      setLoading(false);
    }
  };

  const connectIntegration = async () => {
    if (!selectedIntegration) return;

    try {
      const response = await fetch(`${API_URL}/api/integrations/connect`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          integration_type: selectedIntegration,
          credentials: connectForm,
          settings: {}
        })
      });

      if (response.ok) {
        const data = await response.json();
        toast.success(`Connected to ${availableIntegrations[selectedIntegration]?.name}`);
        setSelectedIntegration(null);
        setConnectForm({});
        fetchData();
        
        // Auto-verify
        await fetch(`${API_URL}/api/integrations/${data.id}/verify`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        fetchData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to connect');
      }
    } catch (error) {
      toast.error('Error connecting integration');
    }
  };

  const disconnectIntegration = async (integrationId) => {
    if (!window.confirm('Disconnect this integration? Data sync will stop.')) return;

    try {
      const response = await fetch(`${API_URL}/api/integrations/${integrationId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        toast.success('Integration disconnected');
        fetchData();
      }
    } catch (error) {
      toast.error('Error disconnecting');
    }
  };

  const syncIntegration = async (integrationId) => {
    try {
      const response = await fetch(`${API_URL}/api/integrations/${integrationId}/sync`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        toast.success('Sync started');
      }
    } catch (error) {
      toast.error('Error starting sync');
    }
  };

  const getAuthFields = (integrationType) => {
    const integration = availableIntegrations[integrationType];
    if (!integration) return [];

    switch (integration.auth_type) {
      case 'oauth2':
        return [
          { key: 'client_id', label: 'Client ID', type: 'text' },
          { key: 'client_secret', label: 'Client Secret', type: 'password' },
          { key: 'access_token', label: 'Access Token (if available)', type: 'password', optional: true }
        ];
      case 'api_key':
        return [
          { key: 'api_key', label: 'API Key', type: 'password' }
        ];
      case 'basic':
        return [
          { key: 'username', label: 'Username', type: 'text' },
          { key: 'password', label: 'Password', type: 'password' }
        ];
      default:
        return [
          { key: 'api_key', label: 'API Key / Token', type: 'password' }
        ];
    }
  };

  const isConnected = (integrationType) => {
    return connectedIntegrations.some(i => i.integration_type === integrationType);
  };

  const getConnectedIntegration = (integrationType) => {
    return connectedIntegrations.find(i => i.integration_type === integrationType);
  };

  const filteredIntegrations = Object.entries(availableIntegrations).filter(([key, value]) => {
    if (activeTab === 'all') return true;
    return value.type === activeTab;
  });

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => navigate(-1)} className="text-slate-400">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                <Link2 className="w-6 h-6 text-purple-400" />
                External Integrations
              </h1>
              <p className="text-slate-400 text-sm mt-1">
                Connect with CRM and ERP systems • {connectedIntegrations.length} active connections
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {[
            { id: 'all', label: 'All', icon: Globe },
            { id: 'crm', label: 'CRM', icon: Users },
            { id: 'erp', label: 'ERP', icon: Calculator }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
              {tab.id !== 'all' && (
                <span className="ml-1 bg-slate-700 px-1.5 py-0.5 rounded text-xs">
                  {categories[tab.id]?.length || 0}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Connected Integrations Banner */}
        {connectedIntegrations.length > 0 && (
          <Card className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 border-purple-500/30 mb-6">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                  <div>
                    <h3 className="text-white font-medium">Active Integrations</h3>
                    <p className="text-slate-300 text-sm">
                      {connectedIntegrations.map(i => i.integration_name).join(', ')}
                    </p>
                  </div>
                </div>
                <Button 
                  size="sm" 
                  variant="ghost" 
                  onClick={() => connectedIntegrations.forEach(i => syncIntegration(i.id))}
                  className="text-purple-400"
                >
                  <RefreshCw className="w-4 h-4 mr-2" /> Sync All
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Integration Connect Modal */}
        {selectedIntegration && (
          <Card className="bg-slate-900 border-slate-700 mb-6">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-3">
                <span className="text-2xl">{integrationIcons[selectedIntegration]}</span>
                Connect {availableIntegrations[selectedIntegration]?.name}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-slate-400 text-sm">
                Enter your credentials to connect. We'll verify the connection automatically.
              </p>
              
              {getAuthFields(selectedIntegration).map(field => (
                <div key={field.key}>
                  <label className="text-slate-300 text-sm mb-1 block">
                    {field.label} {!field.optional && '*'}
                  </label>
                  <Input
                    type={field.type}
                    placeholder={field.label}
                    value={connectForm[field.key] || ''}
                    onChange={(e) => setConnectForm({ ...connectForm, [field.key]: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
              ))}

              <div className="flex justify-end gap-3 pt-4">
                <Button 
                  variant="ghost" 
                  onClick={() => { setSelectedIntegration(null); setConnectForm({}); }}
                  className="text-slate-400"
                >
                  Cancel
                </Button>
                <Button onClick={connectIntegration} className="bg-purple-600 hover:bg-purple-700">
                  <Link2 className="w-4 h-4 mr-2" /> Connect
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Integrations Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {loading ? (
            <div className="col-span-full text-center py-12">
              <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
            </div>
          ) : (
            filteredIntegrations.map(([key, integration]) => {
              const connected = isConnected(key);
              const connectedData = getConnectedIntegration(key);
              
              return (
                <Card 
                  key={key} 
                  className={`bg-slate-900 border-slate-800 hover:border-slate-700 transition-colors ${
                    connected ? 'ring-1 ring-green-500/30' : ''
                  }`}
                >
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <span className="text-3xl">{integrationIcons[key]}</span>
                        <div>
                          <h3 className="text-white font-medium">{integration.name}</h3>
                          <span className={`text-xs px-2 py-0.5 rounded ${
                            integration.type === 'crm' 
                              ? 'bg-blue-500/20 text-blue-400' 
                              : 'bg-orange-500/20 text-orange-400'
                          }`}>
                            {integration.type.toUpperCase()}
                          </span>
                        </div>
                      </div>
                      {connected && (
                        <div className="flex items-center gap-1 text-green-400 text-xs">
                          <CheckCircle className="w-3 h-3" /> Connected
                        </div>
                      )}
                    </div>

                    <div className="flex flex-wrap gap-1 mb-4">
                      {integration.features?.slice(0, 4).map(feature => (
                        <span 
                          key={feature}
                          className="text-xs bg-slate-800 text-slate-400 px-2 py-1 rounded"
                        >
                          {feature}
                        </span>
                      ))}
                    </div>

                    <div className="flex items-center gap-2">
                      {connected ? (
                        <>
                          <Button
                            size="sm"
                            onClick={() => syncIntegration(connectedData.id)}
                            className="flex-1 bg-slate-800 hover:bg-slate-700 text-white"
                          >
                            <RefreshCw className="w-4 h-4 mr-2" /> Sync
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => disconnectIntegration(connectedData.id)}
                            className="text-red-400 hover:text-red-300"
                          >
                            <Unlink className="w-4 h-4" />
                          </Button>
                        </>
                      ) : (
                        <Button
                          size="sm"
                          onClick={() => setSelectedIntegration(key)}
                          className="w-full bg-purple-600 hover:bg-purple-700"
                        >
                          <Link2 className="w-4 h-4 mr-2" /> Connect
                        </Button>
                      )}
                    </div>

                    {connected && connectedData?.last_sync && (
                      <p className="text-slate-500 text-xs mt-3">
                        Last sync: {new Date(connectedData.last_sync).toLocaleString()}
                      </p>
                    )}
                  </CardContent>
                </Card>
              );
            })
          )}
        </div>

        {/* Info Section */}
        <Card className="bg-slate-900/50 border-slate-800 mt-8">
          <CardContent className="p-6">
            <h3 className="text-white font-medium mb-3 flex items-center gap-2">
              <Settings className="w-5 h-5 text-slate-400" />
              Integration Features
            </h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
                  <Users className="w-4 h-4 text-blue-400" />
                </div>
                <div>
                  <h4 className="text-white text-sm font-medium">Contact Sync</h4>
                  <p className="text-slate-400 text-xs">Sync students and leads bidirectionally</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center">
                  <FileText className="w-4 h-4 text-green-400" />
                </div>
                <div>
                  <h4 className="text-white text-sm font-medium">Invoice Integration</h4>
                  <p className="text-slate-400 text-xs">Push invoices to your accounting system</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center">
                  <Zap className="w-4 h-4 text-purple-400" />
                </div>
                <div>
                  <h4 className="text-white text-sm font-medium">Real-time Webhooks</h4>
                  <p className="text-slate-400 text-xs">Instant updates via webhook events</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
