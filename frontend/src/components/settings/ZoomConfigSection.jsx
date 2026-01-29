import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Badge } from '../ui/badge';
import { Video, CheckCircle, XCircle, Eye, EyeOff, TestTube, Save, AlertTriangle } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ZoomConfigSection = ({ config, onSave }) => {
  const [zoomConfig, setZoomConfig] = useState({
    zoom_account_id: config?.zoom_account_id || '',
    zoom_client_id: config?.zoom_client_id || '',
    zoom_client_secret: config?.zoom_client_secret || '',
    zoom_enabled: config?.zoom_enabled || false,
    auto_record: config?.auto_record || false,
    waiting_room: config?.waiting_room || true,
    max_participants: config?.max_participants || 100,
  });
  const [showSecrets, setShowSecrets] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const response = await axios.post(`${API_URL}/institution/settings/zoom/test`, {
        zoom_account_id: zoomConfig.zoom_account_id,
        zoom_client_id: zoomConfig.zoom_client_id,
        zoom_client_secret: zoomConfig.zoom_client_secret,
      });
      setTestResult({ success: true, message: response.data.message });
      toast.success('Zoom connection successful!');
    } catch (error) {
      setTestResult({ 
        success: false, 
        message: error.response?.data?.detail || 'Connection failed' 
      });
      toast.error('Zoom connection failed');
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    try {
      await onSave('zoom', zoomConfig);
      toast.success('Zoom settings saved!');
    } catch (error) {
      toast.error('Failed to save Zoom settings');
    }
  };

  return (
    <div className="space-y-6" data-testid="zoom-config-section">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-blue-500 flex items-center justify-center">
            <Video className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900">Zoom Integration</h3>
            <p className="text-sm text-gray-500">Connect Zoom for live classes</p>
          </div>
        </div>
        <Switch
          checked={zoomConfig.zoom_enabled}
          onCheckedChange={(checked) => setZoomConfig({...zoomConfig, zoom_enabled: checked})}
        />
      </div>

      {zoomConfig.zoom_enabled && (
        <>
          <div className="bg-blue-50 rounded-xl p-4">
            <h4 className="font-semibold text-blue-900 mb-2">Setup Instructions</h4>
            <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
              <li>Go to <a href="https://marketplace.zoom.us" target="_blank" rel="noopener noreferrer" className="underline">Zoom Marketplace</a></li>
              <li>Create a Server-to-Server OAuth app</li>
              <li>Copy the Account ID, Client ID, and Client Secret</li>
            </ol>
          </div>

          <div className="space-y-4">
            <div>
              <Label>Account ID</Label>
              <Input
                type="text"
                value={zoomConfig.zoom_account_id}
                onChange={(e) => setZoomConfig({...zoomConfig, zoom_account_id: e.target.value})}
                placeholder="Your Zoom Account ID"
                className="input-duo"
              />
            </div>
            <div>
              <Label>Client ID</Label>
              <Input
                type="text"
                value={zoomConfig.zoom_client_id}
                onChange={(e) => setZoomConfig({...zoomConfig, zoom_client_id: e.target.value})}
                placeholder="Your Zoom Client ID"
                className="input-duo"
              />
            </div>
            <div>
              <Label>Client Secret</Label>
              <div className="relative">
                <Input
                  type={showSecrets ? 'text' : 'password'}
                  value={zoomConfig.zoom_client_secret}
                  onChange={(e) => setZoomConfig({...zoomConfig, zoom_client_secret: e.target.value})}
                  placeholder="Your Zoom Client Secret"
                  className="input-duo pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowSecrets(!showSecrets)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showSecrets ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          </div>

          {/* Additional Settings */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <Label>Auto-record meetings</Label>
              <Switch
                checked={zoomConfig.auto_record}
                onCheckedChange={(checked) => setZoomConfig({...zoomConfig, auto_record: checked})}
              />
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <Label>Enable waiting room</Label>
              <Switch
                checked={zoomConfig.waiting_room}
                onCheckedChange={(checked) => setZoomConfig({...zoomConfig, waiting_room: checked})}
              />
            </div>
          </div>

          {/* Test Result */}
          {testResult && (
            <div className={`p-4 rounded-xl ${testResult.success ? 'bg-green-50' : 'bg-red-50'}`}>
              <div className="flex items-center gap-2">
                {testResult.success ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-600" />
                )}
                <span className={testResult.success ? 'text-green-700' : 'text-red-700'}>
                  {testResult.message}
                </span>
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={handleTest}
              disabled={testing || !zoomConfig.zoom_client_id}
              data-testid="test-zoom"
            >
              <TestTube className="w-4 h-4 mr-2" />
              {testing ? 'Testing...' : 'Test Connection'}
            </Button>
            <Button onClick={handleSave} className="btn-duo" data-testid="save-zoom">
              <Save className="w-4 h-4 mr-2" />
              Save Zoom Settings
            </Button>
          </div>
        </>
      )}
    </div>
  );
};
