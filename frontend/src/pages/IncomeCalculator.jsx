import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { 
  DollarSign, TrendingUp, Brain, BookOpen, Mic, GraduationCap,
  ArrowLeft, Calculator
} from 'lucide-react';

export default function IncomeCalculator() {
  const navigate = useNavigate();

  // Pricing configuration
  const [licensePricing, setLicensePricing] = useState({
    baseCostPerExam: 0.94,
    aiTutorCostPerMin: 0.06,
    writingTestCost: 0.05,
    speakingTestCost: 0.85,
    volumeMultipliers: {
      tier_100: 2.00,
      tier_500: 1.85,
      tier_1000: 1.72,
      tier_2000: 1.60,
      tier_5000: 1.50,
      tier_10000: 1.42,
      tier_100000: 1.35,
    },
    aiTutorPrices: {
      basic: 5.00,
      standard: 9.00,
      premium: 15.00,
      unlimited: 35.00,
    },
    writingTestPrice: 1.10,
    speakingTestPrice: 2.70,
    mockExamPrice: 2.20,
  });

  // Income Simulator State
  const [incomeSimulator, setIncomeSimulator] = useState({
    licenses: {
      plan_5: { quantity: 0, examsPerLicense: 5 },
      plan_10: { quantity: 100, examsPerLicense: 10 },
      plan_20: { quantity: 50, examsPerLicense: 20 },
      plan_40: { quantity: 20, examsPerLicense: 40 },
      plan_60: { quantity: 10, examsPerLicense: 60 },
      plan_100: { quantity: 5, examsPerLicense: 100 },
    },
    aiTutor: {
      basic: 50,
      standard: 80,
      premium: 30,
      unlimited: 10,
    },
    testPackages: {
      writing: 2000,
      speaking: 1000,
      mockExams: 500,
    },
  });

  const [incomeResults, setIncomeResults] = useState(null);

  // Calculate total income simulation
  const calculateIncomeSimulation = () => {
    const results = {
      licenses: { items: [], subtotalCost: 0, subtotalRevenue: 0, subtotalProfit: 0 },
      aiTutor: { items: [], subtotalCost: 0, subtotalRevenue: 0, subtotalProfit: 0 },
      testPackages: { items: [], subtotalCost: 0, subtotalRevenue: 0, subtotalProfit: 0 },
      grandTotal: { cost: 0, revenue: 0, profit: 0, margin: 0 },
    };

    const planDetails = {
      plan_5: { exams: 5, name: '5 Exams' },
      plan_10: { exams: 10, name: '10 Exams' },
      plan_20: { exams: 20, name: '20 Exams' },
      plan_40: { exams: 40, name: '40 Exams' },
      plan_60: { exams: 60, name: '60 Exams' },
      plan_100: { exams: 100, name: '100 Exams' },
    };

    Object.entries(incomeSimulator.licenses).forEach(([planId, data]) => {
      if (data.quantity > 0) {
        const plan = planDetails[planId];
        const costPerLicense = licensePricing.baseCostPerExam * plan.exams;
        
        let multiplier = licensePricing.volumeMultipliers.tier_100;
        if (data.quantity > 10000) multiplier = licensePricing.volumeMultipliers.tier_100000;
        else if (data.quantity > 5000) multiplier = licensePricing.volumeMultipliers.tier_10000;
        else if (data.quantity > 2000) multiplier = licensePricing.volumeMultipliers.tier_5000;
        else if (data.quantity > 1000) multiplier = licensePricing.volumeMultipliers.tier_2000;
        else if (data.quantity > 500) multiplier = licensePricing.volumeMultipliers.tier_1000;
        else if (data.quantity > 100) multiplier = licensePricing.volumeMultipliers.tier_500;

        const pricePerLicense = costPerLicense * multiplier;
        const totalCost = costPerLicense * data.quantity;
        const totalRevenue = pricePerLicense * data.quantity;
        const totalProfit = totalRevenue - totalCost;

        results.licenses.items.push({
          plan: plan.name,
          quantity: data.quantity,
          pricePerUnit: pricePerLicense,
          costPerUnit: costPerLicense,
          totalCost,
          totalRevenue,
          totalProfit,
          margin: ((totalProfit / totalRevenue) * 100).toFixed(1),
        });

        results.licenses.subtotalCost += totalCost;
        results.licenses.subtotalRevenue += totalRevenue;
        results.licenses.subtotalProfit += totalProfit;
      }
    });

    const aiTutorDetails = {
      basic: { minutes: 30, name: 'Basic (30 min)' },
      standard: { minutes: 60, name: 'Standard (60 min)' },
      premium: { minutes: 120, name: 'Premium (120 min)' },
      unlimited: { minutes: 300, name: 'Unlimited (300 min)' },
    };
    const aiCosts = { basic: 1.80, standard: 3.60, premium: 7.20, unlimited: 18.00 };

    Object.entries(incomeSimulator.aiTutor).forEach(([option, quantity]) => {
      if (quantity > 0) {
        const details = aiTutorDetails[option];
        const cost = aiCosts[option];
        const price = licensePricing.aiTutorPrices[option];
        const totalCost = cost * quantity;
        const totalRevenue = price * quantity;
        const totalProfit = totalRevenue - totalCost;

        results.aiTutor.items.push({
          option: details.name,
          quantity,
          pricePerUnit: price,
          costPerUnit: cost,
          totalCost,
          totalRevenue,
          totalProfit,
          margin: ((totalProfit / totalRevenue) * 100).toFixed(1),
        });

        results.aiTutor.subtotalCost += totalCost;
        results.aiTutor.subtotalRevenue += totalRevenue;
        results.aiTutor.subtotalProfit += totalProfit;
      }
    });

    const testPackageDetails = [
      { id: 'writing', name: 'Writing Tests', cost: licensePricing.writingTestCost, price: licensePricing.writingTestPrice },
      { id: 'speaking', name: 'Speaking Tests', cost: licensePricing.speakingTestCost, price: licensePricing.speakingTestPrice },
      { id: 'mockExams', name: 'Mock Exams', cost: licensePricing.baseCostPerExam, price: licensePricing.mockExamPrice },
    ];

    testPackageDetails.forEach((pkg) => {
      const quantity = incomeSimulator.testPackages[pkg.id];
      if (quantity > 0) {
        const totalCost = pkg.cost * quantity;
        const totalRevenue = pkg.price * quantity;
        const totalProfit = totalRevenue - totalCost;

        results.testPackages.items.push({
          name: pkg.name,
          quantity,
          pricePerUnit: pkg.price,
          costPerUnit: pkg.cost,
          totalCost,
          totalRevenue,
          totalProfit,
          margin: ((totalProfit / totalRevenue) * 100).toFixed(1),
        });

        results.testPackages.subtotalCost += totalCost;
        results.testPackages.subtotalRevenue += totalRevenue;
        results.testPackages.subtotalProfit += totalProfit;
      }
    });

    results.grandTotal.cost = results.licenses.subtotalCost + results.aiTutor.subtotalCost + results.testPackages.subtotalCost;
    results.grandTotal.revenue = results.licenses.subtotalRevenue + results.aiTutor.subtotalRevenue + results.testPackages.subtotalRevenue;
    results.grandTotal.profit = results.licenses.subtotalProfit + results.aiTutor.subtotalProfit + results.testPackages.subtotalProfit;
    results.grandTotal.margin = results.grandTotal.revenue > 0 
      ? ((results.grandTotal.profit / results.grandTotal.revenue) * 100).toFixed(1) 
      : 0;

    setIncomeResults(results);
  };

  useEffect(() => {
    calculateIncomeSimulation();
  }, [incomeSimulator, licensePricing]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-lg border-b border-white/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-green-500 to-blue-500 flex items-center justify-center">
                <Calculator className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Income Simulator</h1>
                <p className="text-sm text-gray-300">ProficientHub - Revenue Projection Tool</p>
              </div>
            </div>
            <Button 
              variant="outline" 
              className="text-white border-white/30 hover:bg-white/10"
              onClick={() => navigate('/admin')}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Admin
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        
        {/* GRAND TOTAL - At the top for visibility */}
        {incomeResults && (
          <Card className="bg-gradient-to-r from-green-600 to-blue-600 text-white border-0 shadow-2xl">
            <CardContent className="p-8">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
                <DollarSign className="w-8 h-8 text-yellow-300" />
                TOTAL PROJECTED INCOME
              </h2>
              <div className="grid md:grid-cols-4 gap-6">
                <div className="bg-white/20 rounded-2xl p-6 text-center backdrop-blur">
                  <p className="text-white/80 text-sm mb-2">Total Cost</p>
                  <p className="text-3xl font-bold text-red-200">
                    ${incomeResults.grandTotal.cost.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                  </p>
                </div>
                <div className="bg-white/20 rounded-2xl p-6 text-center backdrop-blur">
                  <p className="text-white/80 text-sm mb-2">Total Revenue</p>
                  <p className="text-3xl font-bold text-blue-200">
                    ${incomeResults.grandTotal.revenue.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                  </p>
                </div>
                <div className="bg-white/20 rounded-2xl p-6 text-center backdrop-blur">
                  <p className="text-white/80 text-sm mb-2">Total Profit</p>
                  <p className="text-4xl font-bold text-green-200">
                    ${incomeResults.grandTotal.profit.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                  </p>
                </div>
                <div className="bg-white/20 rounded-2xl p-6 text-center backdrop-blur">
                  <p className="text-white/80 text-sm mb-2">Overall Margin</p>
                  <p className="text-3xl font-bold text-yellow-200">
                    {incomeResults.grandTotal.margin}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Input Section */}
        <Card className="bg-white/10 backdrop-blur border-white/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-green-400" />
              Adjust Sales Volume to Simulate Income
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-8">
            
            {/* License Sales Input */}
            <div>
              <h4 className="font-bold text-white mb-4 flex items-center gap-2">
                <GraduationCap className="w-5 h-5 text-blue-400" />
                License Sales by Plan
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {Object.entries(incomeSimulator.licenses).map(([planId, data]) => (
                  <div key={planId} className="bg-white/10 border border-white/20 rounded-xl p-4 text-center">
                    <Label className="text-xs text-gray-300 block mb-2">
                      {planId.replace('plan_', '')} Exams/License
                    </Label>
                    <input
                      type="number"
                      min="0"
                      value={data.quantity}
                      onChange={(e) => setIncomeSimulator(prev => ({
                        ...prev,
                        licenses: {
                          ...prev.licenses,
                          [planId]: { ...data, quantity: parseInt(e.target.value) || 0 }
                        }
                      }))}
                      className="w-full text-center border-0 rounded-lg px-3 py-2 font-bold text-lg bg-white text-gray-900"
                    />
                    <span className="text-xs text-gray-400">licenses</span>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Tutor Add-ons Input */}
            <div>
              <h4 className="font-bold text-white mb-4 flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-400" />
                AI Tutor Add-ons Sold
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { id: 'basic', label: 'Basic (30 min)' },
                  { id: 'standard', label: 'Standard (60 min)' },
                  { id: 'premium', label: 'Premium (120 min)' },
                  { id: 'unlimited', label: 'Unlimited (300 min)' },
                ].map((option) => (
                  <div key={option.id} className="bg-white/10 border border-white/20 rounded-xl p-4 text-center">
                    <Label className="text-xs text-gray-300 block mb-2">{option.label}</Label>
                    <input
                      type="number"
                      min="0"
                      value={incomeSimulator.aiTutor[option.id]}
                      onChange={(e) => setIncomeSimulator(prev => ({
                        ...prev,
                        aiTutor: {
                          ...prev.aiTutor,
                          [option.id]: parseInt(e.target.value) || 0
                        }
                      }))}
                      className="w-full text-center border-0 rounded-lg px-3 py-2 font-bold text-lg bg-white text-gray-900"
                    />
                    <span className="text-xs text-gray-400">units</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Test Packages Input */}
            <div>
              <h4 className="font-bold text-white mb-4 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-orange-400" />
                Test Packages Sold
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white/10 border border-white/20 rounded-xl p-4 text-center">
                  <Label className="text-xs text-gray-300 block mb-2">Writing Tests</Label>
                  <input
                    type="number"
                    min="0"
                    value={incomeSimulator.testPackages.writing}
                    onChange={(e) => setIncomeSimulator(prev => ({
                      ...prev,
                      testPackages: { ...prev.testPackages, writing: parseInt(e.target.value) || 0 }
                    }))}
                    className="w-full text-center border-0 rounded-lg px-3 py-2 font-bold text-lg bg-white text-gray-900"
                  />
                  <span className="text-xs text-gray-400">tests</span>
                </div>
                <div className="bg-white/10 border border-white/20 rounded-xl p-4 text-center">
                  <Label className="text-xs text-gray-300 block mb-2">Speaking Tests</Label>
                  <input
                    type="number"
                    min="0"
                    value={incomeSimulator.testPackages.speaking}
                    onChange={(e) => setIncomeSimulator(prev => ({
                      ...prev,
                      testPackages: { ...prev.testPackages, speaking: parseInt(e.target.value) || 0 }
                    }))}
                    className="w-full text-center border-0 rounded-lg px-3 py-2 font-bold text-lg bg-white text-gray-900"
                  />
                  <span className="text-xs text-gray-400">tests</span>
                </div>
                <div className="bg-white/10 border border-white/20 rounded-xl p-4 text-center">
                  <Label className="text-xs text-gray-300 block mb-2">Mock Exams</Label>
                  <input
                    type="number"
                    min="0"
                    value={incomeSimulator.testPackages.mockExams}
                    onChange={(e) => setIncomeSimulator(prev => ({
                      ...prev,
                      testPackages: { ...prev.testPackages, mockExams: parseInt(e.target.value) || 0 }
                    }))}
                    className="w-full text-center border-0 rounded-lg px-3 py-2 font-bold text-lg bg-white text-gray-900"
                  />
                  <span className="text-xs text-gray-400">exams</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results Tables */}
        {incomeResults && (
          <div className="space-y-6">
            {/* Licenses Results */}
            {incomeResults.licenses.items.length > 0 && (
              <Card className="bg-white border-0 shadow-xl overflow-hidden">
                <div className="bg-blue-600 px-6 py-4 flex justify-between items-center">
                  <span className="text-white font-bold text-lg flex items-center gap-2">
                    <GraduationCap className="w-5 h-5" />
                    License Sales Breakdown
                  </span>
                  <span className="text-green-200 font-bold text-xl">
                    Profit: ${incomeResults.licenses.subtotalProfit.toLocaleString('en-US', {minimumFractionDigits: 2})}
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left py-3 px-4 font-semibold">Plan</th>
                        <th className="text-center py-3 px-4 font-semibold">Qty</th>
                        <th className="text-center py-3 px-4 font-semibold">Unit Price</th>
                        <th className="text-right py-3 px-4 font-semibold text-red-600">Total Cost</th>
                        <th className="text-right py-3 px-4 font-semibold text-blue-600">Total Revenue</th>
                        <th className="text-right py-3 px-4 font-semibold text-green-600">Profit</th>
                        <th className="text-center py-3 px-4 font-semibold">Margin</th>
                      </tr>
                    </thead>
                    <tbody>
                      {incomeResults.licenses.items.map((item, idx) => (
                        <tr key={idx} className="border-t hover:bg-gray-50">
                          <td className="py-3 px-4 font-medium">{item.plan}</td>
                          <td className="text-center py-3 px-4">{item.quantity.toLocaleString()}</td>
                          <td className="text-center py-3 px-4">${item.pricePerUnit.toFixed(2)}</td>
                          <td className="text-right py-3 px-4 text-red-600">${item.totalCost.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                          <td className="text-right py-3 px-4 text-blue-600">${item.totalRevenue.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                          <td className="text-right py-3 px-4 text-green-600 font-bold">${item.totalProfit.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                          <td className="text-center py-3 px-4">
                            <Badge className="bg-green-100 text-green-700">{item.margin}%</Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot className="bg-blue-50 font-bold">
                      <tr>
                        <td colSpan="3" className="py-3 px-4">Subtotal Licenses</td>
                        <td className="text-right py-3 px-4 text-red-600">${incomeResults.licenses.subtotalCost.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                        <td className="text-right py-3 px-4 text-blue-600">${incomeResults.licenses.subtotalRevenue.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                        <td className="text-right py-3 px-4 text-green-600">${incomeResults.licenses.subtotalProfit.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                        <td></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </Card>
            )}

            {/* AI Tutor Results */}
            {incomeResults.aiTutor.items.length > 0 && (
              <Card className="bg-white border-0 shadow-xl overflow-hidden">
                <div className="bg-purple-600 px-6 py-4 flex justify-between items-center">
                  <span className="text-white font-bold text-lg flex items-center gap-2">
                    <Brain className="w-5 h-5" />
                    AI Tutor Add-ons Breakdown
                  </span>
                  <span className="text-green-200 font-bold text-xl">
                    Profit: ${incomeResults.aiTutor.subtotalProfit.toLocaleString('en-US', {minimumFractionDigits: 2})}
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left py-3 px-4 font-semibold">Option</th>
                        <th className="text-center py-3 px-4 font-semibold">Qty</th>
                        <th className="text-center py-3 px-4 font-semibold">Unit Price</th>
                        <th className="text-right py-3 px-4 font-semibold text-red-600">Total Cost</th>
                        <th className="text-right py-3 px-4 font-semibold text-purple-600">Total Revenue</th>
                        <th className="text-right py-3 px-4 font-semibold text-green-600">Profit</th>
                        <th className="text-center py-3 px-4 font-semibold">Margin</th>
                      </tr>
                    </thead>
                    <tbody>
                      {incomeResults.aiTutor.items.map((item, idx) => (
                        <tr key={idx} className="border-t hover:bg-gray-50">
                          <td className="py-3 px-4 font-medium">{item.option}</td>
                          <td className="text-center py-3 px-4">{item.quantity.toLocaleString()}</td>
                          <td className="text-center py-3 px-4">${item.pricePerUnit.toFixed(2)}</td>
                          <td className="text-right py-3 px-4 text-red-600">${item.totalCost.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                          <td className="text-right py-3 px-4 text-purple-600">${item.totalRevenue.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                          <td className="text-right py-3 px-4 text-green-600 font-bold">${item.totalProfit.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                          <td className="text-center py-3 px-4">
                            <Badge className="bg-purple-100 text-purple-700">{item.margin}%</Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot className="bg-purple-50 font-bold">
                      <tr>
                        <td colSpan="3" className="py-3 px-4">Subtotal AI Tutor</td>
                        <td className="text-right py-3 px-4 text-red-600">${incomeResults.aiTutor.subtotalCost.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                        <td className="text-right py-3 px-4 text-purple-600">${incomeResults.aiTutor.subtotalRevenue.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                        <td className="text-right py-3 px-4 text-green-600">${incomeResults.aiTutor.subtotalProfit.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                        <td></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </Card>
            )}

            {/* Test Packages Results */}
            {incomeResults.testPackages.items.length > 0 && (
              <Card className="bg-white border-0 shadow-xl overflow-hidden">
                <div className="bg-orange-500 px-6 py-4 flex justify-between items-center">
                  <span className="text-white font-bold text-lg flex items-center gap-2">
                    <BookOpen className="w-5 h-5" />
                    Test Packages Breakdown
                  </span>
                  <span className="text-green-200 font-bold text-xl">
                    Profit: ${incomeResults.testPackages.subtotalProfit.toLocaleString('en-US', {minimumFractionDigits: 2})}
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left py-3 px-4 font-semibold">Package</th>
                        <th className="text-center py-3 px-4 font-semibold">Qty</th>
                        <th className="text-center py-3 px-4 font-semibold">Unit Price</th>
                        <th className="text-right py-3 px-4 font-semibold text-red-600">Total Cost</th>
                        <th className="text-right py-3 px-4 font-semibold text-orange-600">Total Revenue</th>
                        <th className="text-right py-3 px-4 font-semibold text-green-600">Profit</th>
                        <th className="text-center py-3 px-4 font-semibold">Margin</th>
                      </tr>
                    </thead>
                    <tbody>
                      {incomeResults.testPackages.items.map((item, idx) => (
                        <tr key={idx} className="border-t hover:bg-gray-50">
                          <td className="py-3 px-4 font-medium">{item.name}</td>
                          <td className="text-center py-3 px-4">{item.quantity.toLocaleString()}</td>
                          <td className="text-center py-3 px-4">${item.pricePerUnit.toFixed(2)}</td>
                          <td className="text-right py-3 px-4 text-red-600">${item.totalCost.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                          <td className="text-right py-3 px-4 text-orange-600">${item.totalRevenue.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                          <td className="text-right py-3 px-4 text-green-600 font-bold">${item.totalProfit.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                          <td className="text-center py-3 px-4">
                            <Badge className="bg-orange-100 text-orange-700">{item.margin}%</Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot className="bg-orange-50 font-bold">
                      <tr>
                        <td colSpan="3" className="py-3 px-4">Subtotal Test Packages</td>
                        <td className="text-right py-3 px-4 text-red-600">${incomeResults.testPackages.subtotalCost.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                        <td className="text-right py-3 px-4 text-orange-600">${incomeResults.testPackages.subtotalRevenue.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                        <td className="text-right py-3 px-4 text-green-600">${incomeResults.testPackages.subtotalProfit.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                        <td></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </Card>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="text-center text-gray-400 text-sm py-8">
          <p>Projection based on current pricing configuration. Adjust volumes above to simulate different scenarios.</p>
          <p className="mt-2">© 2025 ProficientHub - All rights reserved</p>
        </div>
      </div>
    </div>
  );
}
