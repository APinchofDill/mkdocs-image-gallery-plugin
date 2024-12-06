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
        self.categories = None

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

    def on_pre_build(self, config):
        """ Create the new page before the build process starts. """
        docs_dir = config["docs_dir"]
        page_name = "image-gallery.md"
        page_path = os.path.join(docs_dir, page_name)

        # Write the content to the new page file
        with open(page_path, "w") as f:
            f.write("{{generated_gallery}}")
        
        # Add the new page to the navigation
        new_page_nav = {
            "Image Gallery": page_name
        }

        if "nav" in config:
            config["nav"].append(new_page_nav)
        else:
            config["nav"] = [new_page_nav]

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

    # def on_post_page(self, output_content, page, config):
    #     """ Modify the HTML content of the page. """
    #     # Return the unmodified or modified full HTML
    #     return output_content

    # def on_page_content(self, html, page, config, **kwargs):
    #     """ HTML modifications """
    #     return html

    def on_page_markdown(self, markdown, page, config, files):
        """ Find and replace the placeholder with the gallery HTML. """

        inline_parent_pattern = re.compile(r"\{\{\s*image_gallery\s*\}\}")
        generate_gallery_pattern = re.compile(r"\{\{\s*generated_gallery\s*\}\}")
        
        self.categories = self.get_categories()

        if generate_gallery_pattern.search(markdown):
            gallery_html = self.render_page_gallery()
            return generate_gallery_pattern.sub(f"\n\n{gallery_html}\n\n", markdown)

        # Check if the placeholder {{image_gallery}} exists if not return the markdown as is
        if inline_parent_pattern.search(markdown):
            gallery_preview = self.generate_gallery_html()
            return inline_parent_pattern.sub(f"\n\n{gallery_preview}\n\n", markdown)

        return markdown

    def get_categories(self):
        """ Get the list of categories in the image folder. """

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

        return categories

    def generate_gallery_html(self):
        """ Generate the categories object. """

        if not os.path.exists(self.image_folder):
            return "<p>Error: Image folder does not exist.</p>"

        return self.render_gallery()

    def get_web_Safe_image(self, site_url, file_location):
        """ Get the web-safe image path. """

        return os.path.join(site_url, self.image_folder_raw, Path(file_location).parent.name, Path(file_location).name).replace('\\', '/')

    def find_thumbnail(self, folder_path):
        """ Find the thumbnail image in the folder. """

        # Iterate over files in the folder
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Check if the file name is 'thumbnail' with any allowed extension
                if any(file.lower().startswith("thumbnail") and file.lower().endswith(ext) for ext in self.valid_extensions):
                    file_location = os.path.join(root, file).replace('\\', '/')

                    web_safe = self.get_web_Safe_image(self.config['site_url'], file_location)

                    return web_safe  # Return the full path of the file
        return None  # Return None if no file is found

    def get_images(self, folder, exclude_thumbnail):
        """ Get all images in the folder except the thumbnail. """

        folder = Path(folder)
        
        # Get all image files in the folder
        images = [
            f for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in self.valid_extensions and f.name != Path(exclude_thumbnail).name
        ]
        
        # Format the image paths to be web-safe
        formatted_images = [
            self.get_web_Safe_image(self.config['site_url'], img) for img in images
        ]

        return formatted_images

    def render_page_gallery(self):
        """ Render the gallery HTML using Jinja2. """
        
        pages_template = Template('''<div class="image-gallery-page-container">
        {% for category in categories %}
            <h1>{{ category.name }}</h1>
            <div class="category-images">
                {% for image in category.images %}
                    <img src="{{ image }}" alt="">
                {% endfor %}
            </div>
        {% endfor %}
        </div>''')

        return pages_template.render(categories=self.categories)


    def render_gallery(self):
        """ Render the gallery HTML using Jinja2. """

        gallery_template = Template('''<div class="image-gallery">
        {% for category in categories %}
            <div class="gallery-category">
                <div class="header"> <h2>{{ category.name }}</h2> <a href="#todo-add-image-gallery-link" class="see-all-link">View All</a> </div>
                <a href="{{ category.name }}.html">
                    <img src="{{ category.thumbnail }}" alt="{{ category.name }}">
                </a>
            </div>
        {% endfor %}
        </div>''')

        return gallery_template.render(categories=self.categories)
