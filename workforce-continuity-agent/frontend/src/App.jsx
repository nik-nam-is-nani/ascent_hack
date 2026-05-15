import React, { useState, useEffect, useCallback } from 'react'
import EmployeeDashboard from './components/EmployeeDashboard'
import AgentActivityFeed from './components/AgentActivityFeed'
import TaskManifest from './components/TaskManifest'
import ManagerReport from './components/ManagerReport'

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

    try {
      const res = await fetch(`${API_BASE}/api/absence/${employeeId}`, {
        method: 'POST'
      })
      const data = await res.json()

      if (data.result?.report) {
        setReport(data.result.report)
      }

      // Refresh data
      fetchEmployees()
      fetchTasks()
      setActiveTab('report')
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">WC</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Workforce Continuity Agent</h1>
              <p className="text-sm text-gray-500">Multi-agent autonomous task management</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {wsConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-1">
            {[
              { id: 'dashboard', label: 'Employee Dashboard' },
              { id: 'tasks', label: 'Task Manifest' },
              { id: 'report', label: 'Manager Report' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'dashboard' && (
          <div className="flex gap-6">
            <div className="flex-1">
              <EmployeeDashboard
                employees={employees}
                tasks={tasks}
                onMarkAbsent={handleMarkAbsent}
                onReset={handleReset}
                isProcessing={isProcessing}
              />
            </div>
            <div className="w-96">
              <AgentActivityFeed
                activities={activities}
                onClear={clearActivities}
                isProcessing={isProcessing}
              />
            </div>
          </div>
        )}

        {activeTab === 'tasks' && (
          <TaskManifest tasks={tasks} employees={employees} />
        )}

        {activeTab === 'report' && (
          <ManagerReport
            report={report}
            selectedEmployee={selectedEmployee}
            employees={employees}
          />
        )}
      </main>
    </div>
  )
}

export default App