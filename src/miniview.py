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
from gi.repository import Gdk
from gi.repository import GObject
import cairo
import math
import time
import comun
from threading import Thread

def wait(time_lapse):
	time_start = time.time()
	time_end = (time_start + time_lapse)
	while time_end > time.time():
		while Gtk.events_pending():
			Gtk.main_iteration()

class Renderer(Thread):
	def __init__ (self,page=None,size=None,callback=None):
		Thread.__init__(self)
		self.page = page
		if page:
			self.size = page.get_size()
		else:
			self.size = size
		self.is_rendered = False
		self.page_surface = None
		self.callback = callback

	def run(self):
		width, height = self.size
		width = int(width*comun.RESOLUTION)
		height = int(height*comun.RESOLUTION)
		self.page_surface = cairo.PDFSurface(None,width,height)
		context = cairo.Context(self.page_surface)
		context.scale(comun.RESOLUTION,comun.RESOLUTION)
		if self.page:
			self.page.render(context)		
		self.is_rendered = True
		self.callback()


class MiniView(Gtk.DrawingArea):
	__gsignals__ = {
        'selected' : (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,()),
        'unselected' : (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,())
        }
	
	def __init__(self,width=200.0,height=280.00,margin=10.0,border=2.0,force=False):
		Gtk.DrawingArea.__init__(self)
		self.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)
		self.height = height
		self.width = width
		self.image_surface = None
		self.margin = margin
		self.border = border
		self.is_rendered = False
		self.page = None
		self.is_blank_page = False
		self.page_width = -1
		self.page_height = -1
		self.margin_width = -1
		self.margin_height = -1
		self.selected = False
		self.rotation_angle = 0.0
		self.force = force
		self.drawings = []
		self.connect('draw', self.on_expose, None)
		self.connect('button-release-event',self.on_button_release_event)
		self.connect('selected',self.on_selected)
		self.set_size_request(self.width, self.height)
	
	def on_button_release_event(self,widget,data):
		self.selected = not self.selected
		if self.selected:
			self.emit('selected')
			self.queue_draw()
			
	def on_selected(self,widget):
		self.force = True
		self.queue_draw()
		
	def render(self):
		if self.renderer.is_rendered == False:
			if not self.renderer.isAlive():
				self.renderer.run()					
			if self.force:
				while not self.renderer.is_rendered:
					wait(0.1)
			self.force = False
		self.queue_draw()
		
	def on_expose(self, widget, cr, data):
		if self.page or self.is_blank_page:
			if self.rotation_angle == 0.0 or self.rotation_angle == 2.0:
				zw = (self.width-2.0*self.margin)/self.or_width
				zh = (self.height-2.0*self.margin)/self.or_height
				if zw < zh:
					self.zoom = zw
				else:
					self.zoom = zh
				self.page_width = self.or_width*self.zoom
				self.page_height = self.or_height*self.zoom
				self.margin_width = (self.width - self.page_width)/2.0
				self.margin_height = (self.height - self.page_height)/2.0
			else:
				zw = (self.width-2.0*self.margin)/self.or_height
				zh = (self.height-2.0*self.margin)/self.or_width
				if zw < zh:
					self.zoom = zw
				else:
					self.zoom = zh
				self.page_width = self.or_height*self.zoom
				self.page_height = self.or_width*self.zoom
				self.margin_width = (self.width - self.page_width)/2.0
				self.margin_height = (self.height - self.page_height)/2.0				
			
			if not self.is_rendered:				
				self.image_surface = cairo.ImageSurface(cairo.FORMAT_RGB24,int(self.page_width),int(self.page_height)) 
				context = cairo.Context(self.image_surface)
				context.save()
				context.set_source_rgba(1.0, 1.0, 1.0, 1.0)
				context.paint()
				mtr = cairo.Matrix()
				mtr.rotate(self.rotation_angle*math.pi/2.0)
				mtr.scale(self.zoom, self.zoom)
				context.transform(mtr)
				if self.rotation_angle == 1.0:
						context.translate(0.0,-self.page_width/self.zoom)
				elif self.rotation_angle == 2.0:
						context.translate(-self.page_width/self.zoom,-self.page_height/self.zoom)
				elif self.rotation_angle == 3.0:
						context.translate(-self.page_height/self.zoom,0.0)
				if self.renderer.is_rendered:
					context.set_source_surface(self.renderer.page_surface)
					context.paint()
					self.is_rendered = True
				else:
					self.render()
					pass
				for drawing in self.drawings:
					drawing.draw(context)				
				context.restore()
				
			cr.save()
			if self.selected:
				cr.set_source_rgba(1.0, 0.5, 0.0, 0.5)
			else:
				cr.set_source_rgba(0.0, 0.0, 0.0, 0.5)
			cr.rectangle(self.margin_width-self.border, self.margin_height-self.border,
			self.page_width+2.0*self.border, self.page_height+2.0*self.border)
			cr.stroke()
			cr.restore()
			#
			cr.set_source_surface(self.image_surface,self.margin_width,self.margin_height)
			cr.paint()
			### Painting drawings ###
			cr.save()
			cr.rectangle(self.margin_width,self.margin_height,self.page_width,self.page_height)
			cr.clip()
			cr.translate(self.margin_width,self.margin_height)
			mtr = cairo.Matrix()
			'''
			'''
			mtr.rotate(self.rotation_angle*math.pi/2.0)
			mtr.scale(self.zoom, self.zoom)
			cr.transform(mtr)
			if self.rotation_angle == 1.0:
				cr.translate(0.0,-self.page_width/self.zoom)
			elif self.rotation_angle == 2.0:
				cr.translate(-self.page_width/self.zoom,-self.page_height/self.zoom)
			elif self.rotation_angle == 3.0:
				cr.translate(-self.page_height/self.zoom,0.0)			
			'''
			mtr.scale(self.zoom, self.zoom)
			cr.transform(mtr)			
			'''
			for drawing in self.drawings:
				drawing.draw(cr)
			cr.restore()
	def get_image(self):
		self.render()
		self.queue_draw()
		return self.renderer.page_surface
		
	def get_selected(self):
		return self.selected
	
	def set_selected(self,selected):
		self.selected = selected
		self.force = True
		self.queue_draw()
		if selected:
			self.emit('selected')		
		else:
			self.emit('unselected')

	def rotate_clockwise(self):
		self.rotation_angle += 1.0
		if self.rotation_angle > 3.0:
			self.rotation_angle = 0.0
		self.is_rendered = False
		self.queue_draw()		

	def rotate_counter_clockwise(self):
		self.rotation_angle -= 1.0
		if self.rotation_angle < 0.0:
			self.rotation_angle = 3.0
		self.is_rendered = False
		self.queue_draw()
		
	def set_page(self, page):
		self.is_rendered = False
		self.page = page
		self.is_blank_page = False
		self.selected = False
		self.rotation_angle = 0.0
		self.drawings = []		
		self.or_width, self.or_height = self.page.get_size()
		self.or_width = int(self.or_width*comun.RESOLUTION)
		self.or_height = int(self.or_height*comun.RESOLUTION)
		self.renderer = Renderer(page=page,callback=self.queue_draw)
		self.queue_draw()
		for i in page.get_annot_mapping():
			try:
				annot = i.annot
				print annot.get_annot_type()
				print annot.get_label()
				contents = annot.get_contents()
				if contents:
					print "Annotation: %s" % contents
			except AttributeError,e:
				print e
				# ooops...
				pass		

	def set_blank_page(self, width, height):
		self.is_rendered = False
		self.page = None
		self.is_blank_page = True
		self.selected = False
		self.rotation_angle = 0.0
		self.drawings = []		
		self.blank_page_size = (width,height)
		self.or_width = int(width*comun.RESOLUTION)
		self.or_height = int(height*comun.RESOLUTION)
		self.renderer = Renderer(size=(width,height),callback=self.queue_draw)
		self.queue_draw()

	def get_page(self):
		return self.page

	def get_size(self):
		if self.page:
			return self.page.get_size()
		return self.blank_page_size
			
			
