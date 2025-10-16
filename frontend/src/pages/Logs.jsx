import { useEffect, useState } from 'react'
import api from '../api/axiosInstance'
import Navbar from '../components/Navbar'

export default function Logs() {
    const [logs, setLogs] = useState([])
    useEffect(() => {
        (async () => {
            const { data } = await api.get('/api/monitor/logs?limit=100')
            setLogs(data.logs || [])
        })()
    }, [])

    return (
        <div className="min-h-screen bg-gray-950 text-gray-100">
            <Navbar />
            <div className="max-w-6xl mx-auto p-6">
                <h1 className="text-xl font-semibold mb-4">Logs</h1>
                <div className="grid gap-3">
                    {logs.map((l) => (
                        <div key={l.id} className="p-3 bg-gray-900 border border-gray-800 rounded">
                            <div className="text-xs text-gray-400">{l.timestamp}</div>
                            <div className="text-sm">{l.label} | score {l.score?.toFixed?.(3)}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}


