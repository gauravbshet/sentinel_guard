import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './index.css'
import Dashboard from './components/dashboard.jsx'
import Login from './components/Login.jsx'
import Logs from './components/Logs.jsx'

// Auth guard components
function RequireAuth({ children }) {
  const token = localStorage.getItem('sg_token')
  return token ? children : <Navigate to="/login" replace />
}

function PublicOnly({ children }) {
  const token = localStorage.getItem('sg_token')
  return token ? <Navigate to="/" replace /> : children
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<PublicOnly><Login /></PublicOnly>} />
        <Route path="/" element={<RequireAuth><Dashboard /></RequireAuth>} />
        <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
        <Route path="/logs" element={<RequireAuth><Logs /></RequireAuth>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)