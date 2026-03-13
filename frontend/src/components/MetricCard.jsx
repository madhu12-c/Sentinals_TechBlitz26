import React from 'react';

const MetricCard = ({ label, value, icon: Icon, color, loading }) => {
  const colors = {
    blue: 'text-blue-500 bg-blue-500/10',
    amber: 'text-amber-500 bg-amber-500/10',
    green: 'text-green-500 bg-green-500/10',
    purple: 'text-purple-500 bg-purple-500/10',
  };

  return (
    <div className="glass-card p-6 relative overflow-hidden group">
      {loading ? (
        <div className="animate-pulse space-y-4">
          <div className="flex justify-between items-start">
            <div className="h-8 w-16 bg-gray-700/50 rounded" />
            <div className="h-6 w-6 bg-gray-700/50 rounded" />
          </div>
          <div className="h-4 w-24 bg-gray-700/50 rounded" />
        </div>
      ) : (
        <>
          <div className="flex justify-between items-start">
            <div className="text-3xl font-bold text-white tracking-tight">
              {value}
            </div>
            <div className={`p-2 rounded-lg ${colors[color] || colors.blue}`}>
              <Icon size={24} />
            </div>
          </div>
          <div className="mt-4 text-sm font-medium text-white/50 uppercase tracking-wider">
            {label}
          </div>
          {label === 'Awaiting' && value > 0 && (
            <div className="absolute bottom-0 left-0 h-1 bg-amber-500 w-full animate-pulse" />
          )}
        </>
      )}
    </div>
  );
};

export default MetricCard;

