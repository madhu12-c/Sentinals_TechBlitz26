import React from 'react';

const ActivityLog = ({ events, loading }) => {
  const getNodeColor = (node) => {
    const config = {
      research_lead: 'bg-blue-500',
      score_lead: 'bg-purple-500',
      notify_rep: 'bg-amber-500',
      send_outreach: 'bg-green-500',
      follow_up: 'bg-green-500',
      archive_lead: 'bg-red-500',
      log_to_db: 'bg-gray-500',
      ui_decision: 'bg-teal-500',
      webhook: 'bg-gray-400',
    };
    return config[node] || 'bg-gray-500';
  };

  const getTimeAgo = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffInMs = now - date;
    const diffInSecs = Math.floor(diffInMs / 1000);
    const diffInMins = Math.floor(diffInSecs / 60);

    if (diffInSecs < 60) return `${diffInSecs}s ago`;
    return `${diffInMins}m ago`;
  };

  if (loading) {
    return (
      <div className="glass-card p-6 min-h-[400px]">
        <h3 className="text-lg font-semibold text-white/90 mb-6">Agent Activity</h3>
        <div className="space-y-6">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="flex space-x-4 animate-pulse">
              <div className="w-3 h-3 rounded-full bg-gray-700 self-start mt-1" />
              <div className="flex-1 space-y-2">
                <div className="h-4 w-1/2 bg-gray-700 rounded" />
                <div className="h-3 w-1/4 bg-gray-700 rounded" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-6 h-full flex flex-col">
      <h3 className="text-lg font-semibold text-white/90 mb-6">Agent Activity</h3>
      <div className="flex-1 overflow-y-auto pr-2 space-y-6 custom-scrollbar">
        {events.length === 0 ? (
          <div className="text-center text-white/30 italic py-12">
            No activity logged yet.
          </div>
        ) : (
          events.map((event, idx) => (
            <div key={event._id || idx} className="flex space-x-4 group">
              <div className="relative flex flex-col items-center">
                <div className={`w-3 h-3 rounded-full ${getNodeColor(event.node)} z-10 shadow-[0_0_10px_rgba(255,255,255,0.2)]`} />
                {idx !== events.length - 1 && (
                  <div className="w-0.5 h-full bg-white/10 absolute top-3" />
                )}
              </div>
              <div className="flex-1 -mt-1 pb-4">
                <div className="flex justify-between items-start">
                  <div className="text-sm font-bold text-white/90 uppercase tracking-tight">
                    {event.node.replace('_', ' ')}
                  </div>
                  <div className="text-[10px] text-white/30 font-medium">
                    {getTimeAgo(event.timestamp)}
                  </div>
                </div>
                <div className="text-sm text-white/60 mt-1 leading-relaxed">
                  {event.description}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ActivityLog;

