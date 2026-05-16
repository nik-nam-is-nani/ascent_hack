import React, { useState } from 'react'

const API_BASE = 'http://127.0.0.1:8000'

function WebhookTrigger({ isProcessing, setIsProcessing, onTrigger, employees, githubToken, repoUrl }) {
  const [employeeId, setEmployeeId] = useState('')
  const [source, setSource] = useState('webhook')
  const [reason, setReason] = useState('')
  const [webhookResponse, setWebhookResponse] = useState(null)
  const [showCurl, setShowCurl] = useState(false)

  const handleWebhookTrigger = async () => {
    if (!employeeId.trim()) return
    setIsProcessing(true)
    setWebhookResponse(null)

    try {
      const res = await fetch(`${API_BASE}/webhook/absence`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          employee_id: employeeId.trim(),
          source: source,
          reason: reason || `Triggered via ${source}`,
          github_token: githubToken,
          github_repo_url: repoUrl
        })
      })
      const data = await res.json()
      setWebhookResponse({ ok: res.ok, data })
      if (res.ok) onTrigger(employeeId.trim())
    } catch (err) {
      setWebhookResponse({ ok: false, data: { error: err.message } })
    } finally {
      setIsProcessing(false)
    }
  }

  const handleDirectTrigger = async () => {
    if (!employeeId.trim()) return
    setIsProcessing(true)
    setWebhookResponse(null)

    try {
      const res = await fetch(`${API_BASE}/api/absence/${employeeId.trim()}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          github_token: githubToken,
          github_repo_url: repoUrl
        })
      })
      const data = await res.json()
      setWebhookResponse({ ok: res.ok, data })
      if (res.ok) onTrigger(employeeId.trim())
    } catch (err) {
      setWebhookResponse({ ok: false, data: { error: err.message } })
    } finally {
      setIsProcessing(false)
    }
  }

  const curlExample = `curl -X POST ${API_BASE}/webhook/absence \\
  -H "Content-Type: application/json" \\
  -d '{"employee_id": "${employeeId || 'EMP-001'}", "source": "hr-system", "reason": "sick leave"}'`

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-50 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">Webhook / Custom Trigger</h3>
              <p className="text-xs text-slate-500">Trigger absence pipeline via webhook or direct API call</p>
            </div>
          </div>
          <button
            onClick={() => setShowCurl(!showCurl)}
            className="text-xs text-indigo-600 font-semibold hover:text-indigo-800 transition-colors"
          >
            {showCurl ? 'Hide' : 'Show'} cURL
          </button>
        </div>
      </div>

      {/* Input Form */}
      <div className="p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Employee ID Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Employee ID</label>
            <div className="relative">
              <select
                value={employeeId}
                onChange={(e) => setEmployeeId(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all appearance-none"
              >
                <option value="">Select or type below...</option>
                {employees.map(emp => (
                  <option key={emp.id} value={emp.id}>
                    {emp.id} - {emp.name} ({emp.role})
                  </option>
                ))}
              </select>
              <svg className="w-4 h-4 text-slate-400 absolute right-3 top-3 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Or type custom ID..."
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              className="w-full mt-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
            />
          </div>

          {/* Source Select */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Source</label>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
            >
              <option value="webhook">Webhook</option>
              <option value="hr-system">HR System</option>
              <option value="calendar">Calendar</option>
              <option value="slack">Slack</option>
              <option value="manual">Manual</option>
            </select>
          </div>

          {/* Reason Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Reason (optional)</label>
            <input
              type="text"
              placeholder="e.g., sick leave, vacation..."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleWebhookTrigger}
            disabled={!employeeId.trim() || isProcessing}
            className="flex items-center gap-2 px-5 py-2.5 bg-amber-500 hover:bg-amber-600 disabled:bg-slate-300 disabled:cursor-not-allowed text-white text-sm font-bold rounded-xl transition-all shadow-lg shadow-amber-200"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            {isProcessing ? 'Processing...' : 'Trigger Webhook'}
          </button>

          <button
            onClick={handleDirectTrigger}
            disabled={!employeeId.trim() || isProcessing}
            className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white text-sm font-bold rounded-xl transition-all shadow-lg shadow-indigo-200"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {isProcessing ? 'Processing...' : 'Direct API Call'}
          </button>

          <span className="text-xs text-slate-400">
            Webhook: POST /webhook/absence &nbsp;|&nbsp; Direct: POST /api/absence/{`{id}`}
          </span>
        </div>

        {/* cURL Example */}
        {showCurl && (
          <div className="bg-slate-900 rounded-xl p-4 overflow-x-auto">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-slate-400 font-mono">cURL Example</span>
              <button
                onClick={() => navigator.clipboard.writeText(curlExample)}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-mono"
              >
                Copy
              </button>
            </div>
            <pre className="text-xs text-emerald-400 font-mono whitespace-pre-wrap">{curlExample}</pre>
          </div>
        )}

        {/* Response */}
        {webhookResponse && (
          <div className={`rounded-xl p-4 border ${webhookResponse.ok ? 'bg-emerald-50 border-emerald-200' : 'bg-rose-50 border-rose-200'}`}>
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-2 h-2 rounded-full ${webhookResponse.ok ? 'bg-emerald-500' : 'bg-rose-500'}`}></div>
              <span className={`text-xs font-bold ${webhookResponse.ok ? 'text-emerald-700' : 'text-rose-700'}`}>
                {webhookResponse.ok ? 'Success' : 'Error'}
              </span>
            </div>
            <pre className="text-xs text-slate-600 font-mono whitespace-pre-wrap overflow-auto max-h-32">
              {JSON.stringify(webhookResponse.data, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}

export default WebhookTrigger
