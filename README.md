# mkdocs-image-gallery-plugin
MKDocs plugin to autogenerate a gallery based on a folder of images

## How to use this plugin?

Add this plugin to your mkdocs.yml configuration as follows:

``` yml
plugins:
  - image-gallery:
      image_folder: "./assets/images/gallery"  # Folder in the docs directory containing images
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

## The Future

More customization options coming.


## Notes

This plugin requires `glightbox` plugin to display clicked images in a lightbox.

`pip install mkdocs-glightbox`

## Server URLs

Offline plugin causes .html in the gallery urls. This plugin supports both server urls and offline urls.