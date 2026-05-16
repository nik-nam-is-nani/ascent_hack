import React from 'react'

function EmployeeCard({ employee, taskCount, onMarkAbsent, onReset, onSelect, isSelected, isProcessing }) {
  const getWorkloadColor = (workload) => {
    switch (workload) {
      case 'low': return 'text-emerald-600 bg-emerald-50 border-emerald-100'
      case 'medium': return 'text-amber-600 bg-amber-50 border-amber-100'
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-100'
      case 'critical': return 'text-rose-600 bg-rose-50 border-rose-100'
      default: return 'text-slate-600 bg-slate-50 border-slate-100'
    }
  }

  const isHighLoad = taskCount >= 5 || employee.workload === 'high' || employee.workload === 'critical'

  return (
    <div
      onClick={onSelect}
      className={`
      relative overflow-hidden rounded-2xl border transition-all duration-300
      ${employee.is_absent 
        ? 'bg-rose-50/30 border-rose-200 shadow-lg shadow-rose-100/50' 
        : 'bg-white border-slate-200 hover:border-indigo-300 hover:shadow-xl hover:shadow-slate-200/50 hover:-translate-y-1'
      }
      ${isSelected ? 'ring-2 ring-indigo-500 ring-offset-2' : ''}
      cursor-pointer
    `}>
      {/* Absent Overlay / Indicator */}
      {employee.is_absent && (
        <div className="absolute top-0 right-0 left-0 h-1 bg-rose-500"></div>
      )}

      <div className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between mb-5">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div
                className="w-14 h-14 rounded-2xl flex items-center justify-center text-white text-xl font-bold shadow-inner"
                style={{ backgroundColor: employee.avatar_color }}
              >
                {employee.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div className={`
                absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white
                ${employee.is_absent ? 'bg-rose-500' : 'bg-emerald-500'}
              `}></div>
            </div>
            <div>
              <h3 className="font-bold text-slate-900 leading-tight">{employee.name}</h3>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{employee.role}</p>
            </div>
          </div>

          {employee.is_absent && (
            <div className="flex flex-col items-end">
              <span className="px-2 py-1 bg-rose-500 text-white text-[10px] font-bold rounded-lg shadow-sm shadow-rose-200 uppercase tracking-widest">
                Absent
              </span>
            </div>
          )}
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3 mb-5">
          <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
            <p className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">Department</p>
            <p className="text-xs font-bold text-slate-700 truncate">{employee.department}</p>
          </div>
          <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
            <p className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">Current Load</p>
            <div className={`px-1.5 py-0.5 inline-block rounded text-[10px] font-bold uppercase ${getWorkloadColor(employee.workload)}`}>
              {employee.workload}
            </div>
          </div>
        </div>

        {/* Task Progress */}
        <div className="mb-5">
          <div className="flex justify-between items-end mb-1.5">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Pending Tasks</p>
            <span className={`text-xs font-bold ${isHighLoad ? 'text-orange-600' : 'text-slate-700'}`}>
              {taskCount} {taskCount === 1 ? 'task' : 'tasks'}
            </span>
          </div>
          <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
            <div 
              className={`h-full transition-all duration-500 ${isHighLoad ? 'bg-orange-500' : 'bg-indigo-500'}`}
              style={{ width: `${Math.min(100, (taskCount / 8) * 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Skills */}
        <div className="mb-6">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Expertise</p>
          <div className="flex flex-wrap gap-1.5">
            {employee.skills.slice(0, 3).map((skill, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-white border border-slate-200 text-slate-600 text-[10px] font-bold rounded-lg"
              >
                {skill.skill}
              </span>
            ))}
            {employee.skills.length > 3 && (
              <span className="px-2 py-1 bg-slate-100 text-slate-500 text-[10px] font-bold rounded-lg">
                +{employee.skills.length - 3}
              </span>
            )}
          </div>
        </div>

        {/* Action Button */}
        <div className="flex gap-2">
          {employee.is_absent ? (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onReset()
              }}
              className="w-full py-2.5 px-4 bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-bold rounded-xl transition-all shadow-md shadow-emerald-100 flex items-center justify-center gap-2"
              disabled={isProcessing}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Mark as Returned
            </button>
          ) : (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onMarkAbsent()
              }}
              className={`
                w-full py-2.5 px-4 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-2 shadow-md
                ${isProcessing 
                  ? 'bg-slate-100 text-slate-400 cursor-not-allowed' 
                  : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-100'
                }
              `}
              disabled={isProcessing}
            >
              {isProcessing ? (
                <>
                  <div className="w-3 h-3 border-2 border-slate-300 border-t-slate-500 rounded-full animate-spin"></div>
                  Neural Syncing...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  Trigger Absence
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default EmployeeCard
