import React, { useMemo, useEffect, useState, useCallback } from 'react';
import ReactFlow, { 
  Node, 
  Edge, 
  Background, 
  Controls, 
  ConnectionLineType,
  MarkerType,
  useNodesState,
  useEdgesState,
  Handle,
  Position
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Zap, 
  Search, 
  BarChart3, 
  Cpu, 
  CheckCircle2, 
  AlertCircle, 
  Brain,
  Activity,
  Layers,
  Share2
} from 'lucide-react';
import confetti from 'canvas-confetti';

// --- Types ---

interface ActivityDetail {
  phase: string;
  message: string;
  timestamp: string;
  details?: any;
}

interface NeuralBrainProps {
  activities: ActivityDetail[];
}

// --- Custom Node Components ---

const NeuralNode = ({ data }: any) => {
  const isRoot = data.type === 'root';
  const isActive = data.active;
  const isCompleted = data.status === 'completed';
  const isFailed = data.status === 'failed';

  const getIcon = () => {
    switch (data.phase) {
      case 'phase_1': return <Search className="w-4 h-4" />;
      case 'phase_2': return <Layers className="w-4 h-4" />;
      case 'phase_3': return <BarChart3 className="w-4 h-4" />;
      case 'phase_4': return <Zap className="w-4 h-4" />;
      case 'phase_5': return <Cpu className="w-4 h-4" />;
      case 'phase_6': return <CheckCircle2 className="w-4 h-4" />;
      default: return <Brain className="w-4 h-4" />;
    }
  };

  return (
    <div className={`relative px-4 py-3 rounded-xl border-2 transition-all duration-500 ${
      isActive 
        ? 'bg-indigo-950/80 border-indigo-400 shadow-[0_0_20px_rgba(129,140,248,0.5)] scale-110' 
        : isCompleted 
          ? 'bg-emerald-950/40 border-emerald-500/50 shadow-[0_0_10px_rgba(16,185,129,0.2)]'
          : isFailed
            ? 'bg-rose-950/40 border-rose-500/50 shadow-[0_0_10px_rgba(244,63,94,0.2)]'
            : 'bg-slate-900/80 border-slate-700 shadow-lg'
    }`}>
      {isActive && (
        <motion.div 
          layoutId="glow"
          className="absolute -inset-1 rounded-xl bg-indigo-500/20 blur-md"
          animate={{ opacity: [0.2, 0.5, 0.2] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}
      
      <Handle type="target" position={Position.Top} className="w-2 h-2 !bg-indigo-500" />
      
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${
          isActive ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-400'
        }`}>
          {getIcon()}
        </div>
        <div>
          <div className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest leading-none mb-1">
            {data.label_top}
          </div>
          <div className="text-xs font-bold text-white truncate max-w-[150px]">
            {data.label}
          </div>
          {data.progress !== undefined && (
            <div className="mt-2 w-full bg-slate-800 h-1 rounded-full overflow-hidden">
              <motion.div 
                className={`h-full ${isCompleted ? 'bg-emerald-500' : 'bg-indigo-500'}`}
                initial={{ width: 0 }}
                animate={{ width: `${data.progress}%` }}
              />
            </div>
          )}
        </div>
      </div>

      {data.reasoning && isActive && (
        <motion.div 
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-3 pt-3 border-t border-slate-700/50"
        >
          <div className="text-[9px] text-indigo-300 font-mono italic leading-tight">
            &gt; {data.reasoning}
          </div>
        </motion.div>
      )}

      <Handle type="source" position={Position.Bottom} className="w-2 h-2 !bg-indigo-500" />
    </div>
  );
};

const SkillNode = ({ data }: any) => {
  const isMastered = data.status === 'mastered';
  
  return (
    <div className={`px-3 py-2 rounded-lg border transition-all duration-700 ${
      isMastered 
        ? 'bg-emerald-950/30 border-emerald-500/50 shadow-sm' 
        : 'bg-slate-900/50 border-indigo-500/30 animate-pulse'
    }`}>
      <Handle type="target" position={Position.Left} className="!opacity-0" />
      <div className="flex items-center gap-2">
        <Activity className={`w-3 h-3 ${isMastered ? 'text-emerald-400' : 'text-indigo-400'}`} />
        <span className={`text-[10px] font-bold uppercase tracking-tighter ${
          isMastered ? 'text-emerald-400' : 'text-indigo-300'
        }`}>
          {data.label}
        </span>
        {isMastered && <CheckCircle2 className="w-3 h-3 text-emerald-500" />}
      </div>
      <Handle type="source" position={Position.Right} className="!opacity-0" />
    </div>
  );
};

const nodeTypes = {
  neural: NeuralNode,
  skill: SkillNode
};

// --- Main Component ---

const NeuralBrain: React.FC<NeuralBrainProps> = ({ activities }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const buildTree = useCallback(() => {
    if (activities.length === 0) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const newNodes: Node[] = [];
    const newEdges: Edge[] = [];

    // 1. Root Node
    newNodes.push({
      id: 'root',
      type: 'neural',
      position: { x: 400, y: 0 },
      data: { 
        label: 'NEURAL ORCHESTRATOR', 
        label_top: 'Central Intelligence',
        type: 'root',
        active: true,
        phase: 'root'
      }
    });

    // 2. Phase Nodes
    const phases = [
      { id: 'phase_1', label: 'Detection', top: 'Phase 01', x: 0 },
      { id: 'phase_2', label: 'Retrieval', top: 'Phase 02', x: 160 },
      { id: 'phase_3', label: 'Analysis', top: 'Phase 03', x: 320 },
      { id: 'phase_4', label: 'Planning', top: 'Phase 04', x: 480 },
      { id: 'phase_5', label: 'Execution', top: 'Phase 05', x: 640 },
      { id: 'phase_6', label: 'Reporting', top: 'Phase 06', x: 800 },
    ];

    const currentPhase = activities[activities.length - 1]?.phase;

    phases.forEach((phase) => {
      const phaseActivities = activities.filter(a => a.phase === phase.id);
      const isStarted = phaseActivities.length > 0;
      const isActive = currentPhase === phase.id;
      const isCompleted = isStarted && !isActive && phases.indexOf(phase) < phases.findIndex(p => p.id === currentPhase);
      
      // Check if later phases are started
      const laterPhasesStarted = phases.slice(phases.indexOf(phase) + 1).some(p => activities.some(a => a.phase === p.id));
      const finalStatus = laterPhasesStarted ? 'completed' : (isActive ? 'active' : (isStarted ? 'started' : 'pending'));

      newNodes.push({
        id: phase.id,
        type: 'neural',
        position: { x: phase.x, y: 150 },
        data: { 
          label: phase.label,
          label_top: phase.top,
          phase: phase.id,
          active: isActive,
          status: finalStatus === 'completed' ? 'completed' : 'normal',
          progress: finalStatus === 'completed' ? 100 : (isActive ? 50 : 0),
          reasoning: isActive ? phaseActivities[phaseActivities.length - 1]?.message : null
        }
      });

      newEdges.push({
        id: `e-root-${phase.id}`,
        source: 'root',
        target: phase.id,
        animated: isActive || (isStarted && !laterPhasesStarted),
        style: { 
          stroke: isActive ? '#818cf8' : (isStarted ? '#10b981' : '#334155'),
          strokeWidth: isActive ? 3 : 2
        },
        markerEnd: { type: MarkerType.ArrowClosed, color: isActive ? '#818cf8' : (isStarted ? '#10b981' : '#334155') }
      });
    });

    // 3. Sub-nodes (Skills for Phase 5)
    const skills = new Map();
    activities.forEach(a => {
      if (a.phase === 'phase_5' && a.details?.skill) {
        const skill = a.details.skill;
        const status = a.details.sub_phase;
        if (!skills.has(skill) || status === 'mastered') {
          skills.set(skill, status);
        }
      }
    });

    let skillIdx = 0;
    skills.forEach((status, skill) => {
      const skillId = `skill-${skill}`;
      newNodes.push({
        id: skillId,
        type: 'skill',
        position: { x: 640 + (skillIdx % 2 === 0 ? 180 : 250), y: 250 + (Math.floor(skillIdx / 2) * 60) },
        data: { label: skill, status: status }
      });

      newEdges.push({
        id: `e-phase5-${skillId}`,
        source: 'phase_5',
        target: skillId,
        animated: status !== 'mastered',
        style: { stroke: status === 'mastered' ? '#10b981' : '#818cf8', strokeWidth: 1 },
        curve: 'step'
      } as any);
      skillIdx++;
    });

    // 4. Task Analysis Nodes (Phase 3)
    const phase3Details = activities.find(a => a.phase === 'phase_3' && a.details?.task_analyses);
    if (phase3Details?.details?.task_analyses) {
      phase3Details.details.task_analyses.forEach((analysis: any, idx: number) => {
        const taskId = analysis.task_id;
        const nodeId = `task-${taskId}`;
        newNodes.push({
          id: nodeId,
          type: 'skill',
          position: { x: 320 - 150, y: 250 + (idx * 100) },
          data: { label: `Analyzing ${taskId}`, status: 'mastered' }
        });
        newEdges.push({
          id: `e-phase3-${nodeId}`,
          source: 'phase_3',
          target: nodeId,
          style: { stroke: '#10b981', strokeWidth: 1 }
        });

        // Subtasks branching
        if (analysis.analysis?.subtasks) {
          analysis.analysis.subtasks.forEach((sub: any, sIdx: number) => {
            const subId = `${nodeId}-sub-${sIdx}`;
            newNodes.push({
              id: subId,
              type: 'skill',
              position: { x: 320 - 300, y: 250 + (idx * 100) + (sIdx * 40) },
              data: { label: sub.title, status: 'mastered' }
            });
            newEdges.push({
              id: `e-${nodeId}-${subId}`,
              source: nodeId,
              target: subId,
              style: { stroke: '#10b981', strokeWidth: 0.5 }
            });
          });
        }
      });
    }

    // 4. Planning Nodes (Phase 4)
    const phase4Activities = activities.filter(a => a.phase === 'phase_4' && a.details?.task_id);
    phase4Activities.forEach((activity, idx) => {
      const taskId = activity.details.task_id;
      const assignedTo = activity.details.assigned_to;
      const nodeId = `decision-${taskId}`;
      newNodes.push({
        id: nodeId,
        type: 'skill',
        position: { x: 480 + 100, y: 250 + (idx * 50) },
        data: { label: `${taskId} → ${assignedTo}`, status: 'mastered' }
      });
      newEdges.push({
        id: `e-phase4-${nodeId}`,
        source: 'phase_4',
        target: nodeId,
        animated: true,
        style: { stroke: '#818cf8', strokeWidth: 1 }
      });
    });

    setNodes(newNodes);
    setEdges(newEdges);

    // Confetti on completion
    if (currentPhase === 'phase_6' && !activities.find(a => a.phase === 'complete_celebrated')) {
      confetti({
        particleCount: 150,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#818cf8', '#10b981', '#ffffff']
      });
      // We can't easily mutate activities here, but this is fine for a demo
    }
  }, [activities, setNodes, setEdges]);

  useEffect(() => {
    buildTree();
  }, [activities, buildTree]);

  return (
    <div className="h-[600px] w-full bg-slate-950 rounded-[2rem] border border-slate-800 overflow-hidden relative shadow-2xl">
      <div className="absolute top-6 left-8 z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-white font-bold text-lg leading-none">Neural Activity Matrix</h3>
            <p className="text-[10px] text-indigo-400 font-black uppercase tracking-[0.3em] mt-1">Live Agent Cognition Stream</p>
          </div>
        </div>
      </div>

      <div className="absolute top-6 right-8 z-10 flex gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-900/80 rounded-full border border-slate-800 backdrop-blur-sm">
          <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></div>
          <span className="text-[10px] font-bold text-slate-300 uppercase tracking-widest">Processing</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-900/80 rounded-full border border-slate-800 backdrop-blur-sm">
          <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
          <span className="text-[10px] font-bold text-slate-300 uppercase tracking-widest">Optimized</span>
        </div>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        className="bg-grid-slate-900/50"
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#1e293b" gap={20} size={1} />
        <Controls showInteractive={false} className="!bg-slate-900 !border-slate-800 !fill-white" />
      </ReactFlow>

      {/* Particle Overlay (CSS only) */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_50%_50%,rgba(99,102,241,0.1),transparent_70%)]"></div>
      </div>
    </div>
  );
};

export default NeuralBrain;
