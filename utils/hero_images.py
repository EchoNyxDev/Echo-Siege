import os
import re


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HERO_IMAGE_DIR = os.path.join(ROOT_DIR, "assets", "herois_img")


def get_hero_image_path(hero_id):
    hero_id = str(hero_id or "").strip().lower()
    if not re.fullmatch(r"[a-z0-9_-]+", hero_id):
        return None
    path = os.path.join(HERO_IMAGE_DIR, f"{hero_id}.jpg")
    return path if os.path.isfile(path) else None


def get_hero_attachment(hero_id, prefix="hero"):
    path = get_hero_image_path(hero_id)
    if not path:
        return None, None
    return path, f"{prefix}_{hero_id}.jpg"
