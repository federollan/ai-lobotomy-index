"""Publicación vía Instagram Graph API oficial (cuenta Business/Creator).

La Graph API exige que la imagen esté en una URL pública (no acepta upload
directo), así que el flujo es: subir la imagen a tu hosting (S3, GitHub Pages,
etc.), pasar esa URL acá, crear el contenedor y publicarlo.

Sin credenciales configuradas, todo queda en out/ para publicación manual:
ese es el modo recomendado para arrancar (revisión humana antes de postear).
"""

import json
import os
import urllib.parse
import urllib.request

GRAPH_URL = "https://graph.facebook.com/v21.0"


def _post(url: str, params: dict) -> dict:
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=60) as resp:
        return json.load(resp)


def publish(image_url: str, caption: str) -> str | None:
    """Crea el contenedor de media y lo publica. Devuelve el id del post."""
    ig_user_id = os.environ.get("IG_USER_ID")
    access_token = os.environ.get("IG_ACCESS_TOKEN")
    if not (ig_user_id and access_token):
        return None

    container = _post(f"{GRAPH_URL}/{ig_user_id}/media", {
        "image_url": image_url,
        "caption": caption,
        "access_token": access_token,
    })
    result = _post(f"{GRAPH_URL}/{ig_user_id}/media_publish", {
        "creation_id": container["id"],
        "access_token": access_token,
    })
    return result.get("id")


def save_for_manual_post(item: dict, image_path: str, out_dir: str) -> str:
    """Guarda caption + hashtags junto a la imagen, listos para copiar y pegar."""
    base = os.path.splitext(os.path.basename(image_path))[0]
    caption_path = os.path.join(out_dir, f"{base}.txt")
    with open(caption_path, "w", encoding="utf-8") as f:
        f.write(item["caption"] + "\n\n" + " ".join(item["hashtags"]) + "\n")
    return caption_path
