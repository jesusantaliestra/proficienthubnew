import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
  ArrowLeft, FileText, DollarSign, TrendingUp, TrendingDown,
  CreditCard, Users, Calendar, Filter, Download, Plus,
  CheckCircle, Clock, AlertCircle, BarChart3, PieChart,
  Building2, Receipt, Wallet, ChevronRight
} from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function ERPDashboard() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [invoices, setInvoices] = useState([]);
  const [invoiceStats, setInvoiceStats] = useState(null);
  const [subscriptionMetrics, setSubscriptionMetrics] = useState(null);
  const [chartOfAccounts, setChartOfAccounts] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch invoices
      const invoicesRes = await fetch(`${API_URL}/api/erp/invoices?page=1&per_page=10`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const invoicesData = await invoicesRes.json();
      setInvoices(invoicesData.invoices || []);

      // Fetch invoice stats
      const statsRes = await fetch(`${API_URL}/api/erp/invoices/stats/summary?period=month`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const statsData = await statsRes.json();
      setInvoiceStats(statsData);

      // Fetch MRR metrics
      const mrrRes = await fetch(`${API_URL}/api/erp/subscriptions/metrics/mrr`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const mrrData = await mrrRes.json();
      setSubscriptionMetrics(mrrData);

      // Fetch chart of accounts
      const coaRes = await fetch(`${API_URL}/api/erp/accounting/chart-of-accounts`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const coaData = await coaRes.json();
      setChartOfAccounts(coaData);

    } catch (error) {
      console.error('Error fetching ERP data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount || 0);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'paid': return 'text-green-400 bg-green-500/20';
      case 'sent': return 'text-blue-400 bg-blue-500/20';
      case 'overdue': return 'text-red-400 bg-red-500/20';
      case 'draft': return 'text-slate-400 bg-slate-500/20';
      default: return 'text-slate-400 bg-slate-500/20';
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'invoices', label: 'Invoices', icon: FileText },
    { id: 'subscriptions', label: 'Subscriptions', icon: CreditCard },
    { id: 'accounting', label: 'Accounting', icon: Receipt }
  ];

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
                <Building2 className="w-6 h-6 text-emerald-400" />
                ERP Dashboard
              </h1>
              <p className="text-slate-400 text-sm mt-1">Financial management and billing</p>
            </div>
          </div>
          <Button className="bg-emerald-600 hover:bg-emerald-700">
            <Plus className="w-4 h-4 mr-2" /> New Invoice
          </Button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-emerald-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          </div>
        ) : (
          <>
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <Card className="bg-slate-900 border-slate-800">
                    <CardContent className="p-5">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-slate-400 text-sm">Monthly Revenue</p>
                          <p className="text-2xl font-bold text-white mt-1">
                            {formatCurrency(subscriptionMetrics?.current_mrr || invoiceStats?.totals?.collected || 0)}
                          </p>
                        </div>
                        <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                          <DollarSign className="w-6 h-6 text-emerald-400" />
                        </div>
                      </div>
                      <div className="flex items-center gap-1 mt-2 text-sm">
                        <TrendingUp className="w-4 h-4 text-green-400" />
                        <span className="text-green-400">+12%</span>
                        <span className="text-slate-500">vs last month</span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-slate-900 border-slate-800">
                    <CardContent className="p-5">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-slate-400 text-sm">ARR</p>
                          <p className="text-2xl font-bold text-white mt-1">
                            {formatCurrency(subscriptionMetrics?.current_arr || 0)}
                          </p>
                        </div>
                        <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                          <TrendingUp className="w-6 h-6 text-blue-400" />
                        </div>
                      </div>
                      <p className="text-slate-500 text-sm mt-2">
                        {subscriptionMetrics?.active_subscriptions || 0} active subscriptions
                      </p>
                    </CardContent>
                  </Card>

                  <Card className="bg-slate-900 border-slate-800">
                    <CardContent className="p-5">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-slate-400 text-sm">Outstanding</p>
                          <p className="text-2xl font-bold text-white mt-1">
                            {formatCurrency(invoiceStats?.totals?.outstanding || 0)}
                          </p>
                        </div>
                        <div className="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center">
                          <Clock className="w-6 h-6 text-amber-400" />
                        </div>
                      </div>
                      <p className="text-slate-500 text-sm mt-2">
                        {invoiceStats?.by_status?.sent?.count || 0} pending invoices
                      </p>
                    </CardContent>
                  </Card>

                  <Card className="bg-slate-900 border-slate-800">
                    <CardContent className="p-5">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-slate-400 text-sm">Avg MRR/Customer</p>
                          <p className="text-2xl font-bold text-white mt-1">
                            {formatCurrency(subscriptionMetrics?.avg_mrr_per_subscription || 0)}
                          </p>
                        </div>
                        <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
                          <Users className="w-6 h-6 text-purple-400" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Revenue by Status */}
                {invoiceStats?.by_status && (
                  <Card className="bg-slate-900 border-slate-800">
                    <CardHeader>
                      <CardTitle className="text-white text-lg">Invoice Status Distribution</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {Object.entries(invoiceStats.by_status).map(([status, data]) => (
                          <div key={status} className="p-4 bg-slate-800 rounded-lg">
                            <div className="flex items-center gap-2 mb-2">
                              <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(status)}`}>
                                {status.toUpperCase()}
                              </span>
                            </div>
                            <p className="text-2xl font-bold text-white">{data.count}</p>
                            <p className="text-slate-400 text-sm">{formatCurrency(data.total)}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* MRR by Plan */}
                {subscriptionMetrics?.mrr_by_plan && Object.keys(subscriptionMetrics.mrr_by_plan).length > 0 && (
                  <Card className="bg-slate-900 border-slate-800">
                    <CardHeader>
                      <CardTitle className="text-white text-lg">MRR by Plan</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {Object.entries(subscriptionMetrics.mrr_by_plan).map(([plan, data]) => {
                          const percentage = (data.mrr / subscriptionMetrics.current_mrr * 100) || 0;
                          return (
                            <div key={plan}>
                              <div className="flex justify-between text-sm mb-1">
                                <span className="text-white">{plan}</span>
                                <span className="text-slate-400">
                                  {formatCurrency(data.mrr)} ({data.count} subs)
                                </span>
                              </div>
                              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                                <div 
                                  className="h-full bg-emerald-500 rounded-full transition-all"
                                  style={{ width: `${percentage}%` }}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}

            {/* Invoices Tab */}
            {activeTab === 'invoices' && (
              <div className="space-y-4">
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle className="text-white">Recent Invoices</CardTitle>
                    <Button size="sm" variant="ghost" className="text-slate-400">
                      <Filter className="w-4 h-4 mr-2" /> Filter
                    </Button>
                  </CardHeader>
                  <CardContent>
                    {invoices.length === 0 ? (
                      <div className="text-center py-12">
                        <FileText className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                        <p className="text-slate-400">No invoices yet</p>
                        <Button className="mt-4 bg-emerald-600 hover:bg-emerald-700">
                          <Plus className="w-4 h-4 mr-2" /> Create First Invoice
                        </Button>
                      </div>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="text-left border-b border-slate-800">
                              <th className="pb-3 text-slate-400 font-medium text-sm">Invoice #</th>
                              <th className="pb-3 text-slate-400 font-medium text-sm">Customer</th>
                              <th className="pb-3 text-slate-400 font-medium text-sm">Amount</th>
                              <th className="pb-3 text-slate-400 font-medium text-sm">Status</th>
                              <th className="pb-3 text-slate-400 font-medium text-sm">Due Date</th>
                              <th className="pb-3 text-slate-400 font-medium text-sm"></th>
                            </tr>
                          </thead>
                          <tbody>
                            {invoices.map(invoice => (
                              <tr key={invoice.id} className="border-b border-slate-800/50">
                                <td className="py-4 text-white font-mono text-sm">{invoice.invoice_number}</td>
                                <td className="py-4 text-white">{invoice.customer_name}</td>
                                <td className="py-4 text-white">{formatCurrency(invoice.totals?.total, invoice.currency)}</td>
                                <td className="py-4">
                                  <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(invoice.status)}`}>
                                    {invoice.status}
                                  </span>
                                </td>
                                <td className="py-4 text-slate-400 text-sm">
                                  {new Date(invoice.due_date).toLocaleDateString()}
                                </td>
                                <td className="py-4">
                                  <Button size="sm" variant="ghost" className="text-slate-400">
                                    <ChevronRight className="w-4 h-4" />
                                  </Button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Subscriptions Tab */}
            {activeTab === 'subscriptions' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card className="bg-slate-900 border-slate-800">
                    <CardContent className="p-5">
                      <p className="text-slate-400 text-sm">Current MRR</p>
                      <p className="text-3xl font-bold text-white mt-1">
                        {formatCurrency(subscriptionMetrics?.current_mrr || 0)}
                      </p>
                    </CardContent>
                  </Card>
                  <Card className="bg-slate-900 border-slate-800">
                    <CardContent className="p-5">
                      <p className="text-slate-400 text-sm">Current ARR</p>
                      <p className="text-3xl font-bold text-white mt-1">
                        {formatCurrency(subscriptionMetrics?.current_arr || 0)}
                      </p>
                    </CardContent>
                  </Card>
                  <Card className="bg-slate-900 border-slate-800">
                    <CardContent className="p-5">
                      <p className="text-slate-400 text-sm">Active Subscriptions</p>
                      <p className="text-3xl font-bold text-white mt-1">
                        {subscriptionMetrics?.active_subscriptions || 0}
                      </p>
                    </CardContent>
                  </Card>
                </div>

                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="text-white">Subscription Plans</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center py-8">
                      <CreditCard className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                      <p className="text-slate-400 mb-4">No subscription plans configured</p>
                      <Button className="bg-emerald-600 hover:bg-emerald-700">
                        <Plus className="w-4 h-4 mr-2" /> Create Plan
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Accounting Tab */}
            {activeTab === 'accounting' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card 
                    className="bg-slate-900 border-slate-800 cursor-pointer hover:border-slate-700 transition-colors"
                    onClick={() => {/* Navigate to trial balance */}}
                  >
                    <CardContent className="p-5">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                          <BarChart3 className="w-5 h-5 text-blue-400" />
                        </div>
                        <h3 className="text-white font-medium">Trial Balance</h3>
                      </div>
                      <p className="text-slate-400 text-sm">View account balances</p>
                    </CardContent>
                  </Card>

                  <Card 
                    className="bg-slate-900 border-slate-800 cursor-pointer hover:border-slate-700 transition-colors"
                  >
                    <CardContent className="p-5">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                          <TrendingUp className="w-5 h-5 text-green-400" />
                        </div>
                        <h3 className="text-white font-medium">Income Statement</h3>
                      </div>
                      <p className="text-slate-400 text-sm">Profit & Loss report</p>
                    </CardContent>
                  </Card>

                  <Card 
                    className="bg-slate-900 border-slate-800 cursor-pointer hover:border-slate-700 transition-colors"
                  >
                    <CardContent className="p-5">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                          <PieChart className="w-5 h-5 text-purple-400" />
                        </div>
                        <h3 className="text-white font-medium">Balance Sheet</h3>
                      </div>
                      <p className="text-slate-400 text-sm">Assets & liabilities</p>
                    </CardContent>
                  </Card>
                </div>

                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="text-white">Chart of Accounts</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {chartOfAccounts?.is_default ? (
                      <div className="text-center py-8">
                        <Receipt className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                        <p className="text-slate-400 mb-2">Using default chart of accounts</p>
                        <p className="text-slate-500 text-sm mb-4">
                          Customize accounts as needed for your business
                        </p>
                        <Button variant="outline" className="border-slate-700 text-slate-300">
                          View Default Accounts
                        </Button>
                      </div>
                    ) : (
                      <p className="text-slate-400">
                        {Object.keys(chartOfAccounts?.accounts || {}).length} accounts configured
                      </p>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
