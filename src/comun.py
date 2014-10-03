#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# comun.py
#
# Copyright (C) 2012 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#

__author__ = 'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'
__date__ ='$12/08/2011'
__copyright__ = 'Copyright (c) 2011 Lorenzo Carbonell'
__license__ = 'GPLV3'
__url__ = 'http://www.atareao.es'
__version__ = '0.0.2.4'

import os
import locale
import gettext
######################################

def is_package():
    return __file__.find('src') < 0

######################################

PARAMS = {	'first-time':True,
			'version':''
			}
			
RESOLUTION = 110.0/72.0


VERSION = __version__
APP = 'updf'
APP_CONF = APP + '.conf'
APPNAME = 'uPdf'
CONFIG_DIR = os.path.join(os.path.expanduser('~'),'.config')
CONFIG_APP_DIR = os.path.join(CONFIG_DIR, APP)
CONFIG_FILE = os.path.join(CONFIG_APP_DIR, APP_CONF)
#########################################
# check if running from source
if is_package():
    ROOTDIR = '/usr/share/'
    LANGDIR = os.path.join(ROOTDIR, 'locale-langpack')
    APPDIR = os.path.join(ROOTDIR, APP)
    ICONDIR = os.path.join(APPDIR, 'icons')
    CSSDIR = os.path.join(APPDIR,'css')
else:
    VERSION = VERSION + '-src'
    ROOTDIR = os.path.dirname(__file__)
    LANGDIR = os.path.normpath(os.path.join(ROOTDIR, '../template1'))
    ICONDIR = os.path.normpath(os.path.join(ROOTDIR, '../data/icons'))
    CSSDIR = os.path.normpath(os.path.join(ROOTDIR, '../data/css'))
    APPDIR = ROOTDIR
####
ICON = os.path.join(ICONDIR,'updf.svg')
CSSFILE = os.path.join(CSSDIR,'style.css')
current_locale, encoding = locale.getdefaultlocale()
try:
	language = gettext.translation (APP, LANGDIR, [current_locale] )
	language.install()
	_ = language.ugettext
except:
	_ = str
