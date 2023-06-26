# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Software (information) --------------------------------------------------

from delft_fiat.version import __version__

import os
import shutil
import sphinx_autosummary_accessors


def remove_dir_content(path: str) -> None:
    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    if os.path.isdir(path):
        shutil.rmtree(path)


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Delft-FIAT"
copyright = "Deltares"
author = "B.W. Dalmijn"
version = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "m2r2",
    "numpydoc",
    "sphinx_design",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.duration",
    "sphinx_autosummary_accessors",
]

autosummary_generate = True
templates_path = ["../_templates", sphinx_autosummary_accessors.templates_path]
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
todo_include_todos = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# napoleon_numpy_docstring = True
# napoleon_google_docstring = False
# napoleon_preprocess_types = True

numpydoc_attributes_as_param_list = False

html_theme = "pydata_sphinx_theme"
html_logo = "../../res/FIAT.png"
autodoc_member_order = "bysource"
autoclass_content = "both"
html_static_path = ["_static"]
html_css_files = ["theme-deltares.css"]
html_show_sourcelink = False
html_theme_options = {
    "show_nav_level": 1,
    "navigation_depth": 4,
    "navbar_align": "content",
    "search_bar_text": "Search the docs...",
    "search_bar_position": "navbar",
    "use_edit_page_button": False,
    "show_prev_next": False,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/Deltares/Delft-FIAT",
            "icon": "fab fa-github",
            "type": "fontawesome",
        },
        {
            "name": "Deltares",
            "url": "https://www.deltares.nl/en/",
            "icon": "_static/deltares-blue.svg",
            "type": "local",
        },
    ],
    "logo": {
        "text": "Delft-FIAT",
    },
    # "navbar_end": ["navbar-icon-links"],
}

html_context = {
    "github_url": "https://github.com",  # or your GitHub Enterprise interprise
    "github_user": "Deltares",
    "github_repo": "Delft-FIAT",
    "github_version": "master",  # FIXME
    "doc_path": "docs",
    "default_mode": "auto",
}

remove_from_toctrees = ["_generated/*"]

# -- Options for HTMLHelp output ------------------------------------------
htmlhelp_basename = "fiat_doc"
