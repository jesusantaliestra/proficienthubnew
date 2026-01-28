import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { 
  Bell, Send, Users, Clock, CheckCircle, 
  AlertCircle, Smartphone, History, Filter
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function PushNotificationsPanel() {
  const [notification, setNotification] = useState({
    title: '',
    body: '',
    notification_type: 'general'
  });
  const [sending, setSending] = useState(false);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total_devices: 0, active_today: 0 });

  useEffect(() => {
    fetchHistory();
    fetchStats();
  }, []);

  const fetchHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/notifications/history`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setHistory(response.data.notifications || []);
    } catch (error) {
      console.error('Failed to fetch notification history:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    // In a real implementation, this would fetch actual stats
    setStats({ total_devices: 45, active_today: 32 });
  };

  const sendNotification = async () => {
    if (!notification.title || !notification.body) {
      toast.error('Please fill in title and message');
      return;
    }

    setSending(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_URL}/notifications/send`, notification, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success(`Notification sent to ${response.data.sent} devices`);
      setNotification({ title: '', body: '', notification_type: 'general' });
      fetchHistory();
    } catch (error) {
      console.error('Failed to send notification:', error);
      toast.error('Failed to send notification');
    } finally {
      setSending(false);
    }
  };

  const notificationTypes = [
    { id: 'general', label: 'General', icon: '📢', color: 'bg-blue-100 text-blue-700' },
    { id: 'class_reminder', label: 'Class Reminder', icon: '🎥', color: 'bg-purple-100 text-purple-700' },
    { id: 'study_reminder', label: 'Study Reminder', icon: '📚', color: 'bg-green-100 text-green-700' },
    { id: 'announcement', label: 'Announcement', icon: '📣', color: 'bg-yellow-100 text-yellow-700' },
    { id: 'promotion', label: 'Promotion', icon: '🎁', color: 'bg-pink-100 text-pink-700' }
  ];

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-ES', { 
      day: 'numeric', 
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
            <Bell className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900">Push Notifications</h3>
            <p className="text-sm text-gray-500">Send notifications to your students' devices</p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
          <CardContent className="p-4 text-center">
            <Smartphone className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-blue-700">{stats.total_devices}</p>
            <p className="text-xs text-blue-600">Registered Devices</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
          <CardContent className="p-4 text-center">
            <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-green-700">{stats.active_today}</p>
            <p className="text-xs text-green-600">Active Today</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-purple-50 to-violet-50 border-purple-200">
          <CardContent className="p-4 text-center">
            <History className="w-8 h-8 text-purple-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-purple-700">{history.length}</p>
            <p className="text-xs text-purple-600">Sent This Month</p>
          </CardContent>
        </Card>
      </div>

      {/* Compose Notification */}
      <Card className="border-2 border-gray-100">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Send className="w-5 h-5 text-[#58CC02]" />
            Compose Notification
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Notification Type */}
          <div>
            <Label className="font-semibold mb-2 block">Notification Type</Label>
            <div className="flex flex-wrap gap-2">
              {notificationTypes.map(type => (
                <button
                  key={type.id}
                  onClick={() => setNotification({ ...notification, notification_type: type.id })}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                    notification.notification_type === type.id 
                      ? 'bg-[#58CC02] text-white' 
                      : type.color
                  }`}
                >
                  {type.icon} {type.label}
                </button>
              ))}
            </div>
          </div>

          {/* Title */}
          <div>
            <Label htmlFor="notif-title" className="font-semibold">Title</Label>
            <Input
              id="notif-title"
              placeholder="Notification title..."
              value={notification.title}
              onChange={(e) => setNotification({ ...notification, title: e.target.value })}
              maxLength={60}
            />
            <p className="text-xs text-gray-400 mt-1">{notification.title.length}/60 characters</p>
          </div>

          {/* Body */}
          <div>
            <Label htmlFor="notif-body" className="font-semibold">Message</Label>
            <Textarea
              id="notif-body"
              placeholder="Your message here..."
              value={notification.body}
              onChange={(e) => setNotification({ ...notification, body: e.target.value })}
              rows={3}
              maxLength={200}
            />
            <p className="text-xs text-gray-400 mt-1">{notification.body.length}/200 characters</p>
          </div>

          {/* Preview */}
          {(notification.title || notification.body) && (
            <div className="bg-gray-900 rounded-2xl p-4 text-white">
              <p className="text-xs text-gray-400 mb-2">Preview</p>
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-[#58CC02] flex items-center justify-center flex-shrink-0">
                  <span className="text-lg">📱</span>
                </div>
                <div>
                  <p className="font-semibold text-sm">{notification.title || 'Notification Title'}</p>
                  <p className="text-xs text-gray-300 mt-1">{notification.body || 'Your message will appear here...'}</p>
                </div>
              </div>
            </div>
          )}

          <Button 
            className="w-full bg-[#58CC02] hover:bg-[#46A302] text-white"
            onClick={sendNotification}
            disabled={sending}
          >
            {sending ? (
              <>Sending...</>
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Send to All Students
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Recent Notifications */}
      <Card className="border-2 border-gray-100">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <History className="w-5 h-5 text-gray-600" />
            Recent Notifications
          </CardTitle>
        </CardHeader>
        <CardContent>
          {history.length > 0 ? (
            <div className="space-y-3">
              {history.slice(0, 5).map((notif, idx) => {
                const type = notificationTypes.find(t => t.id === notif.notification_type) || notificationTypes[0];
                return (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">{type.icon}</span>
                      <div>
                        <p className="font-semibold text-gray-900 text-sm">{notif.title}</p>
                        <p className="text-xs text-gray-500">{notif.body?.substring(0, 50)}...</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline" className="text-xs">
                        {notif.recipients} recipients
                      </Badge>
                      <p className="text-xs text-gray-400 mt-1">{formatDate(notif.created_at)}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Bell className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No notifications sent yet</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
