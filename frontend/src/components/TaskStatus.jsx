import { Clock, Loader2, CheckCircle2, XCircle } from 'lucide-react'

const statusConfig = {
  pending: {
    label: 'Pendente',
    className: 'bg-white/10 text-vf-text-secondary',
    icon: Clock,
  },
  running: {
    label: 'Processando',
    className: 'bg-blue-500/20 text-blue-400',
    icon: Loader2,
    animate: true,
  },
  done: {
    label: 'Concluído',
    className: 'bg-green-500/20 text-green-400',
    icon: CheckCircle2,
  },
  failed: {
    label: 'Falhou',
    className: 'bg-red-500/20 text-red-400',
    icon: XCircle,
  },
}

export default function TaskStatus({ status, size = 'sm' }) {
  const config = statusConfig[status] || statusConfig.pending
  const Icon = config.icon

  const sizeClasses = size === 'sm'
    ? 'px-2.5 py-1 text-xs gap-1.5'
    : 'px-3 py-1.5 text-sm gap-2'

  const iconSize = size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'

  return (
    <span className={`
      inline-flex items-center font-medium rounded-full
      ${config.className} ${sizeClasses}
      ${config.animate ? 'animate-pulse-blue' : ''}
    `}>
      <Icon className={`${iconSize} ${config.animate ? 'animate-spin' : ''}`} />
      {config.label}
    </span>
  )
}
