import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Badge } from '../ui/badge';
import { Trophy, Flame, Save, Zap, Users, Gift, Star, Target } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const GamificationConfigSection = ({ config, onSave }) => {
  const [gamificationConfig, setGamificationConfig] = useState({
    gamification_enabled: config?.gamification_enabled || false,
    points_per_exam: config?.points_per_exam || 100,
    points_per_perfect_score: config?.points_per_perfect_score || 500,
    points_per_speaking_practice: config?.points_per_speaking_practice || 50,
    leaderboard_enabled: config?.leaderboard_enabled || true,
    badges_enabled: config?.badges_enabled || true,
    streaks_enabled: config?.streaks_enabled || true,
    streak_multiplier: config?.streak_multiplier || 1.5,
    weekly_challenges_enabled: config?.weekly_challenges_enabled || false,
    rewards_marketplace_enabled: config?.rewards_marketplace_enabled || false,
  });

  const handleSave = async () => {
    try {
      await onSave('gamification', gamificationConfig);
      toast.success('Gamification settings saved!');
    } catch (error) {
      toast.error('Failed to save gamification settings');
    }
  };

  const features = [
    { 
      id: 'leaderboard', 
      name: 'Leaderboard', 
      icon: Users, 
      color: 'blue',
      description: 'Show top performers',
      key: 'leaderboard_enabled'
    },
    { 
      id: 'badges', 
      name: 'Badges', 
      icon: Star, 
      color: 'yellow',
      description: 'Award achievements',
      key: 'badges_enabled'
    },
    { 
      id: 'streaks', 
      name: 'Streaks', 
      icon: Flame, 
      color: 'orange',
      description: 'Daily login rewards',
      key: 'streaks_enabled'
    },
    { 
      id: 'challenges', 
      name: 'Weekly Challenges', 
      icon: Target, 
      color: 'purple',
      description: 'Team competitions',
      key: 'weekly_challenges_enabled'
    },
    { 
      id: 'marketplace', 
      name: 'Rewards Marketplace', 
      icon: Gift, 
      color: 'green',
      description: 'Redeem points for rewards',
      key: 'rewards_marketplace_enabled'
    },
  ];

  return (
    <div className="space-y-6" data-testid="gamification-config-section">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
            <Trophy className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900">Gamification</h3>
            <p className="text-sm text-gray-500">Engage students with points, badges, and leaderboards</p>
          </div>
        </div>
        <Switch
          checked={gamificationConfig.gamification_enabled}
          onCheckedChange={(checked) => setGamificationConfig({...gamificationConfig, gamification_enabled: checked})}
        />
      </div>

      {gamificationConfig.gamification_enabled && (
        <>
          {/* Feature Toggles */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {features.map((feature) => {
              const Icon = feature.icon;
              const isEnabled = gamificationConfig[feature.key];
              return (
                <div
                  key={feature.id}
                  onClick={() => setGamificationConfig({
                    ...gamificationConfig,
                    [feature.key]: !isEnabled
                  })}
                  className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                    isEnabled 
                      ? `border-${feature.color}-300 bg-${feature.color}-50` 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      isEnabled ? `bg-${feature.color}-500` : 'bg-gray-300'
                    }`}>
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 text-sm">{feature.name}</h4>
                      <p className="text-xs text-gray-500">{feature.description}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Points Configuration */}
          <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl p-4">
            <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-500" />
              Points Configuration
            </h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-sm">Points per Exam Completion</Label>
                <Input
                  type="number"
                  value={gamificationConfig.points_per_exam}
                  onChange={(e) => setGamificationConfig({
                    ...gamificationConfig,
                    points_per_exam: parseInt(e.target.value)
                  })}
                  className="input-duo"
                  min="0"
                />
              </div>
              <div>
                <Label className="text-sm">Bonus for Perfect Score</Label>
                <Input
                  type="number"
                  value={gamificationConfig.points_per_perfect_score}
                  onChange={(e) => setGamificationConfig({
                    ...gamificationConfig,
                    points_per_perfect_score: parseInt(e.target.value)
                  })}
                  className="input-duo"
                  min="0"
                />
              </div>
              <div>
                <Label className="text-sm">Points per Speaking Session</Label>
                <Input
                  type="number"
                  value={gamificationConfig.points_per_speaking_practice}
                  onChange={(e) => setGamificationConfig({
                    ...gamificationConfig,
                    points_per_speaking_practice: parseInt(e.target.value)
                  })}
                  className="input-duo"
                  min="0"
                />
              </div>
              <div>
                <Label className="text-sm">Streak Multiplier</Label>
                <Input
                  type="number"
                  step="0.1"
                  value={gamificationConfig.streak_multiplier}
                  onChange={(e) => setGamificationConfig({
                    ...gamificationConfig,
                    streak_multiplier: parseFloat(e.target.value)
                  })}
                  className="input-duo"
                  min="1"
                  max="5"
                />
                <p className="text-xs text-gray-500 mt-1">Points multiplied by streak days</p>
              </div>
            </div>
          </div>

          {/* Preview */}
          <div className="bg-gray-50 rounded-xl p-4">
            <h4 className="font-semibold text-gray-900 mb-3">Example Student Rewards</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Complete 1 exam:</span>
                <Badge className="bg-green-100 text-green-700">+{gamificationConfig.points_per_exam} XP</Badge>
              </div>
              <div className="flex justify-between">
                <span>Perfect score bonus:</span>
                <Badge className="bg-yellow-100 text-yellow-700">+{gamificationConfig.points_per_perfect_score} XP</Badge>
              </div>
              <div className="flex justify-between">
                <span>7-day streak bonus:</span>
                <Badge className="bg-orange-100 text-orange-700">
                  {gamificationConfig.streak_multiplier}x multiplier
                </Badge>
              </div>
            </div>
          </div>
        </>
      )}

      <Button onClick={handleSave} className="btn-duo" data-testid="save-gamification">
        <Save className="w-4 h-4 mr-2" />
        Save Gamification Settings
      </Button>
    </div>
  );
};
