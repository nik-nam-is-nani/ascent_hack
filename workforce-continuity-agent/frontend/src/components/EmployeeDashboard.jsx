import React from 'react'
import EmployeeCard from './EmployeeCard'

function EmployeeDashboard({ employees, tasks, onMarkAbsent, onReset, isProcessing }) {
  const getEmployeeTasks = (employeeId) => {
    return tasks.filter(t => t.assigned_to === employeeId)
  }

  const getPendingTaskCount = (employeeId) => {
    return getEmployeeTasks(employeeId).filter(
      t => t.status === 'not_started' || t.status === 'in_progress'
    ).length
  }

  const stats = {
    total: employees.length,
    atWork: employees.filter(e => !e.is_absent).length,
    absent: employees.filter(e => e.is_absent).length
  }

  return (
    <div>
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="card p-4">
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          <div className="text-sm text-gray-500">Total Employees</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-bold text-green-600">{stats.atWork}</div>
          <div className="text-sm text-gray-500">At Work</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-bold text-red-600">{stats.absent}</div>
          <div className="text-sm text-gray-500">Absent</div>
        </div>
      </div>

      {/* Employee Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {employees.map(employee => (
          <EmployeeCard
            key={employee.id}
            employee={employee}
            taskCount={getPendingTaskCount(employee.id)}
            onMarkAbsent={() => onMarkAbsent(employee.id)}
            onReset={() => onReset(employee.id)}
            isProcessing={isProcessing}
          />
        ))}
      </div>
    </div>
  )
}

export default EmployeeDashboard