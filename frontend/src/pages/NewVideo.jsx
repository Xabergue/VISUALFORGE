import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  ArrowLeft, Loader2, Sparkles, AlertTriangle,
  FileText, Tags, X, Plus, Check, RotateCcw, Wand2, Play
} from 'lucide-react'
import { fetchStyles, previewScript, createTask } from '../lib/api'
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

  // ---- Novos estados para o fluxo de revisão ----
  const [step, setStep] = useState('form')         // 'form' | 'preview'
  const [previewLoading, setPreviewLoading] = useState(false)
  const [script, setScript] = useState('')
  const [keywords, setKeywords] = useState([])      // array de strings
  const [newKeyword, setNewKeyword] = useState('')

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
              persona: { type: 'select', label: 'Persona', options: ['neutro', 'educativo', 'entretenimento', 'corporativo'], default: 'neutro' },
              language: { type: 'select', label: 'Idioma', options: ['pt-BR', 'en-US', 'es-ES'], default: 'pt-BR' },
              duration_seconds: { type: 'range', label: 'Duração (segundos)', min: 15, max: 300, default: 60 },
              voice: { type: 'select', label: 'Voz', options: ['pm_alex', 'pm_santa', 'pf_dora'], default: 'pm_alex' },
              music_file: { type: 'text', label: 'Arquivo de música', default: '' },
              subtitle_position: { type: 'select', label: 'Posição das legendas', options: ['bottom', 'top', 'center'], default: 'bottom' },
              subtitle_font: { type: 'select', label: 'Fonte das legendas', options: ['default', 'bold', 'italic'], default: 'default' },
              subtitle_mode: { type: 'select', label: 'Modo das legendas', options: ['whisper', 'edge'], default: 'whisper' },
              orientation: { type: 'select', label: 'Orientação', options: ['landscape', 'portrait'], default: 'landscape' },
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

  // ---- Gerar roteiro (preview) ----
  const handlePreview = async (e) => {
    e.preventDefault()
    if (!selectedStyle || !subject.trim()) return

    setPreviewLoading(true)
    setError(null)

    try {
      const result = await previewScript({
        subject: subject.trim(),
        config: config,
      })
      setScript(result.script)
      setKeywords(result.keywords || [])
      setStep('preview')
    } catch (err) {
      setError(err.message)
    } finally {
      setPreviewLoading(false)
    }
  }

  // ---- Confirmar e gerar vídeo ----
  const handleConfirm = async () => {
    setLoading(true)
    setError(null)

    try {
      const task = await createTask({
        style: selectedStyle.id,
        subject: subject.trim(),
        config: config,
        script: script,
        keywords: keywords,
      })
      navigate(`/tasks/${task.id}`)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  // ---- Keywords: adicionar e remover ----
  const handleAddKeyword = () => {
    const trimmed = newKeyword.trim()
    if (!trimmed || keywords.includes(trimmed)) return
    setKeywords(prev => [...prev, trimmed])
    setNewKeyword('')
  }

  const handleRemoveKeyword = (kw) => {
    setKeywords(prev => prev.filter(k => k !== kw))
  }

  const handleKeywordKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddKeyword()
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

  // ====================================================
  // STEP: PREVIEW (revisão do roteiro e keywords)
  // ====================================================
  if (step === 'preview') {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Back to form */}
        <button
          onClick={() => { setStep('form'); setError(null) }}
          className="inline-flex items-center gap-2 text-vf-text-secondary hover:text-vf-text transition-colors mb-6 text-sm"
        >
          <ArrowLeft className="w-4 h-4" />
          Voltar ao formulário
        </button>

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-vf-purple to-vf-blue flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-vf-text">Revisar Roteiro</h1>
              <p className="text-vf-text-secondary text-sm">Edite o roteiro e as palavras-chave antes de gerar o vídeo</p>
            </div>
          </div>
        </div>

        {/* Subject info */}
        <div className="bg-vf-card border border-white/5 rounded-xl p-4 mb-6 flex items-center gap-3">
          <span className="text-xl">{selectedStyle?.icon || '🎬'}</span>
          <div className="min-w-0 flex-1">
            <p className="text-vf-text font-medium truncate">{subject}</p>
            <p className="text-vf-text-secondary text-xs capitalize">{selectedStyle?.id?.replace(/_/g, ' ')}</p>
          </div>
          <span className="px-3 py-1 rounded-full bg-green-500/15 text-green-400 text-xs font-medium flex items-center gap-1">
            <Check className="w-3 h-3" />
            Roteiro gerado
          </span>
        </div>

        {/* Script textarea */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <label className="flex items-center gap-2 text-sm font-semibold text-vf-text">
              <FileText className="w-4 h-4 text-vf-purple-light" />
              Roteiro gerado
            </label>
            <span className="text-xs text-vf-text-secondary">
              {script.length} caracteres
            </span>
          </div>
          <textarea
            value={script}
            onChange={(e) => setScript(e.target.value)}
            rows={12}
            className="w-full px-4 py-3 bg-[#0d0d0d] border border-white/10 rounded-xl text-vf-text text-sm leading-relaxed font-mono placeholder:text-vf-text-secondary/50 focus:outline-none focus:border-vf-purple focus:ring-1 focus:ring-vf-purple/50 transition-colors resize-y"
          />
          <p className="text-xs text-vf-text-secondary mt-2 flex items-center gap-1.5">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-vf-purple-light" />
            Os segmentos são separados por <code className="bg-white/5 px-1.5 py-0.5 rounded text-vf-purple-light font-mono">---</code>. Edite livremente.
          </p>
        </div>

        {/* Keywords chips */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-3">
            <label className="flex items-center gap-2 text-sm font-semibold text-vf-text">
              <Tags className="w-4 h-4 text-vf-purple-light" />
              Palavras-chave
            </label>
            <span className="text-xs text-vf-text-secondary">
              {keywords.length} {keywords.length === 1 ? 'palavra' : 'palavras'}
            </span>
          </div>

          {/* Chips container */}
          <div className="bg-[#0d0d0d] border border-white/10 rounded-xl p-4 min-h-[80px]">
            <div className="flex flex-wrap gap-2 mb-3">
              {keywords.map((kw, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-vf-purple/15 border border-vf-purple/30 text-vf-purple-light rounded-lg text-sm font-medium group hover:bg-vf-purple/25 transition-colors"
                >
                  {kw}
                  <button
                    onClick={() => handleRemoveKeyword(kw)}
                    className="w-4 h-4 rounded-full flex items-center justify-center hover:bg-white/10 text-vf-text-secondary hover:text-red-400 transition-colors"
                    title="Remover"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
              {keywords.length === 0 && (
                <p className="text-vf-text-secondary/50 text-sm py-1">Nenhuma palavra-chave. Adicione abaixo.</p>
              )}
            </div>

            {/* Add keyword input */}
            <div className="flex items-center gap-2 mt-2 pt-3 border-t border-white/5">
              <input
                type="text"
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                onKeyDown={handleKeywordKeyDown}
                placeholder="Adicionar palavra-chave..."
                className="flex-1 px-3 py-2 bg-vf-bg border border-white/10 rounded-lg text-vf-text text-sm placeholder:text-vf-text-secondary/50 focus:outline-none focus:border-vf-purple focus:ring-1 focus:ring-vf-purple/50 transition-colors"
              />
              <button
                onClick={handleAddKeyword}
                disabled={!newKeyword.trim()}
                className="px-3 py-2 bg-vf-purple/20 hover:bg-vf-purple/30 disabled:opacity-30 disabled:cursor-not-allowed text-vf-purple-light rounded-lg transition-colors"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <button
            onClick={() => { setStep('form'); setError(null) }}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-vf-card hover:bg-vf-card-hover border border-white/10 text-vf-text font-medium rounded-xl transition-colors text-sm"
          >
            <RotateCcw className="w-4 h-4" />
            Voltar e Editar Config
          </button>
          <button
            onClick={handleConfirm}
            disabled={loading || !script.trim()}
            className="inline-flex items-center justify-center gap-2 px-8 py-3 bg-gradient-to-r from-vf-purple to-vf-blue hover:from-vf-purple-light hover:to-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all text-sm shadow-lg shadow-vf-purple/25 hover:shadow-vf-purple/40"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Gerando vídeo...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Confirmar e Gerar Vídeo
              </>
            )}
          </button>
        </div>
      </div>
    )
  }

  // ====================================================
  // STEP: FORM (seleção de estilo + configuração)
  // ====================================================
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
            <p className="text-vf-text-secondary mt-1">Escolha um estilo, configure e revise o roteiro antes de gerar</p>
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
            <form onSubmit={handlePreview}>
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
                <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              )}

              {/* Submit button — agora gera roteiro, não o vídeo */}
              <div className="mt-6">
                <button
                  type="submit"
                  disabled={previewLoading || !subject.trim()}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3 bg-gradient-to-r from-vf-purple to-vf-blue hover:from-vf-purple-light hover:to-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all text-sm shadow-lg shadow-vf-purple/20 hover:shadow-vf-purple/40"
                >
                  {previewLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Gerando roteiro...
                    </>
                  ) : (
                    <>
                      <Wand2 className="w-4 h-4" />
                      Gerar Roteiro
                    </>
                  )}
                </button>
                <p className="text-xs text-vf-text-secondary mt-2">
                  O roteiro será gerado pela IA para você revisar antes de criar o vídeo.
                </p>
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

                  {/* Fluxo visual */}
                  <div className="pt-3 border-t border-white/5">
                    <p className="text-xs text-vf-text-secondary mb-2">Fluxo de criação</p>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-xs">
                        <span className="w-5 h-5 rounded-full bg-vf-purple/20 text-vf-purple-light text-[10px] font-bold flex items-center justify-center">1</span>
                        <span className="text-vf-text-secondary">Configurar vídeo</span>
                        <Check className="w-3 h-3 text-green-400 ml-auto" />
                      </div>
                      <div className="w-px h-3 bg-white/10 ml-2.5" />
                      <div className="flex items-center gap-2 text-xs">
                        <span className="w-5 h-5 rounded-full bg-vf-purple/20 text-vf-purple-light text-[10px] font-bold flex items-center justify-center">2</span>
                        <span className={subject.trim() ? 'text-vf-text' : 'text-vf-text-secondary'}>Gerar roteiro</span>
                        {subject.trim() && <Sparkles className="w-3 h-3 text-vf-purple-light ml-auto" />}
                      </div>
                      <div className="w-px h-3 bg-white/10 ml-2.5" />
                      <div className="flex items-center gap-2 text-xs">
                        <span className="w-5 h-5 rounded-full bg-vf-purple/20 text-vf-purple-light text-[10px] font-bold flex items-center justify-center">3</span>
                        <span className="text-vf-text-secondary">Revisar e gerar</span>
                      </div>
                    </div>
                  </div>
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
