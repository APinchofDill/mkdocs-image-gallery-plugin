# mkdocs-image-gallery-plugin
MKDocs plugin to autogenerate a gallery based on a folder of images

## How to use this plugin?

Add this plugin to your mkdocs.yml configuration as follows:
``` yml
plugins:
  - image-gallery:
      image_folder: "./assets/images/gallery"  # Folder in the docs directory containing images
```

then use `{{image_gallery}}` anywhere on your page to render the gallery. Simple.

## The Future

More customization options coming.

This plugin requires `glightbox` plugin to be enabled in material docs.