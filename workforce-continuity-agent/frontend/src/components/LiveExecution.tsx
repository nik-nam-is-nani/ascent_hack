import React, { useMemo, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Code2, 
  Terminal, 
  FileCode, 
  Cpu, 
  Database, 
  Mail, 
  Settings, 
  CheckCircle2,
  Activity,
  FilePlus,
  Zap,
  Search,
  Target,
  Brain
} from 'lucide-react';

interface LiveExecutionProps {
  activities: any[];
}

const LiveExecution: React.FC<LiveExecutionProps> = ({ activities }) => {
  const [activeTask, setActiveTask] = useState<any>(null);
  const [logs, setLogs] = useState<any[]>([]);

  const latestStep = useMemo(() => {
    // Get the latest interesting step
    const steps = activities.filter(a => 
      ['analysis_thought', 'planning_step', 'execution_step', 'learning', 'mastered', 'implementing'].includes(a.details?.sub_phase) ||
      a.phase === 'phase_5'
    );
    return steps.length > 0 ? steps[steps.length - 1] : null;
  }, [activities]);

  const latestCodePreview = useMemo(() => {
    const codeSteps = activities.filter(a => a.details?.code_preview);
    return codeSteps.length > 0 ? codeSteps[codeSteps.length - 1].details.code_preview : null;
  }, [activities]);

  useEffect(() => {
    if (latestStep) {
      setActiveTask(latestStep);
      setLogs(prev => {
        // Avoid duplicate logs for the same message
        if (prev.length > 0 && prev[prev.length - 1].message === latestStep.message) return prev;
        return [...prev.slice(-25), {
          id: Date.now() + Math.random(),
          message: latestStep.message,
          action: latestStep.details?.action || latestStep.details?.sub_phase || 'processing',
          timestamp: new Date().toLocaleTimeString()
        }];
      });
    }
  }, [latestStep]);

  if (!activeTask) {
    return (
      <div className="h-[500px] flex flex-col items-center justify-center p-8 bg-slate-950/50 rounded-3xl border border-slate-800 border-dashed">
        <Activity className="w-12 h-12 text-indigo-500/20 mb-4 animate-pulse" />
        <p className="text-slate-600 font-bold uppercase tracking-[0.4em] text-[10px]">Neural Interface: Idle</p>
        <p className="text-slate-700 text-[9px] mt-2 font-mono uppercase tracking-widest">Awaiting Continuity Trigger...</p>
      </div>
    );
  }

  const getIcon = (step: any) => {
    if (!step || !step.details) return <Activity className="w-5 h-5 text-slate-400" />;
    
    const action = step.details.action;
    const subPhase = step.details.sub_phase;

    if (subPhase === 'analysis_thought') return <Search className="w-5 h-5 text-amber-400" />;
    if (subPhase === 'planning_step') return <Target className="w-5 h-5 text-emerald-400" />;
    if (subPhase === 'learning') return <Brain className="w-5 h-5 text-indigo-400" />;
    
    switch (action) {
      case 'creating_files': return <FilePlus className="w-5 h-5 text-emerald-400" />;
      case 'updating_code': return <Code2 className="w-5 h-5 text-indigo-400" />;
      case 'editing_apis': return <Zap className="w-5 h-5 text-amber-400" />;
      case 'writing_react': return <FileCode className="w-5 h-5 text-blue-400" />;
      default: return <Activity className="w-5 h-5 text-slate-400" />;
    }
  };

  const getActionLabel = (step: any) => {
    if (!step || !step.details) return 'PROCESSING';
    
    const subPhase = step.details.sub_phase;
    if (subPhase === 'analysis_thought') return 'COGNITIVE ANALYSIS';
    if (subPhase === 'planning_step') return 'STRATEGIC PLANNING';
    if (subPhase === 'learning') return 'NEURAL ACQUISITION';
    return (step.details.action || 'PROCESSING').replace('_', ' ').toUpperCase();
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-slate-900 border border-slate-800 rounded-[2rem] overflow-hidden shadow-2xl flex flex-col h-[600px]"
    >
      {/* Header */}
      <div className="bg-slate-800/50 p-6 border-b border-slate-700 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-indigo-500 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Cpu className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-white font-black text-lg uppercase tracking-tight">Agent Executor</h3>
              <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[9px] font-black rounded-full border border-emerald-500/30">ACTIVE</span>
            </div>
            <p className="text-slate-400 text-xs font-bold uppercase tracking-widest">Task ID: {activeTask.details?.task_id || 'N/A'}</p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <div className="text-right hidden md:block">
            <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest">Responsibility</p>
            <p className="text-xs text-indigo-400 font-bold">Neural Core V4</p>
          </div>
          <div className="w-10 h-10 rounded-full border-2 border-slate-700 flex items-center justify-center text-xs font-black text-white bg-slate-800">
             72%
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        {/* Left: Code/Artifact View */}
        <div className="flex-1 p-6 flex flex-col border-b md:border-b-0 md:border-r border-slate-800 overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="p-1.5 bg-slate-800 rounded-lg">
                {getIcon(activeTask)}
              </div>
              <div>
                <p className="text-[10px] text-slate-500 font-black uppercase tracking-tighter">Current Action</p>
                <p className="text-sm font-bold text-white">{getActionLabel(activeTask)}</p>
              </div>
            </div>
            <div className="text-[10px] font-mono text-indigo-400 bg-indigo-500/10 px-2 py-1 rounded">
              {activeTask.details?.details?.file || activeTask.details?.details?.route || activeTask.details?.details?.component || 'main.py'}
            </div>
          </div>

          <div className="flex-1 bg-slate-950 rounded-2xl p-6 font-mono text-sm relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>
            <div className="absolute top-4 right-4 text-[10px] text-slate-700 uppercase font-black tracking-widest pointer-events-none">
              Live Implementation Preview
            </div>
            <pre className="text-indigo-300 leading-relaxed overflow-x-auto whitespace-pre-wrap">
              <motion.code
                key={latestCodePreview}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                {latestCodePreview || "# Initializing Neural Implementation Environment...\n# Synchronizing dependencies...\n# Awaiting code generation payload..."}
              </motion.code>
            </pre>
            
            {/* Typing indicator */}
            <div className="mt-4 flex items-center gap-2">
               <span className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse"></span>
               <span className="text-[10px] text-indigo-500/50 font-black uppercase animate-pulse">
                 {latestCodePreview ? "Injecting active logic modules..." : "Synthesizing implementation strategy..."}
               </span>
            </div>

            {/* Futuristic overlay */}
            <div className="absolute bottom-6 right-6 opacity-20 pointer-events-none">
               <Cpu className="w-16 h-16 text-indigo-500" />
            </div>
          </div>

          <div className="mt-6">
             <h4 className="text-[10px] text-slate-500 font-black uppercase tracking-[0.2em] mb-3">Rational Analysis</h4>
             <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
                <p className="text-xs text-slate-300 leading-relaxed font-medium italic">
                  "Based on task priority and required skills ({activeTask.details?.skills_used?.join(', ') || 'General Intelligence'}), 
                  the executor is autonomously implementing {activeTask.message?.toLowerCase() || 'selected strategy'} to ensure workforce continuity."
                </p>
             </div>
          </div>
        </div>

        {/* Right: Terminal Logs */}
        <div className="md:w-80 bg-slate-950 p-6 flex flex-col overflow-hidden">
          <div className="flex items-center justify-between mb-4">
             <div className="flex items-center gap-2">
               <Terminal className="w-4 h-4 text-emerald-400" />
               <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Subsystem Console</span>
             </div>
             <div className="flex gap-1">
                <div className="w-1.5 h-1.5 rounded-full bg-rose-500/50"></div>
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
             </div>
          </div>

          <div className="flex-1 font-mono text-[10px] space-y-3 overflow-y-auto custom-scrollbar pr-2">
            <AnimatePresence mode="popLayout">
              {logs.map((log) => (
                <motion.div 
                  key={log.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="p-2 bg-white/5 rounded-lg border border-white/5 hover:border-emerald-500/20 transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-emerald-500 font-black tracking-tighter">[{log.timestamp}]</span>
                    <span className="text-[8px] text-slate-600 font-black uppercase">{log.action}</span>
                  </div>
                  <div className="text-slate-300 leading-tight">
                    <span className="text-indigo-400 mr-1">&gt;</span>
                    {log.message}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            <div className="flex items-center gap-2 text-indigo-400 animate-pulse mt-4">
               <span>[RUNNING]</span>
               <span className="w-1 h-3 bg-indigo-500"></span>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-slate-900">
             <div className="flex justify-between items-end">
                <div>
                   <p className="text-[9px] text-slate-600 font-black uppercase mb-1">Status</p>
                   <p className="text-[10px] text-emerald-400 font-black">STABLE</p>
                </div>
                <div className="text-right">
                   <p className="text-[9px] text-slate-600 font-black uppercase mb-1">Uptime</p>
                   <p className="text-[10px] text-white font-black">00:12:44</p>
                </div>
             </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default LiveExecution;
