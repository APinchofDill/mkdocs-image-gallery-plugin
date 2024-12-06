import os
import re
import shutil
from mkdocs.plugins import BasePlugin
from mkdocs.config.config_options import Type
from jinja2 import Template
from pathlib import Path

class ImageGalleryPlugin(BasePlugin):
    config_scheme = (
        ('image_folder', Type(str, required=True)),
    )

    def __init__(self):
        self.image_folder = None
        self.image_folder_raw = None
        self.css_file = None
        self.config = None
        self.valid_extensions = [".png", ".jpg", ".jpeg", ".gif", ".webp"]

    def on_config(self, config):
        """ Set the image folder path and asset file paths. """
        self.image_folder_raw = self.config['image_folder']
        self.image_folder = folder_path = os.path.join(config["docs_dir"], self.config['image_folder'])
        self.config = config

        # CSS stuff
        css_file_path = os.path.join(os.path.dirname(__file__), "assets", "css", "styles.css")
        if os.path.exists(css_file_path):
            # Add CSS file to extra_css array in active config
            config['extra_css'] = config.get('extra_css', [])

            config['extra_css'].append(f"assets/stylesheets/image-gallery.css")

            self.css_file = css_file_path
        else:
            print(f"Warning: CSS file not found at {css_file_path}")

        return config

    def on_post_build(self, config):
        """ Copy the CSS file into the assets/css directory. """

        site_dir = config['site_dir']
        target_dir = os.path.join(site_dir, 'assets', 'stylesheets')

        # Ensure the target directory exists
        os.makedirs(target_dir, exist_ok=True)

        # Copy CSS file to stylesheets directory
        if os.path.exists(self.css_file):
            shutil.copy(self.css_file, os.path.join(target_dir, "image-gallery.css"))
        else:
            print(f"Warning: CSS file not found at {self.css_file}")

    def on_page_markdown(self, markdown, page, config, files):
        """ Find and replace the placeholder with the gallery HTML. """

        placeholder_pattern = re.compile(r"\{\{\s*image_gallery\s*\}\}")

        # Check if the placeholder {{image_gallery}} exists if not return the markdown as is
        if not placeholder_pattern.search(markdown):
            return markdown

        gallery_html = self.generate_gallery_html()
        return placeholder_pattern.sub(f"\n\n{gallery_html}\n\n", markdown)

    def generate_gallery_html(self):
        """ Generate the categories object. """

        if not os.path.exists(self.image_folder):
            return "<p>Error: Image folder does not exist.</p>"

        categories = []
        for folder in sorted(Path(self.image_folder).iterdir()):
            if folder.is_dir():
                thumbnail = self.find_thumbnail(folder)
                if thumbnail:
                    categories.append({
                        'name': folder.name,
                        'thumbnail': thumbnail,
                        'images': self.get_images(folder, exclude_thumbnail=thumbnail)
                    })

        return self.render_gallery(categories)

    def find_thumbnail(self, folder_path):
        """ Find the thumbnail image in the folder. """

        # Iterate over files in the folder
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Check if the file name is 'thumbnail' with any allowed extension
                if any(file.lower().startswith("thumbnail") and file.lower().endswith(ext) for ext in self.valid_extensions):
                    file_location = os.path.join(root, file).replace('\\', '/')

                    web_safe = os.path.join(self.config['site_url'], self.image_folder_raw, Path(file_location).parent.name, Path(file_location).name).replace('\\', '/')

                    return web_safe  # Return the full path of the file
        return None  # Return None if no file is found

    def get_images(self, folder, exclude_thumbnail):
        """ Get all images in the folder except the thumbnail. """

        folder = Path(folder)
        
        # Get all image files in the folder
        images = [
            f for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in self.valid_extensions and f.name != exclude_thumbnail
        ]
        
        # Format the image paths to be web-safe
        formatted_images = [
            f"{self.config['site_url']}/{Path(img.parent)}/{img.name}".replace('\\', '/') for img in images
        ]

        return formatted_images

    def render_gallery(self, categories):
        """ Render the gallery HTML using Jinja2. """

        gallery_template = Template('''<div class="image-gallery">
        {% for category in categories %}
            <div class="gallery-category">
                <h2>{{ category.name }}</h2>
                <a href="{{ category.name }}.html">
                    <img src="{{ category.thumbnail }}" alt="{{ category.name }}">
                </a>
            </div>
        {% endfor %}
        </div>''')

        # TODO: Create a separate template for the category pages
        pages_template = Template('''
        {% for category in categories %}
        <html>
        <head>
            <title>{{ category.name }}</title>
        </head>
        <body>
            <h1>{{ category.name }}</h1>
            <div class="category-images">
                {% for image in category.images %}
                    <img src="{{ image }}" alt="">
                {% endfor %}
            </div>
        </body>
        </html>
        {% endfor %}
        ''')

        generated_pages = pages_template.render(categories=categories)
        for category in categories:
            with open(f"{category['name']}.html", "w") as f:
                f.write(generated_pages)

        return gallery_template.render(categories=categories)
