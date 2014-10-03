#! /usr/bin/python
# -*- coding: utf-8 -*-
#
__author__='Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'
__date__ ='$07/07/2012$'
#
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
from gi.repository import Gtk,Gdk, GObject
import drawing
import time

LATENCY = 1#seconds

class ToolScaleButton(Gtk.ToolItem):
	def __init__(self):
		Gtk.ToolItem.__init__(self)
		self.scalebutton = ScaleButton()
		self.scalebutton.set_can_focus(False)
		self.scalebutton.set_size_request(40,40)
		self.add(self.scalebutton)

	def set_sensitive(self,sensitive):
		super(ToolScaleButton,self).set_sensitive(sensitive)
		self.scalebutton.set_sensitive(sensitive)

class ScaleButton(Gtk.DrawingArea):
	
	def __init__(self):
		Gtk.DrawingArea.__init__(self)
		self.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.SCROLL_MASK)
		self.connect('draw', self.on_expose, None)
		self.connect('enter-notify-event',self.mouse_in)
		self.connect('motion-notify-event',self.mouse_in)
		self.connect('leave-notify-event',self.mouse_out)
		self.connect('button-press-event',self.on_button_press)
		self.connect('button-release-event',self.on_button_release)
		self.connect('scroll-event', self.wheel)  
		self.value = 1
		self.set_size_request(40,40)
		self.selected = False
		self.mouse_inside = False
		
	def wheel(self,widget,event):
		if event.direction == Gdk.ScrollDirection.UP:
			value = self.value + 1
			if value > 100:
				value = 100
		elif event.direction == Gdk.ScrollDirection.DOWN:
			value = self.value - 1
			if value < 1:
				value = 1
		self.set_value(value)
		
	def on_button_press(self,widget,event):
		pass

	def on_button_release(self,widget,event):
		pass
				
	def mouse_in(self,widget,color):
		self.mouse_inside = True
		self.queue_draw()

	def mouse_out(self,widget,color):
		self.mouse_inside = False
		self.queue_draw()
		
	def on_expose(self, widget, cr, data):		
		cr.rectangle(0,0,40,40)
		if self.sensitive:
			if self.mouse_inside:
				backgroundcolor = drawing.GREY
			else:
				if self.selected:
					backgroundcolor = drawing.GREY2
				else:
					backgroundcolor = drawing.UBUNTU
		else:
			backgroundcolor = drawing.UBUNTU
		cr.set_source_rgba(backgroundcolor.r,backgroundcolor.g,backgroundcolor.b,backgroundcolor.a)
		cr.fill()		
		if self.sensitive:
			cr.set_source_rgba(drawing.MINE.r,drawing.MINE.g,drawing.MINE.b,drawing.MINE.a)
		else:
			cr.set_source_rgba(drawing.UNACTIVE.r,drawing.UNACTIVE.g,drawing.UNACTIVE.b,drawing.UNACTIVE.a)
		h = int(30*self.value/100)		
		print h,(30-h)/2
		cr.rectangle(5,(h-30)/2,30,h)
		cr.fill()		

	def set_selected(self,selected):
		self.selected = selected
		self.queue_draw()
		
	def get_selected(self):
		return self.selected

	def set_sensitive(self,sensitive):
		self.sensitive = sensitive
		self.mouse_inside = False
		print sensitive
		self.queue_draw()
		
	def set_value(self,value):
		self.value = int(value)
		self.set_tooltip_text(('Value'+' %s'%(self.value)))
		print ('Value'+' %s'%(self.value))
		self.queue_draw()
		
	def get_value(self):
		return int(self.value)

		
class PopUpScale(Gtk.HBox):
	__gsignals__ = {
        'selected' : (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,())
        }
	
	def __init__(self, window, index=0, values = [], height = 150):
		Gtk.HBox.__init__(self)
		self._window = window
		self.entry = Gtk.Entry()
		self.entry.set_editable(False)
		self.button = Gtk.Button()
		self.button.add(Gtk.Arrow.new(Gtk.ArrowType.DOWN,
									  Gtk.ShadowType.IN))
		self.button.connect('clicked', self.on_button)
		self.button.connect('key-press-event',self.on_key_pressed)
		self.entry.connect('key-press-event',self.on_key_pressed)
		self.pack_start(self.entry, True,True,0)
		self.pack_start(self.button, False,False, 0)
		self.index = index
		self.values = values
		self.height = height
		self.sbuffer = ''
		self.refresh_time = 0
		self.create_window()
				
	def create_window(self):
		self.dialog = Gtk.Dialog(None, self._window,
								 Gtk.DialogFlags.MODAL)	
		self.dialog.set_decorated(False)
		self.scale = Gtk.Scale()
		self.dialog.vbox.pack_start(scrolledwindow, True,True,0)
		#
		self.tree = Gtk.TreeView()
		self.tree.set_headers_visible(False)
		renderer = Gtk.CellRendererText()
		column = Gtk.TreeViewColumn(title=None,cell_renderer=renderer, text=0)
		self.tree.append_column(column)
		#
		scrolledwindow.add(self.tree)

		self.dialog.connect('key-press-event',self.on_key_pressed)
		self.dialog.connect('focus-out-event',self.on_focus_out)
		self.tree.connect('cursor-changed',self.on_cursor_changed)
		#
		self.set_values(self.values)
		self.dialog.show_all()
		
	def on_key_pressed(self,widget,event):
		if (time.time() - self.refresh_time)> LATENCY:
			self.sbuffer = ''
		self.refresh_time = time.time()
		if event.keyval == 65364 or event.keyval == 65433:
			self.index+=1
			if self.index > len(self.values)-1:
				self.index = len(self.values)-1
			self.entry.set_text(self.values[self.index])
			self.tree.set_cursor(self.index)
			self.emit('selected')
			return True
		elif event.keyval == 65362 or event.keyval == 65431:
			self.index-=1
			if self.index < 0:
				self.index = 0
			self.entry.set_text(self.values[self.index])
			self.tree.set_cursor(self.index)
			self.emit('selected')
			return True
			
		self.sbuffer += Gdk.keyval_name(event.keyval).upper()
		for index,value in enumerate(self.values):
			if value.upper().startswith(self.sbuffer):
				if type(widget) == Gtk.Button or type(widget) == Gtk.Entry:
					self.index = index
					self.entry.set_text(value)
					self.emit('selected')
				elif type(widget) == Gtk.Dialog:
					self.set_index(index)
					self.emit('selected')
				return

	def set_sensitive(self, is_sensistive):
		self.entry.set_sensitive(is_sensistive)
		self.button.set_sensitive(is_sensistive)

	def set_editable(self, is_editable):
		self.entry.set_editable(is_editable)
		self.button.set_editable(is_editable)

	def set_height(height=150):
		self.height=height
		
	def on_button(self, button):
		win_position = self._window.get_position()
		x_win = win_position[0] + self.entry.get_allocation().x + 3
		y_win = win_position[1] + self.entry.get_allocation().y + 2*self.entry.get_allocation().height + 3
		self.dialog.set_size_request(self.entry.get_allocation().width,self.height)
		
		self.dialog.move(x_win, y_win)
		self.dialog.grab_focus()
		self.set_index(self.index)
		self.dialog.run()
		self.dialog.hide()
			
	def on_focus_out(self,widget,event):
		self.dialog.hide()
		
	def set_index(self,index):
		self.index = index
		self.tree.set_cursor(index)

	def set_values(self,values):
		self.values = values
		self.store = Gtk.ListStore(str)
		for value in self.values:
			if type(value)==list:
				self.store.append(value)
			else:
				self.store.append([value])
		self.tree.set_model(self.store)
		
	def get_index(self):
		return self.index
	
	def get_selected_value(self):
		return self.entry.get_text()
			
	def on_cursor_changed(self,widget):
		store,iter = self.tree.get_selection().get_selected()
		if store and iter:
			self.entry.set_text(store.get_value(iter,0))
			self.index = int(str(store.get_path(iter)))
			if self.index:
				self.emit('selected')
			self.dialog.hide()
