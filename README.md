# mkdocs-image-gallery-plugin
MKDocs plugin to autogenerate a gallery based on a folder of images

## How to use this plugin?

Add this plugin to your mkdocs.yml configuration as follows:

``` yml
plugins:
  - image-gallery:
      image_folder: "./assets/images/gallery"  # Folder in the docs directory containing images
      separate_category_pages: false  # Optional: Set to true to create separate pages for each category
```

## Short Code Usage

Add these short codes to any markdown page in your docs to use the image gallery plugin.

Display Preview Gallery
`{{gallery_preview}}`

Display Full Gallery
`{{gallery_html}}`

Simple.

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

## Features

### Lazy Loading with Skeleton Loaders
The gallery includes built-in lazy loading for all images, which improves page load performance. Images are loaded only when they come into view, and a smooth skeleton loader animation is displayed while images are loading.

### Separate Category Pages
When set to `true`, the plugin will create separate pages for each category instead of displaying all categories on a single page. This is useful for large galleries with many images.

## The Future

More customization options coming.


## Notes

This plugin requires `glightbox` plugin to display clicked images in a lightbox.

`pip install mkdocs-glightbox`

### MkDocs Serve Compatibility

When using `mkdocs serve` with `separate_category_pages: true`, the plugin avoids regenerating category pages if they already exist. This prevents endless rebuild loops that could occur when the file watcher detects newly generated files.

## Server URLs

Offline plugin causes .html in the gallery urls. This plugin supports both server urls and offline urls.