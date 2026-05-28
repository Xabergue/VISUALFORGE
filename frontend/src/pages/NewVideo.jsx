import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Loader2, Sparkles, AlertTriangle } from 'lucide-react'
import { fetchStyles, createTask } from '../lib/api'
import StyleCard from '../components/StyleCard'

export default function NewVideo() {
  const [styles, setStyles] = useState([])
  const [selectedStyle, setSelectedStyle] = useState(null)
  const [config, setConfig] = useState({})
  const [subject, setSubject] = useState('')
  const [loading, setLoading] = useState(false)
  const [stylesLoading, setStylesLoading] = useState(true)
  const [error, setError] = useState(null)
  const [stylesError, setStylesError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    async function loadStyles() {
      try {
        const data = await fetchStyles()
        setStyles(data || [])
        setStylesError(null)
      } catch (err) {
        setStylesError(err.message)
        // Fallback styles when API is down
        setStyles([
          {
            id: 'stock_footage',
            name: 'Stock Footage',
            description: 'Vídeo com imagens de arquivo, narração e legendas',
            icon: '🎬',
            implemented: true,
            config_schema: {
              persona: { type: 'select', label: 'Persona', options: ['narrador', 'educador', 'casual', 'formal'], default: 'narrador' },
              language: { type: 'select', label: 'Idioma', options: ['pt-BR', 'en-US', 'es-ES'], default: 'pt-BR' },
              duration: { type: 'range', label: 'Duração (segundos)', min: 15, max: 120, default: 30 },
              voice: { type: 'select', label: 'Voz', options: ['female-1', 'male-1', 'female-2', 'male-2'], default: 'female-1' },
              music_file: { type: 'text', label: 'Arquivo de música', default: '' },
              subtitle_position: { type: 'select', label: 'Posição das legendas', options: ['bottom', 'top', 'center'], default: 'bottom' },
              subtitle_font: { type: 'select', label: 'Fonte das legendas', options: ['default', 'bold', 'outline'], default: 'default' },
              subtitle_mode: { type: 'select', label: 'Modo das legendas', options: ['word', 'sentence', 'full'], default: 'word' },
              orientation: { type: 'select', label: 'Orientação', options: ['landscape', 'portrait', 'square'], default: 'landscape' },
            }
          },
          {
            id: 'image_carousel',
            name: 'Carrossel de Imagens',
            description: 'Slideshow com imagens geradas por IA e narração',
            icon: '🖼️',
            implemented: false,
          },
          {
            id: 'talking_head',
            name: 'Talking Head',
            description: 'Avatar falante com lip-sync e expressões',
            icon: '🧑‍💬',
            implemented: false,
          },
          {
            id: 'reddit_story',
            name: 'Reddit Story',
            description: 'Histórias do Reddit com imagens e narração',
            icon: '📱',
            implemented: false,
          },
        ])
      } finally {
        setStylesLoading(false)
      }
    }
    loadStyles()
  }, [])

  // Initialize config with defaults when style is selected
  useEffect(() => {
    if (!selectedStyle?.config_schema) {
      setConfig({})
      return
    }
    const defaults = {}
    for (const [key, schema] of Object.entries(selectedStyle.config_schema)) {
      defaults[key] = schema.default !== undefined ? schema.default : ''
    }
    setConfig(defaults)
  }, [selectedStyle])

  const handleConfigChange = (key, value) => {
    setConfig(prev => ({ ...prev, [key]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!selectedStyle || !subject.trim()) return

    setLoading(true)
    setError(null)

    try {
      const task = await createTask({
        style: selectedStyle.id,
        subject: subject.trim(),
        config: config,
      })
      navigate(`/tasks/${task.id}`)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  const renderConfigField = (key, schema) => {
    const value = config[key]

    switch (schema.type) {
      case 'select':
        return (
          <div key={key}>
            <label className="block text-sm font-medium text-vf-text mb-2">
              {schema.label}
            </label>
            <select
              value={value || ''}
              onChange={(e) => handleConfigChange(key, e.target.value)}
              className="w-full px-3 py-2.5 bg-vf-bg border border-white/10 rounded-lg text-vf-text text-sm focus:outline-none focus:border-vf-purple focus:ring-1 focus:ring-vf-purple/50 transition-colors appearance-none cursor-pointer"
            >
              {schema.options?.map(opt => (
                <option key={opt} value={opt} className="bg-vf-card">
                  {opt}
                </option>
              ))}
            </select>
          </div>
        )

      case 'range':
        return (
          <div key={key}>
            <label className="block text-sm font-medium text-vf-text mb-2">
              {schema.label}
            </label>
            <div className="flex items-center gap-3">
              <input
                type="range"
                min={schema.min}
                max={schema.max}
                value={value || schema.default}
                onChange={(e) => handleConfigChange(key, Number(e.target.value))}
                className="flex-1 h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-vf-purple"
              />
              <span className="text-sm text-vf-purple-light font-medium min-w-[3rem] text-right">
                {value || schema.default}s
              </span>
            </div>
          </div>
        )

      case 'text':
        return (
          <div key={key}>
            <label className="block text-sm font-medium text-vf-text mb-2">
              {schema.label}
            </label>
            <input
              type="text"
              value={value || ''}
              onChange={(e) => handleConfigChange(key, e.target.value)}
              placeholder={schema.placeholder || ''}
              className="w-full px-3 py-2.5 bg-vf-bg border border-white/10 rounded-lg text-vf-text text-sm placeholder:text-vf-text-secondary/50 focus:outline-none focus:border-vf-purple focus:ring-1 focus:ring-vf-purple/50 transition-colors"
            />
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      {/* Back button */}
      <Link
        to="/"
        className="inline-flex items-center gap-2 text-vf-text-secondary hover:text-vf-text transition-colors mb-6 text-sm"
      >
        <ArrowLeft className="w-4 h-4" />
        Voltar ao painel
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main form */}
        <div className="lg:col-span-2 space-y-8">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-vf-text">Novo Vídeo</h1>
            <p className="text-vf-text-secondary mt-1">Escolha um estilo e configure seu vídeo</p>
          </div>

          {/* Style selection error */}
          {stylesError && (
            <div className="flex items-start gap-3 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm text-yellow-200">Usando estilos padrão (API offline)</p>
                <p className="text-xs text-yellow-200/60 mt-0.5">{stylesError}</p>
              </div>
            </div>
          )}

          {/* Step 1: Style selection */}
          <div>
            <h2 className="text-lg font-semibold text-vf-text mb-4 flex items-center gap-2">
              <span className="w-7 h-7 rounded-full bg-vf-purple/20 text-vf-purple-light text-sm font-bold flex items-center justify-center">1</span>
              Escolha o estilo
            </h2>

            {stylesLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-5 h-5 text-vf-purple animate-spin" />
                <span className="ml-2 text-vf-text-secondary text-sm">Carregando estilos...</span>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {styles.map(style => (
                  <StyleCard
                    key={style.id}
                    style={style}
                    selected={selectedStyle?.id === style.id}
                    onClick={setSelectedStyle}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Step 2: Configuration */}
          {selectedStyle && (
            <form onSubmit={handleSubmit}>
              <h2 className="text-lg font-semibold text-vf-text mb-4 flex items-center gap-2">
                <span className="w-7 h-7 rounded-full bg-vf-purple/20 text-vf-purple-light text-sm font-bold flex items-center justify-center">2</span>
                Configure o vídeo
              </h2>

              <div className="space-y-4 bg-vf-card border border-white/5 rounded-xl p-5 sm:p-6">
                {/* Subject field - always shown */}
                <div>
                  <label className="block text-sm font-medium text-vf-text mb-2">
                    Assunto do vídeo <span className="text-red-400">*</span>
                  </label>
                  <textarea
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    placeholder="Descreva o tema ou assunto do vídeo..."
                    rows={3}
                    required
                    className="w-full px-3 py-2.5 bg-vf-bg border border-white/10 rounded-lg text-vf-text text-sm placeholder:text-vf-text-secondary/50 focus:outline-none focus:border-vf-purple focus:ring-1 focus:ring-vf-purple/50 transition-colors resize-none"
                  />
                </div>

                {/* Dynamic config fields */}
                {selectedStyle.config_schema && Object.entries(selectedStyle.config_schema).map(([key, schema]) => (
                  renderConfigField(key, schema)
                ))}
              </div>

              {/* Error message */}
              {error && (
                <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              )}

              {/* Submit button */}
              <div className="mt-6">
                <button
                  type="submit"
                  disabled={loading || !subject.trim()}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3 bg-vf-purple hover:bg-vf-purple-light disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors text-sm shadow-lg shadow-vf-purple/20"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Gerando vídeo...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Gerar Vídeo
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Preview sidebar - desktop only */}
        <div className="hidden lg:block">
          <div className="sticky top-24">
            <div className="bg-vf-card border border-white/5 rounded-xl p-6">
              <h3 className="text-sm font-medium text-vf-text-secondary mb-4 uppercase tracking-wider">
                Pré-visualização
              </h3>

              {selectedStyle ? (
                <div className="space-y-4">
                  <div className="w-full aspect-video bg-vf-bg rounded-lg flex items-center justify-center border border-white/5">
                    <span className="text-4xl">{selectedStyle.icon}</span>
                  </div>

                  <div>
                    <p className="text-vf-text font-semibold">{selectedStyle.name}</p>
                    <p className="text-vf-text-secondary text-sm mt-1">{selectedStyle.description}</p>
                  </div>

                  {subject && (
                    <div className="pt-3 border-t border-white/5">
                      <p className="text-xs text-vf-text-secondary mb-1">Assunto</p>
                      <p className="text-sm text-vf-text">{subject}</p>
                    </div>
                  )}

                  {Object.keys(config).length > 0 && (
                    <div className="pt-3 border-t border-white/5 space-y-2">
                      <p className="text-xs text-vf-text-secondary mb-1">Configuração</p>
                      {Object.entries(config).map(([key, value]) => {
                        if (!value) return null
                        const schema = selectedStyle.config_schema?.[key]
                        return (
                          <div key={key} className="flex items-center justify-between text-sm">
                            <span className="text-vf-text-secondary">{schema?.label || key}</span>
                            <span className="text-vf-text font-medium">
                              {schema?.type === 'range' ? `${value}s` : String(value)}
                            </span>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              ) : (
                <div className="py-8 text-center">
                  <p className="text-vf-text-secondary text-sm">
                    Selecione um estilo para ver a pré-visualização
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
