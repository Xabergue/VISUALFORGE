import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { listStyles, createTask } from '../lib/api'
import StyleCard from '../components/StyleCard'

export default function NewVideo() {
  const navigate = useNavigate(), [styles, setStyles] = useState([]), [sel, setSel] = useState(null), [subject, setSubject] = useState(''), [config, setConfig] = useState({}), [loading, setLoading] = useState(false), [error, setError] = useState(null)
  useEffect(() => { listStyles().then(setStyles).catch(e=>setError(e.message)) }, [])
  const selData = styles.find(s=>s.id===sel)
  const handleConfigChange = (k, v) => setConfig(p=>({...p, [k]: v}))
  const handleSubmit = async (e) => { e.preventDefault(); if(!sel||!subject.trim()) return; setLoading(true); try { const t = await createTask(sel, subject.trim(), config); navigate(`/tasks/${t.id}`) } catch(e) { setError(e.message); setLoading(false) } }
  const renderField = (key, schema) => {
    const val = config[key] ?? schema.default ?? ''
    const inputClass = "w-full bg-forge-bg border border-forge-border rounded-lg px-3 py-2.5 text-sm text-forge-text focus:outline-none focus:ring-2 focus:ring-forge-purple/50"
    if(schema.type==='select') return <div key={key}><label className="block text-sm font-medium text-forge-text mb-1">{schema.label}</label><select value={val} onChange={e=>handleConfigChange(key,e.target.value)} className={inputClass}>{(schema.options||[]).map(o=><option key={o} value={o}>{o}</option>)}</select></div>
    if(schema.type==='number') return <div key={key}><label className="block text-sm font-medium text-forge-text mb-1">{schema.label}</label><input type="number" value={val} min={schema.min} max={schema.max} onChange={e=>handleConfigChange(key,parseInt(e.target.value)||schema.default)} className={inputClass}/></div>
    if(schema.type==='textarea') return <div key={key}><label className="block text-sm font-medium text-forge-text mb-1">{schema.label}</label><textarea value={val||''} onChange={e=>handleConfigChange(key,e.target.value||null)} rows={4} className={inputClass+' resize-none'}/></div>
    return <div key={key}><label className="block text-sm font-medium text-forge-text mb-1">{schema.label}</label><input type="text" value={val||''} onChange={e=>handleConfigChange(key,e.target.value||null)} placeholder={schema.description||''} className={inputClass}/></div>
  }

  return (
    <div className="min-h-screen bg-forge-bg">
      <header className="border-b border-forge-border bg-forge-bg/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center gap-4">
          <button onClick={()=>navigate('/')} className="p-2 rounded-lg hover:bg-forge-card text-forge-muted">? </button>
          <h1 className="text-lg font-bold text-forge-text">Novo Vídeo</h1>
        </div>
      </header>
      <main className="max-w-5xl mx-auto px-4 py-8">
        <form onSubmit={handleSubmit} className="space-y-10">
          <section>
            <h2 className="text-lg font-semibold text-forge-text mb-4">1. Escolha o Estilo</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {styles.map(s => <StyleCard key={s.id} style={s} selected={sel} onClick={setSel}/>)}
            </div>
          </section>
          {sel && selData && (
            <section>
              <h2 className="text-lg font-semibold text-forge-text mb-4">2. Configure o Vídeo</h2>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-6">
                  <div><label className="block text-sm font-medium text-forge-text mb-1">Tema do Vídeo *</label><input type="text" value={subject} onChange={e=>setSubject(e.target.value)} required className="w-full bg-forge-bg border border-forge-border rounded-lg px-4 py-3 text-sm text-forge-text focus:outline-none focus:ring-2 focus:ring-forge-purple/50" placeholder="Ex: Benefícios da inteligência artificial"/></div>
                  {selData.config_schema && <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-forge-surface p-5 rounded-xl border border-forge-border">{Object.entries(selData.config_schema).map(([k,s])=>renderField(k,s))}</div>}
                </div>
                <div>
                  <div className="bg-forge-surface rounded-xl border border-forge-border p-5 mb-4"><h3 className="text-sm font-semibold text-forge-text mb-2">{selData.name}</h3><p className="text-xs text-forge-muted">{selData.description}</p></div>
                  <button type="submit" disabled={loading||!subject.trim()||!selData.implemented} className="w-full py-3 rounded-lg bg-gradient-to-r from-forge-purple to-forge-purple-dark text-white font-semibold text-sm disabled:opacity-50">{loading?'Criando...':'Gerar Vídeo'}</button>
                </div>
              </div>
            </section>
          )}
          {error && <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 text-red-400 text-sm">{error}</div>}
        </form>
      </main>
    </div>
  )
}
