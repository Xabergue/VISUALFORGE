# -*- coding: utf-8 -*-
import os, json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:3000/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "localkey")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-thinking")

client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)

PERSONA_PROMPTS = {
    "neutro": "Voc� � um narrador profissional. Crie roteiros informativos e diretos, com tom imparcial e claro. Evite adjetivos excessivos e mantenha o texto objetivo.",
    "educativo": "Voc� � um professor dedicado. Crie roteiros explicativos, did�ticos e pacientes, que facilitem o aprendizado. Use exemplos e analogias quando apropriado.",
    "entretenimento": "Voc� � um criador de conte�do din�mico. Crie roteiros empolgados, coloquiais e envolventes, como um YouTuber. Use express�es naturais e mantenha o ritmo acelerado.",
    "corporativo": "Voc� � um apresentador corporativo. Crie roteiros formais, profissionais e objetivos, adequados para apresenta��es empresariais. Use vocabul�rio t�cnico quando necess�rio.",
}

def generate_script(subject: str, persona: str = "neutro", language: str = "pt-BR", duration_seconds: int = 60) -> str:
    word_count = int(duration_seconds * 2.5)
    system_prompt = PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS["neutro"])
    user_prompt = (
        f"Crie um roteiro de narra��o para um v�deo sobre: {subject}\n\n"
        f"Idioma: {language}\nDura��o aproximada: {duration_seconds} segundos (~{word_count} palavras)\n"
        f"O roteiro deve ser apenas o texto da narra��o, sem marca��es, sem t�tulo, sem instru��es. Apenas o texto que ser� lido pelo narrador.\n"
        f"N�o use markdown, n�o use asteriscos, n�o use cabe�alhos. Escreva em par�grafos separados por linha em branco."
    )
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        temperature=0.7, max_tokens=2000
    )
    script = response.choices[0].message.content.strip()
    script = script.replace("**", "").replace("##", "").replace("#", "").strip()
    return script

def generate_keywords(script_segment: str) -> list:
    user_prompt = (
        f"Given this narration segment, return 3 to 5 English search keywords for finding relevant stock video clips on Pexels.\n\n"
        f"Narration: {script_segment}\n\nReturn ONLY a JSON array of strings. Example: [\"technology\", \"computer\"]\nNo explanation, no markdown."
    )
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "system", "content": "You are a stock footage search assistant. Return only JSON arrays of search keywords in English."}, {"role": "user", "content": user_prompt}],
        temperature=0.3, max_tokens=200
    )
    content = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
    try: return [str(k).strip() for k in json.loads(content) if str(k).strip()]
    except: return script_segment.split()[:5]
