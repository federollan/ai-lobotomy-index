# Argentina vs Australia — generador de placas para Instagram

Pipeline que produce placas comparativas (1080×1350) entre Argentina y
Australia para una cuenta de assessments/estudios en Australia. Genera la
imagen con plantilla fija, el caption con CTA y los hashtags, todo listo
para publicar.

## Principios

1. **Ningún dato sin fuente.** Cada placa muestra fuente y año. Si el LLM no
   puede verificar un dato, la placa se descarta (no se inventa).
2. **Producción automática, publicación supervisada.** Por defecto todo queda
   en `out/` para que lo revises antes de postear. La publicación automática
   usa solo la Graph API oficial (nada de APIs no oficiales que arriesguen
   la cuenta).
3. **Identidad visual fija.** Colores, tipografías y layout viven en
   `theme.py`; tocás un archivo y cambia toda la cuenta.

## Uso rápido (sin ninguna API key)

```bash
pip install -r requirements.txt
python main.py --limit 3
```

Genera en `out/` un `.jpg` (la placa) y un `.txt` (caption + hashtags) por
tema, usando los datos verificados de `data/seed_facts.json`.

## Generar datos nuevos con un LLM

1. Copiá `.env.example` a `.env` y completá `OPENAI_API_KEY` (o apuntá
   `LLM_BASE_URL` a cualquier endpoint compatible).
2. Agregá temas a `topics.csv`.
3. `python main.py`

El prompt (en `content.py`) exige JSON con fuente y año por dato, y
`content.validate()` descarta cualquier respuesta incompleta.

> ⚠️ Igual **verificá los números antes de publicar**: los LLM citan fuentes
> con confianza aunque el número esté desactualizado. Los datos de
> `seed_facts.json` también conviene revalidarlos cada tanto.

## Publicación automática (opcional)

La Graph API de Instagram necesita: cuenta Business/Creator, una app de Meta
con `instagram_content_publish`, y que la imagen esté en una URL pública.
Completá `IG_USER_ID`, `IG_ACCESS_TOKEN` e `IMAGE_HOSTING_URL` en `.env` y
subí el contenido de `out/` a ese hosting antes de correr `main.py`.

## Estructura

| Archivo | Rol |
|---|---|
| `theme.py` | Colores, fuentes, medidas, handle |
| `content.py` | Prompt al LLM + validación de fuentes |
| `render.py` | Composición de la placa con Pillow |
| `publish.py` | Graph API oficial o guardado para post manual |
| `main.py` | Orquesta: temas → contenido → imagen → out/ |
| `topics.csv` | Cola de temas a producir |
| `data/seed_facts.json` | Datos curados a mano con fuente y año |
