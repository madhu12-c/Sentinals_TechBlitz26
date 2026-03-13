import React from 'react';

const StatusBadge = ({ status }) => {
  const config = {
    new: { color: 'bg-gray-500/20 text-gray-400', label: 'New' },
    researching: { color: 'bg-blue-500/20 text-blue-400 animate-pulse', label: 'Researching' },
    scored: { color: 'bg-blue-500/20 text-blue-400', label: 'Scored' },
    awaiting_decision: { color: 'bg-amber-500/20 text-amber-400 border border-amber-500/50', label: 'Awaiting' },
    contacted: { color: 'bg-green-500/20 text-green-400', label: 'Contacted' },
    follow_up: { color: 'bg-green-500/20 text-green-400', label: 'Follow Up' },
    converted: { color: 'bg-purple-500/20 text-purple-400', label: 'Converted' },
    rejected: { color: 'bg-red-500/20 text-red-400', label: 'Rejected' },
    cold: { color: 'bg-gray-500/20 text-gray-400', label: 'Cold' },
  };

  const { color, label } = config[status] || config.new;

  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {status === 'awaiting_decision' && <span className="inline-block w-2 h-2 mr-1.5 bg-amber-500 rounded-full animate-ping" />}
      {label}
    </span>
  );
};

export default StatusBadge;
