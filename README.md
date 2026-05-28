# VisualForge

Plataforma local de geracao de videos automatizados com IA.
Escolha um estilo, configure os parametros e deixe a IA fazer o resto.

## Estilos disponiveis

- **Stock Footage Narrado** — Video narrado com clipes de stock footage relevantes ao tema
- **Carrossel de Imagens** — Em breve
- **Reddit Story Narrado** — Em breve
- **Talking Head** — Em breve

## Requisitos

- Python 3.11+
- Node.js 18+
- FFmpeg (instalado automaticamente pelo install.bat)
- LLM rodando localmente em localhost:3000 (ex: LM Studio, Ollama, jsputer-proxy)

## Instalacao

1. Clone o repositorio:
```bash
git clone https://github.com/Xabergue/VISUALFORGE.git
cd VISUALFORGE
```

2. Rode o script de instalacao (Windows):
```bash
install.bat
```

Ou instale manualmente:

```bash
# Backend
cd backend
uv venv
uv pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

3. Configure as variaveis de ambiente:
```bash
cp backend/.env.example backend/.env
# Edite o arquivo .env com suas chaves
```

## Configuracao

Edite o arquivo `backend/.env` com suas configuracoes:

```env
# LLM — servidor local compativel com OpenAI
LLM_BASE_URL=http://localhost:3000/v1
LLM_API_KEY=localkey
LLM_MODEL=deepseek-thinking

# Pexels — API para busca de videos de stock
PEXELS_API_KEY=your_pexels_key_here

# TTS — motor de sintese de voz
TTS_ENGINE=kokoro
TTS_DEFAULT_VOICE=pm_alex

# Whisper — modelo para geracao de legendas
WHISPER_MODEL=base
```

## Rodando o projeto

```bash
start.bat
```

Ou inicie os servicos separadamente:

```bash
# Backend (porta 8000)
start-backend.bat

# Frontend (porta 5173)
start-frontend.bat
```

Acesse:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Documentacao API: http://localhost:8000/docs

## Estrutura do projeto

```
visualforge/
├── backend/
│   ├── main.py                  # FastAPI entrypoint
│   ├── database.py              # SQLite + SQLAlchemy
│   ├── models/task.py           # Modelo da tabela tasks
│   ├── routers/
│   │   ├── tasks.py             # CRUD + SSE
│   │   └── styles.py            # Estilos disponiveis
│   ├── pipeline/
│   │   ├── base.py              # Classe base BasePipeline
│   │   ├── stock_footage.py     # Estilo 1 — completo
│   │   ├── image_carousel.py    # Estilo 2 — nao implementado
│   │   ├── reddit_story.py      # Estilo 3 — nao implementado
│   │   └── talking_head.py      # Estilo 4 — placeholder
│   ├── services/
│   │   ├── llm.py               # Chamadas a LLM (OpenAI compativel)
│   │   ├── tts.py               # Sintese de voz (Kokoro-82M)
│   │   ├── media.py             # Busca de midia (Pexels + local)
│   │   └── ffmpeg_service.py    # Montagem de video (FFmpeg)
│   ├── resource/
│   │   ├── fonts/               # Fontes para legendas
│   │   ├── songs/               # Musicas de fundo
│   │   └── local_media/         # Videos e imagens locais
│   └── output/                  # Videos gerados
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Dashboard.jsx    # Pagina inicial
│       │   ├── NewVideo.jsx     # Criacao de video
│       │   └── TaskDetail.jsx   # Acompanhamento em tempo real
│       ├── components/
│       │   ├── StyleCard.jsx    # Card de estilo
│       │   ├── TaskStatus.jsx   # Badge de status
│       │   └── VideoPlayer.jsx  # Player de video
│       └── lib/
│           └── api.js           # Chamadas ao backend
├── install.bat
├── start.bat
├── start-backend.bat
├── start-frontend.bat
└── README.md
```

## Stack

- **Backend:** [Python](https://python.org) + [FastAPI](https://fastapi.tiangolo.com) + [SQLAlchemy](https://sqlalchemy.org) + [SQLite](https://sqlite.org)
- **Frontend:** [React](https://react.dev) + [Vite](https://vitejs.dev) + [Tailwind CSS](https://tailwindcss.com)
- **LLM:** OpenAI-compatible API ([LM Studio](https://lmstudio.ai), [Ollama](https://ollama.ai))
- **TTS:** [Kokoro-82M](https://github.com/hexgrad/kokoro) (sintese de voz local)
- **Legendas:** [Whisper](https://github.com/openai/whisper) + [edge-tts](https://github.com/rany2/edge-tts)
- **Video:** [FFmpeg](https://ffmpeg.org) (montagem e renderizacao)
- **Midia:** [Pexels API](https://www.pexels.com/api/) (videos de stock)

## Personas disponiveis (Stock Footage)

| Persona | Descricao |
|---------|-----------|
| Neutro | Tom informativo e direto |
| Educativo | Explicativo, didatico, paciente |
| Entretenimento | Dinamico, empolgado, coloquial |
| Corporativo | Formal, profissional, objetivo |

## Vozes disponiveis (pt-BR)

| Voz | Descricao |
|-----|-----------|
| pm_alex | Masculino (padrao) |
| pm_santa | Masculino alternativo |
| pf_dora | Feminino |
