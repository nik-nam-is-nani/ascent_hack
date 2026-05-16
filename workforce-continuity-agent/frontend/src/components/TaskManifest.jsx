import React, { useState } from 'react'

function TaskManifest({ tasks, employees }) {
  const [filter, setFilter] = useState('all')
  const [sortBy, setSortBy] = useState('priority')

  const getEmployeeName = (employeeId) => {
    const emp = employees.find(e => e.id === employeeId)
    return emp ? emp.name : 'Unknown'
  }

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'not_started': return 'status-badge status-not-started'
      case 'in_progress': return 'status-badge status-in-progress'
      case 'completed': return 'status-badge status-completed'
      case 'reassigned': return 'status-badge status-reassigned'
      case 'auto_completed': return 'status-badge status-auto-completed'
      default: return 'status-badge bg-gray-100 text-gray-700'
    }
  }

  const getPriorityBadgeClass = (priority) => {
    switch (priority) {
      case 'critical': return 'status-badge priority-critical'
      case 'high': return 'status-badge priority-high'
      case 'medium': return 'status-badge priority-medium'
      case 'low': return 'status-badge priority-low'
      default: return 'status-badge bg-gray-100 text-gray-700'
    }
  }

  const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 }

  const filteredTasks = tasks
    .filter(task => {
      if (filter === 'all') return true
      if (filter === 'pending') return ['not_started', 'in_progress'].includes(task.status)
      if (filter === 'completed') return task.status === 'completed'
      if (filter === 'reassigned') return task.status === 'reassigned'
      if (filter === 'auto_completed') return task.status === 'auto_completed'
      return true
    })
    .sort((a, b) => {
      if (sortBy === 'priority') {
        return priorityOrder[a.priority] - priorityOrder[b.priority]
      }
      if (sortBy === 'status') {
        return a.status.localeCompare(b.status)
      }
      if (sortBy === 'assigned') {
        return getEmployeeName(a.assigned_to).localeCompare(getEmployeeName(b.assigned_to))
      }
      return 0
    })

  const stats = {
    total: tasks.length,
    notStarted: tasks.filter(t => t.status === 'not_started').length,
    inProgress: tasks.filter(t => t.status === 'in_progress').length,
    completed: tasks.filter(t => t.status === 'completed').length,
    reassigned: tasks.filter(t => t.status === 'reassigned').length,
    autoCompleted: tasks.filter(t => t.status === 'auto_completed').length
  }

  return (
    <div>
      {/* Stats */}
      <div className="grid grid-cols-6 gap-4 mb-6">
        <div className="card p-3 text-center">
          <div className="text-xl font-bold text-gray-900">{stats.total}</div>
          <div className="text-xs text-gray-500">Total</div>
        </div>
        <div className="card p-3 text-center">
          <div className="text-xl font-bold text-gray-600">{stats.notStarted}</div>
          <div className="text-xs text-gray-500">Not Started</div>
        </div>
        <div className="card p-3 text-center">
          <div className="text-xl font-bold text-blue-600">{stats.inProgress}</div>
          <div className="text-xs text-gray-500">In Progress</div>
        </div>
        <div className="card p-3 text-center">
          <div className="text-xl font-bold text-green-600">{stats.completed}</div>
          <div className="text-xs text-gray-500">Completed</div>
        </div>
        <div className="card p-3 text-center">
          <div className="text-xl font-bold text-yellow-600">{stats.reassigned}</div>
          <div className="text-xs text-gray-500">Reassigned</div>
        </div>
        <div className="card p-3 text-center">
          <div className="text-xl font-bold text-purple-600">{stats.autoCompleted}</div>
          <div className="text-xs text-gray-500">Auto-Completed</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex gap-2">
          {['all', 'pending', 'completed', 'reassigned', 'auto_completed'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                filter === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {f === 'all' ? 'All' : f === 'pending' ? 'Pending' : f === 'completed' ? 'Completed' : f === 'reassigned' ? 'Reassigned' : 'Auto-Complete'}
            </button>
          ))}
        </div>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-3 py-1.5 border rounded-lg text-sm"
        >
          <option value="priority">Sort by Priority</option>
          <option value="status">Sort by Status</option>
          <option value="assigned">Sort by Assignee</option>
        </select>
      </div>

      {/* Task Table */}
      <div className="card overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Task</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Assigned To</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Progress</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filteredTasks.map(task => (
              <tr key={task.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div>
                    <div className="font-medium text-gray-900">{task.title}</div>
                    <div className="text-xs text-gray-500">{task.id}</div>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {getEmployeeName(task.assigned_to)}
                </td>
                <td className="px-4 py-3">
                  <span className={getPriorityBadgeClass(task.priority)}>
                    {task.priority}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={getStatusBadgeClass(task.status)}>
                    {task.status.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-600 rounded-full"
                        style={{ width: `${task.progress}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-500">{task.progress}%</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {task.task_type}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default TaskManifest