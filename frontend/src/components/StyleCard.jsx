export default function StyleCard({ style, selected, onClick }) {
  const isSel = selected === style.id, isDis = !style.implemented
  return (
    <button onClick={() => !isDis && onClick(style.id)} disabled={isDis}
      className={`relative w-full text-left p-5 rounded-xl border-2 transition-all duration-200 ${isDis ? 'border-forge-border/30 bg-forge-surface/30 opacity-50 cursor-not-allowed' : isSel ? 'border-forge-purple bg-forge-purple/10 shadow-lg shadow-forge-purple/10' : 'border-forge-border bg-forge-card hover:border-forge-purple/40'}`}>
      {isDis && <span className="absolute top-3 right-3 text-[10px] font-semibold uppercase tracking-wider bg-forge-border/50 text-forge-muted px-2 py-0.5 rounded-full">Em breve</span>}
      <h3 className={`text-sm font-semibold mb-1 ${isSel ? 'text-forge-purple-light' : 'text-forge-text'}`}>{style.name}</h3>
      <p className="text-xs text-forge-muted leading-relaxed">{style.description}</p>
      {isSel && <div className="absolute top-3 right-3 w-5 h-5 rounded-full bg-forge-purple flex items-center justify-center"><svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg></div>}
    </button>
  )
}
