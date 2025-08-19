import os
import re
# import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import yaml
from jinja2 import Template

# log = logging.getLogger("mkdocs.plugins.image-gallery")


YOUTUBE_ID_REGEX = re.compile(
    r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/|shorts/))([A-Za-z0-9_-]{11})"
)


def extract_youtube_id(url: str) -> Optional[str]:
    """Extract the YouTube video ID from a variety of URL formats.

    Supported examples:
    - https://www.youtube.com/watch?v=VIDEOID
    - https://youtu.be/VIDEOID
    - https://www.youtube.com/embed/VIDEOID
    - https://www.youtube.com/shorts/VIDEOID
    """
    if not url:
        return None
    match = YOUTUBE_ID_REGEX.search(url)
    if match:
        return match.group(1)
    return None


def build_thumbnail_url(video_id: str) -> str:
    return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"


def build_embed_url(video_id: str) -> str:
    return f"https://www.youtube.com/embed/{video_id}?rel=0"


class YouTubeGalleryData:
    def __init__(self, categories: Optional[Dict[str, List[str]]] = None, flat_links: Optional[List[str]] = None):
        self.categories = categories or {}
        self.flat_links = flat_links or []

    @property
    def has_categories(self) -> bool:
        return bool(self.categories)


class YouTubeGallery:
    """Loads and renders a YouTube gallery from a YAML file."""

    def __init__(self, docs_dir: str, youtube_links_file: str, package_dir: str):
        self.docs_dir = docs_dir
        self.youtube_links_file = youtube_links_file
        self.package_dir = package_dir
        self.templates_dir = os.path.join(self.package_dir, "assets", "templates")

    def _resolve_yaml_path(self) -> Optional[str]:
        # Prefer a path relative to docs_dir
        candidate = os.path.join(self.docs_dir, self.youtube_links_file)
        if os.path.exists(candidate):
            # log.debug("[image-gallery] YouTube YAML resolved (docs_dir-relative): %s", candidate)
            return candidate
        # Fallback: absolute path if provided
        if os.path.isabs(self.youtube_links_file) and os.path.exists(self.youtube_links_file):
            # log.debug("[image-gallery] YouTube YAML resolved (absolute): %s", self.youtube_links_file)
            return self.youtube_links_file
        # log.info("[image-gallery] No YouTube YAML found at %s or absolute %s", candidate, self.youtube_links_file)
        return None

    def load_data(self) -> YouTubeGalleryData:
        yaml_path = self._resolve_yaml_path()
        if not yaml_path or not os.path.exists(yaml_path):
            # log.info("[image-gallery] YouTube YAML missing; rendering empty gallery")
            return YouTubeGalleryData()

        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                payload = yaml.safe_load(f) or {}
        except Exception as e:
            # log.error("[image-gallery] Failed to read/parse YAML %s: %s", yaml_path, e)
            return YouTubeGalleryData()

        # Two supported shapes:
        # 1) List[str] of links
        # 2) Dict[str, List[str]] mapping category name -> list of links
        if isinstance(payload, list):
            links = [link for link in payload if isinstance(link, str)]
            # log.debug("[image-gallery] YouTube YAML shape: flat list with %d links", len(links))
            return YouTubeGalleryData(flat_links=links)

        if isinstance(payload, dict):
            categories: Dict[str, List[str]] = {}
            for key, value in payload.items():
                if not isinstance(key, str):
                    continue
                if isinstance(value, list):
                    categories[key] = [link for link in value if isinstance(link, str)]
            # log.debug("[image-gallery] YouTube YAML shape: %d categories", len(categories))
            return YouTubeGalleryData(categories=categories)

        return YouTubeGalleryData()

    def _load_template(self, template_name: str) -> Template:
        template_path = os.path.join(self.templates_dir, template_name)
        with open(template_path, "r", encoding="utf-8") as f:
            return Template(f.read())

    def _links_to_video_models(self, links: List[str]) -> List[Dict[str, str]]:
        models: List[Dict[str, str]] = []
        for link in links:
            video_id = extract_youtube_id(link)
            if not video_id:
                continue
            models.append({
                "video_id": video_id,
                "thumbnail_url": build_thumbnail_url(video_id),
                "embed_url": build_embed_url(video_id)
            })
        return models

    def build_view_model(self, data: YouTubeGalleryData) -> Dict[str, Union[bool, Dict[str, List[Dict[str, str]]], List[Dict[str, str]]]]:
        if data.has_categories:
            by_category: Dict[str, List[Dict[str, str]]] = {}
            for category_name, links in data.categories.items():
                by_category[category_name] = self._links_to_video_models(links)
            return {
                "has_categories": True,
                "videos_by_category": by_category,
                "videos": [],
            }
        else:
            return {
                "has_categories": False,
                "videos_by_category": {},
                "videos": self._links_to_video_models(data.flat_links),
            }

    def render_gallery_html(self) -> str:
        template = self._load_template("youtube_gallery.html")
        data = self.load_data()
        model = self.build_view_model(data)
        if model.get("has_categories"):
            # log.info("[image-gallery] Rendering YouTube gallery: %d categories", len(model.get("videos_by_category", {})))
            pass
        else:
            # log.info("[image-gallery] Rendering YouTube gallery: %d videos", len(model.get("videos", [])))
            pass
        return template.render(**model)


