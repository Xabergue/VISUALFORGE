import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Download, Loader2, AlertTriangle, CheckCircle2, Terminal, RefreshCw } from 'lucide-react'
import { fetchTask, getVideoUrl, createEventSource } from '../lib/api'
import TaskStatus from '../components/TaskStatus'
import VideoPlayer from '../components/VideoPlayer'

export default function TaskDetail() {
  const { id } = useParams()
  const [task, setTask] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [connected, setConnected] = useState(false)
  const logsEndRef = useRef(null)
  const eventSourceRef = useRef(null)

  const loadTask = useCallback(async () => {
    try {
      const data = await fetchTask(id)
      setTask(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    loadTask()
  }, [loadTask])

  // SSE connection for real-time updates
  useEffect(() => {
    if (!task) return
    // Only connect SSE for pending/running tasks
    if (task.status !== 'pending' && task.status !== 'running') return

    const es = createEventSource(id)
    eventSourceRef.current = es

    es.onopen = () => {
      setConnected(true)
    }

    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)

        setTask(prev => {
          if (!prev) return prev
          return {
            ...prev,
            status: data.status || prev.status,
            progress: data.progress != null ? data.progress : prev.progress,
            log: data.log != null ? data.log : prev.log,
          }
        })

        // If task completed or failed, close connection and do a final refresh
        if (data.status === 'done' || data.status === 'failed') {
          es.close()
          setConnected(false)
          // Final refresh to get complete data including output_path
          setTimeout(() => loadTask(), 500)
        }
      } catch {
        // ignore parse errors
      }
    }

    es.onerror = () => {
      setConnected(false)
      es.close()
      // Reconnect after a delay if task might still be running
      setTimeout(() => {
        loadTask()
      }, 5000)
    }

    return () => {
      es.close()
      setConnected(false)
    }
  }, [id, task?.status, loadTask])

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [task?.log])

  const progress = task?.progress || 0
  const videoUrl = task?.output_path ? getVideoUrl(task.output_path) : null

  // Parse log text into lines
  const logLines = (task?.log || '').split('\n').filter(line => line.trim())

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-6 h-6 text-vf-purple animate-spin" />
          <span className="ml-3 text-vf-text-secondary">Carregando tarefa...</span>
        </div>
      </div>
    )
  }

  if (error && !task) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <AlertTriangle className="w-12 h-12 text-yellow-500 mb-4" />
          <h2 className="text-lg font-semibold text-vf-text mb-2">Erro ao carregar</h2>
          <p className="text-vf-text-secondary mb-6 max-w-md">{error}</p>
          <button
            onClick={loadTask}
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
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      {/* Back button */}
      <Link
        to="/"
        className="inline-flex items-center gap-2 text-vf-text-secondary hover:text-vf-text transition-colors mb-6 text-sm"
      >
        <ArrowLeft className="w-4 h-4" />
        Voltar ao painel
      </Link>

      {/* Task header */}
      <div className="bg-vf-card border border-white/5 rounded-xl p-5 sm:p-6 mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
          <div className="flex items-center gap-3 min-w-0">
            <span className="text-2xl">{task.style === 'stock_footage' ? '🎬' : task.style === 'image_carousel' ? '🖼️' : task.style === 'reddit_story' ? '📱' : '🧑‍💬'}</span>
            <div className="min-w-0">
              <h1 className="text-lg sm:text-xl font-bold text-vf-text truncate">
                {task.subject || 'Sem assunto'}
              </h1>
              <p className="text-sm text-vf-text-secondary capitalize">
                {task.style?.replace(/_/g, ' ') || 'Vídeo'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <TaskStatus status={task.status} size="md" />
            {connected && (
              <span className="flex items-center gap-1.5 text-xs text-green-400">
                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                Ao vivo
              </span>
            )}
          </div>
        </div>

        {/* Progress bar */}
        {(task.status === 'running' || task.status === 'pending') && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-vf-text-secondary">Progresso</span>
              <span className="text-sm font-medium text-vf-purple-light">{progress}%</span>
            </div>
            <div className="w-full h-2.5 bg-white/5 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-vf-purple to-vf-blue rounded-full transition-all duration-700 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Video player when done */}
      {task.status === 'done' && videoUrl && (
        <div className="mb-6">
          <VideoPlayer src={videoUrl} title={task.subject} />
          <div className="mt-3 flex items-center gap-3">
            <a
              href={videoUrl}
              download
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-vf-purple hover:bg-vf-purple-light text-white font-medium rounded-lg transition-colors text-sm"
            >
              <Download className="w-4 h-4" />
              Baixar Vídeo
            </a>
          </div>
        </div>
      )}

      {/* Success message when done but no output */}
      {task.status === 'done' && !videoUrl && (
        <div className="mb-6 bg-green-500/10 border border-green-500/20 rounded-xl p-5 flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-green-300 font-medium">Vídeo gerado com sucesso!</p>
            <p className="text-green-300/60 text-sm mt-1">O vídeo será disponibilizado em breve.</p>
          </div>
        </div>
      )}

      {/* Error message when failed */}
      {task.status === 'failed' && (
        <div className="mb-6 bg-red-500/10 border border-red-500/20 rounded-xl p-5 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-red-300 font-medium">Falha na geração do vídeo</p>
            <p className="text-red-300/60 text-sm mt-1">
              Verifique os logs abaixo para mais detalhes sobre o erro.
            </p>
          </div>
        </div>
      )}

      {/* Logs area */}
      <div className="bg-[#0d0d0d] border border-white/5 rounded-xl overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/5 bg-vf-card/50">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-vf-text-secondary" />
            <span className="text-sm font-medium text-vf-text-secondary">Logs</span>
          </div>
          <span className="text-xs text-vf-text-secondary">
            {logLines.length} {logLines.length === 1 ? 'linha' : 'linhas'}
          </span>
        </div>

        <div className="max-h-96 overflow-y-auto p-4 font-mono text-xs leading-relaxed">
          {logLines.length === 0 ? (
            <p className="text-vf-text-secondary/50">
              {task.status === 'pending'
                ? 'Aguardando início do processamento...'
                : 'Nenhum log disponível.'
              }
            </p>
          ) : (
            logLines.map((log, i) => (
              <div key={i} className="text-vf-text-secondary/80 py-0.5 hover:text-vf-text-secondary transition-colors">
                <span className="text-vf-text-secondary/30 mr-2 select-none">{String(i + 1).padStart(3, ' ')}</span>
                {log}
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>
      </div>
    </div>
  )
}
