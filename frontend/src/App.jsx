import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { Zap, Plus } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import NewVideo from './pages/NewVideo'
import TaskDetail from './pages/TaskDetail'

function Layout({ children }) {
  const location = useLocation()
  const isNewPage = location.pathname === '/new'
  const isTaskPage = location.pathname.startsWith('/tasks/')

  return (
    <div className="min-h-screen bg-vf-bg flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-vf-card/80 backdrop-blur-md border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2 group">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-vf-purple to-vf-blue flex items-center justify-center group-hover:scale-105 transition-transform">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-vf-text tracking-tight">
                Visual<span className="text-vf-purple-light">Forge</span>
              </span>
            </Link>

            {!isNewPage && !isTaskPage && (
              <Link
                to="/new"
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-vf-purple hover:bg-vf-purple-light text-white font-medium rounded-lg transition-colors text-sm"
              >
                <Plus className="w-4 h-4" />
                <span className="hidden sm:inline">Novo Vídeo</span>
                <span className="sm:hidden">Novo</span>
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 py-6 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-vf-text-secondary text-sm">
            VisualForge &mdash; Geração automática de vídeos com IA
          </p>
        </div>
      </footer>
    </div>
  )
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/new" element={<NewVideo />} />
        <Route path="/tasks/:id" element={<TaskDetail />} />
      </Routes>
    </Layout>
  )
}
