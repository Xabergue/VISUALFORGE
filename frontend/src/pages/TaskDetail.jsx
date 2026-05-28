import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getTask, createTaskStream, getVideoUrl } from '../lib/api'
import TaskStatus from '../components/TaskStatus'
import VideoPlayer from '../components/VideoPlayer'

export default function TaskDetail() {
  const { id } = useParams(), navigate = useNavigate(), logRef = useRef(null)
  const [task, setTask] = useState(null), [loading, setLoading] = useState(true)
  useEffect(() => { getTask(id).then(d=>setTask(d)).catch(()=>{}).finally(()=>setLoading(false)) }, [id])
  useEffect(() => { if(!task||task.status==='done'||task.status==='failed') return; const es = createTaskStream(id, d=>setTask(p=>({...p,...d})), null, null); return ()=>es.close() }, [id, task])
  useEffect(() => { if(logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight }, [task?.log])
  const names = { stock_footage: 'Stock Footage', image_carousel: 'Carrossel', reddit_story: 'Reddit Story', talking_head: 'Talking Head' }

  if(loading) return <div className="min-h-screen bg-forge-bg flex items-center justify-center"><div className="w-8 h-8 border-2 border-forge-purple border-t-transparent rounded-full animate-spin"/></div>
  if(!task) return <div className="min-h-screen bg-forge-bg flex flex-col items-center justify-center"><h2 className="text-lg font-semibold text-red-400 mb-4">Task não encontrada</h2><button onClick={()=>navigate('/')} className="text-forge-purple-light">Voltar</button></div>

  return (
    <div className="min-h-screen bg-forge-bg">
      <header className="border-b border-forge-border bg-forge-bg/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button onClick={()=>navigate('/')} className="p-2 rounded-lg hover:bg-forge-card text-forge-muted">?</button>
            <div><h1 className="text-sm font-semibold text-forge-text leading-tight">{task.subject}</h1><p className="text-xs text-forge-muted">{names[task.style]}</p></div>
          </div>
          <TaskStatus status={task.status} size="md" />
        </div>
      </header>
      <main className="max-w-5xl mx-auto px-4 py-8 space-y-6">
        <div className="bg-forge-surface rounded-xl border border-forge-border p-5">
          <div className="flex justify-between mb-3"><span className="text-sm font-medium text-forge-text">Progresso</span><span className="text-sm font-semibold text-forge-purple-light">{task.progress}%</span></div>
          <div className="w-full h-3 rounded-full bg-forge-border overflow-hidden"><div className={`h-full rounded-full progress-bar-fill ${task.status==='done'?'bg-emerald-500':task.status==='failed'?'bg-red-500':'bg-gradient-to-r from-forge-purple to-forge-blue'}`} style={{width:`${task.progress}%`}}/></div>
        </div>
        {task.status==='done' && <div><VideoPlayer taskId={task.id}/><a href={getVideoUrl(task.id)} download className="block mt-3 py-2.5 rounded-lg bg-forge-purple text-white font-semibold text-sm text-center">Baixar Vídeo</a></div>}
        {task.status==='failed' && <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-5 text-red-400"><h3 className="text-sm font-semibold mb-1">Falha na geração</h3><p className="text-sm text-red-300/80">{task.log?.split('\n').filter(l=>l.startsWith('ERRO:')).pop()?.replace('ERRO: ','')||'Erro no processamento.'}</p></div>}
        <div className="bg-[#0d0d0d] rounded-xl border border-forge-border overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-forge-border bg-forge-surface/50"><span className="text-xs font-medium text-forge-muted uppercase tracking-wider">Logs</span>{(task.status==='running'||task.status==='pending')&&<span className="flex items-center gap-1.5 text-xs text-blue-400"><span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"/>Ao vivo</span>}</div>
          <div ref={logRef} className="p-4 h-72 overflow-y-auto log-terminal text-forge-muted">
            {task.log ? task.log.split('\n').map((l,i)=><div key={i} className={l.startsWith('ERRO:')?'text-red-400':l.includes('sucesso')?'text-emerald-400':''}><span className="text-forge-border mr-2">{String(i+1).padStart(3,'0')}</span>{l}</div>) : <span className="text-forge-border">Aguardando...</span>}
          </div>
        </div>
      </main>
    </div>
  )
}
