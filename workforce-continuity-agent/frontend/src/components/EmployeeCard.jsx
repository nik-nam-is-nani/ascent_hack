import React from 'react'

function EmployeeCard({ employee, taskCount, onMarkAbsent, onReset, isProcessing }) {
  const getWorkloadColor = (workload) => {
    switch (workload) {
      case 'low': return 'text-green-600'
      case 'medium': return 'text-yellow-600'
      case 'high': return 'text-orange-600'
      case 'critical': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getWorkloadBg = (workload) => {
    switch (workload) {
      case 'low': return 'bg-green-50'
      case 'medium': return 'bg-yellow-50'
      case 'high': return 'bg-orange-50'
      case 'critical': return 'bg-red-50'
      default: return 'bg-gray-50'
    }
  }

  return (
    <div className={`card p-4 ${employee.is_absent ? 'ring-2 ring-red-400' : ''}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div
            className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold"
            style={{ backgroundColor: employee.avatar_color }}
          >
            {employee.name.split(' ').map(n => n[0]).join('')}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{employee.name}</h3>
            <p className="text-sm text-gray-500">{employee.role}</p>
          </div>
        </div>

        {employee.is_absent && (
          <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-medium rounded">
            ABSENT
          </span>
        )}
      </div>

      {/* Details */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">Department</span>
          <span className="text-gray-900">{employee.department}</span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">Pending Tasks</span>
          <span className={`font-medium ${taskCount > 3 ? 'text-orange-600' : 'text-gray-900'}`}>
            {taskCount}
          </span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">Workload</span>
          <span className={`font-medium ${getWorkloadColor(employee.workload)}`}>
            <span className={`px-2 py-0.5 rounded ${getWorkloadBg(employee.workload)}`}>
              {employee.workload}
            </span>
          </span>
        </div>
      </div>

      {/* Skills */}
      <div className="mb-4">
        <p className="text-xs text-gray-500 mb-1">Skills</p>
        <div className="flex flex-wrap gap-1">
          {employee.skills.slice(0, 4).map((skill, idx) => (
            <span
              key={idx}
              className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded"
            >
              {skill.skill}
            </span>
          ))}
          {employee.skills.length > 4 && (
            <span className="px-2 py-0.5 bg-gray-100 text-gray-500 text-xs rounded">
              +{employee.skills.length - 4}
            </span>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        {employee.is_absent ? (
          <button
            onClick={onReset}
            className="flex-1 btn-success text-sm py-2"
            disabled={isProcessing}
          >
            Reset Status
          </button>
        ) : (
          <button
            onClick={onMarkAbsent}
            className="flex-1 btn-danger text-sm py-2"
            disabled={isProcessing}
          >
            {isProcessing ? 'Processing...' : 'Mark Absent'}
          </button>
        )}
      </div>
    </div>
  )
}

export default EmployeeCard