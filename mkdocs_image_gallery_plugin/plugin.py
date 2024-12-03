from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.structure.pages import Page
from jinja2 import Template
import os
import re

class ImageGalleryPlugin(BasePlugin):
    """ MKDocs plugin to generate an image gallery from a folder """

    config_scheme = (
        ("image_folder", config_options.Type(str, default="images")),
        ("grid_class", config_options.Type(str, default="mkdocs-image-grid")),
        ("item_class", config_options.Type(str, default="mkdocs-image-grid-item")),
    )

    def on_page_markdown(self, markdown, page, config, files):
        image_folder = self.config["image_folder"]
        grid_class = self.config["grid_class"]
        item_class = self.config["item_class"]

        # Regex to match both {{ image_grid }} and {{image_grid}}
        placeholder_pattern = re.compile(r"\{\{\s*image_grid\s*\}\}")

        # Check if the placeholder exists
        if not placeholder_pattern.search(markdown):
            return markdown

        # Path to the folder in the docs directory
        folder_path = os.path.join(config["docs_dir"], image_folder)
        if not os.path.exists(folder_path):
            return markdown

        # Collect all image files in the folder
        image_files = [
            f for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
        ]

        if not image_files:
            return markdown

        # Generate the HTML grid
        grid_html = f"<div class='{grid_class}'>"
        for image in image_files:
            image_path = f"{config['site_url']}/{image_folder}/{image}".replace('\\', '/')  # Fix Windows paths
            grid_html += f"""
            <div class='{item_class}'>
                <img src='{image_path}' alt='{image}' />
            </div>
            """
        grid_html += "</div>"

        # Replace all occurrences of the placeholder with the generated grid HTML
        return placeholder_pattern.sub(f"\n\n{grid_html}\n\n", markdown)
