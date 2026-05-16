import React from 'react'
import EmployeeCard from './EmployeeCard'

function EmployeeDashboard({
  employees,
  tasks,
  onMarkAbsent,
  onReset,
  onSelectEmployee,
  selectedEmployeeId,
  isProcessing
}) {
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

  const selectedEmployee = employees.find(e => e.id === selectedEmployeeId)
  const selectedEmployeeTasks = selectedEmployee ? getEmployeeTasks(selectedEmployee.id) : []

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
            onSelect={() => onSelectEmployee(employee.id)}
            isSelected={selectedEmployeeId === employee.id}
            isProcessing={isProcessing}
          />
        ))}
      </div>

      {selectedEmployee && (
        <div className="mt-6 bg-white border border-slate-200 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">{selectedEmployee.name} — Allocated Tasks</h3>
              <p className="text-xs text-slate-500">Live task list for the selected employee.</p>
            </div>
            <span className="px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold">
              {selectedEmployeeTasks.length} total
            </span>
          </div>
          {selectedEmployeeTasks.length === 0 ? (
            <p className="text-sm text-slate-500">No tasks currently allocated.</p>
          ) : (
            <div className="space-y-2">
              {selectedEmployeeTasks.map((task) => (
                <div key={task.id} className="border border-slate-100 rounded-xl p-3 bg-slate-50">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="text-sm font-semibold text-slate-900">{task.title}</p>
                      <p className="text-xs text-slate-500">{task.id}</p>
                    </div>
                    <span className="px-2 py-1 rounded-md bg-white border border-slate-200 text-[11px] font-semibold text-slate-700">
                      {task.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default EmployeeDashboard
