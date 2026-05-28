# -*- coding: utf-8 -*-
"""
Serviço de LLM — geração de roteiro e palavras-chave via OpenAI-compatible API.
"""

import os
import json
import re
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

# Cliente OpenAI compatível (usado com servidor local ou remoto)
client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:3000/v1"),
    api_key=os.getenv("LLM_API_KEY", "localkey"),
)

LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-thinking")

# Prompts de sistema por persona
PERSONA_PROMPTS = {
    "neutro": "Você é um narrador com tom informativo e direto. Seja claro e objetivo.",
    "educativo": "Você é um professor explicativo, didático e paciente. Explique conceitos de forma acessível.",
    "entretenimento": "Você é um narrador dinâmico, empolgado e coloquial. Use linguagem informal e envolvente.",
    "corporativo": "Você é um narrador formal, profissional e objetivo. Use linguagem corporativa adequada.",
}


def generate_script(subject: str, persona: str = "neutro", language: str = "pt-BR", duration: int = 60) -> str:
    """
    Gera um roteiro de vídeo baseado no tema e persona.
    O roteiro é dividido em segmentos separados por '---' para busca de palavras-chave.
    A duração em segundos guia o tamanho do roteiro.

    Returns:
        str: Roteiro com segmentos separados por '---'
    """
    persona_prompt = PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS["neutro"])

    # Estimar número de segmentos baseado na duração (~10s por segmento)
    num_segments = max(2, duration // 10)

    language_names = {
        "pt-BR": "português brasileiro",
        "en-US": "inglês americano",
        "es-ES": "espanhol",
    }
    lang_name = language_names.get(language, "português brasileiro")

    system_message = (
        f"{persona_prompt}\n\n"
        f"Você deve escrever um roteiro para um vídeo de aproximadamente {duration} segundos sobre o tema fornecido. "
        f"Escreva em {lang_name}.\n\n"
        f"REGRAS IMPORTANTES:\n"
        f"- Divida o roteiro em {num_segments} segmentos, separados por '---' (três hifens) em uma linha separada.\n"
        f"- Cada segmento deve ter cerca de 2-3 frases, correspondendo a aproximadamente 10 segundos de narração.\n"
        f"- O texto deve ser natural para narração — evite marcações, títulos ou formatação especial.\n"
        f"- Apenas o texto narrado, sem instruções de cena ou notas de produção.\n"
        f"- Seja conciso e direto ao ponto.\n"
    )

    user_message = f"Tema do vídeo: {subject}"

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        script = response.choices[0].message.content.strip()
        return script
    except Exception as e:
        raise RuntimeError(f"Erro ao gerar roteiro via LLM: {str(e)}")


def generate_keywords(script_segment: str) -> list:
    """
    Gera 2-3 palavras-chave de busca para um segmento do roteiro.
    As palavras-chave serão usadas para buscar vídeos de stock.

    Returns:
        list[str]: Lista de palavras-chave
    """
    system_message = (
        "Você é um assistente que gera palavras-chave para busca de vídeos de stock footage.\n"
        "Dado um trecho de roteiro de vídeo, gere 2-3 palavras-chave em inglês que representem "
        "visualmente o conteúdo do trecho. As palavras-chave devem ser úteis para encontrar "
        "vídeos de stock relevantes.\n\n"
        "RESPONDA APENAS com um JSON array de strings, sem explicação. Exemplo: [\"ocean waves\", \"beach sunset\"]"
    )

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Trecho do roteiro:\n{script_segment}"},
            ],
            temperature=0.3,
            max_tokens=200,
        )
        content = response.choices[0].message.content.strip()

        # Extrair JSON da resposta (pode estar dentro de code blocks)
        json_match = re.search(r'\[.*?\]', content, re.DOTALL)
        if json_match:
            keywords = json.loads(json_match.group())
            return keywords[:3]  # Limitar a 3 palavras-chave

        # Fallback: usar palavras do próprio segmento
        words = script_segment.split()[:3]
        return words
    except Exception as e:
        # Fallback simples: primeiras palavras significativas
        words = script_segment.split()[:3]
        return [w.strip(".,;:!?") for w in words if len(w) > 3][:3]
