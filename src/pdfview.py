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

from gi.repository import Gtk
from gi.repository import GObject
from miniview import MiniView
import cairo

#class PdfView(Gtk.Table):

class PdfView(Gtk.VBox):
	__gsignals__ = {
        'selected' : (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,(int,)),
        'unselected' : (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,(int,))        
        }
	
	def __init__(self,width=200,height=280):
		#Gtk.Table.__init__(self,rows=1,columns=1,homogeneous=True)
		Gtk.VBox.__init__(self)
		self.selected = -1
		self.columns = 1
		self.width = width
		self.height = height

	def reset(self):
		for page in self.get_children():
			self.remove(page)
		self.resize_children()
		#Gtk.Table.__init__(self,rows=1,columns=1,homogeneous=True)
		Gtk.VBox.__init__(self)
		self.selected = -1
		self.columns = 1
		self.queue_draw()

	def update_current_page(self):
		self.get_children()[self.selected].set_selected(True)
		self.get_children()[self.selected].force = True
		self.get_children()[self.selected].queue_draw()
		self.emit('selected',self.selected)

	def unselect(self):
		if self.selected > -1 and self.selected < self.get_number_of_pages()-1:
			self.get_children()[self.selected].set_selected(False)
			self.get_children()[self.selected].queue_draw()
			#self.emit('unselected',self.selected)
		self.selected = -1
	
	def select_page(self,number_of_page):
		self.unselect()
		self.selected = number_of_page
		self.get_children()[self.selected].set_selected(True)
		self.get_children()[self.selected].force = True
		self.get_children()[self.selected].queue_draw()
		#self.emit('selected',number_of_page)

	def get_number_of_selected_page(self):
		return self.selected
		
	def get_selected_page(self):
		if self.selected>-1:
			return self.get_children()[self.selected]
		return None
		
	def get_page(self,number_of_page):
		return self.get_children()[number_of_page]

	def set_page(self,number_of_page,page):
		self.get_children()[number_of_page] = page

	def on_page_selected(self,widget):		
		sp = self.get_index_of_selected_child(widget)
		if sp !=self.selected:
			self.unselect()
			self.selected = sp
			self.emit('selected',sp)

	def on_page_unselected(self,widget):
		sp = self.get_index_of_selected_child(widget)
		self.emit('unselected',sp)
		
	def get_index_of_selected_child(self,child):
		for index,achild in enumerate(self.get_children()):
			if achild == child:
				return index
		return -1

	def get_number_of_pages(self):
		return len(self.get_children())
	
	def remove_page(self,number_of_page):
		if self.selected > number_of_page:
			self.get_children()[self.selected].set_selected(False)
			if self.selected > 0:
				self.select_page(self.selected-1)
		self.remove(self.get_children()[number_of_page])
		
	def insert_page(self,page,position=None):
		view = MiniView(self.width,self.height)
		view.connect('selected',self.on_page_selected)
		view.connect('unselected',self.on_page_unselected)
		view.set_page(page)
		view.show()
		self.pack_start(view, expand=True, fill=True, padding=0)
		self.set_homogeneous(True)
		if position!=None:
			if position>0:
				self.reorder_child(self.get_children()[-1],position)
			else:
				self.reorder_child(self.get_children()[-1],1)
				self.reorder_child(self.get_children()[0],1)
				
	def insert_blank_page(self,width,height,position=None):
		view = MiniView(self.width,self.height)
		view.connect('selected',self.on_page_selected)
		view.connect('unselected',self.on_page_unselected)
		view.set_blank_page(width,height)
		view.show()
		self.pack_start(view, expand=True, fill=True, padding=0)
		self.set_homogeneous(True)
		if position!=None:
			if position>0:
				self.reorder_child(self.get_children()[-1],position)
			else:
				self.reorder_child(self.get_children()[-1],1)
				self.reorder_child(self.get_children()[0],1)
if __name__ == '__main__':
	pv =PdfView()
