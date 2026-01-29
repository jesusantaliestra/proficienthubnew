import React, { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { 
  Users, MessageSquare, Trophy, Star, CheckCircle, Award, Crown,
  Save, Zap, TrendingUp, Gift
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const CommunityGamificationSection = ({ onSave }) => {
  const [config, setConfig] = useState({
    community_gamification_enabled: false,
    points_per_post: 10,
    points_per_reply: 5,
    points_per_solution: 50,
    points_per_like_received: 2,
    points_per_group_created: 25,
    points_per_group_joined: 5,
    show_contributor_leaderboard: true,
    show_reputation_badges: true,
    weekly_top_contributor_reward: 100
  });
  const [badges, setBadges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/community/gamification/config`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConfig(response.data.config);
      setBadges(response.data.badges || []);
    } catch (error) {
      console.error('Failed to fetch community gamification config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API_URL}/community/gamification/config`, config, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Community gamification settings saved!');
      if (onSave) onSave('community_gamification', config);
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const getBadgeIcon = (iconName) => {
    const icons = {
      MessageSquare,
      CheckCircle,
      TrendingUp,
      Star,
      Users,
      Award,
      Crown
    };
    return icons[iconName] || Star;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="community-gamification-section">
      {/* Header with Toggle */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
            <Users className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900">Community Gamification</h3>
            <p className="text-sm text-gray-500">Reward active community contributors</p>
          </div>
        </div>
        <Switch
          checked={config.community_gamification_enabled}
          onCheckedChange={(checked) => setConfig({...config, community_gamification_enabled: checked})}
          data-testid="community-gamification-toggle"
        />
      </div>

      {config.community_gamification_enabled && (
        <>
          {/* Points Configuration */}
          <Card className="border-2 border-gray-100 rounded-2xl">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-500" />
                Reputation Points
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <Label className="text-sm">Points per Post</Label>
                  <Input
                    type="number"
                    value={config.points_per_post}
                    onChange={(e) => setConfig({...config, points_per_post: parseInt(e.target.value) || 0})}
                    className="input-duo"
                    min="0"
                  />
                </div>
                <div>
                  <Label className="text-sm">Points per Reply</Label>
                  <Input
                    type="number"
                    value={config.points_per_reply}
                    onChange={(e) => setConfig({...config, points_per_reply: parseInt(e.target.value) || 0})}
                    className="input-duo"
                    min="0"
                  />
                </div>
                <div>
                  <Label className="text-sm">Points per Solution</Label>
                  <Input
                    type="number"
                    value={config.points_per_solution}
                    onChange={(e) => setConfig({...config, points_per_solution: parseInt(e.target.value) || 0})}
                    className="input-duo"
                    min="0"
                  />
                  <p className="text-xs text-gray-500 mt-1">When reply is marked as solution</p>
                </div>
                <div>
                  <Label className="text-sm">Points per Like Received</Label>
                  <Input
                    type="number"
                    value={config.points_per_like_received}
                    onChange={(e) => setConfig({...config, points_per_like_received: parseInt(e.target.value) || 0})}
                    className="input-duo"
                    min="0"
                  />
                </div>
                <div>
                  <Label className="text-sm">Points for Creating Group</Label>
                  <Input
                    type="number"
                    value={config.points_per_group_created}
                    onChange={(e) => setConfig({...config, points_per_group_created: parseInt(e.target.value) || 0})}
                    className="input-duo"
                    min="0"
                  />
                </div>
                <div>
                  <Label className="text-sm">Points for Joining Group</Label>
                  <Input
                    type="number"
                    value={config.points_per_group_joined}
                    onChange={(e) => setConfig({...config, points_per_group_joined: parseInt(e.target.value) || 0})}
                    className="input-duo"
                    min="0"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Display Options */}
          <Card className="border-2 border-gray-100 rounded-2xl">
            <CardHeader>
              <CardTitle className="text-lg">Display Options</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                <div>
                  <Label className="font-semibold">Contributor Leaderboard</Label>
                  <p className="text-xs text-gray-500">Show top community contributors</p>
                </div>
                <Switch
                  checked={config.show_contributor_leaderboard}
                  onCheckedChange={(checked) => setConfig({...config, show_contributor_leaderboard: checked})}
                />
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                <div>
                  <Label className="font-semibold">Reputation Badges</Label>
                  <p className="text-xs text-gray-500">Award badges for community achievements</p>
                </div>
                <Switch
                  checked={config.show_reputation_badges}
                  onCheckedChange={(checked) => setConfig({...config, show_reputation_badges: checked})}
                />
              </div>
              <div className="p-3 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl">
                <div className="flex items-center gap-2 mb-2">
                  <Gift className="w-5 h-5 text-orange-500" />
                  <Label className="font-semibold">Weekly Top Contributor Bonus</Label>
                </div>
                <div className="flex items-center gap-3">
                  <Input
                    type="number"
                    value={config.weekly_top_contributor_reward}
                    onChange={(e) => setConfig({...config, weekly_top_contributor_reward: parseInt(e.target.value) || 0})}
                    className="input-duo w-32"
                    min="0"
                  />
                  <span className="text-sm text-gray-600">bonus XP each week</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Available Badges Preview */}
          {config.show_reputation_badges && badges.length > 0 && (
            <Card className="border-2 border-gray-100 rounded-2xl">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Trophy className="w-5 h-5 text-yellow-500" />
                  Community Badges
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {badges.map((badge) => {
                    const Icon = getBadgeIcon(badge.icon);
                    return (
                      <div key={badge.id} className="p-3 bg-gray-50 rounded-xl text-center">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center mx-auto mb-2">
                          <Icon className="w-5 h-5 text-white" />
                        </div>
                        <h4 className="font-semibold text-sm text-gray-900">{badge.name}</h4>
                        <p className="text-xs text-gray-500 mt-1">{badge.description}</p>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Example Calculation */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-4">
            <h4 className="font-semibold text-gray-900 mb-3">Example Reputation Earnings</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Create a helpful post:</span>
                <Badge className="bg-indigo-100 text-indigo-700">+{config.points_per_post} rep</Badge>
              </div>
              <div className="flex justify-between">
                <span>Reply marked as solution:</span>
                <Badge className="bg-green-100 text-green-700">+{config.points_per_solution} rep</Badge>
              </div>
              <div className="flex justify-between">
                <span>Weekly top contributor:</span>
                <Badge className="bg-yellow-100 text-yellow-700">+{config.weekly_top_contributor_reward} rep</Badge>
              </div>
            </div>
          </div>
        </>
      )}

      <Button onClick={handleSave} disabled={saving} className="btn-duo" data-testid="save-community-gamification">
        <Save className="w-4 h-4 mr-2" />
        {saving ? 'Saving...' : 'Save Community Gamification Settings'}
      </Button>
    </div>
  );
};
