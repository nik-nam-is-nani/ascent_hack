import React, { useEffect, useRef } from 'react'

function AgentActivityFeed({ activities, onClear, isProcessing }) {
  const scrollRef = useRef(null)

  // Auto-scroll to bottom when new activities arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [activities])

  const getPhaseColor = (phase) => {
    switch (phase) {
      case 'phase_1':
        return 'bg-red-500'
      case 'phase_2':
        return 'bg-orange-500'
      case 'phase_3':
        return 'bg-yellow-500'
      case 'phase_4':
        return 'bg-green-500'
      case 'phase_5':
        return 'bg-blue-500'
      case 'phase_6':
        return 'bg-purple-500'
      case 'system':
        return 'bg-gray-500'
      case 'reset':
        return 'bg-teal-500'
      default:
        return 'bg-gray-400'
    }
  }

  const getPhaseLabel = (phase) => {
    switch (phase) {
      case 'phase_1': return 'Detection'
      case 'phase_2': return 'Task Retrieval'
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
    <div className="card h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b flex items-center justify-between">
        <div>
          <h2 className="font-semibold text-gray-900">Agent Activity Feed</h2>
          <p className="text-xs text-gray-500">
            {activities.length} events
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isProcessing && (
            <div className="flex items-center gap-2 text-sm text-blue-600">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
              Processing
            </div>
          )}
          <button
            onClick={onClear}
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Activity List */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3">
        {activities.length === 0 ? (
          <div className="text-center text-gray-400 py-8">
            <p className="text-sm">No activity yet</p>
            <p className="text-xs">Mark an employee absent to see the agent pipeline in action</p>
          </div>
        ) : (
          activities.map((activity, idx) => (
            <div
              key={activity.id || idx}
              className={`activity-item p-3 rounded-lg border ${isProcessing && idx === activities.length - 1 ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200'}`}
            >
              <div className="flex items-start gap-3">
                <div className={`w-2 h-2 rounded-full mt-2 ${getPhaseColor(activity.phase)}`}></div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-gray-600">
                      {getPhaseLabel(activity.phase)}
                    </span>
                    <span className="text-xs text-gray-400">
                      {formatTime(activity.timestamp)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-900">{activity.message}</p>
                  {activity.details && Object.keys(activity.details).length > 0 && (
                    <div className="mt-2 text-xs text-gray-500">
                      {Object.entries(activity.details).map(([key, value]) => (
                        <div key={key}>
                          <span className="capitalize">{key}:</span>{' '}
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default AgentActivityFeed