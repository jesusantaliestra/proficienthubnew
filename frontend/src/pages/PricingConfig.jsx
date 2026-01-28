import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Switch } from '../components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  DollarSign, Package, Smartphone, Zap, Save, Plus, Trash2,
  ArrowLeft, RefreshCw, CheckCircle, AlertTriangle
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

const PricingConfig = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState(null);
  const [activeTab, setActiveTab] = useState('exam-plans');

  const token = localStorage.getItem('token');

  const fetchConfig = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/pricing/config`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConfig(response.data);
    } catch (error) {
      toast.error('Failed to load pricing configuration');
      if (error.response?.status === 403) {
        navigate('/admin');
      }
    } finally {
      setLoading(false);
    }
  }, [token, navigate]);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  const saveConfig = async () => {
    try {
      setSaving(true);
      await axios.put(`${API_URL}/pricing/config`, config, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Pricing configuration saved!');
    } catch (error) {
      toast.error('Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const updateExamPlan = (index, field, value) => {
    const newPlans = [...config.exam_plans];
    newPlans[index] = { ...newPlans[index], [field]: value };
    setConfig({ ...config, exam_plans: newPlans });
  };

  const updateVolumeTier = (index, field, value) => {
    const newTiers = [...config.volume_tiers];
    newTiers[index] = { ...newTiers[index], [field]: value };
    setConfig({ ...config, volume_tiers: newTiers });
  };

  const updateMobileAppTier = (index, field, value) => {
    const newTiers = [...config.mobile_app_pricing];
    newTiers[index] = { ...newTiers[index], [field]: value };
    setConfig({ ...config, mobile_app_pricing: newTiers });
  };

  const updateCreditPackage = (index, field, value) => {
    const newPackages = [...config.credit_packages];
    newPackages[index] = { ...newPackages[index], [field]: value };
    setConfig({ ...config, credit_packages: newPackages });
  };

  const addNewPlan = (type) => {
    const newItem = type === 'exam_plans' 
      ? { plan_id: `plan_new_${Date.now()}`, exams: 10, base_cost: 10, price: 20, label: 'New Plan', enabled: true }
      : type === 'credit_packages'
      ? { package_id: `pkg_new_${Date.now()}`, credits: 100, price: 10, bonus_credits: 0, label: 'New Package', popular: false, enabled: true }
      : null;
    
    if (newItem) {
      setConfig({ ...config, [type]: [...config[type], newItem] });
    }
  };

  const removePlan = (type, index) => {
    const newArray = config[type].filter((_, i) => i !== index);
    setConfig({ ...config, [type]: newArray });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => navigate('/superadmin')}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Pricing Configuration</h1>
                <p className="text-gray-500 text-sm">Manage all platform pricing</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm" onClick={fetchConfig}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              <Button onClick={saveConfig} disabled={saving} className="bg-purple-600 hover:bg-purple-700">
                {saving ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                ) : (
                  <Save className="w-4 h-4 mr-2" />
                )}
                Save Changes
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8" data-testid="pricing-config">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-6">
            <TabsTrigger value="exam-plans" className="flex items-center gap-2">
              <Package className="w-4 h-4" />
              Exam Plans
            </TabsTrigger>
            <TabsTrigger value="volume-tiers" className="flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              Volume Discounts
            </TabsTrigger>
            <TabsTrigger value="mobile-app" className="flex items-center gap-2">
              <Smartphone className="w-4 h-4" />
              Mobile App
            </TabsTrigger>
            <TabsTrigger value="credits" className="flex items-center gap-2">
              <Zap className="w-4 h-4" />
              AI Credits
            </TabsTrigger>
          </TabsList>

          {/* Exam Plans */}
          <TabsContent value="exam-plans">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Exam Plans</CardTitle>
                    <CardDescription>Configure mock exam packages</CardDescription>
                  </div>
                  <Button size="sm" onClick={() => addNewPlan('exam_plans')}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Plan
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {config?.exam_plans?.map((plan, index) => (
                    <div key={plan.plan_id} className="p-4 border rounded-lg bg-gray-50">
                      <div className="grid grid-cols-6 gap-4 items-center">
                        <div>
                          <label className="text-xs text-gray-500">Plan ID</label>
                          <Input
                            value={plan.plan_id}
                            onChange={(e) => updateExamPlan(index, 'plan_id', e.target.value)}
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500">Exams</label>
                          <Input
                            type="number"
                            value={plan.exams}
                            onChange={(e) => updateExamPlan(index, 'exams', parseInt(e.target.value))}
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500">Base Cost ($)</label>
                          <Input
                            type="number"
                            step="0.01"
                            value={plan.base_cost}
                            onChange={(e) => updateExamPlan(index, 'base_cost', parseFloat(e.target.value))}
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500">Price ($)</label>
                          <Input
                            type="number"
                            step="0.01"
                            value={plan.price}
                            onChange={(e) => updateExamPlan(index, 'price', parseFloat(e.target.value))}
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500">Label</label>
                          <Input
                            value={plan.label}
                            onChange={(e) => updateExamPlan(index, 'label', e.target.value)}
                            className="mt-1"
                          />
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="flex items-center gap-2">
                            <Switch
                              checked={plan.enabled}
                              onCheckedChange={(v) => updateExamPlan(index, 'enabled', v)}
                            />
                            <span className="text-sm">Enabled</span>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-500 hover:text-red-700"
                            onClick={() => removePlan('exam_plans', index)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="mt-2 text-sm text-gray-500">
                        Margin: ${(plan.price - plan.base_cost).toFixed(2)} ({((plan.price - plan.base_cost) / plan.price * 100).toFixed(0)}%)
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Volume Tiers */}
          <TabsContent value="volume-tiers">
            <Card>
              <CardHeader>
                <CardTitle>Volume Discount Tiers</CardTitle>
                <CardDescription>Configure pricing discounts based on license volume</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {config?.volume_tiers?.map((tier, index) => (
                    <div key={tier.tier_id} className="p-4 border rounded-lg bg-gray-50">
                      <div className="grid grid-cols-6 gap-4 items-center">
                        <div>
                          <label className="text-xs text-gray-500">Tier ID</label>
                          <Input value={tier.tier_id} disabled className="mt-1 bg-gray-100" />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500">Min Licenses</label>
                          <Input
                            type="number"
                            value={tier.min_licenses}
                            onChange={(e) => updateVolumeTier(index, 'min_licenses', parseInt(e.target.value))}
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500">Max Licenses</label>
                          <Input
                            type="number"
                            value={tier.max_licenses}
                            onChange={(e) => updateVolumeTier(index, 'max_licenses', parseInt(e.target.value))}
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500">Price Multiplier</label>
                          <Input
                            type="number"
                            step="0.01"
                            value={tier.price_multiplier}
                            onChange={(e) => updateVolumeTier(index, 'price_multiplier', parseFloat(e.target.value))}
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500">Discount %</label>
                          <Input
                            type="number"
                            value={tier.discount_percent}
                            onChange={(e) => updateVolumeTier(index, 'discount_percent', parseInt(e.target.value))}
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500">Label</label>
                          <Input
                            value={tier.label}
                            onChange={(e) => updateVolumeTier(index, 'label', e.target.value)}
                            className="mt-1"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Mobile App Pricing */}
          <TabsContent value="mobile-app">
            <Card>
              <CardHeader>
                <CardTitle>Mobile App Pricing Tiers</CardTitle>
                <CardDescription>Configure iOS/Android app pricing options</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {config?.mobile_app_pricing?.map((tier, index) => (
                    <div key={tier.tier_id} className={`p-6 border-2 rounded-xl ${
                      tier.tier_id === 'premium' ? 'border-purple-500 bg-purple-50' :
                      tier.tier_id === 'enterprise' ? 'border-amber-500 bg-amber-50' :
                      'border-gray-200 bg-white'
                    }`}>
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <Badge className={
                            tier.tier_id === 'premium' ? 'bg-purple-500' :
                            tier.tier_id === 'enterprise' ? 'bg-amber-500' :
                            'bg-gray-500'
                          }>
                            {tier.tier_id.toUpperCase()}
                          </Badge>
                        </div>
                        <Switch
                          checked={tier.enabled}
                          onCheckedChange={(v) => updateMobileAppTier(index, 'enabled', v)}
                        />
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                          <label className="text-xs text-gray-500 font-medium">Name</label>
                          <Input
                            value={tier.name}
                            onChange={(e) => updateMobileAppTier(index, 'name', e.target.value)}
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 font-medium">Description</label>
                          <Input
                            value={tier.description}
                            onChange={(e) => updateMobileAppTier(index, 'description', e.target.value)}
                            className="mt-1"
                          />
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                          <label className="text-xs text-gray-500 font-medium">Setup Fee ($)</label>
                          <Input
                            type="number"
                            value={tier.setup_fee}
                            onChange={(e) => updateMobileAppTier(index, 'setup_fee', parseFloat(e.target.value))}
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 font-medium">Monthly Fee ($)</label>
                          <Input
                            type="number"
                            value={tier.monthly_fee}
                            onChange={(e) => updateMobileAppTier(index, 'monthly_fee', parseFloat(e.target.value))}
                            className="mt-1"
                          />
                        </div>
                      </div>
                      
                      <div>
                        <label className="text-xs text-gray-500 font-medium">Features (one per line)</label>
                        <textarea
                          value={tier.features?.join('\n') || ''}
                          onChange={(e) => updateMobileAppTier(index, 'features', e.target.value.split('\n').filter(f => f.trim()))}
                          className="mt-1 w-full p-3 border rounded-lg text-sm"
                          rows={4}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Credit Packages */}
          <TabsContent value="credits">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>AI Credit Packages</CardTitle>
                    <CardDescription>Configure credit packages for institutions</CardDescription>
                  </div>
                  <Button size="sm" onClick={() => addNewPlan('credit_packages')}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Package
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {config?.credit_packages?.map((pkg, index) => (
                    <div key={pkg.package_id} className={`p-4 border-2 rounded-xl ${
                      pkg.popular ? 'border-purple-500 bg-purple-50' : 'border-gray-200'
                    }`}>
                      <div className="flex items-center justify-between mb-4">
                        <Input
                          value={pkg.label}
                          onChange={(e) => updateCreditPackage(index, 'label', e.target.value)}
                          className="font-semibold text-lg border-none bg-transparent p-0 h-auto"
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-500"
                          onClick={() => removePlan('credit_packages', index)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                      
                      <div className="space-y-3">
                        <div className="flex items-center gap-2">
                          <Zap className="w-4 h-4 text-purple-500" />
                          <Input
                            type="number"
                            value={pkg.credits}
                            onChange={(e) => updateCreditPackage(index, 'credits', parseInt(e.target.value))}
                            className="w-24"
                          />
                          <span className="text-sm text-gray-500">credits</span>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          <DollarSign className="w-4 h-4 text-green-500" />
                          <Input
                            type="number"
                            step="0.01"
                            value={pkg.price}
                            onChange={(e) => updateCreditPackage(index, 'price', parseFloat(e.target.value))}
                            className="w-24"
                          />
                        </div>
                        
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-500">Bonus:</span>
                          <Input
                            type="number"
                            value={pkg.bonus_credits}
                            onChange={(e) => updateCreditPackage(index, 'bonus_credits', parseInt(e.target.value))}
                            className="w-20"
                          />
                        </div>
                        
                        <div className="flex items-center gap-4 pt-2 border-t">
                          <label className="flex items-center gap-2 text-sm">
                            <Switch
                              checked={pkg.popular}
                              onCheckedChange={(v) => updateCreditPackage(index, 'popular', v)}
                            />
                            Popular
                          </label>
                          <label className="flex items-center gap-2 text-sm">
                            <Switch
                              checked={pkg.enabled}
                              onCheckedChange={(v) => updateCreditPackage(index, 'enabled', v)}
                            />
                            Enabled
                          </label>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default PricingConfig;
