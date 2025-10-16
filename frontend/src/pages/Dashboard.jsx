import { useEffect, useState } from 'react'
import api from '../api/axiosInstance'
import Navbar from '../components/Navbar'
import SystemChart from '../components/SystemChart'
import AlertCard from '../components/AlertCard'

export default function Dashboard() {
    const [metricsHistory, setMetricsHistory] = useState([])
    const [alerts, setAlerts] = useState([])
    const [processes, setProcesses] = useState([])

    useEffect(() => {
        let canceled = false
        const tick = async () => {
            try {
                const [m, a] = await Promise.all([
                    api.get('/api/monitor/system'),
                    api.post('/api/anomaly/detect'),
                ])
                if (canceled) return
                const t = new Date().toLocaleTimeString()
                setMetricsHistory((prev) => [...prev.slice(-59), { t, cpu: m.data.cpu_percent, mem: m.data.memory_percent }])
                setProcesses(m.data.processes?.slice(0, 10) || [])
                setAlerts((prev) => [a.data, ...prev].slice(0, 10))
            } catch (e) {
                // ignore
            }
        }
        tick()
        const id = setInterval(tick, 3000)
        return () => { canceled = true; clearInterval(id) }
    }, [])

    const kill = async (pid) => {
        await api.post('/api/defense/trigger', { action: 'kill_process', pid })
    }

    return (
        <div className="min-h-screen bg-gray-950 text-gray-100">
            <Navbar />
            <div className="max-w-7xl mx-auto p-6 grid gap-6">
                <div className="grid md:grid-cols-2 gap-6">
                    <div>
                        <h2 className="mb-2 font-semibold">CPU</h2>
                        <SystemChart data={metricsHistory} dataKey="cpu" color="#22d3ee" />
                    </div>
                    <div>
                        <h2 className="mb-2 font-semibold">Memory</h2>
                        <SystemChart data={metricsHistory} dataKey="mem" color="#a78bfa" />
                    </div>
                </div>

                <div className="grid md:grid-cols-3 gap-6">
                    <div className="md:col-span-2">
                        <h2 className="mb-2 font-semibold">Threat Alerts</h2>
                        <div className="grid gap-3">
                            {alerts.map((a, i) => <AlertCard key={i} alert={a} />)}
                        </div>
                    </div>
                    <div>
                        <h2 className="mb-2 font-semibold">Top Processes</h2>
                        <div className="space-y-2">
                            {processes.map((p) => (
                                <div key={p.pid} className="flex items-center justify-between p-2 bg-gray-900 border border-gray-800 rounded">
                                    <div>
                                        <div className="text-sm">{p.name}</div>
                                        <div className="text-xs text-gray-400">PID {p.pid} | CPU {p.cpu_percent}% | MEM {p.memory_percent?.toFixed?.(2)}%</div>
                                    </div>
                                    <button onClick={() => kill(p.pid)} className="px-2 py-1 text-xs bg-red-600 hover:bg-red-500 rounded">Kill</button>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}


