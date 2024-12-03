# mkdocs-image-gallery-plugin
MKDocs plugin to autogenerate a gallery based on a folder of images

## How to use this plugin?

Add this plugin to your mkdocs.yml configuration as follows:
plugins:
``` yml
  - image-gallery:
      image_folder: "./assets/images/gallery"  # Folder in the docs directory containing images
      grid_class: "your-grid-class"  # Optional, CSS class for the grid container
      item_class: "your-item-class"  # Optional, CSS class for the grid items
```
