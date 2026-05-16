import React, { useState, useEffect, useCallback } from 'react'
import EmployeeDashboard from './components/EmployeeDashboard'
import AgentActivityFeed from './components/AgentActivityFeed'
import TaskManifest from './components/TaskManifest'
import ManagerReport from './components/ManagerReport'
import AgentVisualizer from './components/AgentVisualizer'
import WorkspaceExplorer from './components/WorkspaceExplorer'
import WebhookTrigger from './components/WebhookTrigger'

const API_BASE = 'http://127.0.0.1:8000'

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("React Error Boundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-8 text-center">
          <div className="w-20 h-20 bg-rose-500/20 rounded-3xl flex items-center justify-center mb-6 border border-rose-500/50">
            <span className="text-4xl">⚠️</span>
          </div>
          <h1 className="text-white text-2xl font-black uppercase tracking-tight mb-4">Neural Link Severed</h1>
          <p className="text-slate-400 font-mono text-sm max-w-lg mb-8">
            The frontend application encountered a critical runtime error. This usually happens due to malformed data streams or missing component dependencies.
          </p>
          <div className="bg-black/50 p-4 rounded-xl border border-white/10 mb-8 w-full max-w-2xl text-left">
            <p className="text-rose-400 font-mono text-xs overflow-auto">
              {this.state.error?.toString()}
            </p>
          </div>
          <button 
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-black uppercase tracking-widest text-xs hover:bg-indigo-700 transition-all"
          >
            Reconnect Neural Interface
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [employees, setEmployees] = useState([])
  const [tasks, setTasks] = useState([])
  const [activities, setActivities] = useState([])
  const [selectedEmployee, setSelectedEmployee] = useState(null)
  const [report, setReport] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [wsConnected, setWsConnected] = useState(false)
  const [githubToken, setGithubToken] = useState(() => localStorage.getItem('ascent_github_token') || '')
  const [repoUrl, setRepoUrl] = useState(() => localStorage.getItem('ascent_repo_url') || '')

  // Persistence
  useEffect(() => {
    localStorage.setItem('ascent_github_token', githubToken)
  }, [githubToken])

  useEffect(() => {
    localStorage.setItem('ascent_repo_url', repoUrl)
  }, [repoUrl])

  // WebSocket connection
  useEffect(() => {
    let ws

    const connectWebSocket = () => {
      ws = new WebSocket('ws://127.0.0.1:8000/ws/activity')

      ws.onopen = () => {
        setWsConnected(true)
        console.log('WebSocket connected')
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === 'initial' || data.type === 'reset') {
            setActivities(data.activities || [])
          } else if (data.phase) {
            // New activity
            setActivities(prev => [...prev, data])
            
            // Check for completion
            if (data.phase === 'phase_6') {
              setIsProcessing(false)
              // Fetch report when done
              setTimeout(() => {
                fetchReport(selectedEmployee)
                setActiveTab('report')
              }, 2000)
            }
          }
        } catch (err) {
          console.error('WebSocket message parse error:', err)
        }
      }

      ws.onclose = () => {
        setWsConnected(false)
        // Reconnect after 2 seconds
        setTimeout(connectWebSocket, 2000)
      }

      ws.onerror = (err) => {
        console.error('WebSocket error:', err)
      }
    }

    connectWebSocket()

    return () => {
      if (ws) ws.close()
    }
  }, [])

  // Fetch initial data
  useEffect(() => {
    fetchEmployees()
    fetchTasks()
  }, [])

  const fetchEmployees = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/employees`)
      const data = await res.json()
      setEmployees(data.employees || [])
    } catch (err) {
      console.error('Failed to fetch employees:', err)
    }
  }

  const fetchTasks = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/tasks`)
      const data = await res.json()
      setTasks(data.tasks || [])
    } catch (err) {
      console.error('Failed to fetch tasks:', err)
    }
  }

  const fetchReport = async (employeeId) => {
    if (!employeeId) return
    try {
      const res = await fetch(`${API_BASE}/api/report/${employeeId}`)
      const data = await res.json()
      if (data.report) {
        setReport(data.report)
      }
    } catch (err) {
      console.error('Failed to fetch report:', err)
    }
  }

  const handleMarkAbsent = async (employeeId) => {
    if (isProcessing) return

    setIsProcessing(true)
    setSelectedEmployee(employeeId)
    setActivities([])
    setReport(null)

    try {
      console.log(`Triggering pipeline for ${employeeId}...`)
      const res = await fetch(`${API_BASE}/api/absence/${employeeId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ github_token: githubToken, github_repo_url: repoUrl })
      })
      
      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.detail || 'Server responded with an error')
      }

      const data = await res.json()
      console.log('Pipeline triggered successfully:', data)

      // Background task started, we don't expect a report yet
      // The WebSocket will stream the progress
      
      // Refresh status immediately
      await fetchEmployees()
      await fetchTasks()
      
    } catch (err) {
      console.error('Failed to trigger agent pipeline:', err)
      alert(`Agent failed to trigger pipeline: ${err.message}`)
      setIsProcessing(false)
    }
    // Note: setIsProcessing(false) is handled by the WebSocket completion or manual reset
    // but we keep it in catch for error cases.
  }

  const handleReset = async (employeeId) => {
    try {
      await fetch(`${API_BASE}/api/absence/${employeeId}/reset`, {
        method: 'POST'
      })
      fetchEmployees()
      fetchTasks()
      setReport(null)
      setActivities([])
    } catch (err) {
      console.error('Failed to reset:', err)
    }
  }

  const startSimulation = async () => {
    if (isProcessing) return
    setIsProcessing(true)
    setActivities([])
    try {
      const res = await fetch(`${API_BASE}/api/simulation/start`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ github_token: githubToken, github_repo_url: repoUrl })
      })
      const data = await res.json()
      setSelectedEmployee('P1')
      await fetchEmployees()
      await fetchTasks()
      alert('Project Simulation Started: Lead Architect marked absent. Agent taking over architecture implementation...')
    } catch (err) {
      console.error('Failed to start simulation:', err)
    } finally {
      setIsProcessing(false)
    }
  }

  const clearActivities = async () => {
    try {
      await fetch(`${API_BASE}/api/activity/clear`, { method: 'POST' })
      setActivities([])
    } catch (err) {
      console.error('Failed to clear activities:', err)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-100">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight text-slate-900">Ascent <span className="text-indigo-600">Continuity</span></h1>
                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Multi-Agent Workforce Protection</p>
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="hidden lg:flex items-center gap-2 group">
                <div className={`w-2 h-2 rounded-full ${githubToken ? 'bg-emerald-500' : 'bg-slate-300'}`}></div>
                <input 
                  type="password" 
                  placeholder="GitHub PAT (Saved)" 
                  value={githubToken}
                  onChange={(e) => setGithubToken(e.target.value)}
                  className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 text-[10px] w-44 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-all"
                />
                {githubToken && (
                  <button 
                    onClick={() => setGithubToken('')}
                    className="text-[10px] text-rose-500 font-bold opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    Clear
                  </button>
                  )}
                </div>

              <div className="hidden lg:flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${repoUrl ? 'bg-indigo-500' : 'bg-slate-300'}`}></div>
                <input
                  type="text"
                  placeholder="GitHub Repo URL"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 text-[10px] w-56 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-all"
                />
              </div>

              <button 
                onClick={startSimulation}
                className="hidden lg:flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-xl border border-indigo-100 font-bold text-xs hover:bg-indigo-600 hover:text-white transition-all shadow-sm"
              >
                <span>🚀</span>
                Run Project Simulation
              </button>

              <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-slate-50 rounded-full border border-slate-100">
                <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`}></div>
                <span className="text-xs font-semibold text-slate-600">
                  {wsConnected ? 'Neural Link Active' : 'Neural Link Offline'}
                </span>
              </div>
              
              <div className="h-8 w-8 rounded-full bg-slate-200 border-2 border-white shadow-sm overflow-hidden">
                <img src={`https://ui-avatars.com/api/?name=Manager&background=6366f1&color=fff`} alt="Profile" />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <div className="bg-white border-b border-slate-200 sticky top-16 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex -mb-px space-x-8">
            {[
              { id: 'dashboard', label: 'Workforce Hub', icon: '👥' },
              { id: 'tasks', label: 'Task Manifest', icon: '📋' },
              { id: 'workspace', label: 'Neural Workspace', icon: '💻' },
              { id: 'report', label: 'Continuity Reports', icon: '📊' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 py-4 px-1 border-b-2 font-semibold text-sm transition-all
                  ${activeTab === tab.id
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                  }
                `}
              >
                <span className="text-lg">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <AgentVisualizer
              activities={activities}
              isProcessing={isProcessing}
              targetEmployee={employees.find(e => e.id === selectedEmployee)}
            />

            {/* Webhook / Custom Input Panel */}
            <WebhookTrigger
              isProcessing={isProcessing}
              setIsProcessing={setIsProcessing}
              onTrigger={handleMarkAbsent}
              employees={employees}
              githubToken={githubToken}
              repoUrl={repoUrl}
            />

            <div className="flex flex-col lg:flex-row gap-8">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-lg font-bold text-slate-900">Workforce Status</h2>
                    <p className="text-sm text-slate-500">Real-time presence and task load</p>
                  </div>
                </div>
                <EmployeeDashboard
                  employees={employees}
                  tasks={tasks}
                  onMarkAbsent={handleMarkAbsent}
                  onReset={handleReset}
                  onSelectEmployee={setSelectedEmployee}
                  selectedEmployeeId={selectedEmployee}
                  isProcessing={isProcessing}
                />
              </div>
              <div className="lg:w-96">
                <AgentActivityFeed
                  activities={activities}
                  onClear={clearActivities}
                  isProcessing={isProcessing}
                />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'tasks' && (
          <div className="animate-in fade-in duration-500">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-slate-900">Task Manifest</h2>
              <p className="text-slate-500">Comprehensive view of all organizational tasks and their current state.</p>
            </div>
            <TaskManifest tasks={tasks} employees={employees} />
          </div>
        )}

        {activeTab === 'workspace' && (
          <div className="animate-in fade-in duration-500">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-slate-900">Neural Workspace</h2>
              <p className="text-slate-500">Real-time repository of implementation artifacts generated by autonomous agents.</p>
            </div>
            <WorkspaceExplorer
              activities={activities}
              githubToken={githubToken}
              repoUrl={repoUrl}
              onRepoUrlChange={setRepoUrl}
            />
          </div>
        )}

        {activeTab === 'report' && (
          <div className="animate-in fade-in duration-500 max-w-4xl mx-auto">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-slate-900">Continuity Intelligence Report</h2>
              <p className="text-slate-500">Automated analysis and reallocation strategy for workforce absences.</p>
            </div>
            <ManagerReport
              report={report}
              selectedEmployee={selectedEmployee}
              employees={employees}
            />
          </div>
        )}
      </main>
    </div>
  )
}

export { ErrorBoundary }
export default App
