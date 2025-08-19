import os
import re
import shutil
# import logging
from mkdocs.plugins import BasePlugin
from mkdocs.config.config_options import Type
from jinja2 import Template
from pathlib import Path
from .youtube import YouTubeGallery

# log = logging.getLogger("mkdocs.plugins.image-gallery")

class ImageGalleryPlugin(BasePlugin):
    config_scheme = (
        ('image_folder', Type(str, required=True)),
        ('separate_category_pages', Type(bool, default=False)),
        ('youtube_links_file', Type(str, default='youtube-links.yaml')),
    )

    def __init__(self):
        self.image_folder = None
        self.image_folder_raw = None
        self.css_file = None
        self.youtube_js_file = None
        self.config = None
        self.valid_extensions = [".png", ".jpg", ".jpeg", ".gif", ".webp"]
        self.categories = None
        self.gallery_markdown_path = None
        self.gallery_markdown_name = None
        self.use_server_urls = None
        self.docs_path = None
        self.gallery_preview_pattern = None
        self.gallery_pattern = None
        self.separate_category_pages = None
        self.category_pages = {}
        self.youtube_gallery_placeholder = None
        self.youtube_gallery = None

    def on_config(self, config):
        """ Set the image folder path and asset file paths. """

        self.image_folder_raw = self.config['image_folder']
        self.image_folder = folder_path = os.path.join(config["docs_dir"], self.config['image_folder'])
        # log.info("[image-gallery] on_config: docs_dir=%s image_folder_raw=%s resolved_image_folder=%s", config.get("docs_dir"), self.image_folder_raw, self.image_folder)
        
        # Get the separate_category_pages config option
        self.separate_category_pages = self.config.get('separate_category_pages', False)
        # log.debug("[image-gallery] separate_category_pages=%s", self.separate_category_pages)

        # get the use_directory_urls config for  url routing
        self.use_server_urls = config["use_directory_urls"]
        self.docs_path = config["docs_dir"]

        # CSS stuff
        css_file_path = os.path.join(os.path.dirname(__file__), "assets", "css", "styles.css")

        if os.path.exists(css_file_path):
            # Add CSS file to extra_css array in active config
            config['extra_css'] = config.get('extra_css', [])
            config['extra_css'].append(f"assets/stylesheets/image-gallery.css")

            self.css_file = css_file_path
        else:
            # log.warning("[image-gallery] CSS file not found at %s", css_file_path)
            pass

        # JavaScript for YouTube gallery
        js_file_path = os.path.join(os.path.dirname(__file__), "assets", "js", "youtube-gallery.js")
        if os.path.exists(js_file_path):
            config['extra_javascript'] = config.get('extra_javascript', [])
            config['extra_javascript'].append("assets/javascripts/youtube-gallery.js")
            self.youtube_js_file = js_file_path
        else:
            # log.warning("[image-gallery] JS file not found at %s", js_file_path)
            pass

        self.config = config
        return config

    def on_pre_build(self, config):
        """ Create the new page before the build process starts. """

        # Define patterns for placeholders
        self.gallery_preview_pattern = re.compile(r"\{\{\s*gallery_preview\s*\}\}")
        self.gallery_pattern = re.compile(r"\{\{\s*gallery_html\s*\}\}")
        self.youtube_gallery_placeholder = re.compile(r"\{\{\s*youtube_gallery\s*\}\}")
        # log.debug("[image-gallery] Patterns compiled: gallery_preview, gallery_html, youtube_gallery")
        # Get the path of gallery
        self.gallery_markdown_path = self.find_first_markdown_with_pattern(config["docs_dir"], self.gallery_pattern)
        if self.gallery_markdown_path:
            # Get the name of the page
            self.gallery_markdown_name = Path(self.gallery_markdown_path).name.rsplit('.', 1)[0]
            # log.debug("[image-gallery] Found gallery_html in %s (name=%s)", self.gallery_markdown_path, self.gallery_markdown_name)
        else:
            self.gallery_markdown_name = None
            # log.info("[image-gallery] No page with {{gallery_html}} found. This is OK if only YouTube or previews are used.")
        
        # Get the categories
        self.categories = self.get_categories()

        # Prepare YouTube gallery helper
        self.youtube_gallery = YouTubeGallery(
            docs_dir=config["docs_dir"],
            youtube_links_file=self.config.get('youtube_links_file', 'youtube-links.yaml'),
            package_dir=os.path.dirname(__file__),
        )
        
        # If separate category pages are enabled, generate them
        if self.separate_category_pages:
            self.generate_category_pages(config)
            
    def generate_category_pages(self, config):
        """ Generate separate markdown files for each category. """
        
        # Get the directory of the gallery markdown file
        gallery_dir = os.path.dirname(self.gallery_markdown_path)
        
        # Create a directory for category pages if it doesn't exist
        category_dir = os.path.join(gallery_dir, "categories")
        os.makedirs(category_dir, exist_ok=True)
        
        # markdown file for each category
        for category in self.categories:
            # Create the filename for the category page
            category_filename = f"{category['name'].lower().replace(' ', '_')}.md"
            category_path = os.path.join(category_dir, category_filename)
            
            # Calculate the URL for the category page
            if self.use_server_urls:
                page_url = f"{self.config['site_url']}categories/{category_filename.rsplit('.', 1)[0]}/"
            else:
                page_url = f"{self.config['site_url']}categories/{category_filename}"
                
            # Add the page URL to the category object
            category['page_url'] = page_url
            
            # Store the category page info for later use
            self.category_pages[category['name']] = {
                'path': category_path,
                'url': page_url
            }
            
            # Skip file generation if it already exists to prevent endless rebuild loops in 'mkdocs serve'
            if os.path.exists(category_path):
                continue
                
            # Generate the content for the category page
            content = f"# {category['name']}\n\n{{{{category_{category['name']}}}}}\n"
            
            # Write the content to the file
            with open(category_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def find_first_markdown_with_pattern(self, directory, pattern):
        """ Find the first markdown file that matches the pattern. """

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".md"):  # Check if the file is a markdown file
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if pattern.search(content):
                                return file_path  # Return the file path immediately
                    except Exception as e:
                        # log.error("[image-gallery] Error reading %s: %s", file_path, e)
                        pass
        return None  # Return None if no file matches the pattern

    def on_post_build(self, config):
        """ Copy the CSS and JS files into the site assets directory. """

        site_dir = config['site_dir']
        target_css_dir = os.path.join(site_dir, 'assets', 'stylesheets')
        target_js_dir = os.path.join(site_dir, 'assets', 'javascripts')

        # Ensure the target directories exist
        os.makedirs(target_css_dir, exist_ok=True)
        os.makedirs(target_js_dir, exist_ok=True)

        # Copy CSS file to stylesheets directory
        if os.path.exists(self.css_file):
            shutil.copy(self.css_file, os.path.join(target_css_dir, "image-gallery.css"))
        else:
            # log.warning("[image-gallery] CSS file not found at %s", self.css_file)
            pass

        # Copy JS file to javascripts directory
        if self.youtube_js_file and os.path.exists(self.youtube_js_file):
            shutil.copy(self.youtube_js_file, os.path.join(target_js_dir, "youtube-gallery.js"))
        elif self.youtube_js_file:
            # log.warning("[image-gallery] JS file not found at %s", self.youtube_js_file)
            pass

    def on_page_markdown(self, markdown, page, config, files):
        """ Find and replace the placeholder with the gallery HTML. """

        # Get the categories if not already loaded
        if self.categories is None:
            self.categories = self.get_categories()

        rendered = markdown

        # Replace YouTube first so it doesn't get skipped if other placeholders also exist
        if self.youtube_gallery_placeholder.search(rendered):
            # log.info("[image-gallery] Replacing {{youtube_gallery}} on page: %s", getattr(page, 'file', getattr(page, 'title', 'unknown')))
            if self.youtube_gallery:
                yt_html = self.youtube_gallery.render_gallery_html()
                rendered = self.youtube_gallery_placeholder.sub(f"\n\n{yt_html}\n\n", rendered)
            else:
                # log.error("[image-gallery] YouTubeGallery not initialized before on_page_markdown")
                pass

        # Replace {{gallery_html}}
        if self.gallery_pattern.search(rendered):
            # log.info("[image-gallery] Replacing {{gallery_html}} on page: %s", getattr(page, 'file', getattr(page, 'title', 'unknown')))
            gallery_html = self.render_page_gallery(page)
            rendered = self.gallery_pattern.sub(f"\n\n{gallery_html}\n\n", rendered)

        # Replace {{gallery_preview}}
        if self.gallery_preview_pattern.search(rendered):
            # log.info("[image-gallery] Replacing {{gallery_preview}} on page: %s", getattr(page, 'file', getattr(page, 'title', 'unknown')))
            gallery_preview = self.render_gallery_preview(page)
            rendered = self.gallery_preview_pattern.sub(f"\n\n{gallery_preview}\n\n", rendered)
            
        # Check for category page placeholders
        if self.separate_category_pages:
            for category in self.categories:
                category_pattern = re.compile(r"\{\{\s*category_" + category['name'] + r"\s*\}\}")
                if category_pattern.search(markdown):
                    # log.info("[image-gallery] Replacing {{category_%s}} on page: %s", category['name'], getattr(page, 'file', getattr(page, 'title', 'unknown')))
                    category_html = self.render_category_page(category)
                    rendered = category_pattern.sub(f"\n\n{category_html}\n\n", rendered)

        return rendered

    def get_categories(self):
        """ Get the list of categories in the image folder. """

        # If the configured image folder is missing, avoid crashing the build
        if not self.image_folder or not os.path.isdir(self.image_folder):
            # log.info("[image-gallery] Image folder missing or not a directory: %s (continuing without image categories)", self.image_folder)
            return []

        # Get all folders in the image folder and thumbnail
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

    def get_web_Safe_image(self, site_url, file_location):
        """ Get the web-safe image path. """

        return os.path.join(site_url, self.image_folder_raw, Path(file_location).parent.name, Path(file_location).name).replace(os.path.sep, '/')

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

    def render_page_gallery(self, page):
        """ Render the gallery HTML using Jinja2. """

        # If separate category pages are enabled, only show a list of categories with links
        if self.separate_category_pages:
            pages_template = Template('''<div class="image-gallery">
            {% for category in categories %}
                <div class="gallery-category">
                    <div class="header"> <h2>{{ category.name }}</h2> <a href="{{ category.page_url }}" class="see-all-link">View All</a> </div>
                    <a href="{{ category.page_url }}">
                        <div class="image-wrapper">
                            <div class="skeleton-loader"></div>
                            <img src="{{ category.thumbnail }}" alt="{{ category.name }}" loading="lazy" class="gallery-image" onload="this.classList.add('loaded')">
                        </div>
                    </a>
                </div>
            {% endfor %}
            </div>''')
        else:
            pages_template = Template('''<div class="image-gallery-page-container">
            {% for category in categories %}
                <h1 id="{{category.name}}">{{ category.name }}</h1>
                <div class="category-images">
                    {% for image in category.images %}
                        <div class="image-wrapper">
                            <div class="skeleton-loader"></div>
                            <img src="{{ image }}" alt="" loading="lazy" class="gallery-image" onload="this.classList.add('loaded')">
                        </div>
                    {% endfor %}
                </div>
            {% endfor %}
            </div>''')

        return pages_template.render(categories=self.categories)
        
    def render_category_page(self, category):
        """ Render a single category page. """
        
        category_template = Template('''<div class="image-gallery-page-container">
        <div class="category-images">
            {% for image in category.images %}
                <div class="image-wrapper">
                    <div class="skeleton-loader"></div>
                    <img src="{{ image }}" alt="" loading="lazy" class="gallery-image" onload="this.classList.add('loaded')">
                </div>
            {% endfor %}
        </div>
        </div>''')
        
        return category_template.render(category=category)


    def render_gallery_preview(self, page):
        """ Render the gallery HTML using Jinja2. """

        if not os.path.exists(self.image_folder):
            return "<p>Error: Image folder does not exist.</p>"

        # Different templates based on whether separate category pages are enabled
        if self.separate_category_pages:
            gallery_template = Template('''<div class="image-gallery">
            {% for category in categories %}
                <div class="gallery-category">
                    <div class="header"> <h2>{{ category.name }}</h2> <a href="{{ category.page_url }}" class="see-all-link">View All</a> </div>
                    <a href="{{ category.page_url }}">
                        <div class="image-wrapper">
                            <div class="skeleton-loader"></div>
                            <img src="{{ category.thumbnail }}" alt="{{ category.name }}" loading="lazy" class="gallery-image" onload="this.classList.add('loaded')">
                        </div>
                    </a>
                </div>
            {% endfor %}
            </div>''')
            
            return gallery_template.render(categories=self.categories)
        else:
            root_url = None
            
            if self.gallery_markdown_path and self.gallery_markdown_name:
                # Get the relative path
                relative_path = os.path.relpath(self.gallery_markdown_path, self.docs_path)
                folders_between = f"{os.path.dirname(relative_path).replace(os.path.sep, '/')}" # make it web safe
                if folders_between:
                    folders_between = f"{folders_between}/"
            
                # use_directory_urls True = server / False = local .html
                site_url = self.config["site_url"]
                if self.use_server_urls:
                    root_url = f"{site_url}{folders_between}{self.gallery_markdown_name}/#"
                else:
                    root_url = f"{site_url}{folders_between}{self.gallery_markdown_name}.html#"
            else:
                # Fallback if the gallery page is not discovered
                site_url = self.config["site_url"]
                root_url = f"{site_url}#"
                # log.debug("[image-gallery] gallery_markdown_path not set; using fallback root_url=%s", root_url)

            gallery_template = Template('''<div class="image-gallery">
            {% for category in categories %}
                <div class="gallery-category">
                    <div class="header"> <h2>{{ category.name }}</h2> <a href="{{root_url}}{{ category.name }}" class="see-all-link">View All</a> </div>
                    <a href="{{ category.name }}.html">
                        <div class="image-wrapper">
                            <div class="skeleton-loader"></div>
                            <img src="{{ category.thumbnail }}" alt="{{ category.name }}" loading="lazy" class="gallery-image" onload="this.classList.add('loaded')">
                        </div>
                    </a>
                </div>
            {% endfor %}
            </div>''')
    
            return gallery_template.render(root_url=root_url, categories=self.categories)
