"""Generación y validación del contenido de cada placa.

Dos modos:
 - Sin API key: usa los datos verificados de data/seed_facts.json.
 - Con OPENAI_API_KEY (u otro endpoint compatible): le pide al modelo un dato
   nuevo para el tema indicado, en JSON estricto, y lo valida antes de aceptar.

Regla de oro: ningún dato sin fuente y año llega al render.
"""

import json
import os
import urllib.request

PROMPT_TEMPLATE = """Actuás como analista de datos para una cuenta de Instagram \
sobre estudiar en Australia, dirigida a argentinos.

Generá UNA comparación Argentina vs Australia sobre el tema: {tema}

Reglas estrictas:
- Usá SOLO datos reales y verificables. Citá fuente exacta y año de cada dato.
- Si no tenés un dato confiable, devolvé {{"error": "DATO NO VERIFICADO"}}.
- Si comparás dinero, convertí a USD y aclará la fecha del tipo de cambio.

Respondé ÚNICAMENTE con JSON válido con esta forma exacta:
{{
  "tema": "...",
  "titulo": "máx 6 palabras, con gancho",
  "dato_argentina": {{"valor": "texto corto", "valor_num": numero_o_null, "fuente": "...", "anio": "..."}},
  "dato_australia": {{"valor": "texto corto", "valor_num": numero_o_null, "fuente": "...", "anio": "..."}},
  "insight": "1 frase que explique por qué sorprende",
  "caption": "2-3 frases + llamado a consultar por skills assessment",
  "hashtags": ["10 a 15 hashtags mezcla de nicho y amplios"]
}}"""

REQUIRED_FACT_KEYS = ("valor", "fuente", "anio")


def validate(item: dict) -> list[str]:
    """Devuelve la lista de problemas; vacía si la placa es publicable."""
    problems = []
    for key in ("titulo", "insight", "caption", "hashtags"):
        if not item.get(key):
            problems.append(f"falta '{key}'")
    for country in ("dato_argentina", "dato_australia"):
        fact = item.get(country) or {}
        for k in REQUIRED_FACT_KEYS:
            if not fact.get(k):
                problems.append(f"{country}: falta '{k}' (dato sin fuente = no se publica)")
    return problems


def load_seed_facts(path: str = None) -> list[dict]:
    path = path or os.path.join(os.path.dirname(__file__), "data", "seed_facts.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def generate_with_llm(tema: str) -> dict | None:
    """Pide un dato nuevo al LLM. Devuelve None si no hay key, si el modelo no
    pudo verificar el dato, o si la respuesta no pasa la validación."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    base_url = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("LLM_MODEL", "gpt-4o")
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": PROMPT_TEMPLATE.format(tema=tema)}],
        "response_format": {"type": "json_object"},
        "temperature": 0.4,
    }).encode()

    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)

    item = json.loads(data["choices"][0]["message"]["content"])
    if item.get("error"):
        print(f"  [skip] El modelo no pudo verificar un dato para '{tema}'")
        return None
    problems = validate(item)
    if problems:
        print(f"  [skip] '{tema}' descartado: {'; '.join(problems)}")
        return None
    return item


def get_content(tema: str, seeds: list[dict]) -> dict | None:
    """Primero busca el tema en los datos semilla; si no está, intenta con el LLM."""
    for item in seeds:
        if item["tema"].lower() == tema.lower() and not validate(item):
            return item
    return generate_with_llm(tema)
