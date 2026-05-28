import { useState, useEffect, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { listTasks, deleteTask, checkHealth } from '../lib/api'
import TaskStatus from '../components/TaskStatus'

export default function Dashboard() {
  const [tasks, setTasks] = useState([]), [loading, setLoading] = useState(true), [online, setOnline] = useState(true), navigate = useNavigate()
  const fetchTasks = useCallback(async () => { try { setTasks(await listTasks()); setOnline(true) } catch (e) { if(e.status===0) setOnline(false) } finally { setLoading(false) } }, [])
  useEffect(() => { fetchTasks(); checkHealth().then(()=>setOnline(true)).catch(()=>setOnline(false)); const i = setInterval(() => { if(tasks.some(t=>t.status==='pending'||t.status==='running')) fetchTasks() }, 5000); return () => clearInterval(i) }, [fetchTasks, tasks])
  const handleDelete = async (e, id) => { e.stopPropagation(); if(!confirm('Deletar?')) return; await deleteTask(id); fetchTasks() }
  const icons = { stock_footage: '??', image_carousel: '???', reddit_story: '??', talking_head: '???' }
  const names = { stock_footage: 'Stock Footage', image_carousel: 'Carrossel', reddit_story: 'Reddit Story', talking_head: 'Talking Head' }
  const timeAgo = d => { if(!d) return ''; const m=Math.floor((Date.now()-new Date(d))/60000); if(m<1) return 'agora'; if(m<60) return m+'min'; const h=Math.floor(m/60); return h<24?h+'h':Math.floor(h/24)+'d' }

  return (
    <div className="min-h-screen bg-forge-bg">
      <header className="border-b border-forge-border bg-forge-bg/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-forge-purple to-forge-blue flex items-center justify-center text-white text-lg">??</div>
            <h1 className="text-lg font-bold text-forge-text">Visual<span className="text-forge-purple-light">Forge</span></h1>
          </div>
          <button onClick={() => navigate('/new')} disabled={!online} className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-forge-purple to-forge-purple-dark text-white font-semibold text-sm disabled:opacity-50">+ Novo Vídeo</button>
        </div>
      </header>
      {!online && <div className="bg-red-500/10 border-b border-red-500/20 px-4 py-3 text-center text-red-400 text-sm">Backend offline — verifique localhost:8000</div>}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {loading ? <div className="flex justify-center py-20"><div className="w-8 h-8 border-2 border-forge-purple border-t-transparent rounded-full animate-spin"/></div> :
        tasks.length === 0 ? (
          <div className="flex flex-col items-center py-24 text-center">
            <h2 className="text-xl font-semibold text-forge-text mb-2">Nenhum vídeo ainda</h2>
            <p className="text-forge-muted text-sm mb-8">Crie seu primeiro vídeo automatizado com IA.</p>
            <button onClick={() => navigate('/new')} className="px-6 py-3 rounded-lg bg-forge-purple text-white font-semibold text-sm">Criar Primeiro Vídeo</button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tasks.map(t => (
              <Link key={t.id} to={`/tasks/${t.id}`} className={`block p-5 rounded-xl border bg-forge-card border-forge-border hover:border-forge-purple/30 transition-all ${t.status==='running'?'running-glow':''}`}>
                <div className="flex items-start justify-between mb-3">
                  <span className="text-xl">{icons[t.style]||'??'}</span>
                  <TaskStatus status={t.status} />
                </div>
                <h3 className="text-sm font-semibold text-forge-text mb-3 line-clamp-2">{t.subject}</h3>
                {(t.status==='running'||t.status==='pending') && <div className="w-full h-1.5 rounded-full bg-forge-border mb-3 overflow-hidden"><div className="h-full rounded-full bg-gradient-to-r from-forge-purple to-forge-blue progress-bar-fill" style={{width:`${t.progress}%`}}/></div>}
                <div className="flex justify-between text-xs text-forge-muted"><span>{t.progress}%</span><span>{timeAgo(t.created_at)}</span></div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
