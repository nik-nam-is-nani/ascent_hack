import React, { useMemo, useEffect, useState, useRef } from 'react'
import NeuralBrain from './NeuralBrain'
import LiveExecution from './LiveExecution'
import { motion, AnimatePresence } from 'framer-motion'

const PHASES = [
  { id: 'phase_1', label: 'Detection', icon: '🔍', color: 'rose' },
  { id: 'phase_2', label: 'Retrieval', icon: '📥', color: 'orange' },
  { id: 'phase_3', label: 'Analysis', icon: '🧠', color: 'amber' },
  { id: 'phase_4', label: 'Reallocation', icon: '🎯', color: 'emerald' },
  { id: 'phase_5', label: 'Execution', icon: '⚙️', color: 'indigo' },
  { id: 'phase_6', label: 'Reporting', icon: '📄', color: 'violet' }
]

function AgentVisualizer({ activities, isProcessing, targetEmployee }) {
  const [terminalLogs, setTerminalLogs] = useState([])
  const logContainerRef = useRef(null)

  const currentPhase = useMemo(() => {
    if (!Array.isArray(activities) || activities.length === 0) return null
    const phaseActivities = activities.filter(a => a && a.phase && a.phase.startsWith('phase_'))
    return phaseActivities.length > 0 ? phaseActivities[phaseActivities.length - 1].phase : null
  }, [activities])

  const currentActivity = (Array.isArray(activities) && activities.length > 0) ? activities[activities.length - 1] : null

  // Process logs for terminal effect
  useEffect(() => {
    if (Array.isArray(activities) && activities.length > 0) {
      const latest = activities[activities.length - 1]
      if (!latest || !latest.message) return
      
      const logEntry = {
        id: Date.now() + Math.random(),
        text: `[${new Date().toLocaleTimeString()}] ${latest.message}`,
        type: latest.phase === 'system' ? 'system' : 'agent'
      }
      setTerminalLogs(prev => [...prev.slice(-15), logEntry])
    } else {
      setTerminalLogs([])
    }
  }, [activities])

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [terminalLogs])

  const getPhaseStatus = (phaseId) => {
    if (!currentPhase || typeof currentPhase !== 'string') return 'pending'
    try {
      const phaseNum = parseInt(phaseId.split('_')[1])
      const currentNum = parseInt(currentPhase.split('_')[1])
      if (isNaN(phaseNum) || isNaN(currentNum)) return 'pending'
      if (phaseNum < currentNum) return 'completed'
      if (phaseNum === currentNum) return isProcessing ? 'active' : 'completed'
    } catch (e) {
      return 'pending'
    }
    return 'pending'
  }

  const getProgressPercentage = () => {
    if (!currentPhase) return 0
    const currentNum = parseInt(currentPhase.split('_')[1])
    
    // Base progress from current phase
    let progress = ((currentNum - 1) / PHASES.length) * 100
    
    // Add sub-progress for phase 5 (Execution)
    if (currentNum === 5 && currentActivity?.details?.progress_sub) {
      const phaseWeight = 100 / PHASES.length
      progress += (currentActivity.details.progress_sub / 100) * phaseWeight
    } else if (currentNum >= PHASES.length && !isProcessing) {
       progress = 100
    } else {
       // Regular phase step
       progress = (currentNum / PHASES.length) * 100
    }
    
    return Math.min(progress, 100)
  }

  return (
    <div className="space-y-6">
      <div className="card overflow-hidden border-slate-200 bg-white shadow-2xl shadow-indigo-100/50">
        {/* Animated Header Section */}
        <div className="relative bg-slate-900 p-8 overflow-hidden">
          <div className="absolute inset-0 bg-grid-animate opacity-20"></div>
          <div className="scanline"></div>
          
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="flex items-center gap-6">
              <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-blue-500 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200 animate-pulse"></div>
                <div className="relative w-20 h-20 bg-slate-800 rounded-2xl flex items-center justify-center border border-white/10 shadow-2xl shadow-indigo-500/20">
                  <span className="text-4xl animate-float">🤖</span>
                </div>
              </div>
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-2xl font-black text-white tracking-tight uppercase">
                    Neural <span className="text-indigo-400">Orchestrator</span>
                  </h2>
                  <div className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-[0.2em] border shadow-lg ${
                    isProcessing 
                      ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/50 animate-glow' 
                      : 'bg-slate-800 text-slate-500 border-slate-700'
                  }`}>
                    {isProcessing ? 'Agent Processing' : 'System Standby'}
                  </div>
                </div>
                <p className="text-sm text-slate-400 font-bold tracking-widest uppercase flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-ping"></span>
                  Autonomous Continuity Protocol 4.0
                </p>
              </div>
            </div>

            {targetEmployee && isProcessing && (
              <div className="flex items-center gap-4 bg-white/5 p-4 rounded-3xl border border-white/10 backdrop-blur-xl animate-in zoom-in duration-500">
                <div className="text-right">
                  <p className="text-[10px] text-indigo-300 font-black uppercase tracking-widest mb-1">Replacing Instance</p>
                  <p className="text-lg font-black text-white leading-tight">{targetEmployee.name}</p>
                  <p className="text-[10px] text-slate-500 font-bold">{targetEmployee.role}</p>
                </div>
                <div className="relative">
                  <div 
                    className="w-16 h-16 rounded-2xl flex items-center justify-center text-xl font-black border border-white/20 shadow-inner"
                    style={{ backgroundColor: targetEmployee.avatar_color }}
                  >
                    {targetEmployee.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-rose-500 rounded-full border-2 border-slate-900 flex items-center justify-center text-[10px] font-bold text-white shadow-lg">
                    !
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Progress Visualization */}
          <div className="mt-10 relative z-10">
            <div className="flex items-end justify-between mb-3">
              <div className="flex gap-2">
                <span className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em]">Quantum Sync</span>
                <span className="text-[10px] font-mono text-slate-500">ADDR: 0x7FFD2B84</span>
              </div>
              <div className="flex items-baseline gap-1">
                <span className="text-5xl font-black font-mono text-white tracking-tighter leading-none">
                  {Math.round(getProgressPercentage())}
                </span>
                <span className="text-xl font-black text-indigo-400">%</span>
              </div>
            </div>
            <div className="h-4 bg-slate-800 rounded-full overflow-hidden p-1 border border-white/5 shadow-inner">
              <div 
                className="h-full bg-gradient-to-r from-indigo-600 via-blue-500 to-indigo-400 transition-all duration-1000 ease-out rounded-full relative"
                style={{ width: `${getProgressPercentage()}%` }}
              >
                <div className="absolute top-0 right-0 bottom-0 w-24 bg-white/20 blur-md"></div>
                <div className="absolute inset-0 bg-[linear-gradient(45deg,rgba(255,255,255,0.2)_25%,transparent_25%,transparent_50%,rgba(255,255,255,0.2)_50%,rgba(255,255,255,0.2)_75%,transparent_75%,transparent)] bg-[length:20px_20px] animate-[data-flow_1s_linear_infinite]"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Neural Pipeline Section */}
        <div className="p-10 bg-white relative">
          <div className="absolute inset-0 bg-slate-50/50 pointer-events-none"></div>
          
          <div className="relative grid grid-cols-6 gap-6 mb-12">
            {PHASES.map((phase, idx) => {
              const status = getPhaseStatus(phase.id)
              return (
                <div key={phase.id} className="relative group">
                  <div className="flex flex-col items-center">
                    <div className={`
                      w-16 h-16 rounded-3xl flex items-center justify-center text-2xl mb-4 z-10 transition-all duration-700 relative
                      ${status === 'completed' ? 'bg-emerald-50 text-emerald-500 border-2 border-emerald-400 shadow-xl shadow-emerald-50' : 
                        status === 'active' ? 'bg-indigo-600 text-white shadow-2xl shadow-indigo-200 scale-125 rotate-6 animate-glow' : 
                        'bg-slate-50 text-slate-300 border border-slate-200'}
                    `}>
                      {status === 'active' && (
                        <div className="absolute -inset-2 bg-indigo-500/20 rounded-3xl animate-ping"></div>
                      )}
                      {status === 'completed' ? (
                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        <span className={`${status === 'active' ? 'animate-bounce' : ''}`}>{phase.icon}</span>
                      )}
                    </div>
                    <span className={`text-[11px] font-black uppercase tracking-wider text-center transition-colors duration-500 ${status === 'active' ? 'text-indigo-600' : 'text-slate-400'}`}>
                      {phase.label}
                    </span>
                    <div className={`mt-1 h-1 w-4 rounded-full transition-all duration-500 ${status === 'active' ? 'bg-indigo-500 w-8' : 'bg-transparent'}`}></div>
                  </div>
                  {idx < PHASES.length - 1 && (
                    <div className="absolute top-8 left-1/2 w-full h-[2px] -z-0">
                      <svg className="w-full h-full overflow-visible">
                        <line 
                          x1="0" y1="0" x2="100%" y2="0" 
                          stroke={getPhaseStatus(PHASES[idx+1].id) !== 'pending' ? '#34d399' : '#e2e8f0'} 
                          strokeWidth="2"
                          strokeDasharray={status === 'active' ? "4 4" : "0"}
                          className={status === 'active' ? "path-animate" : ""}
                        />
                      </svg>
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {/* Activity Center */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Current implementation Detail */}
            <div className="space-y-4">
              <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] ml-2">Neural Implementation</h4>
              {currentActivity ? (
                <div className="bg-slate-900 rounded-[2rem] p-8 border border-slate-800 shadow-2xl relative overflow-hidden group">
                  <div className="absolute top-0 right-0 p-6 opacity-10 text-8xl grayscale select-none">
                    {PHASES.find(p => p.id === currentActivity.phase)?.icon || '🤖'}
                  </div>
                  <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="px-3 py-1 bg-indigo-500/20 text-indigo-400 text-[10px] font-black rounded-lg border border-indigo-500/30 uppercase tracking-widest">
                        Phase {currentActivity.phase?.split('_')[1]}
                      </div>
                      <span className="text-slate-600 text-[10px] font-mono font-bold tracking-widest">
                        {new Date(currentActivity.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-white font-black text-2xl leading-tight mb-6 group-hover:text-indigo-400 transition-colors duration-300">
                      {currentActivity.message}
                    </p>
                    
                    {currentActivity?.details && Object.keys(currentActivity.details).length > 0 && (
                      <div className="grid grid-cols-2 gap-3">
                        {Object.entries(currentActivity.details).map(([key, value]) => {
                          if (typeof value === 'object' || key === 'phase' || !value) return null
                          return (
                            <div key={key} className="bg-white/5 px-4 py-3 rounded-2xl border border-white/5 hover:border-indigo-500/30 transition-all duration-300">
                              <p className="text-[9px] text-slate-500 font-black uppercase tracking-tighter mb-1">{key.replace('_', ' ')}</p>
                              <p className="text-xs font-black text-slate-200 truncate tracking-wide">{String(value)}</p>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="h-full min-h-[200px] flex flex-col items-center justify-center bg-slate-50 rounded-[2rem] border-2 border-dashed border-slate-200 p-8 text-center">
                  <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-sm mb-4">
                    <span className="text-2xl opacity-30">⏳</span>
                  </div>
                  <h5 className="text-slate-900 font-black uppercase tracking-widest text-sm mb-2">Awaiting Input</h5>
                  <p className="text-slate-400 text-xs font-medium max-w-xs">The agent is currently on standby. Trigger an absence to begin the continuity pipeline.</p>
                </div>
              )}
            </div>

            {/* Terminal Logs */}
            <div className="space-y-4">
              <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] ml-2">Subsystem Logs</h4>
              <div className="bg-slate-900 rounded-[2rem] p-6 border border-slate-800 h-[280px] shadow-2xl relative">
                <div className="absolute top-4 right-6 flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-rose-500"></div>
                  <div className="w-2 h-2 rounded-full bg-amber-500"></div>
                  <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                </div>
                <div ref={logContainerRef} className="h-full overflow-y-auto font-mono text-[10px] space-y-2 pr-2 custom-scrollbar">
                  {terminalLogs.length === 0 ? (
                    <div className="text-slate-700 italic">Initializing neural uplink...</div>
                  ) : (
                    terminalLogs.map(log => (
                      <div key={log.id} className={`${log.type === 'system' ? 'text-indigo-400' : 'text-emerald-400'} border-l-2 border-current pl-2 py-0.5 bg-white/5 rounded-r-md`}>
                        <span className="opacity-50 tracking-tighter mr-2">{log.text.split(']')[0]}]</span>
                        <span className="font-bold">{log.text.split(']')[1]}</span>
                      </div>
                    ))
                  )}
                  {isProcessing && (
                    <div className="text-white animate-pulse flex items-center gap-1">
                      <span>_</span>
                      <span className="cursor-blink">|</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          <AnimatePresence>
            {isProcessing && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="mt-12"
              >
                <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] ml-2 mb-4">Live Autonomous Execution</h4>
                <LiveExecution activities={activities} />
              </motion.div>
            )}
          </AnimatePresence>

          <div className="mt-12">
            <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] ml-2 mb-4">Neural Cognition Matrix</h4>
            <NeuralBrain activities={activities} />
          </div>
        </div>

        {/* System Meta footer */}
        <div className="bg-slate-50 px-10 py-4 border-t border-slate-100 flex items-center justify-between text-[10px] font-black text-slate-400 tracking-[0.2em] uppercase">
          <div className="flex gap-8">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span>
              API: 200 OK
            </div>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span>
              WS: CONNECTED
            </div>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-ping"></span>
              LATENCY: 12MS
            </div>
          </div>
          <div className="font-mono">
            SH_V4.0.1-STABLE // SYSTEM_UPTIME: 99.9%
          </div>
        </div>
      </div>
    </div>
  )
}

export default AgentVisualizer