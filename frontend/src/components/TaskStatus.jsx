const C = {
  pending: { label: 'Pendente', bg: 'bg-gray-700/50', text: 'text-gray-300', dot: 'bg-gray-400' },
  running: { label: 'Gerando', bg: 'bg-blue-500/15', text: 'text-blue-400', dot: 'bg-blue-400', animate: true },
  done: { label: 'Concluído', bg: 'bg-emerald-500/15', text: 'text-emerald-400', dot: 'bg-emerald-400' },
  failed: { label: 'Falhou', bg: 'bg-red-500/15', text: 'text-red-400', dot: 'bg-red-400' },
}
export default function TaskStatus({ status, size = 'sm' }) {
  const c = C[status] || C.pending
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-medium ${c.bg} ${c.text} ${size === 'sm' ? 'text-xs px-2.5 py-1' : 'text-sm px-3 py-1.5'}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot} ${c.animate ? 'animate-pulse' : ''}`} />
      {c.label}
    </span>
  )
}
