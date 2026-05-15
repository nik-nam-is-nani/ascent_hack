import React from 'react'

function ManagerReport({ report, selectedEmployee, employees }) {
  const getEmployeeName = (employeeId) => {
    const emp = employees.find(e => e.id === employeeId)
    return emp ? emp.name : 'Unknown'
  }

  if (!report) {
    return (
      <div className="card p-8 text-center">
        <div className="text-gray-400 mb-2">
          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-1">No Report Available</h3>
        <p className="text-gray-500">
          Mark an employee as absent to generate the manager report
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
          <h1 key={idx} className="text-2xl font-bold text-gray-900 mb-4 mt-6">
            {line.replace('# ', '')}
          </h1>
        )
      } else if (line.startsWith('## ')) {
        elements.push(
          <h2 key={idx} className="text-xl font-semibold text-gray-900 mb-3 mt-4">
            {line.replace('## ', '')}
          </h2>
        )
      } else if (line.startsWith('### ')) {
        elements.push(
          <h3 key={idx} className="text-lg font-medium text-gray-900 mb-2 mt-3">
            {line.replace('### ', '')}
          </h3>
        )
      }
      // Lists
      else if (line.startsWith('- ')) {
        elements.push(
          <li key={idx} className="text-gray-700 ml-4 mb-1">
            {line.replace('- ', '')}
          </li>
        )
      }
      // Table
      else if (line.startsWith('|')) {
        const cells = line.split('|').filter(c => c.trim())

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
          <table key={`table-${idx}`} className="w-full mb-4 border">
            <thead>
              <tr className="bg-gray-50">
                {tableHeaders.map((h, i) => (
                  <th key={i} className="px-4 py-2 text-left text-sm font-medium text-gray-600 border-b">
                    {h.trim()}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tableRows.map((row, rowIdx) => (
                <tr key={rowIdx} className="border-b">
                  {row.map((cell, cellIdx) => (
                    <td key={cellIdx} className="px-4 py-2 text-sm text-gray-700">
                      {cell.trim()}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )
        inTable = false
        tableRows = []
        tableHeaders = []
      }
      // Regular paragraphs
      else if (line.trim()) {
        elements.push(
          <p key={idx} className="text-gray-700 mb-2">
            {line}
          </p>
        )
      }
    })

    return elements
  }

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Manager Report</h2>
          <p className="text-sm text-gray-500">
            Generated for {selectedEmployee ? getEmployeeName(selectedEmployee) : 'Unknown'}
          </p>
        </div>
        <button
          onClick={() => window.print()}
          className="btn-primary"
        >
          Print Report
        </button>
      </div>

      <div className="prose max-w-none">
        {renderMarkdown(report)}
      </div>
    </div>
  )
}

export default ManagerReport