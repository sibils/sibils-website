# SIBILS documentation

## How to edit the documentation

### Git clone

* Python must be installed
* `git clone git@github.com:sibils/sibils-website`
* `cd sibils.github.io`
* Start mkdocs:
    * Linux and Mac: `./serve`
    * Windows: `.\serve.bat`
* Open http://127.0.0.1:8000/
* Change some files; the browser page is updated automatically.
* `git add .; git commit; git push`
* The website is going to update itself after a few minutes.

### On GitHub

* On a web page, click on the pencil icon in the top right corner: the link goes to the GitHub page.
* Make the change on GitHub; check using the Preview tab.
* Confirm the change using the "Commit changes" at the bottom of the page (commit into the master branch).
* The website is going to update itself after a few minutes.

### Change the website structure

* git clone the project.
* make the change into the `nav` section of `mkdocs.yml`.

## Syntax

* [markdown with Mkdocs](https://www.mkdocs.org/user-guide/writing-your-docs/#writing-with-markdown)
* markdown extensions provided by Material for Mkdocs:
    * [Admonitions](https://squidfunk.github.io/mkdocs-material/reference/admonitions/) (Tips, Warning boxes)
    * [Diagrams](https://squidfunk.github.io/mkdocs-material/reference/diagrams/), see also [mermaid documentation](https://mermaid-js.github.io/mermaid/#/README?id=diagram-types)
    * [Content tabs](https://squidfunk.github.io/mkdocs-material/reference/content-tabs/)
    * [Footnotes](https://squidfunk.github.io/mkdocs-material/reference/footnotes/)
    * [Images with captions](https://squidfunk.github.io/mkdocs-material/reference/images/#image-captions)
    * [Various list types](https://squidfunk.github.io/mkdocs-material/reference/lists/)
    * [Abbreviations](https://squidfunk.github.io/mkdocs-material/reference/tooltips/#adding-abbreviations)
    * [Icons and emojis](https://squidfunk.github.io/mkdocs-material/reference/icons-emojis/)

## Python Dependencies

* [MkDocs](https://www.mkdocs.org/) for documentation generator
* [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/getting-started/) for theme

## Customizations used in this repository

* https://squidfunk.github.io/mkdocs-material/customization/
    * `mkdocs.yml`, section `theme.custom_dir`
    * `overrides/partials/copyright.html`: custom footer.
* https://squidfunk.github.io/mkdocs-material/setup/changing-the-colors/#custom-color-schemes
    * `mkdocs.yml`, section `extra_css`
    * `mkdocs.yml`, section `theme.palette.scheme`
    * `docs/assets/extra.css`
* https://squidfunk.github.io/mkdocs-material/setup/changing-the-fonts/#autoloading
    * disable Google Font to complying with the General Data Protection Regulation (GDPR)
    * `mkdocs.yml`, section `theme.font`
* https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/#navigation-tabs
    * `mkdocs.yml`, `theme.features.navigation.tabs`
* https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/#section-index-pages
    * `mkdocs.yml`, `theme.features.navigation.indexes`
* https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/#hiding-the-sidebars
    * `docs/index.md`
    * `docs/vocabularies.md`
