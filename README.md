# mkdocs-image-gallery-plugin
MKDocs plugin to autogenerate a gallery based on a folder of images

## How to use this plugin?

Add this plugin to your mkdocs.yml configuration as follows:

``` yml
plugins:
  - image-gallery:
      image_folder: "./assets/images/gallery"  # Folder in the docs directory containing images
      separate_category_pages: false  # Optional: Set to true to create separate pages for each category
      youtube_links_file: "youtube-links.yaml"  # Optional: Path (relative to docs/) for YouTube links
```

## Short Code Usage

Add these short codes to any markdown page in your docs to use the image gallery plugin.

Display Preview Gallery
`{{gallery_preview}}`

Display Full Gallery
`{{gallery_html}}`

Display Youtube Gallery
`{{youtube_gallery}}`

Simple.

## YouTube Video Gallery

Render a responsive YouTube video gallery from a YAML file in your `docs/` directory.

- **Shortcode**: place `{{youtube_gallery}}` anywhere in your Markdown.
- **Data source**: YAML file under `docs/` (default: `youtube-links.yaml`).
- **Playback**: Built‑in lightbox opens an embedded YouTube player on click.

### YAML formats (`docs/youtube-links.yaml`)

- Flat list of links:

```yaml
- https://www.youtube.com/watch?v=dQw4w9WgXcQ
- https://www.youtube.com/watch?v=ArOS-e2d-cM
```

- Categories mapping to lists of links:

```yaml
Rick Roll:
- https://www.youtube.com/watch?v=dQw4w9WgXcQ
IronMouse:
- https://www.youtube.com/watch?v=ArOS-e2d-cM
```

### Assets

The plugin automatically injects the required CSS and JS and copies them into the built site:

- CSS: `assets/stylesheets/image-gallery.css`
- JS: `assets/javascripts/youtube-gallery.js`

No extra configuration is needed beyond the plugin config below.

### Notes & limitations

- Works with standard YouTube URLs (`watch`, `youtu.be`, `embed`, `shorts`). Invalid links are skipped.
- No YouTube Data API usage; titles/metadata are not fetched.

### youtube_links_file
Path (relative to `docs_dir`) to the YAML file containing YouTube links. Supports either a flat list of links or a mapping of category names to lists of links.

- Default: `youtube-links.yaml`

## Add to Main Nav

Dont forget to add the page that contains your `{{gallery_html}}` short code to the main nav config in `mkdocs.yml` to have a link in the main navigation

Example:

```
nav:
  - Gallery: gallery.md
```

## Configuration Options

### image_folder
The path to the folder containing your gallery images, relative to the docs directory. Each subfolder in this directory will be treated as a separate category.

### separate_category_pages
When set to `true`, the plugin will create separate pages for each category instead of displaying all categories on a single page. This is useful for large galleries with many images.

- Default: `false`
- When enabled:
  - The main gallery page will show a list of categories with links to individual category pages
  - Each category will have its own page with all images from that category
  - The gallery preview will link directly to these separate category pages

### youtube_links_file
Path to your youtube links `youtube-links.yaml`.

## Notes

This plugin requires `glightbox` plugin to display clicked images in a lightbox.

`pip install mkdocs-glightbox`

### MkDocs Serve Compatibility

When using `mkdocs serve` with `separate_category_pages: true`, the plugin avoids regenerating category pages if they already exist. This prevents endless rebuild loops that could occur when the file watcher detects newly generated files.

## Server URLs

Offline plugin causes .html in the gallery urls. This plugin supports both server urls and offline urls.