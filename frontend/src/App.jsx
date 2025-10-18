import { Routes, Route } from 'react-router-dom'
import Dashboard from './components/dashboard.jsx'
import './App.css'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/dashboard" element={<Dashboard />} />
    </Routes>
  )
}

export default App
