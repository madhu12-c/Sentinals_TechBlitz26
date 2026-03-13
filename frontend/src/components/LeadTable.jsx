import React from 'react';
import { Link } from 'react-router-dom';
import { ExternalLink } from 'lucide-react';
import StatusBadge from './StatusBadge';
import ScorePill from './ScorePill';

const LeadTable = ({ leads, loading }) => {
  const getInitials = (name) => {
    return name ? name.split(' ').map(n => n[0]).join('').toUpperCase() : '?';
  };

  const getTimeAgo = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffInMs = now - date;
    const diffInMins = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMins / 60);
    const diffInDays = Math.floor(diffInHours / 24);

    if (diffInMins < 1) return 'Just now';
    if (diffInMins < 60) return `${diffInMins}m ago`;
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return `${diffInDays}d ago`;
  };

  const getSourceBadge = (source) => {
    const config = {
      whatsapp: 'bg-green-500/10 text-green-500 border border-green-500/20',
      form: 'bg-blue-500/10 text-blue-500 border border-blue-500/20',
      instagram: 'bg-purple-500/10 text-purple-500 border border-purple-500/20',
    };
    return config[source.toLowerCase()] || 'bg-gray-500/10 text-gray-500';
  };

  if (loading) {
    return (
      <div className="glass-card overflow-hidden">
        <div className="p-4 border-b border-white/10 flex justify-between items-center">
          <div className="h-6 w-32 bg-gray-700/50 animate-pulse rounded" />
          <div className="h-6 w-24 bg-gray-700/50 animate-pulse rounded" />
        </div>
        {[1, 2, 3, 4, 5].map(i => (
          <div key={i} className="p-4 border-b border-white/10 flex items-center space-x-4">
            <div className="h-10 w-10 bg-gray-700/50 animate-pulse rounded-full" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-1/4 bg-gray-700/50 animate-pulse rounded" />
              <div className="h-3 w-1/6 bg-gray-700/50 animate-pulse rounded" />
            </div>
            <div className="h-6 w-20 bg-gray-700/50 animate-pulse rounded-full" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="glass-card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="text-xs uppercase tracking-wider text-white/40 border-b border-white/10">
            <tr>
              <th className="px-6 py-4 font-semibold">Name</th>
              <th className="px-6 py-4 font-semibold">Source</th>
              <th className="px-6 py-4 font-semibold">Score</th>
              <th className="px-6 py-4 font-semibold">Status</th>
              <th className="px-6 py-4 font-semibold">Time</th>
              <th className="px-6 py-4 font-semibold text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {leads.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-12 text-center text-white/30 italic">
                  No leads found.
                </td>
              </tr>
            ) : (
              leads.map((lead) => (
                <tr key={lead._id} className="hover:bg-white/5 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full bg-brand-teal/20 text-brand-teal flex items-center justify-center font-bold text-sm border border-brand-teal/30">
                        {getInitials(lead.name)}
                      </div>
                      <div>
                        <div className="font-semibold text-white/90">{lead.name}</div>
                        <div className="text-xs text-white/40">{lead.phone}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-tighter ${getSourceBadge(lead.source)}`}>
                      {lead.source}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <ScorePill score={lead.score} />
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={lead.status} />
                  </td>
                  <td className="px-6 py-4 text-sm text-white/40 whitespace-nowrap">
                    {getTimeAgo(lead.created_at)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link 
                      to={`/lead/${lead._id}`}
                      className="inline-flex items-center space-x-1 py-1.5 px-3 rounded-lg bg-brand-teal/10 text-brand-teal hover:bg-brand-teal hover:text-white transition-all text-sm font-medium border border-brand-teal/20"
                    >
                      <span>View</span>
                      <ExternalLink size={14} />
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LeadTable;

