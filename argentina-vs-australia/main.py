"""Punto de entrada: lee los temas de topics.csv, genera el contenido
(semillas verificadas o LLM), renderiza cada placa y la deja en out/
junto con su caption. Si hay credenciales de la Graph API, publica.

Uso:
    python main.py              # procesa todos los temas pendientes
    python main.py --limit 1    # genera una sola placa
"""

import argparse
import csv
import os
import re
import unicodedata

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import content
import publish
import render

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "out")
TOPICS_CSV = os.path.join(BASE, "topics.csv")


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="máximo de placas a generar")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    seeds = content.load_seed_facts()

    with open(TOPICS_CSV, encoding="utf-8") as f:
        topics = [row["tema"] for row in csv.DictReader(f) if row.get("tema")]
    if args.limit:
        topics = topics[: args.limit]

    generated = 0
    for tema in topics:
        print(f"Tema: {tema}")
        item = content.get_content(tema, seeds)
        if item is None:
            print("  [skip] sin dato verificado, no se genera la placa")
            continue

        image_path = os.path.join(OUT_DIR, f"{slugify(tema)}.jpg")
        render.render_card(item, image_path)
        publish.save_for_manual_post(item, image_path, OUT_DIR)
        print(f"  [ok] {image_path}")

        full_caption = item["caption"] + "\n\n" + " ".join(item["hashtags"])
        image_url_base = os.environ.get("IMAGE_HOSTING_URL")
        if image_url_base:
            post_id = publish.publish(
                f"{image_url_base.rstrip('/')}/{os.path.basename(image_path)}", full_caption
            )
            if post_id:
                print(f"  [publicado] id={post_id}")
        generated += 1

    print(f"\nListo: {generated} placa(s) en {OUT_DIR}")


if __name__ == "__main__":
    main()
