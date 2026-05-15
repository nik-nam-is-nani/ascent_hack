import React, { useState, useEffect, useCallback } from 'react'
import EmployeeDashboard from './components/EmployeeDashboard'
import AgentActivityFeed from './components/AgentActivityFeed'
import TaskManifest from './components/TaskManifest'
import ManagerReport from './components/ManagerReport'
import AgentVisualizer from './components/AgentVisualizer'

const API_BASE = 'http://localhost:8000'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [employees, setEmployees] = useState([])
  const [tasks, setTasks] = useState([])
  const [activities, setActivities] = useState([])
  const [selectedEmployee, setSelectedEmployee] = useState(null)
  const [report, setReport] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [wsConnected, setWsConnected] = useState(false)

  // WebSocket connection
  useEffect(() => {
    let ws

    const connectWebSocket = () => {
      ws = new WebSocket('ws://localhost:8000/ws/activity')

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

  const handleMarkAbsent = async (employeeId) => {
    if (isProcessing) return

    setIsProcessing(true)
    setSelectedEmployee(employeeId)
    // Clear previous activities when starting new process
    setActivities([])

    try {
      const res = await fetch(`${API_BASE}/api/absence/${employeeId}`, {
        method: 'POST'
      })
      const data = await res.json()

      if (data.result?.report) {
        setReport(data.result.report)
      }

      // Refresh data
      await fetchEmployees()
      await fetchTasks()
      
      // Delay switching tab so user can see completion
      setTimeout(() => {
        setActiveTab('report')
      }, 2000)
    } catch (err) {
      console.error('Failed to mark absence:', err)
      alert('Failed to trigger agent pipeline')
    } finally {
      setIsProcessing(false)
    }
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

export default App