#
"""conf - Sphinx configuration information."""
# Copyright © 2012-2018  James Rowe <jnrowe@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0+
#
# This file is part of rdial.
#
# rdial is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# rdial is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# rdial.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from contextlib import suppress
from subprocess import CalledProcessError, PIPE, run

root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, root_dir)

import rdial  # NOQA: E402

on_rtd = 'READTHEDOCS' in os.environ
if not on_rtd:
    import sphinx_rtd_theme

extensions = \
    [f'sphinx.ext.{ext}' for ext in ['autodoc', 'coverage', 'doctest',
                                     'intersphinx', 'napoleon', 'todo',
                                     'viewcode']] \
    + [f'sphinxcontrib.{ext}' for ext in []] \
    + ['sphinx_autodoc_typehints', 'sphinx_click.ext']  # type: List[str]


if not on_rtd:
    # Only activate spelling if it is installed.  It is not required in the
    # general case and we don’t have the granularity to describe this in a
    # clean way
    try:
        from sphinxcontrib import spelling  # NOQA: E401
    except ImportError:
        pass
    else:
        extensions.append('sphinxcontrib.spelling')

master_doc = 'index'
source_suffix = '.rst'

project = 'rdial'
author = 'James Rowe'
copyright = f'2011-2018  {author}'

release = rdial._version.dotted
version = release.rsplit('.', 1)[0]

html_experimental_html5_writer = True
modindex_common_prefix = ['rdial.', ]

# readthedocs.org handles this setup for their builds, but it is nice to see
# approximately correct builds on the local system too
if not on_rtd:
    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path(), ]  \
        # type: List[str]

pygments_style = 'sphinx'
with suppress(CalledProcessError):
    proc = run(['git', 'log', "--pretty=format:'%ad [%h]'", '--date=short',
                '-n1'],
               stdout=PIPE)
    html_last_updated_fmt = proc.stdout.decode()

html_baseurl = 'https://hubugs.readthedocs.io/'

man_pages = [
    ('rdial.1', 'rdial', 'rdial Documentation', ['James Rowe', ], 1)
]  # type: Tuple[str, str, str, List[str], int]

# Autodoc extension settings
autoclass_content = 'init'
autodoc_default_options = {
    'members': None,
}  # type: Dict[str, Optional[str]]

# intersphinx extension settings
intersphinx_mapping = {
    k: (v, os.getenv(f'SPHINX_{k.upper()}_OBJECTS'))
    for k, v in {
        'click': 'https://click.palletsprojects.com/en/7.x/',
        'jnrbase': 'https://jnrbase.readthedocs.io/en/latest/',
        'python': 'https://docs.python.org/3/',
}.items()}  # type: Dict[str, str]

# spelling extension settings
spelling_lang = 'en_GB'
spelling_word_list_filename = 'wordlist.txt'

# napoleon extension settings
napoleon_numpy_docstring = False

# todo extension settings
todo_include_todos = True
