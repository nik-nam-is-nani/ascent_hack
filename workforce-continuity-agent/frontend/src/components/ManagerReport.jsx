import React, { useState, useEffect } from 'react'

function ManagerReport({ report, selectedEmployee, employees }) {
  const [pdfReports, setPdfReports] = useState([])

  useEffect(() => {
    fetch('/api/reports')
      .then(res => res.json())
      .then(data => setPdfReports(data.reports || []))
      .catch(() => {})
  }, [report])
  const getEmployee = (employeeId) => {
    return employees.find(e => e.id === employeeId)
  }

  const employee = selectedEmployee ? getEmployee(selectedEmployee) : null

  if (!report) {
    return (
      <div className="card p-12 text-center border-dashed border-2 border-slate-200 bg-slate-50/50">
        <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm border border-slate-100">
          <svg className="w-10 h-10 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="text-xl font-bold text-slate-900 mb-2">Intelligence Report Pending</h3>
        <p className="text-slate-500 max-w-sm mx-auto">
          No continuity reports have been generated yet. The system will compile a comprehensive report once an absence is processed.
        </p>
      </div>
    )
  }

  // Parse markdown to render
  const renderMarkdown = (markdown) => {
    const lines = markdown.split('\n')
    const elements = []
    let inTable = false
    let tableRows = []
    let tableHeaders = []

    lines.forEach((line, idx) => {
      // Headers
      if (line.startsWith('# ')) {
        elements.push(
          <h1 key={idx} className="text-3xl font-extrabold text-slate-900 mb-6 mt-8 pb-4 border-b border-slate-200">
            {line.replace('# ', '')}
          </h1>
        )
      } else if (line.startsWith('## ')) {
        elements.push(
          <h2 key={idx} className="text-xl font-bold text-slate-800 mb-4 mt-8 flex items-center gap-2">
            <div className="w-1.5 h-6 bg-indigo-600 rounded-full"></div>
            {line.replace('## ', '')}
          </h2>
        )
      } else if (line.startsWith('### ')) {
        elements.push(
          <h3 key={idx} className="text-lg font-bold text-slate-700 mb-3 mt-6">
            {line.replace('### ', '')}
          </h3>
        )
      }
      // Lists
      else if (line.startsWith('- ')) {
        elements.push(
          <li key={idx} className="text-slate-600 ml-5 mb-2 list-disc marker:text-indigo-500">
            {line.replace('- ', '')}
          </li>
        )
      }
      // Table
      else if (line.startsWith('|')) {
        const cells = line.split('|').filter(c => c.trim() || line.includes('||'))

        if (cells.some(c => c.includes('---'))) {
          return // Skip table separator
        }

        if (!inTable) {
          tableHeaders = cells
          inTable = true
        } else {
          tableRows.push(cells)
        }
      }
      // End of table
      else if (inTable && !line.startsWith('|')) {
        elements.push(
          <div key={`table-wrapper-${idx}`} className="overflow-hidden rounded-xl border border-slate-200 mb-6 shadow-sm">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50">
                  {tableHeaders.map((h, i) => (
                    <th key={i} className="px-4 py-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200">
                      {h.trim()}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white">
                {tableRows.map((row, rowIdx) => (
                  <tr key={rowIdx} className="hover:bg-slate-50/50 transition-colors">
                    {row.map((cell, cellIdx) => (
                      <td key={cellIdx} className="px-4 py-3 text-sm text-slate-600 border-b border-slate-100">
                        {cell.trim()}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
        inTable = false
        tableRows = []
        tableHeaders = []
      }
      // Regular paragraphs
      else if (line.trim()) {
        elements.push(
          <p key={idx} className="text-slate-600 mb-4 leading-relaxed">
            {line}
          </p>
        )
      }
    })

    return elements
  }

  return (
    <div className="space-y-6">
      {/* Report Action Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center text-2xl">
            📋
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">Report Strategy Summary</h2>
            <p className="text-xs text-slate-500 font-medium">Verified by Ascent Continuity Agent</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {pdfReports.length > 0 && (
            <a
              href={pdfReports[0].download_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl transition-all shadow-lg shadow-indigo-200"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download PDF Report
            </a>
          )}
          <button
            onClick={() => window.print()}
            className="flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl transition-all shadow-lg shadow-slate-200"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 00-2 2h2m2 4h10a2 2 0 002-2v-4a2 2 0 012-2H5a2 2 0 012 2v4a2 2 0 002 2z" />
            </svg>
            Print
          </button>
        </div>
      </div>

      {/* Main Report Document */}
      <div className="bg-white p-10 rounded-3xl border border-slate-200 shadow-xl shadow-slate-200/50 relative overflow-hidden print:p-0 print:border-none print:shadow-none">
        {/* watermark decoration */}
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-indigo-50 rounded-full opacity-50 blur-3xl"></div>
        <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-slate-50 rounded-full opacity-50 blur-3xl"></div>
        
        <div className="relative">
          {/* Header Info */}
          <div className="flex justify-between items-start mb-12">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-6 h-6 bg-indigo-600 rounded flex items-center justify-center text-white font-bold text-[10px]">AC</div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Ascent Intelligence</span>
              </div>
              <h1 className="text-4xl font-black text-slate-900 tracking-tighter">Continuity Report</h1>
              <p className="text-slate-500 font-medium">Strategic Workflow Reallocation</p>
            </div>
            <div className="text-right">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Status</p>
              <span className="px-3 py-1 bg-emerald-100 text-emerald-700 text-[10px] font-bold rounded-full uppercase tracking-wider">Verified</span>
            </div>
          </div>

          {/* Target Profile Card */}
          {employee && (
            <div className="mb-10 p-6 bg-slate-50 rounded-2xl border border-slate-100 flex items-center gap-6">
              <div 
                className="w-16 h-16 rounded-2xl flex items-center justify-center text-white text-2xl font-bold shadow-inner"
                style={{ backgroundColor: employee.avatar_color }}
              >
                {employee.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div className="grid grid-cols-3 flex-1 gap-4">
                <div>
                  <p className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter mb-0.5">Absent Employee</p>
                  <p className="font-bold text-slate-800 leading-tight">{employee.name}</p>
                </div>
                <div>
                  <p className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter mb-0.5">Role / Position</p>
                  <p className="font-bold text-slate-800 leading-tight">{employee.role}</p>
                </div>
                <div>
                  <p className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter mb-0.5">Department</p>
                  <p className="font-bold text-slate-800 leading-tight">{employee.department}</p>
                </div>
              </div>
            </div>
          )}

          <div className="prose prose-slate max-w-none">
            {renderMarkdown(report)}
          </div>

          {/* Report Footer */}
          <div className="mt-16 pt-8 border-t border-slate-100 flex justify-between items-center text-[10px] font-bold text-slate-400 uppercase tracking-widest">
            <div>System Generated: {new Date().toLocaleDateString()}</div>
            <div>Report ID: {Math.random().toString(36).substring(7).toUpperCase()}</div>
            <div>Ascent v1.0.4</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ManagerReport