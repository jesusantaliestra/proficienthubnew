import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Switch } from '../components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Palette, Globe, Mail, Image, Type, Layout, ExternalLink, 
  CheckCircle, AlertCircle, Copy, ArrowLeft, Save, Eye
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const WhiteLabelSettings = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState({
    custom_domain: '',
    subdomain: '',
    platform_name: 'ProficientHub',
    logo_url: '',
    logo_dark_url: '',
    favicon_url: '',
    primary_color: '#58CC02',
    secondary_color: '#1CB0F6',
    accent_color: '#FF4B4B',
    background_color: '#FFFFFF',
    text_color: '#1F2937',
    font_family: 'Inter, system-ui, sans-serif',
    heading_font: '',
    border_radius: '12px',
    button_style: 'rounded',
    card_style: 'elevated',
    show_powered_by: true,
    enable_dark_mode: true,
    email_from_name: '',
    email_footer_text: '',
    website_url: '',
    facebook_url: '',
    instagram_url: '',
    linkedin_url: '',
    twitter_url: '',
    custom_css: '',
    hero_title: '',
    hero_subtitle: '',
    hero_image_url: '',
    support_email: '',
    support_phone: ''
  });
  const [dnsStatus, setDnsStatus] = useState(null);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await axios.get(`${API_URL}/whitelabel/config`);
      if (response.data.config && !response.data.config.is_default) {
        setConfig(prev => ({ ...prev, ...response.data.config }));
        setDnsStatus({
          verified: response.data.config.dns_verified,
          ssl_status: response.data.config.ssl_status
        });
      }
    } catch (error) {
      console.error('Failed to fetch config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Try to update first
      try {
        await axios.put(`${API_URL}/whitelabel/config`, config);
        toast.success('White-label settings saved!');
      } catch (error) {
        if (error.response?.status === 404) {
          // Config doesn't exist, create it
          await axios.post(`${API_URL}/whitelabel/config`, {
            institution_id: user.id,
            ...config
          });
          toast.success('White-label configuration created!');
        } else {
          throw error;
        }
      }
      fetchConfig();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleVerifyDomain = async () => {
    try {
      const response = await axios.post(`${API_URL}/whitelabel/verify-domain`);
      toast.success('Domain verified!');
      setDnsStatus({
        verified: true,
        ssl_status: 'active'
      });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Domain verification failed');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-[#58CC02] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => navigate(-1)}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-extrabold text-gray-900">White-Label Settings</h1>
              <p className="text-sm text-gray-500">Customize your platform branding and domain</p>
            </div>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" className="flex items-center gap-2">
              <Eye className="w-4 h-4" /> Preview
            </Button>
            <Button onClick={handleSave} disabled={saving} className="btn-duo flex items-center gap-2">
              <Save className="w-4 h-4" /> {saving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <Tabs defaultValue="domain" className="space-y-6">
          <TabsList className="bg-white border rounded-xl p-1">
            <TabsTrigger value="domain" className="flex items-center gap-2 data-[state=active]:bg-[#58CC02] data-[state=active]:text-white rounded-lg">
              <Globe className="w-4 h-4" /> Domain
            </TabsTrigger>
            <TabsTrigger value="branding" className="flex items-center gap-2 data-[state=active]:bg-[#58CC02] data-[state=active]:text-white rounded-lg">
              <Palette className="w-4 h-4" /> Branding
            </TabsTrigger>
            <TabsTrigger value="typography" className="flex items-center gap-2 data-[state=active]:bg-[#58CC02] data-[state=active]:text-white rounded-lg">
              <Type className="w-4 h-4" /> Typography
            </TabsTrigger>
            <TabsTrigger value="layout" className="flex items-center gap-2 data-[state=active]:bg-[#58CC02] data-[state=active]:text-white rounded-lg">
              <Layout className="w-4 h-4" /> Layout
            </TabsTrigger>
            <TabsTrigger value="email" className="flex items-center gap-2 data-[state=active]:bg-[#58CC02] data-[state=active]:text-white rounded-lg">
              <Mail className="w-4 h-4" /> Email
            </TabsTrigger>
            <TabsTrigger value="advanced" className="flex items-center gap-2 data-[state=active]:bg-[#58CC02] data-[state=active]:text-white rounded-lg">
              <ExternalLink className="w-4 h-4" /> Advanced
            </TabsTrigger>
          </TabsList>

          {/* Domain Tab */}
          <TabsContent value="domain" className="space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Custom Domain */}
              <Card className="bg-white border-2 rounded-2xl">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Globe className="w-5 h-5 text-[#58CC02]" />
                    Custom Domain (Premium)
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Your Custom Domain</Label>
                    <Input
                      value={config.custom_domain}
                      onChange={(e) => setConfig({...config, custom_domain: e.target.value})}
                      placeholder="app.youracademy.com"
                      className="input-duo"
                    />
                    <p className="text-xs text-gray-500 mt-1">Your students will access the platform via this domain</p>
                  </div>

                  {config.custom_domain && (
                    <div className="bg-gray-50 rounded-xl p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold">DNS Status</span>
                        {dnsStatus?.verified ? (
                          <Badge className="bg-green-100 text-green-700 flex items-center gap-1">
                            <CheckCircle className="w-3 h-3" /> Verified
                          </Badge>
                        ) : (
                          <Badge className="bg-yellow-100 text-yellow-700 flex items-center gap-1">
                            <AlertCircle className="w-3 h-3" /> Pending
                          </Badge>
                        )}
                      </div>
                      
                      <div className="space-y-2 text-sm">
                        <p className="font-medium">Required DNS Records:</p>
                        <div className="bg-white rounded-lg p-3 border">
                          <div className="flex items-center justify-between">
                            <code className="text-xs">CNAME {config.custom_domain} → app.proficienthub.com</code>
                            <Button size="sm" variant="ghost" onClick={() => copyToClipboard(`CNAME ${config.custom_domain} app.proficienthub.com`)}>
                              <Copy className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                      </div>
                      
                      <Button onClick={handleVerifyDomain} variant="outline" className="w-full">
                        Verify Domain
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Subdomain */}
              <Card className="bg-white border-2 rounded-2xl">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Globe className="w-5 h-5 text-blue-500" />
                    Subdomain (Free)
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Your Subdomain</Label>
                    <div className="flex items-center gap-2">
                      <Input
                        value={config.subdomain}
                        onChange={(e) => setConfig({...config, subdomain: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '')})}
                        placeholder="youracademy"
                        className="input-duo"
                      />
                      <span className="text-gray-500 whitespace-nowrap">.proficienthub.com</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Free option - no DNS configuration required</p>
                  </div>

                  {config.subdomain && (
                    <div className="bg-green-50 rounded-xl p-4 border border-green-200">
                      <p className="text-sm text-green-700">
                        ✅ Your platform will be available at: <strong>{config.subdomain}.proficienthub.com</strong>
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Branding Tab */}
          <TabsContent value="branding" className="space-y-6">
            {/* Preset Themes */}
            <Card className="bg-white border-2 rounded-2xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="w-5 h-5 text-purple-500" />
                  Quick Start: Preset Themes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                  {[
                    { id: 'default', name: 'Classic', colors: ['#58CC02', '#1CB0F6', '#FF4B4B'] },
                    { id: 'ocean', name: 'Ocean Blue', colors: ['#0EA5E9', '#0284C7', '#F59E0B'] },
                    { id: 'forest', name: 'Forest Green', colors: ['#10B981', '#059669', '#8B5CF6'] },
                    { id: 'sunset', name: 'Sunset', colors: ['#F97316', '#EA580C', '#06B6D4'] },
                    { id: 'royal', name: 'Royal Purple', colors: ['#8B5CF6', '#7C3AED', '#EC4899'] },
                    { id: 'midnight', name: 'Midnight', colors: ['#6366F1', '#4F46E5', '#22D3EE'], dark: true }
                  ].map((theme) => (
                    <button
                      key={theme.id}
                      onClick={async () => {
                        try {
                          await axios.post(`${API_URL}/api/whitelabel/apply-theme/${theme.id}`);
                          toast.success(`Theme "${theme.name}" applied!`);
                          fetchConfig();
                        } catch (error) {
                          toast.error('Failed to apply theme');
                        }
                      }}
                      className={`p-4 rounded-xl border-2 border-gray-200 hover:border-purple-300 transition-all text-center ${
                        theme.dark ? 'bg-gray-900' : 'bg-white'
                      }`}
                    >
                      <div className="flex justify-center gap-1 mb-2">
                        {theme.colors.map((color, i) => (
                          <div
                            key={i}
                            className="w-6 h-6 rounded-full"
                            style={{ backgroundColor: color }}
                          />
                        ))}
                      </div>
                      <span className={`text-sm font-medium ${theme.dark ? 'text-white' : 'text-gray-700'}`}>
                        {theme.name}
                      </span>
                    </button>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-3 text-center">
                  Click a theme to apply it instantly. You can customize colors further below.
                </p>
              </CardContent>
            </Card>

            <div className="grid lg:grid-cols-2 gap-6">
              {/* Platform Identity */}
              <Card className="bg-white border-2 rounded-2xl">
                <CardHeader>
                  <CardTitle>Platform Identity</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Platform Name</Label>
                    <Input
                      value={config.platform_name}
                      onChange={(e) => setConfig({...config, platform_name: e.target.value})}
                      placeholder="Your Academy Name"
                      className="input-duo"
                    />
                  </div>
                  <div>
                    <Label>Logo URL (Light Background)</Label>
                    <Input
                      value={config.logo_url}
                      onChange={(e) => setConfig({...config, logo_url: e.target.value})}
                      placeholder="https://..."
                      className="input-duo"
                    />
                  </div>
                  <div>
                    <Label>Logo URL (Dark Background)</Label>
                    <Input
                      value={config.logo_dark_url}
                      onChange={(e) => setConfig({...config, logo_dark_url: e.target.value})}
                      placeholder="https://..."
                      className="input-duo"
                    />
                  </div>
                  <div>
                    <Label>Favicon URL</Label>
                    <Input
                      value={config.favicon_url}
                      onChange={(e) => setConfig({...config, favicon_url: e.target.value})}
                      placeholder="https://..."
                      className="input-duo"
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Colors */}
              <Card className="bg-white border-2 rounded-2xl">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Palette className="w-5 h-5" /> Brand Colors
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Primary Color</Label>
                      <div className="flex items-center gap-2">
                        <input
                          type="color"
                          value={config.primary_color}
                          onChange={(e) => setConfig({...config, primary_color: e.target.value})}
                          className="w-10 h-10 rounded-lg cursor-pointer"
                        />
                        <Input
                          value={config.primary_color}
                          onChange={(e) => setConfig({...config, primary_color: e.target.value})}
                          className="input-duo flex-1"
                        />
                      </div>
                    </div>
                    <div>
                      <Label>Secondary Color</Label>
                      <div className="flex items-center gap-2">
                        <input
                          type="color"
                          value={config.secondary_color}
                          onChange={(e) => setConfig({...config, secondary_color: e.target.value})}
                          className="w-10 h-10 rounded-lg cursor-pointer"
                        />
                        <Input
                          value={config.secondary_color}
                          onChange={(e) => setConfig({...config, secondary_color: e.target.value})}
                          className="input-duo flex-1"
                        />
                      </div>
                    </div>
                    <div>
                      <Label>Accent Color</Label>
                      <div className="flex items-center gap-2">
                        <input
                          type="color"
                          value={config.accent_color}
                          onChange={(e) => setConfig({...config, accent_color: e.target.value})}
                          className="w-10 h-10 rounded-lg cursor-pointer"
                        />
                        <Input
                          value={config.accent_color}
                          onChange={(e) => setConfig({...config, accent_color: e.target.value})}
                          className="input-duo flex-1"
                        />
                      </div>
                    </div>
                    <div>
                      <Label>Text Color</Label>
                      <div className="flex items-center gap-2">
                        <input
                          type="color"
                          value={config.text_color}
                          onChange={(e) => setConfig({...config, text_color: e.target.value})}
                          className="w-10 h-10 rounded-lg cursor-pointer"
                        />
                        <Input
                          value={config.text_color}
                          onChange={(e) => setConfig({...config, text_color: e.target.value})}
                          className="input-duo flex-1"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Preview */}
                  <div className="mt-4 p-4 rounded-xl border" style={{ backgroundColor: config.background_color }}>
                    <h4 className="font-bold mb-2" style={{ color: config.text_color }}>{config.platform_name}</h4>
                    <div className="flex gap-2">
                      <button className="px-4 py-2 rounded-lg text-white text-sm font-semibold" style={{ backgroundColor: config.primary_color }}>
                        Primary
                      </button>
                      <button className="px-4 py-2 rounded-lg text-white text-sm font-semibold" style={{ backgroundColor: config.secondary_color }}>
                        Secondary
                      </button>
                      <button className="px-4 py-2 rounded-lg text-white text-sm font-semibold" style={{ backgroundColor: config.accent_color }}>
                        Accent
                      </button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Options */}
            <Card className="bg-white border-2 rounded-2xl">
              <CardHeader>
                <CardTitle>Display Options</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Show "Powered by ProficientHub"</Label>
                      <p className="text-xs text-gray-500">Display attribution footer</p>
                    </div>
                    <Switch
                      checked={config.show_powered_by}
                      onCheckedChange={(v) => setConfig({...config, show_powered_by: v})}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Enable Dark Mode</Label>
                      <p className="text-xs text-gray-500">Allow users to switch themes</p>
                    </div>
                    <Switch
                      checked={config.enable_dark_mode}
                      onCheckedChange={(v) => setConfig({...config, enable_dark_mode: v})}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Typography Tab */}
          <TabsContent value="typography" className="space-y-6">
            <Card className="bg-white border-2 rounded-2xl">
              <CardHeader>
                <CardTitle>Font Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Body Font Family</Label>
                    <Select value={config.font_family} onValueChange={(v) => setConfig({...config, font_family: v})}>
                      <SelectTrigger className="input-duo">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Inter, system-ui, sans-serif">Inter (Default)</SelectItem>
                        <SelectItem value="'Poppins', sans-serif">Poppins</SelectItem>
                        <SelectItem value="'Roboto', sans-serif">Roboto</SelectItem>
                        <SelectItem value="'Open Sans', sans-serif">Open Sans</SelectItem>
                        <SelectItem value="'Lato', sans-serif">Lato</SelectItem>
                        <SelectItem value="'Montserrat', sans-serif">Montserrat</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Heading Font (optional)</Label>
                    <Input
                      value={config.heading_font}
                      onChange={(e) => setConfig({...config, heading_font: e.target.value})}
                      placeholder="Same as body font"
                      className="input-duo"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Layout Tab */}
          <TabsContent value="layout" className="space-y-6">
            <Card className="bg-white border-2 rounded-2xl">
              <CardHeader>
                <CardTitle>UI Style</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <Label>Border Radius</Label>
                    <Select value={config.border_radius} onValueChange={(v) => setConfig({...config, border_radius: v})}>
                      <SelectTrigger className="input-duo">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="0px">Square (0px)</SelectItem>
                        <SelectItem value="4px">Subtle (4px)</SelectItem>
                        <SelectItem value="8px">Rounded (8px)</SelectItem>
                        <SelectItem value="12px">More Rounded (12px)</SelectItem>
                        <SelectItem value="16px">Very Rounded (16px)</SelectItem>
                        <SelectItem value="24px">Pill (24px)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Button Style</Label>
                    <Select value={config.button_style} onValueChange={(v) => setConfig({...config, button_style: v})}>
                      <SelectTrigger className="input-duo">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="square">Square</SelectItem>
                        <SelectItem value="rounded">Rounded</SelectItem>
                        <SelectItem value="pill">Pill</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Card Style</Label>
                    <Select value={config.card_style} onValueChange={(v) => setConfig({...config, card_style: v})}>
                      <SelectTrigger className="input-duo">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="flat">Flat</SelectItem>
                        <SelectItem value="bordered">Bordered</SelectItem>
                        <SelectItem value="elevated">Elevated (Shadow)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Email Tab */}
          <TabsContent value="email" className="space-y-6">
            <Card className="bg-white border-2 rounded-2xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mail className="w-5 h-5" /> Email Branding
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>From Name</Label>
                    <Input
                      value={config.email_from_name}
                      onChange={(e) => setConfig({...config, email_from_name: e.target.value})}
                      placeholder="Your Academy"
                      className="input-duo"
                    />
                  </div>
                  <div>
                    <Label>Support Email</Label>
                    <Input
                      value={config.support_email}
                      onChange={(e) => setConfig({...config, support_email: e.target.value})}
                      placeholder="support@youracademy.com"
                      className="input-duo"
                    />
                  </div>
                </div>
                <div>
                  <Label>Email Footer Text</Label>
                  <Textarea
                    value={config.email_footer_text}
                    onChange={(e) => setConfig({...config, email_footer_text: e.target.value})}
                    placeholder="© 2025 Your Academy. All rights reserved."
                    className="input-duo"
                    rows={2}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Advanced Tab */}
          <TabsContent value="advanced" className="space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Social Links */}
              <Card className="bg-white border-2 rounded-2xl">
                <CardHeader>
                  <CardTitle>Social Media Links</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Website</Label>
                    <Input
                      value={config.website_url}
                      onChange={(e) => setConfig({...config, website_url: e.target.value})}
                      placeholder="https://youracademy.com"
                      className="input-duo"
                    />
                  </div>
                  <div>
                    <Label>Facebook</Label>
                    <Input
                      value={config.facebook_url}
                      onChange={(e) => setConfig({...config, facebook_url: e.target.value})}
                      placeholder="https://facebook.com/youracademy"
                      className="input-duo"
                    />
                  </div>
                  <div>
                    <Label>Instagram</Label>
                    <Input
                      value={config.instagram_url}
                      onChange={(e) => setConfig({...config, instagram_url: e.target.value})}
                      placeholder="https://instagram.com/youracademy"
                      className="input-duo"
                    />
                  </div>
                  <div>
                    <Label>LinkedIn</Label>
                    <Input
                      value={config.linkedin_url}
                      onChange={(e) => setConfig({...config, linkedin_url: e.target.value})}
                      placeholder="https://linkedin.com/company/youracademy"
                      className="input-duo"
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Custom CSS */}
              <Card className="bg-white border-2 rounded-2xl">
                <CardHeader>
                  <CardTitle>Custom CSS</CardTitle>
                </CardHeader>
                <CardContent>
                  <Textarea
                    value={config.custom_css}
                    onChange={(e) => setConfig({...config, custom_css: e.target.value})}
                    placeholder={`/* Add your custom CSS here */\n.btn-primary {\n  background: linear-gradient(...);\n}`}
                    className="input-duo font-mono text-sm"
                    rows={10}
                  />
                  <p className="text-xs text-gray-500 mt-2">Advanced: Add custom CSS to further customize the look</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default WhiteLabelSettings;
