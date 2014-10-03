#! /usr/bin/python
# -*- coding: iso-8859-15 -*-
#
__author__='atareao'
__date__ ='$06-jun-2010 12:34:44$'
#
# <one line to give the program's name and a brief idea of what it does.>
#
# Copyright (C) 2010 Lorenzo Carbonell
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

class Progreso(Gtk.Dialog):
	def __init__(self,title,parent,max_value):
		#
		Gtk.Dialog.__init__(self,title,parent)
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_size_request(330, 40)
		self.set_resizable(False)
		self.connect('destroy', self.close)
		#
		vbox1 = Gtk.VBox(spacing = 5)
		vbox1.set_border_width(5)
		self.get_content_area().add(vbox1)
		#
		self.progressbar = Gtk.ProgressBar()
		vbox1.pack_start(self.progressbar,True,True,0)
		#
		self.show_all()
		#
		self.max_value=max_value
		self.value=0.0
		self.map()
		while Gtk.events_pending():
			Gtk.main_iteration()


	def set_value(self,value):
		if value >=0 and value<=self.max_value:
			self.value = value
			fraction=self.value/self.max_value
			self.progressbar.set_fraction(fraction)
			self.map()
			while Gtk.events_pending():
				Gtk.main_iteration()
			if self.value==self.max_value:
				self.hide()		
	def close(self,widget=None):
		self.destroy()

	def increase(self):
		self.value+=1.0
		fraction=self.value/self.max_value
		self.progressbar.set_fraction(fraction)
		while Gtk.events_pending():
			Gtk.main_iteration()
		if self.value==self.max_value:
			self.hide()

	def decrease(self):
		self.value-=1.0
		fraction=self.value/self.max_value
		self.progressbar.set_fraction(fraction)
		self.map()
		while Gtk.events_pending():
			Gtk.main_iteration()

if __name__ == '__main__':
	p = Progreso('Prueba',None,100)
	
