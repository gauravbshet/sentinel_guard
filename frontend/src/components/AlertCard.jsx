export default function AlertCard({ alert }) {
    const badge = alert.label === 'anomaly' ? 'bg-red-600' : 'bg-green-600'
    return (
        <div className="p-3 bg-gray-900 border border-gray-800 rounded">
            <div className="flex items-center justify-between">
                <div className={`text-xs px-2 py-1 rounded ${badge}`}>{alert.label}</div>
                <div className="text-xs text-gray-400">score: {alert.score?.toFixed?.(3)}</div>
            </div>
            <div className="mt-2 text-sm text-gray-300">CPU {alert.metrics?.cpu_percent}% | Mem {alert.metrics?.memory_percent}%</div>
        </div>
    )
}


