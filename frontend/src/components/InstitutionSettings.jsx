import React, { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import {
  Video, Mail, Trophy, Settings, Save, TestTube, CheckCircle, XCircle,
  Eye, EyeOff, AlertTriangle, Zap, Users, Gift, Flame, Bot, Sparkles,
  GraduationCap, Calendar, Coins, ShoppingCart
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Avatar/HeyGen Configuration Section
const AvatarConfigSection = ({ config, onSave }) => {
  const [avatarConfig, setAvatarConfig] = useState({
    avatar_mode: config?.avatar_mode || 'simple',
    default_avatar_style: config?.default_avatar_style || 'teacher',
    heygen_enabled: config?.heygen_enabled || false,
    heygen_api_key: config?.heygen_api_key || '',
    heygen_avatar_id: config?.heygen_avatar_id || 'sarah',
    heygen_voice_id: config?.heygen_voice_id || 'en-US-1',
    heygen_monthly_limit: config?.heygen_monthly_limit || 100,
    free_minutes_per_student: config?.free_minutes_per_student || 5,
    free_minutes_enabled: config?.free_minutes_enabled || false,
  });
  const [usage, setUsage] = useState({ credits_used: 0, credits_limit: 100 });

  useEffect(() => {
    fetchUsage();
  }, []);

  const fetchUsage = async () => {
    try {
      const response = await axios.get(`${API_URL}/avatar/heygen/usage`);
      setUsage(response.data);
    } catch (error) {
      console.error('Failed to fetch HeyGen usage:', error);
    }
  };

  const handleSave = async () => {
    try {
      await onSave('avatar', avatarConfig);
      toast.success('Avatar settings saved!');
    } catch (error) {
      toast.error('Failed to save avatar settings');
    }
  };

  const avatarStyles = [
    { id: 'teacher', name: 'Prof. Smith', icon: '👨‍🏫' },
    { id: 'female_teacher', name: 'Ms. Johnson', icon: '👩‍🏫' },
    { id: 'friendly', name: 'Alex', icon: '🧑‍💼' },
  ];

  const heygenAvatars = [
    { id: 'sarah', name: 'Sarah (Professional)' },
    { id: 'james', name: 'James (Casual)' },
    { id: 'maya', name: 'Maya (Friendly)' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900">AI Avatar for Speaking Practice</h3>
            <p className="text-sm text-gray-500">Configure the AI tutor avatar for your students</p>
          </div>
        </div>
      </div>

      {/* Avatar Mode Selection */}
      <div className="bg-gray-50 rounded-xl p-4">
        <Label className="font-semibold mb-3 block">Avatar Type</Label>
        <div className="grid grid-cols-2 gap-4">
          <div 
            onClick={() => setAvatarConfig({...avatarConfig, avatar_mode: 'simple', heygen_enabled: false})}
            className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
              avatarConfig.avatar_mode === 'simple' 
                ? 'border-[#58CC02] bg-green-50' 
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="text-center">
              <span className="text-4xl block mb-2">🎭</span>
              <h4 className="font-bold text-gray-900">Animated Avatar</h4>
              <p className="text-xs text-gray-500 mt-1">Free - Simple animated characters</p>
              <Badge className="mt-2 bg-green-100 text-green-700">Recommended</Badge>
            </div>
          </div>
          
          <div 
            onClick={() => setAvatarConfig({...avatarConfig, avatar_mode: 'heygen', heygen_enabled: true})}
            className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
              avatarConfig.avatar_mode === 'heygen' 
                ? 'border-purple-500 bg-purple-50' 
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="text-center">
              <span className="text-4xl block mb-2">🎬</span>
              <h4 className="font-bold text-gray-900">Premium Avatar</h4>
              <p className="text-xs text-gray-500 mt-1">Realistic AI video tutor</p>
              <Badge className="mt-2 bg-purple-100 text-purple-700">Premium</Badge>
            </div>
          </div>
        </div>
      </div>

      {/* Simple Avatar Style Selection */}
      {avatarConfig.avatar_mode === 'simple' && (
        <div>
          <Label className="font-semibold mb-3 block">Default Avatar Style</Label>
          <div className="grid grid-cols-3 gap-3">
            {avatarStyles.map((style) => (
              <div
                key={style.id}
                onClick={() => setAvatarConfig({...avatarConfig, default_avatar_style: style.id})}
                className={`p-4 rounded-xl border-2 cursor-pointer text-center transition-all ${
                  avatarConfig.default_avatar_style === style.id 
                    ? 'border-[#58CC02] bg-green-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <span className="text-3xl block mb-2">{style.icon}</span>
                <span className="text-sm font-medium">{style.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* HeyGen Configuration */}
      {avatarConfig.avatar_mode === 'heygen' && (
        <div className="space-y-4">
          <div className="bg-purple-50 rounded-xl p-4">
            <h4 className="font-semibold text-purple-900 mb-2 flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              Premium Avatar Setup
            </h4>
            <ol className="text-sm text-purple-800 space-y-1 list-decimal list-inside">
              <li>Your Premium Avatar credits are included in your plan</li>
              <li>Configure your monthly credit limit below</li>
              <li>Students will see a realistic AI tutor during speaking practice</li>
            </ol>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Avatar Style</Label>
              <select 
                value={avatarConfig.heygen_avatar_id}
                onChange={(e) => setAvatarConfig({...avatarConfig, heygen_avatar_id: e.target.value})}
                className="w-full h-10 px-3 border-2 border-gray-200 rounded-xl focus:border-[#58CC02] outline-none"
              >
                {heygenAvatars.map(avatar => (
                  <option key={avatar.id} value={avatar.id}>{avatar.name}</option>
                ))}
              </select>
            </div>
            <div>
              <Label>Monthly Credit Limit</Label>
              <Input
                type="number"
                value={avatarConfig.heygen_monthly_limit}
                onChange={(e) => setAvatarConfig({...avatarConfig, heygen_monthly_limit: parseInt(e.target.value)})}
                className="input-duo"
                min="10"
                max="1000"
              />
            </div>
          </div>

          {/* Free Minutes for Students */}
          <div className="bg-green-50 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Gift className="w-5 h-5 text-green-600" />
              <Label className="font-semibold text-green-900">Free Premium Minutes for Students</Label>
            </div>
            <p className="text-xs text-green-700 mb-3">
              Offer free premium AI tutor minutes to attract and convert students. Uses your credit pool.
            </p>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <Label className="text-sm">Free minutes per student</Label>
                <Input
                  type="number"
                  value={avatarConfig.free_minutes_per_student || 5}
                  onChange={(e) => setAvatarConfig({...avatarConfig, free_minutes_per_student: parseInt(e.target.value)})}
                  className="input-duo"
                  min="0"
                  max="60"
                />
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  id="free-minutes-enabled"
                  checked={avatarConfig.free_minutes_enabled || false}
                  onCheckedChange={(checked) => setAvatarConfig({...avatarConfig, free_minutes_enabled: checked})}
                />
                <Label htmlFor="free-minutes-enabled" className="text-sm">Enable</Label>
              </div>
            </div>
          </div>

          {/* Usage Display */}
          <div className="bg-gray-50 rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <Label className="text-gray-700">Credits Used This Month</Label>
              <span className="text-sm font-bold text-gray-900">
                {usage.credits_used} / {usage.credits_limit}
              </span>
            </div>
            <Progress 
              value={(usage.credits_used / usage.credits_limit) * 100} 
              className="h-2"
            />
            <p className="text-xs text-gray-500 mt-2">
              ~${(usage.credits_used * 0.99).toFixed(2)} cost absorbed by your plan
            </p>
          </div>

          <div className="bg-amber-50 rounded-xl p-4 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-amber-800 font-medium">Cost Control</p>
              <p className="text-xs text-amber-700">
                HeyGen credits are included in your institutional plan. Set a monthly limit to control usage. 
                1 credit ≈ 30 seconds of video.
              </p>
            </div>
          </div>
        </div>
      )}

      <Button onClick={handleSave} className="btn-duo" data-testid="save-avatar">
        <Save className="w-4 h-4 mr-2" />
        Save Avatar Settings
      </Button>
    </div>
  );
};

// Zoom Configuration Section
const ZoomConfigSection = ({ config, onSave }) => {
  const [zoomConfig, setZoomConfig] = useState({
    zoom_account_id: config?.zoom_account_id || '',
    zoom_client_id: config?.zoom_client_id || '',
    zoom_client_secret: config?.zoom_client_secret || '',
    zoom_enabled: config?.zoom_enabled || false,
  });
  const [showSecret, setShowSecret] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const response = await axios.post(`${API_URL}/institution/settings/zoom/test`, zoomConfig);
      setTestResult({ success: true, message: response.data.message });
      toast.success('Zoom connection successful!');
    } catch (error) {
      setTestResult({ success: false, message: error.response?.data?.detail || 'Connection failed' });
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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
            <Video className="w-6 h-6 text-blue-500" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900">Zoom Integration</h3>
            <p className="text-sm text-gray-500">Configure your Zoom account for live classes</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Label htmlFor="zoom-enabled" className="text-sm text-gray-600">Enable Zoom</Label>
          <Switch
            id="zoom-enabled"
            checked={zoomConfig.zoom_enabled}
            onCheckedChange={(checked) => setZoomConfig({...zoomConfig, zoom_enabled: checked})}
          />
        </div>
      </div>

      <div className="bg-blue-50 rounded-xl p-4">
        <h4 className="font-semibold text-blue-900 mb-2">How to get Zoom credentials:</h4>
        <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
          <li>Go to <a href="https://marketplace.zoom.us" target="_blank" rel="noopener noreferrer" className="underline">Zoom Marketplace</a></li>
          <li>Create a Server-to-Server OAuth App</li>
          <li>Copy your Account ID, Client ID, and Client Secret</li>
          <li>Enable the Meeting SDK in the app settings</li>
        </ol>
      </div>

      <div className="grid gap-4">
        <div>
          <Label>Zoom Account ID</Label>
          <Input
            value={zoomConfig.zoom_account_id}
            onChange={(e) => setZoomConfig({...zoomConfig, zoom_account_id: e.target.value})}
            placeholder="Your Zoom Account ID"
            className="input-duo"
            data-testid="zoom-account-id"
          />
        </div>
        <div>
          <Label>Zoom Client ID (SDK Key)</Label>
          <Input
            value={zoomConfig.zoom_client_id}
            onChange={(e) => setZoomConfig({...zoomConfig, zoom_client_id: e.target.value})}
            placeholder="Your Zoom Client ID"
            className="input-duo"
            data-testid="zoom-client-id"
          />
        </div>
        <div>
          <Label>Zoom Client Secret (SDK Secret)</Label>
          <div className="relative">
            <Input
              type={showSecret ? 'text' : 'password'}
              value={zoomConfig.zoom_client_secret}
              onChange={(e) => setZoomConfig({...zoomConfig, zoom_client_secret: e.target.value})}
              placeholder="Your Zoom Client Secret"
              className="input-duo pr-10"
              data-testid="zoom-client-secret"
            />
            <button
              type="button"
              onClick={() => setShowSecret(!showSecret)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              {showSecret ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>

      {testResult && (
        <div className={`p-4 rounded-xl flex items-center gap-3 ${testResult.success ? 'bg-green-50' : 'bg-red-50'}`}>
          {testResult.success ? (
            <CheckCircle className="w-5 h-5 text-green-600" />
          ) : (
            <XCircle className="w-5 h-5 text-red-600" />
          )}
          <span className={testResult.success ? 'text-green-700' : 'text-red-700'}>{testResult.message}</span>
        </div>
      )}

      <div className="flex gap-3">
        <Button onClick={handleTest} variant="outline" disabled={testing || !zoomConfig.zoom_client_id} data-testid="test-zoom">
          <TestTube className="w-4 h-4 mr-2" />
          {testing ? 'Testing...' : 'Test Connection'}
        </Button>
        <Button onClick={handleSave} className="btn-duo" data-testid="save-zoom">
          <Save className="w-4 h-4 mr-2" />
          Save Zoom Settings
        </Button>
      </div>
    </div>
  );
};

// Email SMTP Configuration Section
const EmailConfigSection = ({ config, onSave }) => {
  const [emailConfig, setEmailConfig] = useState({
    smtp_host: config?.smtp_host || '',
    smtp_port: config?.smtp_port || 587,
    smtp_user: config?.smtp_user || '',
    smtp_password: config?.smtp_password || '',
    smtp_from_email: config?.smtp_from_email || '',
    smtp_from_name: config?.smtp_from_name || '',
    smtp_enabled: config?.smtp_enabled || false,
    smtp_use_tls: config?.smtp_use_tls !== false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [testEmail, setTestEmail] = useState('');

  const handleTest = async () => {
    if (!testEmail) {
      toast.error('Please enter a test email address');
      return;
    }
    setTesting(true);
    setTestResult(null);
    try {
      const response = await axios.post(`${API_URL}/institution/settings/email/test`, {
        ...emailConfig,
        test_email: testEmail
      });
      setTestResult({ success: true, message: response.data.message });
      toast.success('Test email sent successfully!');
    } catch (error) {
      setTestResult({ success: false, message: error.response?.data?.detail || 'Failed to send test email' });
      toast.error('Failed to send test email');
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    try {
      await onSave('email', emailConfig);
      toast.success('Email settings saved!');
    } catch (error) {
      toast.error('Failed to save email settings');
    }
  };

  const presets = [
    { name: 'Gmail', host: 'smtp.gmail.com', port: 587 },
    { name: 'Outlook', host: 'smtp-mail.outlook.com', port: 587 },
    { name: 'SendGrid', host: 'smtp.sendgrid.net', port: 587 },
    { name: 'Mailgun', host: 'smtp.mailgun.org', port: 587 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
            <Mail className="w-6 h-6 text-purple-500" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900">Email SMTP Configuration</h3>
            <p className="text-sm text-gray-500">Configure your email server for CRM and notifications</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Label htmlFor="email-enabled" className="text-sm text-gray-600">Enable Email</Label>
          <Switch
            id="email-enabled"
            checked={emailConfig.smtp_enabled}
            onCheckedChange={(checked) => setEmailConfig({...emailConfig, smtp_enabled: checked})}
          />
        </div>
      </div>

      <div className="flex gap-2 flex-wrap">
        <span className="text-sm text-gray-500">Quick presets:</span>
        {presets.map((preset) => (
          <Badge
            key={preset.name}
            variant="outline"
            className="cursor-pointer hover:bg-gray-100"
            onClick={() => setEmailConfig({...emailConfig, smtp_host: preset.host, smtp_port: preset.port})}
          >
            {preset.name}
          </Badge>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label>SMTP Host</Label>
          <Input
            value={emailConfig.smtp_host}
            onChange={(e) => setEmailConfig({...emailConfig, smtp_host: e.target.value})}
            placeholder="smtp.example.com"
            className="input-duo"
            data-testid="smtp-host"
          />
        </div>
        <div>
          <Label>SMTP Port</Label>
          <Input
            type="number"
            value={emailConfig.smtp_port}
            onChange={(e) => setEmailConfig({...emailConfig, smtp_port: parseInt(e.target.value)})}
            placeholder="587"
            className="input-duo"
            data-testid="smtp-port"
          />
        </div>
        <div>
          <Label>SMTP Username</Label>
          <Input
            value={emailConfig.smtp_user}
            onChange={(e) => setEmailConfig({...emailConfig, smtp_user: e.target.value})}
            placeholder="Your email or API key"
            className="input-duo"
            data-testid="smtp-user"
          />
        </div>
        <div>
          <Label>SMTP Password</Label>
          <div className="relative">
            <Input
              type={showPassword ? 'text' : 'password'}
              value={emailConfig.smtp_password}
              onChange={(e) => setEmailConfig({...emailConfig, smtp_password: e.target.value})}
              placeholder="Your password or API secret"
              className="input-duo pr-10"
              data-testid="smtp-password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>
        <div>
          <Label>From Email</Label>
          <Input
            type="email"
            value={emailConfig.smtp_from_email}
            onChange={(e) => setEmailConfig({...emailConfig, smtp_from_email: e.target.value})}
            placeholder="noreply@youracademy.com"
            className="input-duo"
            data-testid="smtp-from-email"
          />
        </div>
        <div>
          <Label>From Name</Label>
          <Input
            value={emailConfig.smtp_from_name}
            onChange={(e) => setEmailConfig({...emailConfig, smtp_from_name: e.target.value})}
            placeholder="Your Academy Name"
            className="input-duo"
            data-testid="smtp-from-name"
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Switch
          id="use-tls"
          checked={emailConfig.smtp_use_tls}
          onCheckedChange={(checked) => setEmailConfig({...emailConfig, smtp_use_tls: checked})}
        />
        <Label htmlFor="use-tls" className="text-sm text-gray-600">Use TLS encryption (recommended)</Label>
      </div>

      <div className="bg-gray-50 rounded-xl p-4">
        <Label>Send Test Email To:</Label>
        <div className="flex gap-2 mt-2">
          <Input
            type="email"
            value={testEmail}
            onChange={(e) => setTestEmail(e.target.value)}
            placeholder="your@email.com"
            className="input-duo"
            data-testid="test-email-address"
          />
          <Button onClick={handleTest} variant="outline" disabled={testing} data-testid="send-test-email">
            <TestTube className="w-4 h-4 mr-2" />
            {testing ? 'Sending...' : 'Send Test'}
          </Button>
        </div>
      </div>

      {testResult && (
        <div className={`p-4 rounded-xl flex items-center gap-3 ${testResult.success ? 'bg-green-50' : 'bg-red-50'}`}>
          {testResult.success ? (
            <CheckCircle className="w-5 h-5 text-green-600" />
          ) : (
            <XCircle className="w-5 h-5 text-red-600" />
          )}
          <span className={testResult.success ? 'text-green-700' : 'text-red-700'}>{testResult.message}</span>
        </div>
      )}

      <Button onClick={handleSave} className="btn-duo" data-testid="save-email">
        <Save className="w-4 h-4 mr-2" />
        Save Email Settings
      </Button>
    </div>
  );
};

// Gamification Configuration Section
const GamificationConfigSection = ({ config, onSave }) => {
  const [gamificationConfig, setGamificationConfig] = useState({
    gamification_enabled: config?.gamification_enabled || false,
    xp_per_exam: config?.xp_per_exam || 50,
    xp_per_section: config?.xp_per_section || 20,
    xp_per_tutor_session: config?.xp_per_tutor_session || 15,
    xp_per_class: config?.xp_per_class || 30,
    streak_bonus_multiplier: config?.streak_bonus_multiplier || 1.5,
    leaderboard_enabled: config?.leaderboard_enabled !== false,
    badges_enabled: config?.badges_enabled !== false,
    challenges_enabled: config?.challenges_enabled !== false,
    weekly_challenges_count: config?.weekly_challenges_count || 3,
  });

  const handleSave = async () => {
    try {
      await onSave('gamification', gamificationConfig);
      toast.success('Gamification settings saved!');
    } catch (error) {
      toast.error('Failed to save gamification settings');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center">
            <Trophy className="w-6 h-6 text-amber-500" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900">Gamification Settings</h3>
            <p className="text-sm text-gray-500">Enable XP, badges, leaderboards, and challenges for your students</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Label htmlFor="gamification-enabled" className="text-sm text-gray-600">Enable Gamification</Label>
          <Switch
            id="gamification-enabled"
            checked={gamificationConfig.gamification_enabled}
            onCheckedChange={(checked) => setGamificationConfig({...gamificationConfig, gamification_enabled: checked})}
          />
        </div>
      </div>

      {gamificationConfig.gamification_enabled && (
        <>
          <div className="grid md:grid-cols-3 gap-4">
            <Card className="border-2 border-gray-100">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Users className="w-5 h-5 text-blue-500" />
                  <Label className="font-semibold">Leaderboard</Label>
                </div>
                <Switch
                  checked={gamificationConfig.leaderboard_enabled}
                  onCheckedChange={(checked) => setGamificationConfig({...gamificationConfig, leaderboard_enabled: checked})}
                />
                <p className="text-xs text-gray-500 mt-2">Rank students by XP</p>
              </CardContent>
            </Card>
            
            <Card className="border-2 border-gray-100">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Trophy className="w-5 h-5 text-amber-500" />
                  <Label className="font-semibold">Badges</Label>
                </div>
                <Switch
                  checked={gamificationConfig.badges_enabled}
                  onCheckedChange={(checked) => setGamificationConfig({...gamificationConfig, badges_enabled: checked})}
                />
                <p className="text-xs text-gray-500 mt-2">Achievement badges</p>
              </CardContent>
            </Card>
            
            <Card className="border-2 border-gray-100">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Gift className="w-5 h-5 text-pink-500" />
                  <Label className="font-semibold">Challenges</Label>
                </div>
                <Switch
                  checked={gamificationConfig.challenges_enabled}
                  onCheckedChange={(checked) => setGamificationConfig({...gamificationConfig, challenges_enabled: checked})}
                />
                <p className="text-xs text-gray-500 mt-2">Weekly challenges</p>
              </CardContent>
            </Card>
          </div>

          <Card className="border-2 border-gray-100">
            <CardHeader>
              <CardTitle className="text-lg">XP Rewards Configuration</CardTitle>
              <CardDescription>Set how much XP students earn for each activity</CardDescription>
            </CardHeader>
            <CardContent className="grid md:grid-cols-2 gap-4">
              <div>
                <Label>XP per Full Exam</Label>
                <Input
                  type="number"
                  value={gamificationConfig.xp_per_exam}
                  onChange={(e) => setGamificationConfig({...gamificationConfig, xp_per_exam: parseInt(e.target.value)})}
                  className="input-duo"
                  min="1"
                />
              </div>
              <div>
                <Label>XP per Section Practice</Label>
                <Input
                  type="number"
                  value={gamificationConfig.xp_per_section}
                  onChange={(e) => setGamificationConfig({...gamificationConfig, xp_per_section: parseInt(e.target.value)})}
                  className="input-duo"
                  min="1"
                />
              </div>
              <div>
                <Label>XP per AI Tutor Session</Label>
                <Input
                  type="number"
                  value={gamificationConfig.xp_per_tutor_session}
                  onChange={(e) => setGamificationConfig({...gamificationConfig, xp_per_tutor_session: parseInt(e.target.value)})}
                  className="input-duo"
                  min="1"
                />
              </div>
              <div>
                <Label>XP per Live Class</Label>
                <Input
                  type="number"
                  value={gamificationConfig.xp_per_class}
                  onChange={(e) => setGamificationConfig({...gamificationConfig, xp_per_class: parseInt(e.target.value)})}
                  className="input-duo"
                  min="1"
                />
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-gray-100">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Flame className="w-5 h-5 text-orange-500" />
                Streak Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Streak Bonus Multiplier</Label>
                <p className="text-xs text-gray-500 mb-2">XP multiplier for maintaining streaks (e.g., 1.5 = 50% bonus)</p>
                <Input
                  type="number"
                  step="0.1"
                  value={gamificationConfig.streak_bonus_multiplier}
                  onChange={(e) => setGamificationConfig({...gamificationConfig, streak_bonus_multiplier: parseFloat(e.target.value)})}
                  className="input-duo w-32"
                  min="1"
                  max="3"
                />
              </div>
            </CardContent>
          </Card>

          {gamificationConfig.challenges_enabled && (
            <Card className="border-2 border-gray-100">
              <CardHeader>
                <CardTitle className="text-lg">Weekly Challenges</CardTitle>
              </CardHeader>
              <CardContent>
                <div>
                  <Label>Number of Weekly Challenges</Label>
                  <Input
                    type="number"
                    value={gamificationConfig.weekly_challenges_count}
                    onChange={(e) => setGamificationConfig({...gamificationConfig, weekly_challenges_count: parseInt(e.target.value)})}
                    className="input-duo w-32"
                    min="1"
                    max="10"
                  />
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}

      <Button onClick={handleSave} className="btn-duo" data-testid="save-gamification">
        <Save className="w-4 h-4 mr-2" />
        Save Gamification Settings
      </Button>
    </div>
  );
};

// AI Agents Configuration Section
const AIAgentsConfigSection = () => {
  const [agents, setAgents] = useState([]);
  const [credits, setCredits] = useState({ remaining_credits: 0, total_credits: 0 });
  const [agentConfig, setAgentConfig] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const [agentsRes, creditsRes, configRes] = await Promise.all([
        axios.get(`${API_URL}/ai-agents/available`, { headers }),
        axios.get(`${API_URL}/ai-agents/credits`, { headers }),
        axios.get(`${API_URL}/ai-agents/config`, { headers })
      ]);
      
      setAgents(configRes.data.agents || []);
      setCredits(creditsRes.data);
      
      // Build config state
      const config = {};
      (configRes.data.agents || []).forEach(agent => {
        config[agent.id] = { enabled: agent.enabled, voice_id: agent.custom_voice_id };
      });
      setAgentConfig(config);
    } catch (error) {
      console.error('Failed to fetch AI agents data:', error);
      toast.error('Error loading AI agents configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAgent = (agentId) => {
    setAgentConfig(prev => ({
      ...prev,
      [agentId]: { ...prev[agentId], enabled: !prev[agentId]?.enabled }
    }));
  };

  const handleSaveConfig = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/ai-agents/config`, {
        agents: agentConfig
      }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('AI Agents configuration saved!');
    } catch (error) {
      console.error('Failed to save config:', error);
      toast.error('Error saving configuration');
    } finally {
      setSaving(false);
    }
  };

  const creditPrices = [
    { credits: 100, price: 10, savings: null },
    { credits: 500, price: 40, savings: '20%' },
    { credits: 1000, price: 70, savings: '30%' },
    { credits: 5000, price: 300, savings: '40%' }
  ];

  const handlePurchaseCredits = async (creditsAmount) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/ai-agents/credits/purchase`, {
        credits: creditsAmount,
        payment_method: 'stripe'
      }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success(`${creditsAmount} créditos añadidos correctamente!`);
      fetchData();
    } catch (error) {
      console.error('Failed to purchase credits:', error);
      toast.error('Error al comprar créditos');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-10">
        <div className="w-8 h-8 border-4 border-[#58CC02] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const AgentIcon = {
    official_tutor: GraduationCap,
    mock_coach: Trophy,
    planner: Calendar
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900">Multi-Agent AI Tutor System</h3>
            <p className="text-sm text-gray-500">Configure AI tutors and manage credits for your students</p>
          </div>
        </div>
      </div>

      {/* Credits Overview */}
      <Card className="bg-gradient-to-r from-amber-50 to-yellow-50 border-amber-200">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full bg-amber-100 flex items-center justify-center">
                <Coins className="w-7 h-7 text-amber-600" />
              </div>
              <div>
                <p className="text-sm text-amber-700 font-medium">AI Credits Balance</p>
                <p className="text-3xl font-bold text-amber-800">{credits.remaining_credits}</p>
                <p className="text-xs text-amber-600">
                  {credits.used_credits} used of {credits.total_credits} total
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xs text-amber-600 mb-1">Free credits: {credits.free_credits || 0}</p>
              <Progress 
                value={(credits.remaining_credits / Math.max(credits.total_credits, 1)) * 100}
                className="w-32 h-2"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Purchase Credits */}
      <div className="bg-gray-50 rounded-xl p-4">
        <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <ShoppingCart className="w-4 h-4" />
          Purchase AI Credits
        </h4>
        <div className="grid grid-cols-4 gap-3">
          {creditPrices.map(tier => (
            <button
              key={tier.credits}
              onClick={() => handlePurchaseCredits(tier.credits)}
              className="p-3 rounded-lg border-2 border-gray-200 hover:border-[#58CC02] hover:bg-green-50 transition-all text-center"
            >
              <p className="text-xl font-bold text-gray-900">{tier.credits}</p>
              <p className="text-sm text-gray-600">créditos</p>
              <p className="text-lg font-semibold text-[#58CC02]">${tier.price}</p>
              {tier.savings && (
                <Badge className="mt-1 bg-green-100 text-green-700 text-xs">
                  {tier.savings} OFF
                </Badge>
              )}
            </button>
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-2">
          * Credits are shared across all your students and AI agents
        </p>
      </div>

      {/* Agent Configuration */}
      <div>
        <h4 className="font-semibold text-gray-900 mb-3">Configure AI Agents</h4>
        <p className="text-sm text-gray-500 mb-4">
          Enable or disable specific AI agents for your students. Disabled agents won't appear in the tutor interface.
        </p>
        
        <div className="space-y-3">
          {agents.map(agent => {
            const Icon = AgentIcon[agent.id] || Bot;
            const isEnabled = agentConfig[agent.id]?.enabled !== false;
            
            return (
              <div
                key={agent.id}
                className={`p-4 rounded-xl border-2 transition-all ${
                  isEnabled ? 'border-[#58CC02] bg-green-50' : 'border-gray-200 bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                      isEnabled ? 'bg-[#58CC02]' : 'bg-gray-300'
                    }`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h5 className="font-semibold text-gray-900">{agent.name}</h5>
                      <p className="text-sm text-gray-500">{agent.name_es}</p>
                      <p className="text-xs text-gray-400 mt-1">{agent.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-700">
                        {agent.credits_per_message} crédito{agent.credits_per_message > 1 ? 's' : ''}/mensaje
                      </p>
                      {agent.voice_enabled && (
                        <Badge variant="outline" className="text-xs">
                          🎤 Voz disponible
                        </Badge>
                      )}
                    </div>
                    <Switch
                      checked={isEnabled}
                      onCheckedChange={() => handleToggleAgent(agent.id)}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Agent Descriptions */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="p-4">
          <h4 className="font-semibold text-blue-900 mb-2">💡 About AI Agents</h4>
          <ul className="text-sm text-blue-800 space-y-2">
            <li><strong>🎓 Official Tutor:</strong> Expert exam preparation with strategies, practice questions, and detailed feedback.</li>
            <li><strong>🏆 Mock Coach:</strong> Practice mode with 5 attempts per question. Provides hints before revealing answers.</li>
            <li><strong>📋 Study Planner:</strong> Creates personalized study schedules based on exam date and available time.</li>
          </ul>
        </CardContent>
      </Card>

      <Button 
        onClick={handleSaveConfig} 
        className="bg-[#58CC02] hover:bg-[#46A302]"
        disabled={saving}
      >
        <Save className="w-4 h-4 mr-2" />
        {saving ? 'Saving...' : 'Save Agent Configuration'}
      </Button>
    </div>
  );
};

// Messaging Configuration Section (WhatsApp/SMS)
const MessagingConfigSection = () => {
  const [config, setConfig] = useState({
    provider: 'twilio',
    account_sid: '',
    api_key: '',
    api_secret: '',
    from_number: '',
    whatsapp_number: '',
    enabled: false,
    sms_enabled: false,
    whatsapp_enabled: false
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testNumber, setTestNumber] = useState('');

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/institution/messaging/config`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConfig(prev => ({ ...prev, ...response.data }));
    } catch (error) {
      console.error('Failed to fetch messaging config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/institution/messaging/config`, config, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Messaging configuration saved!');
    } catch (error) {
      toast.error('Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async (type) => {
    if (!testNumber) {
      toast.error('Enter a test phone number');
      return;
    }
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/institution/messaging/test?message_type=${type}&test_number=${testNumber}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success(`Test ${type.toUpperCase()} sent to ${testNumber}`);
    } catch (error) {
      toast.error('Failed to send test message');
    }
  };

  if (loading) {
    return <div className="flex justify-center py-10"><div className="w-8 h-8 border-4 border-[#58CC02] border-t-transparent rounded-full animate-spin"></div></div>;
  }

  const providers = [
    { id: 'twilio', name: 'Twilio', icon: '📱' },
    { id: 'messagebird', name: 'MessageBird', icon: '🐦' },
    { id: 'vonage', name: 'Vonage', icon: '📞' }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-teal-500 flex items-center justify-center">
          <span className="text-2xl">📱</span>
        </div>
        <div>
          <h3 className="font-bold text-gray-900">WhatsApp & SMS Configuration</h3>
          <p className="text-sm text-gray-500">Send notifications and reminders to students</p>
        </div>
      </div>

      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
        <div className="flex items-center gap-3">
          <Switch checked={config.enabled} onCheckedChange={(v) => setConfig({...config, enabled: v})} />
          <Label className="font-medium">Enable Messaging</Label>
        </div>
      </div>

      {config.enabled && (
        <>
          <div>
            <Label className="font-semibold mb-3 block">Provider</Label>
            <div className="grid grid-cols-3 gap-3">
              {providers.map(p => (
                <button
                  key={p.id}
                  onClick={() => setConfig({...config, provider: p.id})}
                  className={`p-4 rounded-xl border-2 text-center transition-all ${
                    config.provider === p.id ? 'border-[#58CC02] bg-green-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <span className="text-2xl block mb-1">{p.icon}</span>
                  <span className="text-sm font-medium">{p.name}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label>Account SID / API Key</Label>
              <Input
                type="password"
                value={config.account_sid || config.api_key}
                onChange={(e) => setConfig({...config, account_sid: e.target.value, api_key: e.target.value})}
                placeholder="Enter API credentials"
              />
            </div>
            <div>
              <Label>API Secret</Label>
              <Input
                type="password"
                value={config.api_secret}
                onChange={(e) => setConfig({...config, api_secret: e.target.value})}
                placeholder="Enter secret"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label>SMS From Number</Label>
              <Input
                value={config.from_number}
                onChange={(e) => setConfig({...config, from_number: e.target.value})}
                placeholder="+1234567890"
              />
            </div>
            <div>
              <Label>WhatsApp Number</Label>
              <Input
                value={config.whatsapp_number}
                onChange={(e) => setConfig({...config, whatsapp_number: e.target.value})}
                placeholder="whatsapp:+1234567890"
              />
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex items-center gap-2">
              <Switch checked={config.sms_enabled} onCheckedChange={(v) => setConfig({...config, sms_enabled: v})} />
              <Label>Enable SMS</Label>
            </div>
            <div className="flex items-center gap-2">
              <Switch checked={config.whatsapp_enabled} onCheckedChange={(v) => setConfig({...config, whatsapp_enabled: v})} />
              <Label>Enable WhatsApp</Label>
            </div>
          </div>

          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-4">
              <h4 className="font-semibold text-blue-900 mb-2">Test Message</h4>
              <div className="flex gap-2">
                <Input
                  value={testNumber}
                  onChange={(e) => setTestNumber(e.target.value)}
                  placeholder="+1234567890"
                  className="flex-1"
                />
                <Button variant="outline" onClick={() => handleTest('sms')}>Test SMS</Button>
                <Button variant="outline" onClick={() => handleTest('whatsapp')}>Test WhatsApp</Button>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      <Button onClick={handleSave} className="bg-[#58CC02] hover:bg-[#46A302]" disabled={saving}>
        <Save className="w-4 h-4 mr-2" />
        {saving ? 'Saving...' : 'Save Messaging Configuration'}
      </Button>
    </div>
  );
};

// Reports Configuration Section
const ReportsConfigSection = () => {
  const [config, setConfig] = useState({
    weekly_enabled: true,
    monthly_enabled: true,
    send_to_admins: true,
    send_to_students: false,
    include_ai_usage: true,
    include_exam_stats: true,
    include_engagement: true,
    delivery_day: 1
  });
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/institution/reports/config`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConfig(prev => ({ ...prev, ...response.data }));
    } catch (error) {
      console.error('Failed to fetch reports config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/institution/reports/config`, config, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Report configuration saved!');
    } catch (error) {
      toast.error('Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const generateReport = async (type) => {
    setGenerating(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/institution/reports/generate?report_type=${type}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setReport(response.data);
      toast.success('Report generated!');
    } catch (error) {
      toast.error('Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center py-10"><div className="w-8 h-8 border-4 border-[#58CC02] border-t-transparent rounded-full animate-spin"></div></div>;
  }

  const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-500 flex items-center justify-center">
          <span className="text-2xl">📊</span>
        </div>
        <div>
          <h3 className="font-bold text-gray-900">Automatic Reports</h3>
          <p className="text-sm text-gray-500">Configure automatic progress and usage reports</p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <Card className="border-2 border-gray-100">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-semibold">Weekly Reports</h4>
                <p className="text-xs text-gray-500">Sent every {days[config.delivery_day - 1]}</p>
              </div>
              <Switch checked={config.weekly_enabled} onCheckedChange={(v) => setConfig({...config, weekly_enabled: v})} />
            </div>
          </CardContent>
        </Card>
        <Card className="border-2 border-gray-100">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-semibold">Monthly Reports</h4>
                <p className="text-xs text-gray-500">Sent on the 1st of each month</p>
              </div>
              <Switch checked={config.monthly_enabled} onCheckedChange={(v) => setConfig({...config, monthly_enabled: v})} />
            </div>
          </CardContent>
        </Card>
      </div>

      <div>
        <Label className="font-semibold mb-3 block">Report Delivery Day</Label>
        <select
          value={config.delivery_day}
          onChange={(e) => setConfig({...config, delivery_day: parseInt(e.target.value)})}
          className="w-full p-3 border rounded-xl"
        >
          {days.map((day, idx) => (
            <option key={idx} value={idx + 1}>{day}</option>
          ))}
        </select>
      </div>

      <div className="space-y-3">
        <Label className="font-semibold block">Report Contents</Label>
        <div className="grid md:grid-cols-3 gap-3">
          <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
            <Switch checked={config.include_ai_usage} onCheckedChange={(v) => setConfig({...config, include_ai_usage: v})} />
            <Label className="text-sm">AI Usage Stats</Label>
          </div>
          <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
            <Switch checked={config.include_exam_stats} onCheckedChange={(v) => setConfig({...config, include_exam_stats: v})} />
            <Label className="text-sm">Exam Statistics</Label>
          </div>
          <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
            <Switch checked={config.include_engagement} onCheckedChange={(v) => setConfig({...config, include_engagement: v})} />
            <Label className="text-sm">Student Engagement</Label>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <Label className="font-semibold block">Recipients</Label>
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <Switch checked={config.send_to_admins} onCheckedChange={(v) => setConfig({...config, send_to_admins: v})} />
            <Label>Institution Admins</Label>
          </div>
          <div className="flex items-center gap-2">
            <Switch checked={config.send_to_students} onCheckedChange={(v) => setConfig({...config, send_to_students: v})} />
            <Label>Students</Label>
          </div>
        </div>
      </div>

      <Card className="bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200">
        <CardContent className="p-4">
          <h4 className="font-semibold text-indigo-900 mb-3">Generate Report Now</h4>
          <div className="flex gap-3">
            <Button 
              variant="outline" 
              onClick={() => generateReport('weekly')}
              disabled={generating}
              className="flex-1"
            >
              {generating ? 'Generating...' : '📅 Weekly Report'}
            </Button>
            <Button 
              variant="outline" 
              onClick={() => generateReport('monthly')}
              disabled={generating}
              className="flex-1"
            >
              {generating ? 'Generating...' : '📆 Monthly Report'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {report && (
        <Card className="border-2 border-indigo-200">
          <CardHeader>
            <CardTitle className="text-lg">📊 Generated Report</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4 mb-4">
              <div className="p-4 bg-green-50 rounded-xl text-center">
                <p className="text-2xl font-bold text-green-600">{report.engagement?.active_students || 0}</p>
                <p className="text-xs text-gray-600">Active Students</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-xl text-center">
                <p className="text-2xl font-bold text-blue-600">{report.ai_usage?.total_credits_used || 0}</p>
                <p className="text-xs text-gray-600">AI Credits Used</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-xl text-center">
                <p className="text-2xl font-bold text-purple-600">{report.exams?.total_attempts || 0}</p>
                <p className="text-xs text-gray-600">Exam Attempts</p>
              </div>
            </div>
            {report.highlights?.length > 0 && (
              <div className="space-y-2">
                <p className="font-semibold text-sm">Highlights:</p>
                {report.highlights.map((h, i) => (
                  <p key={i} className="text-sm text-gray-700">{h}</p>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Button onClick={handleSave} className="bg-[#58CC02] hover:bg-[#46A302]" disabled={saving}>
        <Save className="w-4 h-4 mr-2" />
        {saving ? 'Saving...' : 'Save Report Configuration'}
      </Button>
    </div>
  );
};

// Main Institution Settings Component
export default function InstitutionSettings() {
  const [activeTab, setActiveTab] = useState('ai-agents');
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await axios.get(`${API_URL}/institution/settings`);
      setConfig(response.data);
    } catch (error) {
      console.error('Failed to fetch settings:', error);
      toast.error('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (section, data) => {
    try {
      await axios.post(`${API_URL}/institution/settings/${section}`, data);
      await fetchConfig(); // Refresh config
      return true;
    } catch (error) {
      console.error('Failed to save settings:', error);
      throw error;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-12 h-12 border-4 border-[#58CC02] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="institution-settings">
      <div>
        <h2 className="text-2xl font-extrabold text-gray-900 flex items-center gap-2">
          <Settings className="w-7 h-7 text-gray-600" />
          Institution Settings
        </h2>
        <p className="text-gray-500">Configure integrations and features for your academy</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="ai-agents" className="flex items-center gap-1 text-xs">
            <Sparkles className="w-4 h-4" /> AI
          </TabsTrigger>
          <TabsTrigger value="avatar" className="flex items-center gap-1 text-xs">
            <Bot className="w-4 h-4" /> Avatar
          </TabsTrigger>
          <TabsTrigger value="zoom" className="flex items-center gap-1 text-xs">
            <Video className="w-4 h-4" /> Zoom
          </TabsTrigger>
          <TabsTrigger value="email" className="flex items-center gap-1 text-xs">
            <Mail className="w-4 h-4" /> Email
          </TabsTrigger>
          <TabsTrigger value="messaging" className="flex items-center gap-1 text-xs">
            📱 SMS
          </TabsTrigger>
          <TabsTrigger value="reports" className="flex items-center gap-1 text-xs">
            📊 Reports
          </TabsTrigger>
          <TabsTrigger value="gamification" className="flex items-center gap-1 text-xs">
            <Trophy className="w-4 h-4" /> XP
          </TabsTrigger>
        </TabsList>

        <div className="mt-6">
          <TabsContent value="ai-agents">
            <Card className="border-2 border-gray-100">
              <CardContent className="p-6">
                <AIAgentsConfigSection />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="avatar">
            <Card className="border-2 border-gray-100">
              <CardContent className="p-6">
                <AvatarConfigSection config={config?.avatar} onSave={handleSave} />
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="zoom">
            <Card className="border-2 border-gray-100">
              <CardContent className="p-6">
                <ZoomConfigSection config={config?.zoom} onSave={handleSave} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="email">
            <Card className="border-2 border-gray-100">
              <CardContent className="p-6">
                <EmailConfigSection config={config?.email} onSave={handleSave} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="messaging">
            <Card className="border-2 border-gray-100">
              <CardContent className="p-6">
                <MessagingConfigSection />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reports">
            <Card className="border-2 border-gray-100">
              <CardContent className="p-6">
                <ReportsConfigSection />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="gamification">
            <Card className="border-2 border-gray-100">
              <CardContent className="p-6">
                <GamificationConfigSection config={config?.gamification} onSave={handleSave} />
              </CardContent>
            </Card>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}
