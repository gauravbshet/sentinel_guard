import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/axiosInstance'

export default function Login() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [mode, setMode] = useState('login')
    const [error, setError] = useState('')

    const navigate = useNavigate()

    const submit = async (e) => {
        e.preventDefault()
        try {
            if (mode === 'signup') {
                await api.post('/api/auth/signup', { email, password })
            }
            const { data } = await api.post('/api/auth/login', { email, password })
            // Try several common shapes for returned access token (backend or Supabase)
            const token = data?.access_token || data?.data?.access_token || data?.data?.session?.access_token || data?.session?.access_token || data?.token
            if (!token) {
                // attempt to extract token from backend raw wrapper
                const raw = data?.raw || data
                let extracted = null
                try {
                    const parsed = typeof raw === 'string' ? JSON.parse(raw) : raw
                    extracted = parsed?.session?.access_token || parsed?.data?.access_token || parsed?.access_token
                } catch (e) {
                    extracted = null
                }
                if (extracted) {
                    localStorage.setItem('sg_token', extracted)
                    navigate('/dashboard')
                    return
                }

                setError('Login succeeded but no access token received: ' + JSON.stringify(raw))
                return
            }
            localStorage.setItem('sg_token', token)
            // SPA navigation to dashboard
            navigate('/dashboard')
        } catch (err) {
            setError(err.response?.data?.detail || 'Request failed')
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-950 text-gray-100">
            <form onSubmit={submit} className="w-full max-w-sm space-y-4 p-6 bg-gray-900 rounded-lg border border-gray-800">
                <h1 className="text-xl font-semibold">{mode === 'login' ? 'Login' : 'Sign Up'} - SentinelGuard AI</h1>
                {error && <div className="text-red-400 text-sm">{error}</div>}
                <input className="w-full px-3 py-2 bg-gray-800 rounded" placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                <input className="w-full px-3 py-2 bg-gray-800 rounded" placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                <button className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 rounded">{mode === 'login' ? 'Login' : 'Create Account'}</button>
                <button type="button" className="w-full py-2 bg-gray-700 hover:bg-gray-600 rounded" onClick={() => setMode(mode === 'login' ? 'signup' : 'login')}>
                    {mode === 'login' ? 'Need an account? Sign up' : 'Have an account? Login'}
                </button>
            </form>
        </div>
    )
}


