import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function SystemChart({ data, color = '#6366f1', dataKey = 'cpu' }) {
    return (
        <div className="h-64 w-full bg-gray-900 border border-gray-800 rounded p-3">
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="t" stroke="#9ca3af" />
                    <YAxis stroke="#9ca3af" />
                    <Tooltip />
                    <Line type="monotone" dataKey={dataKey} stroke={color} dot={false} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    )
}


