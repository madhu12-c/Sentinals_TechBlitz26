import React, { useState, useEffect } from 'react';
import { Users, Clock, CheckCircle, Star, Plus, RefreshCcw } from 'lucide-react';
import toast from 'react-hot-toast';
import * as api from '../api/leads';
import MetricCard from '../components/MetricCard';
import LeadTable from '../components/LeadTable';
import ActivityLog from '../components/ActivityLog';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({ total: 0, awaiting: 0, approved: 0, converted: 0 });
  const [leads, setLeads] = useState([]);
  const [events, setEvents] = useState([]);
  const [filter, setFilter] = useState('All');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchAll = async (showRefresh = false) => {
    try {
      if (showRefresh) setRefreshing(true);
      const [m, l, e] = await Promise.all([
        api.getMetrics(),
        api.getLeads(),
        api.getEvents(null, 20)
      ]);
      setMetrics(m);
      setLeads(l);
      setEvents(e);
      setLoading(false);
    } catch (error) {
      console.error('Fetch error:', error);
      toast.error('Failed to sync with AI Agent');
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAll();
    const interval = setInterval(() => fetchAll(), 10000); // Sync every 10s
    return () => clearInterval(interval);
  }, []);

  const handleAddTestLead = async () => {
    const testLeads = [
      {
        name: "Rajesh Kumar",
        phone: "+919876543210",
        email: "rajesh@example.com",
        message: "Bhai mujhe ek achhi bike chahiye, 150cc ya 200cc. Budget 1.5 lakh hai.",
        source: "form"
      },
      {
        name: "Priya Sharma",
        phone: "+919123456789",
        email: "priya@gmail.com",
        message: "Hi, I saw your ad. Just wanted to know what bikes you have.",
        source: "form"
      },
      {
        name: "Unknown",
        phone: "+1234567890",
        message: "hello",
        source: "whatsapp"
      }
    ];

    const randomLead = testLeads[Math.floor(Math.random() * testLeads.length)];
    
    try {
      toast.promise(
        api.submitTestLead(randomLead),
        {
          loading: 'Sending lead to AI...',
          success: 'Lead received! Agent is starting research.',
          error: 'Failed to send lead.'
        }
      );
      setTimeout(fetchAll, 2000);
    } catch (err) {
      console.error(err);
    }
  };

  const filteredLeads = filter === 'All' 
    ? leads 
    : leads.filter(l => l.source.toLowerCase() === filter.toLowerCase());

  return (
    <div className="min-h-screen bg-[#0d1117] text-[#e6edf3] p-6 lg:p-10">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-center justify-between mb-10 space-y-4 md:space-y-0">
        <div>
          <h1 className="text-3xl font-extrabold text-white flex items-center tracking-tight">
            SalesAgent <span className="ml-3 inline-block w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse shadow-[0_0_10px_#22c55e]" />
          </h1>
          <p className="text-white/40 text-sm mt-1">AI-Powered Lead Automation Dashboard</p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => fetchAll(true)}
            className={`p-2.5 rounded-lg bg-white/5 border border-white/10 text-white/60 hover:text-white transition-all ${refreshing ? 'animate-spin' : ''}`}
          >
            <RefreshCcw size={18} />
          </button>
          <button 
            onClick={handleAddTestLead}
            className="flex items-center space-x-2 bg-brand-teal hover:bg-brand-dark text-white px-5 py-2.5 rounded-xl font-bold transition-all shadow-lg shadow-brand-teal/20"
          >
            <Plus size={18} />
            <span>Add Test Lead</span>
          </button>
        </div>
      </header>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <MetricCard label="Total Leads" value={metrics.total} icon={Users} color="blue" loading={loading} />
        <MetricCard label="Awaiting" value={metrics.awaiting} icon={Clock} color="amber" loading={loading} />
        <MetricCard label="Approved" value={metrics.approved} icon={CheckCircle} color="green" loading={loading} />
        <MetricCard label="Converted" value={metrics.converted} icon={Star} color="purple" loading={loading} />
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 items-start">
        {/* Lead Table Column */}
        <div className="xl:col-span-2 space-y-6">
          <div className="flex items-center justify-between px-2">
            <h2 className="text-xl font-bold text-white/90">Recent Leads</h2>
            <div className="flex items-center space-x-4 bg-white/5 p-1 rounded-lg border border-white/10">
              {['All', 'WhatsApp', 'Form', 'Instagram'].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                    filter === f ? 'bg-brand-teal text-white shadow-md' : 'text-white/40 hover:text-white/60'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
          <LeadTable leads={filteredLeads} loading={loading} />
        </div>

        {/* Activity Log Column */}
        <div className="h-full">
          <ActivityLog events={events} loading={loading} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

