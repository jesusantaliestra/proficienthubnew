import React, { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Bot, Sparkles, Gift, AlertTriangle, Save } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const AvatarConfigSection = ({ config, onSave }) => {
  const [avatarConfig, setAvatarConfig] = useState({
    avatar_mode: config?.avatar_mode || 'simple',
    default_avatar_style: config?.default_avatar_style || 'teacher',
    heygen_enabled: config?.heygen_enabled || false,
    heygen_avatar_id: config?.heygen_avatar_id || 'sarah',
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
    <div className="space-y-6" data-testid="avatar-config-section">
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
              Offer free premium AI tutor minutes to attract students.
            </p>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <Input
                  type="number"
                  value={avatarConfig.free_minutes_per_student || 5}
                  onChange={(e) => setAvatarConfig({...avatarConfig, free_minutes_per_student: parseInt(e.target.value)})}
                  className="input-duo"
                  min="0"
                  max="60"
                />
              </div>
              <Switch
                checked={avatarConfig.free_minutes_enabled || false}
                onCheckedChange={(checked) => setAvatarConfig({...avatarConfig, free_minutes_enabled: checked})}
              />
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
            <Progress value={(usage.credits_used / usage.credits_limit) * 100} className="h-2" />
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
