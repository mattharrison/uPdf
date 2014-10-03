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
from gi.repository import GdkPixbuf
from drawing import *
import os
import sys
import cairo
import array
import tempfile
import numpy
import comun
from comun import _

'''
'GdkPixdata', 'ras', 'tiff', 'wmf', 'icns', 'ico', 'png', 'qtif', 
 'wbmp', 'gif', 'pnm', 'tga', 'ani', 'xbm', 'xpm', 'jpeg2000', 
 'pcx', 'jpeg', 'bmp', 'svg']

'''
def load_image_to_pixbuf(filename):
	pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbuf.get_width(),pixbuf.get_height())
	context = cairo.Context(surface)
	Gdk.cairo_set_source_pixbuf(context, pixbuf,0,0)
	context.paint()
	return surface

class View(Gtk.DrawingArea):
	def __init__(self,viewport=None,parent=None,margin=10.0,border=2.0):
		super(View, self).__init__()
		self.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)
		self.connect('draw', self.on_expose, None)
		self.connect('motion-notify-event', self.on_move, None)
		self.connect('button-press-event', self.on_button_press, None)
		self.connect('button-release-event', self.on_button_release, None)
		self.selection_end = None
		self.selection_start = None
		self.mouse_down = None
		self.page = None
		self.number_of_page = None
		self.zoom = 1.0
		self.margin = margin
		self.border = border
		self.tool = None
		self.snap_to_grid = False
		self.viewport = viewport
		self.parent = parent
		self.text = ''
		self.drawings = []
		self.rotation_angle = 0.0
		self.moving_drawing = None
		self.cairo_context = None

	def zoom_fit(self):
		self.is_rendered = False
		self.selection_end = None
		self.selection_start = None
		self.mouse_down = None
		rect = self.viewport.get_allocation()
		zw = float(rect.width)/float(self.width + 2.0*self.margin)
		zh = float(rect.height)/float(self.height + 2.0*self.margin)
		if zw > zh:
			self.zoom = zh
		else:
			self.zoom = zw
		self.queue_draw()

	def zoom_in(self):
		if self.zoom < 8:
			self.is_rendered = False
			self.selection_end = None
			self.selection_start = None
			self.mouse_down = None
			self.zoom += 0.1
			self.queue_draw()

	def zoom_out(self):
		if self.zoom > 0.3:
			self.is_rendered = False
			self.selection_end = None
			self.selection_start = None
			self.mouse_down = None
			self.zoom -= 0.1
			self.queue_draw()

	def zoom_reset(self):
		self.zoom = 1.0
		self.is_rendered = False
		self.selection_end = None
		self.selection_start = None
		self.mouse_down = None
		self.queue_draw()

	def snap_grid(self, x, y):
		#if not self.page:
		#	return (0, 0)
		rounded = 1.0
		if self.snap_to_grid:
			rounded = 5.0
			width, height = self.page.get_size()
			return (min(int(x / self.zoom / rounded) * rounded, width),
				min(int(y / self.zoom / rounded) * rounded, height))
		return x/self.zoom,y/self.zoom

	def on_move(self, widget, event, data):
		if self.mouse_down:
			if self.moving_drawing:
				x = (event.x - self.margin_width)/self.zoom
				y = (event.y - self.margin_height)/self.zoom
				if self.rotation_angle == 0.0:
					x1 = x
					y1 = y
				elif self.rotation_angle == 1.0:
					x1 = y
					y1 = self.page_width/self.zoom - x
				elif self.rotation_angle == 2.0:
					x1 = self.page_width/self.zoom - x
					y1 = self.page_height/self.zoom - y
				elif self.rotation_angle == 3.0:
					x1 = self.page_height/self.zoom - y
					y1 = x
				x0,y0,drawing = self.moving_drawing
				print('###############################################')
				#drawing.move((x1-x0)/comun.RESOLUTION,(y1-y0)/comun.RESOLUTION)
				drawing.move((x1-x0),(y1-y0))
				self.moving_drawing = (x1,y1,drawing)
				print(self.zoom)
				print(x0,y0,x1,y1)
				self.is_rendered = False
				self.queue_draw()
			else:
				new_selection_end = self.snap_grid(event.x, event.y)
				if self.selection_end or (self.selection_end != new_selection_end):
					self.selection_end = new_selection_end
					self.queue_draw()
		else:
			if self.tool in ['arrow','remove']:
				somethingchanged = False
				x = (event.x - self.margin_width)/self.zoom
				y = (event.y - self.margin_height)/self.zoom
				if self.rotation_angle == 0.0:
					x0 = x
					y0 = y
				elif self.rotation_angle == 1.0:
					x0 = y
					y0 = self.page_width/self.zoom - x
				elif self.rotation_angle == 2.0:
					x0 = self.page_width/self.zoom - x
					y0 = self.page_height/self.zoom - y
				elif self.rotation_angle == 3.0:
					x0 = self.page_height/self.zoom - y
					y0 = x
				for drawing in self.drawings:
					if type(drawing) == DrawingLine or\
					type(drawing) == DrawingRectangle or\
					type(drawing) == DrawingCircle or\
					type(drawing) == DrawingEllipse or\
					type(drawing) == DrawingImage:
						if drawing.bbox.isin(x0,y0):
							if not drawing.inside:
								drawing.inside = True
								somethingchanged = True
						else:
							if drawing.inside:
								drawing.inside = False
								somethingchanged = True
					elif type(drawing) == DrawingText and self.cairo_context:
						if drawing.bbox.isin(x0,y0,self.cairo_context):
							if not drawing.inside:
								drawing.inside = True
								somethingchanged = True
						else:
							if drawing.inside:
								drawing.inside = False
								somethingchanged = True
				if somethingchanged:
					self.is_rendered = False
					self.queue_draw()

	def on_button_press(self, widget, event, data):
		if event.button != 1:
			return
		self.mouse_down = True
		self.moving_drawing = None
		self.selection_start = self.snap_grid(event.x, event.y)
		if self.selection_end:
			self.selection_end = None
		if self.tool == 'arrow':
			x = (event.x - self.margin_width)/self.zoom
			y = (event.y - self.margin_height)/self.zoom
			if self.rotation_angle == 0.0:
				x0 = x
				y0 = y
			elif self.rotation_angle == 1.0:
				x0 = y
				y0 = self.page_width/self.zoom - x
			elif self.rotation_angle == 2.0:
				x0 = self.page_width/self.zoom - x
				y0 = self.page_height/self.zoom - y
			elif self.rotation_angle == 3.0:
				x0 = self.page_height/self.zoom - y
				y0 = x			
			for drawing in self.drawings:
				if type(drawing) == DrawingLine or\
				type(drawing) == DrawingRectangle or\
				type(drawing) == DrawingCircle or\
				type(drawing) == DrawingEllipse or\
				type(drawing) == DrawingImage:
					if drawing.bbox.isin(x0,y0):
						self.moving_drawing = (x0,y0,drawing)						
						return
				elif type(drawing) == DrawingText and self.cairo_context:
					if drawing.bbox.isin(x0,y0,self.cairo_context):					
						self.moving_drawing = (x0,y0,drawing)
						return
			
	def write(self):
		if self.selection_start and self.tool == 'text':
			x0o = self.selection_start[0] -self.margin_width/self.zoom
			y0o = self.selection_start[1] -self.margin_height/self.zoom
			self.selection_end = None
			self.selection_start = None
			if self.rotation_angle == 0.0:
				x0 = x0o
				y0 = y0o
			if self.rotation_angle == 1.0:
				x0 = y0o
				y0 = self.page_width/self.zoom - x0o
			if self.rotation_angle == 2.0:
				x0 = self.page_width/self.zoom - x0o
				y0 = self.page_height/self.zoom - y0o
			if self.rotation_angle == 3.0:
				x0 = self.page_height/self.zoom - y0o
				y0 = x0o
			bordercolor = self.parent.buttons['bordercolor'].colorbutton.get_color()
			fillcolor = self.parent.buttons['fillcolor'].colorbutton.get_color()			
			font,size = self.parent.buttons['font'].fontbutton.get_font_and_size()
			self.drawings.append(DrawingText(x0,y0,rotation_angle = -self.rotation_angle, font = font, size = size, color = bordercolor, text = self.text))
			self.text = ''
			self.is_rendered = False
			self.queue_draw()
			
	def on_button_release(self, widget, event, data):
		if event.button != 1:
			return
		self.mouse_down = None
		if self.moving_drawing:
			self.moving_drawing = None
			self.selection_end = None
			self.selection_start = None
		self.selection_end = self.snap_grid(event.x, event.y)
		if self.selection_end == self.selection_start and self.tool != 'text':
			self.selection_end = None
			self.selection_start = None
			if self.tool in ['arrow','remove']:
				somethingchanged = False
				x = (event.x - self.margin_width)/self.zoom
				y = (event.y - self.margin_height)/self.zoom
				if self.rotation_angle == 0.0:
					x0 = x
					y0 = y
				elif self.rotation_angle == 1.0:
					x0 = y
					y0 = self.page_width/self.zoom - x
				elif self.rotation_angle == 2.0:
					x0 = self.page_width/self.zoom - x
					y0 = self.page_height/self.zoom - y
				elif self.rotation_angle == 3.0:
					x0 = self.page_height/self.zoom - y
					y0 = x
				for drawing in self.drawings:
					if type(drawing) == DrawingLine or\
					type(drawing) == DrawingRectangle or\
					type(drawing) == DrawingCircle or\
					type(drawing) == DrawingEllipse or\
					type(drawing) == DrawingImage:
						if drawing.bbox.isin(x0,y0):
							if self.tool == 'arrow':
								drawing.selected = not drawing.selected
							elif self.tool == 'remove':
								self.drawings.remove(drawing)
							self.is_rendered = False
							self.queue_draw()									
					elif type(drawing) == DrawingText and self.cairo_context:
						if drawing.bbox.isin(x0,y0,self.cairo_context):					
							if self.tool == 'arrow':
								drawing.selected = not drawing.selected
							elif self.tool == 'remove':
								self.drawings.remove(drawing)
							self.is_rendered = False
							self.queue_draw()									

		else:
			if self.selection_start and self.selection_end:
				self.is_rendered = False
				width, height = self.width,self.height
				x0o = self.selection_start[0] -self.margin_width/self.zoom
				y0o = self.selection_start[1] -self.margin_height/self.zoom
				x1o = self.selection_end[0] -self.margin_width/self.zoom
				y1o = self.selection_end[1] -self.margin_height/self.zoom
				if self.tool not in ['text','arrow']:
					self.selection_end = None
					self.selection_start = None
				if self.rotation_angle == 0.0:
					x0 = x0o
					y0 = y0o
					x1 = x1o
					y1 = y1o
				if self.rotation_angle == 1.0:
					x0 = y0o
					y0 = self.page_width/self.zoom - x0o
					x1 = y1o
					y1 = self.page_width/self.zoom - x1o
				if self.rotation_angle == 2.0:
					x0 = self.page_width/self.zoom - x0o
					y0 = self.page_height/self.zoom - y0o
					x1 = self.page_width/self.zoom - x1o
					y1 = self.page_height/self.zoom - y1o
				if self.rotation_angle == 3.0:
					x0 = self.page_height/self.zoom - y0o
					y0 = x0o
					x1 = self.page_height/self.zoom - y1o
					y1 = x1o
				bordercolor = self.parent.buttons['bordercolor'].colorbutton.get_color()
				fillcolor = self.parent.buttons['fillcolor'].colorbutton.get_color()
				borderwidth = self.parent.buttons['size'].get_value()
				if self.tool == 'line':
					self.drawings.append(DrawingLine(x0,y0,x1,y1,bordercolor,width=borderwidth))
				elif self.tool == 'rectangle':
					self.drawings.append(DrawingRectangle(x0,y0,x1,y1,bordercolor=bordercolor,fillcolor=fillcolor,width=borderwidth))
				elif self.tool == 'circle':
					self.drawings.append(DrawingCircle(x0,y0,x1,y1,bordercolor=bordercolor,fillcolor=fillcolor,width=borderwidth))
				elif self.tool == 'ellipse':
					self.drawings.append(DrawingEllipse(x0,y0,x1,y1,bordercolor=bordercolor,fillcolor=fillcolor,width=borderwidth))
				elif self.tool == 'highlight':
					self.drawings.append(DrawingLine(x0,y0,x1,y1,HIGHLIGHT,width=30))
				elif self.tool == 'image':
					dialog = Gtk.FileChooserDialog(_('Select one image'),
													None,
												   Gtk.FileChooserAction.OPEN,
												   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
													Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
					dialog.set_default_response(Gtk.ResponseType.OK)
					#dialog.set_current_folder(self.image_dir)
					filter = Gtk.FileFilter()
					filter.set_name(_('Images'))				
					filter.add_mime_type('image/png')
					filter.add_mime_type('image/jpeg')
					filter.add_mime_type('image/gif')
					filter.add_mime_type('image/x-ms-bmp')
					filter.add_mime_type('image/x-icon')
					filter.add_mime_type('image/tiff')
					filter.add_mime_type('image/x-photoshop')
					filter.add_mime_type('x-portable-pixmap')
					filter.add_pattern('*.png')
					filter.add_pattern('*.jpg')
					filter.add_pattern('*.gif')
					filter.add_pattern('*.bmp')
					filter.add_pattern('*.ico')
					filter.add_pattern('*.tiff')
					filter.add_pattern('*.psd')
					filter.add_pattern('*.ppm')					
					dialog.add_filter(filter)
					preview = Gtk.Image()
					dialog.set_preview_widget(preview)
					dialog.connect('update-preview', self.update_preview_cb, preview)
					response = dialog.run()
					if response == Gtk.ResponseType.OK:
						filename = dialog.get_filename()
						if os.path.exists(filename):
							if filename.lower().endswith('.png'):
								surface = cairo.ImageSurface.create_from_png(filename)
							else:
								surface = load_image_to_pixbuf(filename)
							self.drawings.append(DrawingImage(x0,y0,x1,y1,surface,rotation_angle = -self.rotation_angle))
							self.is_rendered = False
							self.queue_draw()
					dialog.destroy()
		self.queue_draw()
	def update_preview_cb(self,file_chooser, preview):
		filename = file_chooser.get_preview_filename()
		try:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 128, 128)
			preview.set_from_pixbuf(pixbuf)
			have_preview = True
		except:
			have_preview = False
		file_chooser.set_preview_widget_active(have_preview)
		return
		
	def set_tool(self,tool):
		self.tool = tool
		
	def on_expose(self, widget, cr, data):
		if not self.cairo_context:
			self.cairo_context = cr
		if self.page_surface:
		#if self.page:
			if self.rotation_angle == 0.0 or self.rotation_angle == 2.0:
				self.page_width = self.width * self.zoom
				self.page_height = self.height * self.zoom
			else:
				self.page_height = self.width * self.zoom
				self.page_width = self.height * self.zoom
			self.total_width = self.page_width + 2.0*self.margin
			self.total_height = self.page_height + 2.0*self.margin
			self.set_size_request(self.page_width+2.0*self.margin,self.page_height+2.0*self.margin)
			self.margin_width = (self.get_allocation().width - self.page_width)/2.0 - self.margin
			if self.margin_width < 0.0:
				self.margin_width = self.margin
			self.margin_height = (self.get_allocation().height - self.page_height)/2.0 - self.margin
			if self.margin_height < 0.0:
				self.margin_height = self.margin
			if not self.is_rendered:
				self.view_surface = cairo.ImageSurface(cairo.FORMAT_RGB24,int(self.page_width),int(self.page_height))
				context = cairo.Context(self.view_surface)
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
				#self.page.render(context)
				context.set_source_surface(self.page_surface)
				context.paint()				
				for drawing in self.drawings:
					drawing.draw(context)
				self.is_rendered = True
			#
			cr.save()
			cr.translate(self.margin_width,self.margin_height)
			cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)
			cr.rectangle(-self.border,-self.border,self.page_width+2.0*self.border,self.page_height +2.0*self.border)
			cr.fill()
			cr.set_source_surface(self.view_surface,0,0)
			cr.paint()
			cr.rectangle(0,0,self.page_width,self.page_height)
			cr.clip()
			cr.restore()
			### Draw ###
			if self.selection_start and self.tool == 'text':
				x = self.selection_start[0]*self.zoom
				y = self.selection_start[1]*self.zoom				
				font,size = self.parent.buttons['font'].fontbutton.get_font_and_size()
				cr.select_font_face(font)
				cr.set_font_size(size*self.zoom*comun.RESOLUTION)
				cr.move_to(x,y)
				cr.set_source_rgba(0.3, 0.3, 1.0, 0.6)
				cr.show_text(self.text)							
			elif self.selection_start and self.selection_end:
				width = (self.selection_end[0] - self.selection_start[0])*self.zoom
				height = (self.selection_end[1] - self.selection_start[1])*self.zoom
				x = self.selection_start[0]*self.zoom
				y = self.selection_start[1]*self.zoom
				cr.set_line_width(2.0)
				if self.tool == 'arrow' and not self.moving_drawing:
					cr.rectangle(x,y, width, height)
					path = cr.copy_path()
					cr.set_source_rgba(0.4, 0.4, 0.9, 0.4)
					cr.fill()
					cr.append_path(path)
					cr.set_source_rgba(0.3, 0.3, 1.0, 0.6)
					cr.stroke()
				elif self.tool == 'line':
					cr.set_source_rgba(0.3, 0.3, 1.0, 0.6)
					cr.move_to(x,y)
					cr.line_to(x+width,y+height)
					cr.stroke()
				elif self.tool == 'highlight':
					cr.set_source_rgba(0.3, 0.3, 1.0, 0.6)
					cr.move_to(x,y)
					cr.line_to(x+width,y+height)
					cr.stroke()
				elif self.tool == 'rectangle':
					cr.rectangle(x,y, width, height)
					path = cr.copy_path()
					cr.set_source_rgba(0.4, 0.4, 0.9, 0.4)
					cr.fill()
					cr.append_path(path)
					cr.set_source_rgba(0.3, 0.3, 1.0, 0.6)
					cr.stroke()
				elif self.tool == 'circle':
					radius = math.sqrt(math.pow(width,2.0)+math.pow(height,2.0))
					cr.arc(x, y, radius, 0.0, 2.0*math.pi)
					path = cr.copy_path()
					cr.set_source_rgba(0.4, 0.4, 0.9, 0.4)
					cr.fill()
					cr.append_path(path)
					cr.set_source_rgba(0.3, 0.3, 1.0, 0.6)
					cr.stroke()
				elif self.tool == 'ellipse':
					if width<height:
						minimo = width
					else:
						minimo = height
					try:
						if abs(width)>0.0 and abs(height) > 0.0:
							cr.save()
							cr.translate(x + width / 2., y + height / 2.)
							cr.scale(1. * (width / 2.), 1. * (height / 2.))
							cr.arc(0., 0., 1., 0., 2 * math.pi)
							path = cr.copy_path()
							cr.set_source_rgba(0.4, 0.4, 0.9, 0.4)
							cr.fill()
							cr.append_path(path)
							cr.set_source_rgba(0.3, 0.3, 1.0, 0.6)
							cr.set_line_width(2.0/minimo)
							cr.stroke()
							cr.restore()
					except Exception:
						pass
					
				elif self.tool == 'image':
					cr.rectangle(x,y, width, height)
					path = cr.copy_path()
					cr.set_source_rgba(0.4, 0.4, 0.9, 0.4)
					cr.fill()
					cr.append_path(path)
					cr.set_source_rgba(0.3, 0.3, 1.0, 0.6)
					cr.stroke()
	
	def set_page(self, page_surface, number_of_page,rotation_angle,width,height):
		self.drawings = []
		if page_surface:
			self.selection_end = None
			self.selection_start = None
			self.mouse_down = None
			self.is_rendered = False
			self.number_of_page = number_of_page
			self.width, self.height = width,height
			self.rotation_angle = rotation_angle
			self.page_surface = page_surface
			self.is_rendered = False
			self.queue_draw()	
		else:
			self.selection_end = None
			self.selection_start = None
			self.mouse_down = None
			self.is_rendered = False
			self.page = None
			self.number_of_page = -1
			self.width = -1
			self.height = -1
			self.rotation_angle = 0.0
			self.page_surface = None
			self.is_rendered = False
			self.queue_draw()
	
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
	
	def paste_from_pixbuf(self):
		if self.cairo_context and self.tool == 'arrow' and self.selection_start and self.selection_end:
			clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
			pixbuf = clipboard.wait_for_image()
			if pixbuf != None:
				x0o = self.selection_start[0] -self.margin_width/self.zoom
				y0o = self.selection_start[1] -self.margin_height/self.zoom
				x1o = self.selection_end[0] -self.margin_width/self.zoom
				y1o = self.selection_end[1] -self.margin_height/self.zoom
				if self.tool not in ['text','arrow']:
					self.selection_end = None
					self.selection_start = None
				if self.rotation_angle == 0.0:
					x0 = x0o
					y0 = y0o
					x1 = x1o
					y1 = y1o
				if self.rotation_angle == 1.0:
					x0 = y0o
					y0 = self.page_width/self.zoom - x0o
					x1 = y1o
					y1 = self.page_width/self.zoom - x1o
				if self.rotation_angle == 2.0:
					x0 = self.page_width/self.zoom - x0o
					y0 = self.page_height/self.zoom - y0o
					x1 = self.page_width/self.zoom - x1o
					y1 = self.page_height/self.zoom - y1o
				if self.rotation_angle == 3.0:
					x0 = self.page_height/self.zoom - y0o
					y0 = x0o
					x1 = self.page_height/self.zoom - y1o
					y1 = x1o
				surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbuf.get_width(),pixbuf.get_height())
				context = cairo.Context(surface)
				Gdk.cairo_set_source_pixbuf(context, pixbuf,0,0)
				context.paint()
				self.drawings.append(DrawingImage(x0,y0,x1,y1,surface,rotation_angle = -self.rotation_angle))
				self.is_rendered = False
				self.queue_draw()

	def copy_to_pixbuf(self):
		if self.cairo_context and self.view_surface and self.selection_start and self.selection_end:
			x0 = self.selection_start[0]*self.zoom -self.margin_width
			y0 = self.selection_start[1]*self.zoom -self.margin_height
			x1 = self.selection_end[0]*self.zoom -self.margin_width
			y1 = self.selection_end[1]*self.zoom -self.margin_height
			width = abs(x1-x0)
			height = abs(y1-y0)
			imagedest = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
			contextdest = cairo.Context(imagedest)
			contextdest.set_source_surface(self.view_surface, -x0, -y0)
			contextdest.paint()
			filename = tempfile.mkstemp(suffix = '',prefix='updf_tmp', dir='/tmp')[1]
			#
			imagedest.write_to_png(filename)
			pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
			clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
			clipboard.set_image(pixbuf)			
			#
			if os.path.exists(filename):
				os.remove(filename)		
