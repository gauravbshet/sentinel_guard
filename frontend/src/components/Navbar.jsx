export default function Navbar() {
    const logout = () => {
        localStorage.removeItem('sg_token')
        location.href = '/login'
    }
    return (
        <div className="flex items-center justify-between px-6 py-3 bg-gray-900 border-b border-gray-800">
            <div className="font-semibold">SentinelGuard AI</div>
            <button onClick={logout} className="px-3 py-1 bg-red-600 hover:bg-red-500 rounded">Logout</button>
        </div>
    )
}


