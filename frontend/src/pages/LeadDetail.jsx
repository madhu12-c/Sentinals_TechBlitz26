import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ChevronLeft, Copy, Check, X, Info, Brain, Target, MessageSquare, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import * as api from '../api/leads';
import LoadingSpinner from '../components/LoadingSpinner';
import ScorePill from '../components/ScorePill';
import StatusBadge from '../components/StatusBadge';

const LeadDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [lead, setLead] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [showConfirm, setShowConfirm] = useState(null); // 'approve' or 'reject'
  const [copied, setCopied] = useState(false);

  const fetchData = async () => {
    try {
      const [l, e] = await Promise.all([
        api.getLead(id),
        api.getEvents(id, 30)
      ]);
      setLead(l);
      setEvents(e);
      setLoading(false);
    } catch (error) {
      console.error('Fetch error:', error);
      toast.error('Failed to load lead details');
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5s for status updates
    return () => clearInterval(interval);
  }, [id]);

  const handleCopy = () => {
    if (!lead?.suggested_message) return;
    navigator.clipboard.writeText(lead.suggested_message);
    setCopied(true);
    toast.success('Message copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDecision = async (decision) => {
    setActionLoading(true);
    try {
      await api.decideLead(id, decision);
      toast.success(decision === 'approve' ? 'Lead approved! Outreach starting.' : 'Lead archived.');
      setShowConfirm(null);
      fetchData();
    } catch (error) {
      toast.error('Action failed. Please try again.');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <div className="min-h-screen bg-[#0d1117] flex items-center justify-center"><LoadingSpinner /></div>;
  if (!lead) return <div className="min-h-screen bg-[#0d1117] flex items-center justify-center text-white">Lead not found</div>;

  const showButtons = lead.status === 'awaiting_decision' || lead.status === 'scored';

  return (
    <div className="min-h-screen bg-[#0d1117] text-[#e6edf3] p-6 lg:p-10 max-w-7xl mx-auto">
      {/* Back Button */}
      <Link to="/" className="inline-flex items-center space-x-2 text-white/40 hover:text-white transition-colors mb-8 group">
        <ChevronLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
        <span className="font-semibold">Back to Dashboard</span>
      </Link>

      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-10 pb-8 border-b border-white/10 space-y-6 md:space-y-0">
        <div className="flex items-center space-x-5">
          <div className="w-16 h-16 rounded-2xl bg-brand-teal/20 text-brand-teal flex items-center justify-center font-bold text-2xl border border-brand-teal/30 shadow-lg shadow-brand-teal/10">
            {lead.name[0].toUpperCase()}
          </div>
          <div>
            <div className="flex items-center space-x-3 mb-1">
              <h1 className="text-3xl font-extrabold text-white tracking-tight">{lead.name}</h1>
              <ScorePill score={lead.score} />
            </div>
            <div className="flex items-center space-x-4">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest bg-white/5 border border-white/10 text-white/60">
                {lead.source}
              </span>
              <span className="text-sm text-white/30 font-medium">
                Received {new Date(lead.created_at).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
        <div>
          <StatusBadge status={lead.status} />
        </div>
      </div>

      {/* 2x2 Info Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
        {/* Card A: Lead Info */}
        <div className="glass-card p-6 flex flex-col">
          <div className="flex items-center space-x-2 mb-6 text-brand-teal">
            <Info size={18} />
            <h3 className="text-sm font-bold uppercase tracking-wider">Lead Information</h3>
          </div>
          <div className="space-y-5 flex-1">
            <div>
              <label className="text-[10px] font-bold text-white/30 uppercase tracking-widest mb-1 block">Phone Number</label>
              <div className="text-lg font-semibold text-white/90">{lead.phone}</div>
            </div>
            <div>
              <label className="text-[10px] font-bold text-white/30 uppercase tracking-widest mb-1 block">Email</label>
              <div className="text-lg font-semibold text-white/90">{lead.email || 'None provided'}</div>
            </div>
            <div className="p-4 bg-white/5 rounded-xl border border-white/5">
              <label className="text-[10px] font-bold text-white/30 uppercase tracking-widest mb-2 block">Initial Message</label>
              <p className="text-sm text-white/80 leading-relaxed italic">"{lead.message}"</p>
            </div>
          </div>
        </div>

        {/* Card B: AI Research */}
        <div className="glass-card p-6 flex flex-col">
          <div className="flex items-center space-x-2 mb-6 text-blue-400">
            <Brain size={18} />
            <h3 className="text-sm font-bold uppercase tracking-wider">Claude AI Research</h3>
          </div>
          <div className="flex-1">
            {lead.research_summary ? (
              <p className="text-sm text-white/80 leading-relaxed whitespace-pre-wrap">
                {lead.research_summary}
              </p>
            ) : (
              <div className="flex flex-col items-center justify-center h-full space-y-3 py-10 opacity-40">
                <RefreshCcw size={32} className="animate-spin" />
                <span className="text-sm italic">AI is researching the lead...</span>
              </div>
            )}
          </div>
        </div>

        {/* Card C: AI Score & Reason */}
        <div className="glass-card p-6 flex flex-col">
          <div className="flex items-center space-x-2 mb-6 text-purple-400">
            <Target size={18} />
            <h3 className="text-sm font-bold uppercase tracking-wider">AI Scoring Analysis</h3>
          </div>
          <div className="flex-1 flex flex-col">
            <div className="flex items-baseline space-x-2 mb-4">
              <span className={`text-6xl font-black ${
                lead.score >= 8 ? 'text-green-500' : lead.score >= 5 ? 'text-amber-500' : 'text-red-500'
              }`}>
                {lead.score || '?'}
              </span>
              <span className="text-xl text-white/20 font-bold">/ 10</span>
            </div>
            {/* Progress Bar */}
            <div className="w-full h-3 bg-white/5 rounded-full overflow-hidden mb-6 border border-white/5">
              <div 
                className={`h-full transition-all duration-1000 ease-out ${
                  lead.score >= 8 ? 'bg-green-500' : lead.score >= 5 ? 'bg-amber-500' : 'bg-red-500'
                }`}
                style={{ width: `${(lead.score || 0) * 10}%` }}
              />
            </div>
            <div className="p-4 bg-white/5 rounded-xl border border-white/5 mt-auto">
              <label className="text-[10px] font-bold text-white/30 uppercase tracking-widest mb-2 block">Reasoning</label>
              <p className="text-sm text-white/80 leading-relaxed">
                {lead.score_reason || 'Calculating...'}
              </p>
            </div>
          </div>
        </div>

        {/* Card D: Suggested Message */}
        <div className="glass-card p-6 flex flex-col relative">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-2 text-brand-teal">
              <MessageSquare size={18} />
              <h3 className="text-sm font-bold uppercase tracking-wider">Suggested Outreach</h3>
            </div>
            {lead.suggested_message && (
              <button 
                onClick={handleCopy}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  copied ? 'bg-green-500/20 text-green-500' : 'bg-white/5 text-white/40 hover:text-white hover:bg-white/10'
                }`}
              >
                {copied ? <Check size={14} /> : <Copy size={14} />}
                <span>{copied ? 'Copied!' : 'Copy'}</span>
              </button>
            )}
          </div>
          <div className="flex-1">
            {lead.suggested_message ? (
              <div className="p-4 bg-brand-teal/5 border border-brand-teal/10 rounded-xl">
                 <p className="text-sm text-white/90 leading-relaxed font-medium whitespace-pre-wrap">
                  {lead.suggested_message}
                </p>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full space-y-3 py-10 opacity-40">
                <RefreshCcw size={32} className="animate-spin" />
                <span className="text-sm italic">AI is drafting a reply...</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      {showButtons && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          <button 
            onClick={() => setShowConfirm('approve')}
            className="h-16 rounded-2xl bg-brand-teal hover:bg-brand-dark text-white font-black text-lg flex items-center justify-center space-x-3 transition-all shadow-xl shadow-brand-teal/20"
          >
            <Check size={24} strokeWidth={3} />
            <span>APPROVE OUTREACH</span>
          </button>
          <button 
             onClick={() => setShowConfirm('reject')}
            className="h-16 rounded-2xl border-2 border-red-500/50 hover:border-red-500 text-red-500 font-black text-lg flex items-center justify-center space-x-3 transition-all hover:bg-red-500/5"
          >
            <X size={24} strokeWidth={3} />
            <span>REJECT & ARCHIVE</span>
          </button>
        </div>
      )}

      {/* Decision Banner (If already decided) */}
      {!showButtons && lead.status !== 'new' && lead.status !== 'researching' && (
        <div className={`mb-12 p-6 rounded-2xl border-2 flex items-center justify-center space-x-4 ${
          lead.status === 'rejected' ? 'border-red-500/30 bg-red-500/5 text-red-500' : 'border-green-500/30 bg-green-500/5 text-green-500'
        }`}>
          {lead.status === 'rejected' ? <AlertCircle /> : <CheckCircle />}
          <span className="text-xl font-black uppercase tracking-widest">
            {lead.status === 'rejected' ? 'Lead Archived' : `Decision: ${lead.status.replace('_', ' ')}`}
          </span>
        </div>
      )}

      {/* Modal / Confirmation */}
      {showConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-gray-950/80 backdrop-blur-sm">
          <div className="glass-card max-w-md w-full p-8 shadow-2xl border-white/20">
            <h2 className="text-2xl font-bold text-white mb-4">
              {showConfirm === 'approve' ? 'Confirm Approval' : 'Confirm Rejection'}
            </h2>
            <p className="text-white/60 mb-8 leading-relaxed">
              {showConfirm === 'approve' 
                ? "Approve this lead? The agent will send the outreach message immediately via WhatsApp and Email." 
                : "Reject this lead? It will be archived and no further automation will trigger."}
            </p>
            <div className="flex flex-col space-y-3">
              <button 
                onClick={() => handleDecision(showConfirm)}
                disabled={actionLoading}
                className={`h-12 rounded-xl font-bold text-white shadow-lg transition-all ${
                  showConfirm === 'approve' ? 'bg-brand-teal hover:bg-brand-dark shadow-brand-teal/20' : 'bg-red-500 hover:bg-red-700 shadow-red-500/20'
                }`}
              >
                {actionLoading ? 'Processing...' : `Yes, ${showConfirm} lead`}
              </button>
              <button 
                onClick={() => setShowConfirm(null)}
                className="h-12 rounded-xl bg-white/5 hover:bg-white/10 text-white/60 font-medium transition-all"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Timeline Section */}
      <section className="mt-16">
        <h2 className="text-2xl font-black text-white mb-8 tracking-tight">Timeline</h2>
        <div className="glass-card p-8">
          <div className="space-y-8">
            {events.map((event, idx) => (
              <div key={event._id || idx} className="flex space-x-6 relative group">
                {idx !== events.length - 1 && (
                  <div className="absolute left-3.5 top-8 bottom-[-32px] w-0.5 bg-white/5 group-hover:bg-brand-teal/20 transition-colors" />
                )}
                <div className={`w-7 h-7 rounded-full flex items-center justify-center z-10 p-1.5 shadow-lg ${
                  idx === 0 ? 'bg-brand-teal text-white' : 'bg-white/5 text-white/40'
                }`}>
                  <div className="w-full h-full rounded-full bg-current" />
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-black text-white/90 uppercase tracking-widest">{event.node.replace('_', ' ')}</span>
                    <span className="text-xs text-white/30 font-medium">{new Date(event.timestamp).toLocaleString()}</span>
                  </div>
                  <p className="text-sm text-white/60 leading-relaxed">{event.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default LeadDetail;

