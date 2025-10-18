import { useEffect, useState } from 'react'
import { Activity, LogOut } from 'lucide-react'
import api from '../api/axiosInstance'

// Simple Navbar Component
function Navbar() {
    const handleLogout = () => {
        localStorage.removeItem('sg_token')
        window.location.href = '/login'
    }

    return (
        <nav className="bg-gray-900 border-b border-gray-800 px-6 py-4">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Activity className="text-cyan-400" size={28} />
                    <h1 className="text-2xl font-bold">SentinelGuard AI</h1>
                    <span className="text-sm text-gray-400 bg-gray-800 px-2 py-1 rounded">System Logs</span>
                </div>
                <div className="flex items-center gap-4">
                    <a href="/dashboard" className="px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors">
                        Dashboard
                    </a>
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 px-3 py-2 bg-red-600 hover:bg-red-500 rounded-lg transition-colors"
                    >
                        <LogOut className="w-4 h-4" />
                        Logout
                    </button>
                </div>
            </div>
        </nav>
    )
}

export default function Logs() {
    const [logs, setLogs] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                setError('')
                const { data } = await api.get('/api/monitor/logs?limit=100')
                setLogs(data.logs || [])
            } catch (err) {
                console.error('Failed to fetch logs:', err)
                setError('Failed to load logs. Please check your connection.')
                // Set some mock logs for demonstration
                setLogs([
                    {
                        id: 1,
                        timestamp: new Date().toISOString(),
                        label: 'System check completed',
                        score: 0.95
                    },
                    {
                        id: 2,
                        timestamp: new Date(Date.now() - 30000).toISOString(),
                        label: 'Security scan finished',
                        score: 0.87
                    }
                ])
            } finally {
                setLoading(false)
            }
        }

        fetchLogs()
    }, [])

    return (
        <div className="min-h-screen bg-gray-950 text-gray-100">
            <Navbar />
            <div className="max-w-6xl mx-auto p-6">
                <div className="flex items-center justify-between mb-6">
                    <h1 className="text-2xl font-semibold">System Logs</h1>
                    <div className="text-sm text-gray-400">
                        {logs.length} {logs.length === 1 ? 'log entry' : 'log entries'}
                    </div>
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-yellow-950/30 border border-yellow-900 rounded-lg">
                        <div className="text-yellow-400">{error}</div>
                    </div>
                )}

                {loading ? (
                    <div className="text-center py-12">
                        <div className="animate-spin w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full mx-auto mb-4"></div>
                        <div className="text-gray-400">Loading logs...</div>
                    </div>
                ) : logs.length === 0 ? (
                    <div className="text-center py-12 text-gray-500">
                        <div className="text-6xl mb-4">📋</div>
                        <div>No logs available</div>
                    </div>
                ) : (
                    <div className="grid gap-3">
                        {logs.map((log) => (
                            <div key={log.id} className="p-4 bg-gray-900 border border-gray-800 rounded-lg hover:border-gray-700 transition-colors">
                                <div className="flex items-start justify-between mb-2">
                                    <div className="text-sm font-medium text-gray-300">{log.label}</div>
                                    <div className="text-xs text-gray-400">
                                        {new Date(log.timestamp).toLocaleString()}
                                    </div>
                                </div>
                                {log.score !== undefined && (
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs text-gray-500">Score:</span>
                                        <span className={`text-sm font-medium ${log.score > 0.8 ? 'text-green-400' :
                                            log.score > 0.6 ? 'text-yellow-400' : 'text-red-400'
                                            }`}>
                                            {log.score.toFixed(3)}
                                        </span>
                                        <div className="flex-1 bg-gray-800 rounded-full h-1.5 ml-2">
                                            <div
                                                className={`h-1.5 rounded-full ${log.score > 0.8 ? 'bg-green-400' :
                                                    log.score > 0.6 ? 'bg-yellow-400' : 'bg-red-400'
                                                    }`}
                                                style={{ width: `${log.score * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}


