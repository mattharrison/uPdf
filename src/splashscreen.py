#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# splashscreen.py
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

from gi.repository import Gtk
from gi.repository import Gdk
import cairo
import time
import os
import math
import comun
from comun import _

def wait(time_lapse):
	time_start = time.time()
	time_end = (time_start + time_lapse)
	while time_end > time.time():
		while Gtk.events_pending():
			Gtk.main_iteration()
			
class SplashScreen(Gtk.Window):     
	def __init__(self):
		Gtk.Window.__init__(self,type=Gtk.WindowType.TOPLEVEL)
		self.set_title('uPdf')
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_icon_from_file(comun.ICON)		
		self.set_decorated(False)
		self.set_app_paintable(True)

		screen = self.get_screen()
		visual = screen.get_rgba_visual()
		if visual and screen.is_composited():
			self.set_visual(visual)
		
		self.set_default_size(250, 250)
		self.add_events(Gdk.EventMask.ALL_EVENTS_MASK)
		self.connect('draw', self.on_expose, None)		
		image = Gtk.Image()
		image.set_from_file(comun.ICON)
		vbox = Gtk.VBox(False, 1)
		self.add(vbox)
		vbox.pack_start(image, True, True, 2)
		vbox1 = Gtk.VBox(False, 1)
		vbox.add(vbox1)
		titlelabel = Gtk.Label()
		titlelabel.set_markup("<span foreground='black' font_desc='Ubuntu 20'><b>%s</b></span>" % ('uPdf'))
		vbox1.pack_start(titlelabel, False, False, 0)
		versionlabel = Gtk.Label()
		versionlabel.set_markup("<span foreground='black' font_desc='Ubuntu 14'>%s</span>" % (_('Version')+': '+comun.VERSION))
		vbox1.pack_start(versionlabel, False, False, 0)
		otherlabel1 = Gtk.Label()
		otherlabel1.set_markup("<span foreground='black' font_desc='Ubuntu 12'>%s</span>" % ('\nCopyright (c) 2012'))
		vbox1.pack_start(otherlabel1, False, False, 0)
		otherlabel2 = Gtk.Label()
		otherlabel2.set_markup("<span foreground='black' font_desc='Ubuntu 12'>%s</span>" % ('http://www.atareao.es'))
		vbox1.pack_start(otherlabel2, False, False, 0)
		otherlabel3 = Gtk.Label()
		otherlabel3.set_markup("<span foreground='black' font_desc='Ubuntu 12'>%s</span>" % ('Lorenzo Carbonell'))
		vbox1.pack_start(otherlabel3, False, False, 0)
		self.show_all()
		
	def on_expose(self, widget, cr, data):
		cr.save()
		# Sets the operator to clear which deletes everything below where an object is drawn
		cr.set_operator(cairo.OPERATOR_CLEAR)
		# Makes the mask fill the entire window
		cr.rectangle(0.0, 0.0, *widget.get_size())
		# Deletes everything in the window (since the compositing operator is clear and mask fills the entire window
		cr.fill()
		# Set the compositing operator back to the default
		#cr.set_operator(cairo.OPERATOR_OVER)
		cr.restore()
		'''
		cr.set_source_rgba(0.5,1.0,0.0,1)
		cr.arc(widget.get_size()[0]/2,widget.get_size()[1]/2,
			   widget.get_size()[0]/2,0,math.pi*2)
		cr.fill()
		'''
        
class yourApp():
    def __init__(self):
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.set_title('Your app name')
        self.window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.window.connect('destroy',	Gtk.main_quit)
        main_vbox = Gtk.VBox(False, 1) 
        self.window.add(main_vbox)
        hbox = Gtk.HBox(False, 0)
        self.lbl = Gtk.Label('All done! :)')
        self.lbl.set_alignment(0, 0.5)
        main_vbox.pack_start(self.lbl, True, True,0)
        self.window.show_all()      
        
        
if __name__ == "__main__":
    ss = SplashScreen()
    wait(3) 
    app = yourApp()
    ss.destroy() 
    Gtk.main()
