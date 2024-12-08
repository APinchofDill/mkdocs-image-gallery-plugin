from setuptools import setup, find_packages

setup(
    name="mkdocs-image-gallery-plugin",
    version="1.1.1",
    description="An MkDocs plugin to generate an image gallery from a folder of images",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/APinchofDill/mkdocs-image-gallery-plugin",
    keywords="mkdocs image gallery",
    author="APinchofDill",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "jinja2>=3.1.4",
        "mkdocs>=1.4.1"
    ],
    packages=find_packages(),
    data_files=[
        ('', ['mkdocs_image_gallery_plugin/assets/css/styles.css']),
    ],
    include_package_data=True,
    entry_points={
        "mkdocs.plugins": [
            "image-gallery = mkdocs_image_gallery_plugin.plugin:ImageGalleryPlugin",
        ],
    },
)