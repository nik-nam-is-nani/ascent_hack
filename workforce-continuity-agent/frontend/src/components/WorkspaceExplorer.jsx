import React, { useState, useEffect, useMemo, useRef } from 'react'
import { 
  File, 
  Folder, 
  ChevronRight, 
  ChevronDown, 
  RefreshCw, 
  Github, 
  GitPullRequest, 
  GitBranch, 
  Terminal as TerminalIcon, 
  Search, 
  Play, 
  Code2, 
  Settings, 
  Cpu, 
  ExternalLink,
  Save,
  Command
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const API_BASE = 'http://127.0.0.1:8000'

const WorkspaceExplorer = ({
  activities = [],
  githubToken = '',
  repoUrl = '',
  onRepoUrlChange = () => {}
}) => {
  const [files, setFiles] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const [fileContent, setFileContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [activePRs, setActivePRs] = useState([])
  const [terminalLogs, setTerminalLogs] = useState([])
  const [isTerminalOpen, setIsTerminalOpen] = useState(true)
  const [activeSidebarTab, setActiveSidebarTab] = useState('files')
  
  const terminalRef = useRef(null)

  // Extract terminal-like commands from activities
  useEffect(() => {
    if (activities.length > 0) {
      const latest = activities[activities.length - 1]
      
      if (latest.details?.command) {
        setTerminalLogs(prev => [...prev, {
          id: Date.now(),
          type: 'cmd',
          text: `agent@ascent:~/workspace$ ${latest.details.command}`,
          time: new Date().toLocaleTimeString()
        }, {
          id: Date.now() + 1,
          type: 'out',
          text: 'Operation successful. Synchronizing neural buffer...',
          time: new Date().toLocaleTimeString()
        }])
      } else if (latest.phase === 'phase_1') {
        // Fallback for detection phase
        setTerminalLogs(prev => [...prev, {
          id: Date.now(),
          type: 'cmd',
          text: `agent@ascent:~/workspace$ ascent-cli scan --target ${latest.details?.employee_id || 'UNKNOWN'}`,
          time: new Date().toLocaleTimeString()
        }])
      }
    }
  }, [activities])

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [terminalLogs])

  const handleClone = async () => {
    if (!repoUrl) return
    setLoading(true)
    setTerminalLogs(prev => [...prev, {
      id: Date.now(),
      type: 'cmd',
      text: `agent@ascent:~/workspace$ git clone ${repoUrl} .`,
      time: new Date().toLocaleTimeString()
    }])
    
    try {
      const res = await fetch(`${API_BASE}/api/workspace/clone`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: repoUrl, github_token: githubToken })
      })
      if (res.ok) {
        setTerminalLogs(prev => [...prev, {
          id: Date.now() + 1,
          type: 'out',
          text: 'Cloning into \'.\'...\nremote: Enumerating objects: 45, done.\nremote: Counting objects: 100% (45/45), done.\nUnpacking objects: 100% (45/45), 12.45 KiB | 1.24 MiB/s, done.',
          time: new Date().toLocaleTimeString()
        }])
        fetchFiles()
      } else {
        const errData = await res.json()
        setTerminalLogs(prev => [...prev, {
          id: Date.now() + 1,
          type: 'err',
          text: `fatal: ${errData.detail || 'Authentication failed'}`,
          time: new Date().toLocaleTimeString()
        }])
      }
    } catch (err) {
      console.error('Clone failed:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchFiles = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/workspace/files`)
      const data = await res.json()
      setFiles(data.files || [])
    } catch (err) {
      console.error('Failed to fetch workspace files:', err)
    }
  }

  const fetchFileContent = async (path) => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/api/workspace/file/${encodeURIComponent(path)}`)
      const data = await res.json()
      setFileContent(data.content || '')
      setSelectedFile(path)
    } catch (err) {
      console.error('Failed to fetch file content:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchFiles()
    const interval = setInterval(fetchFiles, 5000)
    return () => clearInterval(interval)
  }, [])

  const githubDevUrl = useMemo(() => {
    if (!repoUrl) return null
    try {
      return repoUrl.replace('github.com', 'github.dev')
    } catch (e) {
      return null
    }
  }, [repoUrl])

  return (
    <div className="flex flex-col h-[800px] bg-[#1e1e1e] border border-[#333] rounded-2xl overflow-hidden shadow-2xl font-sans">
      {/* VS Code Title Bar */}
      <div className="h-10 bg-[#323233] flex items-center justify-between px-4 border-b border-[#252526] select-none">
        <div className="flex items-center gap-4">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-[#ff5f56]"></div>
            <div className="w-3 h-3 rounded-full bg-[#ffbd2e]"></div>
            <div className="w-3 h-3 rounded-full bg-[#27c93f]"></div>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-[#969696] font-medium">
            <Github className="w-3 h-3" />
            <span>{repoUrl ? repoUrl.split('/').pop() : 'No Workspace'} — Ascent Continuity IDE</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {githubDevUrl && (
            <a 
              href={githubDevUrl} 
              target="_blank" 
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3 py-1 bg-[#2d2d2d] hover:bg-[#3d3d3d] text-[#ccc] rounded text-[10px] font-bold transition-colors border border-[#444]"
            >
              <ExternalLink className="w-3 h-3" />
              OPEN IN GITHUB.DEV
            </a>
          )}
          <button className="text-[#969696] hover:text-white transition-colors">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="h-12 bg-[#252526] border-b border-[#1e1e1e] px-4 flex items-center gap-3">
        <input
          type="text"
          value={repoUrl}
          onChange={(e) => onRepoUrlChange(e.target.value)}
          placeholder="https://github.com/org/repo.git"
          className="flex-1 h-8 bg-[#1e1e1e] border border-[#3d3d3d] rounded px-3 text-xs text-[#d4d4d4] focus:outline-none focus:border-[#007acc]"
        />
        <button
          onClick={handleClone}
          disabled={loading || !repoUrl}
          className={`h-8 px-3 rounded text-[11px] font-bold border transition-colors ${
            loading || !repoUrl
              ? 'bg-[#2d2d2d] text-[#858585] border-[#3a3a3a] cursor-not-allowed'
              : 'bg-[#007acc] text-white border-[#0e639c] hover:bg-[#0e639c]'
          }`}
        >
          {loading ? 'SYNCING...' : 'SYNC TO IDE'}
        </button>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Activity Bar (Slim Left) */}
        <div className="w-12 bg-[#333333] flex flex-col items-center py-4 gap-6 border-r border-[#252526]">
          {[
            { id: 'files', icon: <File className="w-6 h-6" /> },
            { id: 'search', icon: <Search className="w-6 h-6" /> },
            { id: 'git', icon: <GitBranch className="w-6 h-6" /> },
            { id: 'debug', icon: <Play className="w-6 h-6" /> },
            { id: 'extensions', icon: <Code2 className="w-6 h-6" /> }
          ].map(tab => (
            <button 
              key={tab.id}
              onClick={() => setActiveSidebarTab(tab.id)}
              className={`p-1 transition-colors ${activeSidebarTab === tab.id ? 'text-white border-l-2 border-white' : 'text-[#858585] hover:text-white'}`}
            >
              {tab.icon}
            </button>
          ))}
          <div className="mt-auto flex flex-col items-center gap-6 pb-2">
             <Settings className="w-6 h-6 text-[#858585] hover:text-white cursor-pointer" />
          </div>
        </div>

        {/* Sidebar (File Explorer) */}
        <div className="w-64 bg-[#252526] flex flex-col border-r border-[#1e1e1e]">
          <div className="h-9 flex items-center px-4 justify-between">
            <span className="text-[11px] text-[#bbbbbb] font-bold uppercase tracking-wider">Explorer</span>
            <div className="flex gap-2">
               <RefreshCw 
                 className={`w-3.5 h-3.5 text-[#858585] cursor-pointer hover:text-white ${loading ? 'animate-spin' : ''}`} 
                 onClick={fetchFiles}
               />
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto">
            <div className="px-4 py-2 flex items-center gap-1 text-[11px] text-[#cccccc] font-bold bg-[#37373d]">
              <ChevronDown className="w-4 h-4" />
              <span>{repoUrl ? repoUrl.split('/').pop()?.toUpperCase() : 'WORKSPACE'}</span>
            </div>
            <div className="py-1">
              {files.map(file => (
                <button
                  key={file}
                  onClick={() => fetchFileContent(file)}
                  className={`w-full flex items-center gap-2 px-6 py-1 text-[13px] text-left transition-colors ${
                    selectedFile === file 
                      ? 'bg-[#37373d] text-white' 
                      : 'text-[#cccccc] hover:bg-[#2a2d2e]'
                  }`}
                >
                  <File className={`w-4 h-4 ${file.endsWith('.jsx') || file.endsWith('.tsx') ? 'text-blue-400' : 'text-slate-400'}`} />
                  <span className="truncate">{file}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Editor Area */}
        <div className="flex-1 flex flex-col bg-[#1e1e1e] overflow-hidden">
          {/* Tabs */}
          <div className="h-9 bg-[#252526] flex overflow-x-auto custom-scrollbar no-scrollbar">
            {selectedFile && (
              <div className="flex items-center gap-2 px-3 bg-[#1e1e1e] border-t border-t-[#007acc] h-full text-[12px] text-white min-w-[120px]">
                <File className="w-3.5 h-3.5 text-blue-400" />
                <span>{selectedFile.split('/').pop()}</span>
                <button className="ml-auto text-[#858585] hover:text-white">×</button>
              </div>
            )}
          </div>

          {/* Code Viewer */}
          <div className="flex-1 overflow-auto bg-[#1e1e1e] relative group">
            {selectedFile ? (
              <div className="p-4 flex gap-4 font-mono text-[13px] leading-relaxed">
                <div className="text-[#858585] text-right select-none w-8">
                  {fileContent.split('\n').map((_, i) => (
                    <div key={i}>{i + 1}</div>
                  ))}
                </div>
                <pre className="text-[#d4d4d4] flex-1 whitespace-pre">
                  <code>{fileContent}</code>
                </pre>
              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center gap-8 opacity-20">
                <Cpu className="w-48 h-48 text-[#cccccc]" />
                <div className="text-center">
                  <p className="text-2xl font-black text-white uppercase tracking-[0.5em] mb-4">Neural Workspace</p>
                  <div className="flex flex-col gap-3 text-sm text-[#cccccc] font-bold">
                    <p className="flex items-center gap-4 justify-center">
                      <span className="bg-[#333] px-2 py-0.5 rounded text-[10px]">CMD + P</span>
                      <span>Quick Open</span>
                    </p>
                    <p className="flex items-center gap-4 justify-center">
                      <span className="bg-[#333] px-2 py-0.5 rounded text-[10px]">CMD + SHIFT + P</span>
                      <span>Command Palette</span>
                    </p>
                    <p className="flex items-center gap-4 justify-center">
                      <span className="bg-[#333] px-2 py-0.5 rounded text-[10px]">CMD + J</span>
                      <span>Toggle Terminal</span>
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Integrated Terminal */}
          <AnimatePresence>
            {isTerminalOpen && (
              <motion.div 
                initial={{ height: 0 }}
                animate={{ height: 200 }}
                exit={{ height: 0 }}
                className="bg-[#1e1e1e] border-t border-[#333] flex flex-col"
              >
                <div className="h-9 bg-[#1e1e1e] flex items-center px-4 justify-between border-b border-[#252526]">
                  <div className="flex gap-4 h-full">
                    <button className="text-[11px] text-white font-bold uppercase tracking-wider border-b border-white h-full px-1">Terminal</button>
                    <button className="text-[11px] text-[#858585] font-bold uppercase tracking-wider hover:text-white transition-colors h-full px-1">Output</button>
                    <button className="text-[11px] text-[#858585] font-bold uppercase tracking-wider hover:text-white transition-colors h-full px-1">Debug Console</button>
                  </div>
                  <div className="flex gap-3 text-[#858585]">
                     <button onClick={() => setTerminalLogs([])} className="hover:text-white transition-colors"><RefreshCw className="w-3.5 h-3.5" /></button>
                     <button onClick={() => setIsTerminalOpen(false)} className="hover:text-white transition-colors">×</button>
                  </div>
                </div>
                <div 
                  ref={terminalRef}
                  className="flex-1 p-4 font-mono text-[12px] overflow-y-auto scroll-smooth custom-scrollbar"
                >
                  {terminalLogs.length === 0 && (
                    <div className="text-[#858585]">Welcome to Ascent Neural Terminal v4.0. Agent connection active.</div>
                  )}
                  {terminalLogs.map((log) => (
                    <div key={log.id} className={`mb-1 ${log.type === 'err' ? 'text-rose-400' : log.type === 'cmd' ? 'text-white' : 'text-emerald-400'}`}>
                      <span className="opacity-50 mr-2">[{log.time}]</span>
                      <span className="whitespace-pre-wrap">{log.text}</span>
                    </div>
                  ))}
                  <div className="flex items-center gap-2 text-white mt-1">
                     <span className="text-[#00ff00]">agent@ascent:~/workspace$</span>
                     <span className="w-2 h-4 bg-white animate-pulse"></span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* VS Code Status Bar */}
      <div className="h-6 bg-[#007acc] flex items-center justify-between px-3 text-[11px] text-white select-none">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 hover:bg-[#1f8ad2] px-2 h-full cursor-pointer transition-colors">
            <GitBranch className="w-3 h-3" />
            <span>main*</span>
          </div>
          <div className="flex items-center gap-1.5 hover:bg-[#1f8ad2] px-2 h-full cursor-pointer transition-colors">
            <RefreshCw className="w-3 h-3" />
            <span>Synchronized</span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 hover:bg-[#1f8ad2] px-2 h-full cursor-pointer transition-colors">
             Ln 1, Col 1
          </div>
          <div className="flex items-center gap-1.5 hover:bg-[#1f8ad2] px-2 h-full cursor-pointer transition-colors">
             UTF-8
          </div>
          <div className="flex items-center gap-1.5 hover:bg-[#1f8ad2] px-2 h-full cursor-pointer transition-colors">
             JavaScript
          </div>
          <div className="flex items-center gap-1.5 hover:bg-[#1f8ad2] px-2 h-full cursor-pointer transition-colors">
             <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>
             <span>Neural Sync On</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default WorkspaceExplorer
