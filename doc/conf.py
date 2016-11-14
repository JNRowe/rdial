#
# coding=utf-8
"""conf - Sphinx configuration information."""
# Copyright © 2012-2016  James Rowe <jnrowe@gmail.com>
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

from subprocess import (CalledProcessError, check_output)

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, root_dir)

import rdial

extensions = \
    ['sphinx.ext.%s' % ext for ext in ['autodoc', 'coverage', 'doctest',
                                       'intersphinx', 'napoleon',
                                       'viewcode']] \
    + ['sphinxcontrib.%s' % ext for ext in ['cheeseshop']]

# Only activate spelling if it is installed.  It is not required in the
# general case and we don't have the granularity to describe this in a clean
# way
try:
    from sphinxcontrib import spelling  # NOQA
except ImportError:
    pass
else:
    extensions.append('sphinxcontrib.spelling')

master_doc = 'index'
source_suffix = '.rst'

project = u'rdial'
copyright = rdial.__copyright__

version = '.'.join(map(str, rdial._version.tuple[:2]))
release = rdial._version.dotted

pygments_style = 'sphinx'
try:
    html_last_updated_fmt = check_output(['git', 'log',
                                          "--pretty=format:'%ad [%h]'",
                                          '--date=short', '-n1'])
except CalledProcessError:
    pass

man_pages = [
    ('rdial.1', 'rdial', u'rdial Documentation', [u'James Rowe'], 1)
]

# Autodoc extension settings
autoclass_content = 'init'
autodoc_default_flags = ['members', ]

# intersphinx extension settings
intersphinx_mapping = {k: (v, os.getenv('SPHINX_%s_OBJECTS' % k.upper()))
                       for k, v in {
                           'click': 'http://click.pocoo.org/6/',
                           'python': 'http://docs.python.org/',
}.items()}

# spelling extension settings
spelling_lang = 'en_GB'
spelling_word_list_filename = 'wordlist.txt'

# napoleon extension settings
napoleon_numpy_docstring = False
