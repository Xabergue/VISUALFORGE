import { Check } from 'lucide-react'

export default function StyleCard({ style, selected, onClick }) {
  const isImplemented = style.implemented !== false
  const handleClick = () => {
    if (isImplemented && onClick) onClick(style)
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={!isImplemented}
      className={`
        relative w-full text-left p-5 rounded-xl border-2 transition-all duration-200
        ${isImplemented ? 'cursor-pointer' : 'cursor-not-allowed opacity-50'}
        ${selected
          ? 'border-vf-purple bg-vf-purple/10 shadow-lg shadow-vf-purple/10'
          : isImplemented
            ? 'border-white/10 bg-vf-card hover:border-white/20 hover:bg-vf-card-hover'
            : 'border-white/5 bg-vf-card'
        }
      `}
    >
      {/* Selected indicator */}
      {selected && (
        <div className="absolute top-3 right-3 w-6 h-6 rounded-full bg-vf-purple flex items-center justify-center">
          <Check className="w-4 h-4 text-white" />
        </div>
      )}

      {/* Em breve badge */}
      {!isImplemented && (
        <div className="absolute top-3 right-3 px-2.5 py-0.5 rounded-full bg-white/10 text-vf-text-secondary text-xs font-medium">
          Em breve
        </div>
      )}

      {/* Icon */}
      <div className={`
        w-12 h-12 rounded-lg flex items-center justify-center mb-4
        ${selected
          ? 'bg-vf-purple/20 text-vf-purple-light'
          : isImplemented
            ? 'bg-white/5 text-vf-text-secondary'
            : 'bg-white/5 text-vf-text-secondary/50'
        }
      `}>
        <span className="text-2xl">{style.icon || '🎬'}</span>
      </div>

      {/* Name */}
      <h3 className={`
        text-base font-semibold mb-1
        ${selected ? 'text-vf-text' : isImplemented ? 'text-vf-text' : 'text-vf-text-secondary'}
      `}>
        {style.name}
      </h3>

      {/* Description */}
      <p className="text-sm text-vf-text-secondary leading-relaxed">
        {style.description}
      </p>
    </button>
  )
}
