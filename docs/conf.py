from os import path
import sys

sys.path.append('..')

project = 'ncfacbot'
copyright = '2020, haliphax'
author = 'haliphax'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_theme = 'nature'
html_static_path = ['_static']
