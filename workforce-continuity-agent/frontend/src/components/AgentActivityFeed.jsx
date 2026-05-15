import React, { useEffect, useRef } from 'react'

function AgentActivityFeed({ activities, onClear, isProcessing }) {
  const scrollRef = useRef(null)

  // Auto-scroll to bottom when new activities arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [activities])

  const getPhaseIcon = (phase) => {
    switch (phase) {
      case 'phase_1': return '🔍'
      case 'phase_2': return '📥'
      case 'phase_3': return '🧠'
      case 'phase_4': return '🎯'
      case 'phase_5': return '⚙️'
      case 'phase_6': return '📄'
      case 'system': return '💻'
      case 'reset': return '🔄'
      default: return '✨'
    }
  }

  const getPhaseColor = (phase) => {
    switch (phase) {
      case 'phase_1': return 'text-rose-600 bg-rose-50 border-rose-100'
      case 'phase_2': return 'text-orange-600 bg-orange-50 border-orange-100'
      case 'phase_3': return 'text-amber-600 bg-amber-50 border-amber-100'
      case 'phase_4': return 'text-emerald-600 bg-emerald-50 border-emerald-100'
      case 'phase_5': return 'text-indigo-600 bg-indigo-50 border-indigo-100'
      case 'phase_6': return 'text-violet-600 bg-violet-50 border-violet-100'
      case 'system': return 'text-slate-600 bg-slate-50 border-slate-100'
      case 'reset': return 'text-teal-600 bg-teal-50 border-teal-100'
      default: return 'text-slate-600 bg-slate-50 border-slate-100'
    }
  }

  const getPhaseLabel = (phase) => {
    switch (phase) {
      case 'phase_1': return 'Detection'
      case 'phase_2': return 'Retrieval'
      case 'phase_3': return 'Analysis'
      case 'phase_4': return 'Reallocation'
      case 'phase_5': return 'Execution'
      case 'phase_6': return 'Reporting'
      case 'system': return 'System'
      case 'reset': return 'Reset'
      default: return phase
    }
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <div className="card h-[600px] flex flex-col border-slate-200">
      {/* Header */}
      <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div>
          <h2 className="font-bold text-slate-800 flex items-center gap-2">
            <span className="text-lg">🛰️</span>
            Neural Activity Feed
          </h2>
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
            {activities.length} System Events Logged
          </p>
        </div>
        <div className="flex items-center gap-3">
          {isProcessing && (
            <div className="flex items-center gap-2 text-[10px] font-bold text-indigo-600 uppercase">
              <div className="w-1.5 h-1.5 bg-indigo-600 rounded-full animate-ping"></div>
              Processing
            </div>
          )}
          <button
            onClick={onClear}
            className="p-1.5 hover:bg-slate-200 rounded-md transition-colors text-slate-400 hover:text-slate-600"
            title="Clear Feed"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      {/* Activity List */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 bg-white">
        {activities.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center px-6">
            <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center text-3xl mb-4 border border-slate-100">
              📡
            </div>
            <h3 className="text-slate-900 font-semibold mb-1">Feed Standby</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              System is currently monitoring workforce patterns. Mark an employee absent to trigger agent response.
            </p>
          </div>
        ) : (
          activities.map((activity, idx) => (
            <div
              key={activity.id || idx}
              className={`group relative pl-6 border-l-2 ${idx === activities.length - 1 && isProcessing ? 'border-indigo-500' : 'border-slate-100'} activity-item`}
            >
              {/* Dot on the line */}
              <div className={`absolute -left-[5px] top-0 w-2 h-2 rounded-full border-2 border-white ${idx === activities.length - 1 && isProcessing ? 'bg-indigo-500 ring-4 ring-indigo-50' : 'bg-slate-300'}`}></div>
              
              <div className={`p-3 rounded-xl border transition-all duration-300 ${idx === activities.length - 1 && isProcessing ? 'bg-indigo-50/50 border-indigo-100 shadow-sm' : 'bg-white border-slate-100 hover:border-slate-200'}`}>
                <div className="flex items-center justify-between mb-2">
                  <div className={`px-2 py-0.5 rounded-md border text-[9px] font-bold uppercase tracking-wider flex items-center gap-1.5 ${getPhaseColor(activity.phase)}`}>
                    <span>{getPhaseIcon(activity.phase)}</span>
                    {getPhaseLabel(activity.phase)}
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">
                    {formatTime(activity.timestamp)}
                  </span>
                </div>
                
                <p className="text-sm text-slate-700 font-medium leading-snug">
                  {activity.message}
                </p>
                
                {activity.details && Object.keys(activity.details).length > 0 && (
                  <div className="mt-2 space-y-1">
                    {Object.entries(activity.details).map(([key, value]) => {
                       if (typeof value === 'object') return null;
                       return (
                        <div key={key} className="flex items-center gap-2 text-[10px]">
                          <span className="text-slate-400 font-bold uppercase">{key.replace('_', ' ')}:</span>
                          <span className="text-slate-600 font-medium truncate">{String(value)}</span>
                        </div>
                       )
                    })}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default AgentActivityFeed