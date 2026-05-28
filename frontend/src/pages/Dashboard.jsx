import { useState, useEffect, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Plus, Trash2, Video, AlertTriangle, RefreshCw, ArrowRight, Clock } from 'lucide-react'
import { fetchTasks, deleteTask } from '../lib/api'
import TaskStatus from '../components/TaskStatus'

function formatRelativeTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now - date
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffSeconds < 60) return 'agora mesmo'
  if (diffMinutes < 60) return `há ${diffMinutes} min`
  if (diffHours < 24) return `há ${diffHours}h`
  return `há ${diffDays}d`
}

export default function Dashboard() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [deleting, setDeleting] = useState(null)
  const navigate = useNavigate()

  const loadTasks = useCallback(async () => {
    try {
      const data = await fetchTasks()
      setTasks(data || [])
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadTasks()
  }, [loadTasks])

  // Auto-refresh while any task is running
  useEffect(() => {
    const hasRunning = tasks.some(t => t.status === 'running')
    if (!hasRunning) return

    const interval = setInterval(loadTasks, 5000)
    return () => clearInterval(interval)
  }, [tasks, loadTasks])

  const handleDelete = async (e, taskId) => {
    e.stopPropagation()
    if (!confirm('Tem certeza que deseja excluir esta tarefa?')) return

    setDeleting(taskId)
    try {
      await deleteTask(taskId)
      setTasks(prev => prev.filter(t => t.id !== taskId))
    } catch (err) {
      alert('Erro ao excluir tarefa: ' + err.message)
    } finally {
      setDeleting(null)
    }
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex items-center justify-center py-20">
          <RefreshCw className="w-6 h-6 text-vf-purple animate-spin" />
          <span className="ml-3 text-vf-text-secondary">Carregando tarefas...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <AlertTriangle className="w-12 h-12 text-yellow-500 mb-4" />
          <h2 className="text-lg font-semibold text-vf-text mb-2">Erro ao carregar</h2>
          <p className="text-vf-text-secondary mb-6 max-w-md">{error}</p>
          <button
            onClick={loadTasks}
            className="inline-flex items-center gap-2 px-4 py-2 bg-vf-card hover:bg-vf-card-hover text-vf-text rounded-lg transition-colors border border-white/10"
          >
            <RefreshCw className="w-4 h-4" />
            Tentar novamente
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      {/* Page header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-vf-text">Meus Vídeos</h1>
          <p className="text-vf-text-secondary mt-1 text-sm sm:text-base">
            Gerencie suas tarefas de geração de vídeo
          </p>
        </div>
        <Link
          to="/new"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-vf-purple hover:bg-vf-purple-light text-white font-medium rounded-lg transition-colors text-sm shadow-lg shadow-vf-purple/20"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">Novo Vídeo</span>
          <span className="sm:hidden">Novo</span>
        </Link>
      </div>

      {/* Task grid or empty state */}
      {tasks.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-20 h-20 rounded-2xl bg-vf-card flex items-center justify-center mb-6">
            <Video className="w-10 h-10 text-vf-text-secondary" />
          </div>
          <h2 className="text-xl font-semibold text-vf-text mb-2">Nenhum vídeo ainda</h2>
          <p className="text-vf-text-secondary mb-8 max-w-md">
            Crie seu primeiro vídeo automaticamente com IA. Escolha um estilo e deixe o VisualForge trabalhar para você.
          </p>
          <Link
            to="/new"
            className="inline-flex items-center gap-2 px-6 py-3 bg-vf-purple hover:bg-vf-purple-light text-white font-medium rounded-lg transition-colors shadow-lg shadow-vf-purple/20"
          >
            <Plus className="w-5 h-5" />
            Criar Primeiro Vídeo
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {tasks.map(task => (
            <div
              key={task.id}
              onClick={() => navigate(`/tasks/${task.id}`)}
              className="group relative bg-vf-card hover:bg-vf-card-hover border border-white/5 hover:border-white/10 rounded-xl p-5 transition-all duration-200 cursor-pointer"
            >
              {/* Delete button */}
              <button
                onClick={(e) => handleDelete(e, task.id)}
                disabled={deleting === task.id}
                className="absolute top-3 right-3 p-1.5 rounded-lg bg-transparent hover:bg-red-500/20 text-vf-text-secondary hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                title="Excluir tarefa"
              >
                <Trash2 className="w-4 h-4" />
              </button>

              {/* Style name */}
              <div className="flex items-center gap-2 mb-3">
                <span className="text-lg">{task.style === 'stock_footage' ? '🎬' : '🎨'}</span>
                <span className="text-sm font-medium text-vf-purple-light capitalize">
                  {task.style?.replace(/_/g, ' ') || 'Vídeo'}
                </span>
              </div>

              {/* Subject */}
              <h3 className="text-vf-text font-medium mb-3 line-clamp-2 leading-snug">
                {task.subject || 'Sem assunto'}
              </h3>

              {/* Status and time */}
              <div className="flex items-center justify-between mt-auto pt-3 border-t border-white/5">
                <TaskStatus status={task.status} />
                <div className="flex items-center gap-1.5 text-vf-text-secondary text-xs">
                  <Clock className="w-3 h-3" />
                  {formatRelativeTime(task.created_at)}
                </div>
              </div>

              {/* Progress bar for running tasks */}
              {task.status === 'running' && task.progress != null && (
                <div className="mt-3">
                  <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-vf-purple to-vf-blue rounded-full transition-all duration-500"
                      style={{ width: `${task.progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-vf-text-secondary mt-1">{task.progress}% concluído</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
