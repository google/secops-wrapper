# -*- coding: utf-8 -*-
import datetime
import os
import sys
from subprocess import PIPE, Popen

# Add parent directory to path for module imports
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
project = "Google SecOps SDK for Python"
author = "Google Cloud Security"
copyright = f"{datetime.date.today().year}, {author}"

# The version info for the project you're documenting
try:
    pipe = Popen("git describe --tags --always", stdout=PIPE, shell=True)
    git_version = pipe.stdout.read().decode("utf8").strip()

    if git_version:
        version = git_version.rsplit("-", 1)[0]
        release = git_version
    else:
        version = "0.1.0"
        release = "0.1.0"
except Exception:
    version = "0.1.0"
    release = "0.1.0"

# Add any Sphinx extension module names here
extensions = [
    "myst_parser",           # Markdown support
    "sphinx_copybutton",     # Add copy buttons to code blocks
    "sphinx.ext.autodoc",    # API documentation
    "sphinx.ext.viewcode",   # Add links to view source code
    "sphinx.ext.napoleon",   # Support for Google-style docstrings
    "sphinx.ext.intersphinx", # Link to other projects' documentation
    "sphinx_click",         # Document click-based CLI applications
]

# MyST Parser configuration for extended Markdown support
myst_enable_extensions = [
    "colon_fence",           # Code blocks with colons
    "deflist",              # Definition lists
    "fieldlist",            # Field lists
    "html_admonition",      # HTML admonitions
    "html_image",           # HTML images
    "replacements",         # Text replacements
    "smartquotes",          # Smart quotes
    "tasklist",            # Task lists with checkboxes
]

# Support both .md and .rst files
source_suffix = [".rst", ".md"]

# The master toctree document
master_doc = "index"

# Add any paths that contain templates
templates_path = ["_templates"]

# Files to exclude from documentation build
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "venv",
    "env",
    "**/.git/**",
    "requirements.txt",
    "Makefile"
]

# Syntax highlighting style
pygments_style = "default"

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"

html_logo = "img/SecOps-512-color.png"
html_favicon = "img/SecOps-32-color.png"

# documentation.
html_theme_options = {}
html_title = project

# Create _static directory if it doesn't exist
static_dir = os.path.join(os.path.dirname(__file__), '_static')
os.makedirs(static_dir, exist_ok=True)

# Set static paths for custom CSS/JS/images
html_static_path = ["_static", "img"]

# Theme options
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#1a73e8",    # Google Blue
        "color-brand-content": "#1a73e8",
    },
    "dark_css_variables": {
        "color-brand-primary": "#8ab4f8",    # Google Blue (dark mode)
        "color-brand-content": "#8ab4f8",
    },
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "announcement": "This is documentation for the Google SecOps SDK for Python.",
}

# Intersphinx mapping to other projects
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
}

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False

# Copy button settings
copybutton_prompt_text = "$ "
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = False
copybutton_remove_prompts = True

# Output file base name for HTML help builder.
htmlhelp_basename = "secops-sdk-doc"

# -- Options for LaTeX output ---------------------------------------------
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "secops-sdk.tex",
        project,
        author,
        "manual",
    )
]
