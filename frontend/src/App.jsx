import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import NewVideo from './pages/NewVideo'
import TaskDetail from './pages/TaskDetail'

export default function App() {
  return (
    <div className="min-h-screen bg-forge-bg text-forge-text font-sans">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/new" element={<NewVideo />} />
        <Route path="/tasks/:id" element={<TaskDetail />} />
      </Routes>
    </div>
  )
}
