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

import comun
import math
import cairo
from gi.repository import GObject

GAP =5

class DrawingColor(GObject.GObject):
	def __init__(self,r=0,g=0,b=0,a=1):
		self.r = r
		self.g = g
		self.b = b
		self.a = a
		
	def __str__(self):
		return 'red = %s, green = %s, blue = %s, alpha = %s'%(self.r,self.g,self.b,self.a)

UBUNTU = DrawingColor(r=0.242,g=0.242,b=0.242,a=1)
BLACK = DrawingColor(r=0,g=0,b=0,a=1)
WHITE = DrawingColor(r=1,g=1,b=1,a=1)
RED = DrawingColor(r=1,g=0,b=0,a=1)
BLUE = DrawingColor(r=0,g=0,b=1,a=1)
GREEN = DrawingColor(r=0,g=1,b=0,a=1)
YELLOW = DrawingColor(r=1,g=1,b=0,a=1)
GREY = DrawingColor(r=0.5,g=0.5,b=0.5,a=1)
GREY2 = DrawingColor(r=0.3,g=0.3,b=0.3,a=0.5)
UNACTIVE = DrawingColor(r=0.4,g=0.4,b=0.4,a=1)
MINE = DrawingColor(r=1,g=0.4,b=0,a=1)
HIGHLIGHT = DrawingColor(r=1,g=1,b=0,a=0.5)
SELECTION = DrawingColor(r=0.4, g=0.4, b=0.9, a=0.4)
def fromGdk2Color(color,alpha):
	r = float(color.red/65535.0)
	g = float(color.green/65535.0)
	b = float(color.blue/65535.0)
	a = float(alpha/65535.0)
	return DrawingColor(r,g,b,a)

def fromCB2Color(colorbutton):
	r = float(colorbutton.get_color().red/65535.0)
	g = float(colorbutton.get_color().green/65535.0)
	b = float(colorbutton.get_color().blue/65535.0)
	a = float(colorbutton.get_alpha()/65535.0)
	return DrawingColor(r,g,b,a)

def rotate(rotation_angle,x0,y0,x1,y1):	
	x11 = x1 - x0
	y11 = y1 - y0
	radius = math.sqrt(math.pow(x11,2.0)+math.pow(y11,2.0))
	if x11 == 0.0:		
		if y11 > 0.0:
			old_angle = math.pi/2.0
		else:
			old_angle = - math.pi/2.0
	else:
		old_angle = math.atan(y11/x11)
		
	new_angle = old_angle + rotation_angle
	x1r = radius * math.cos(new_angle)
	y1r = radius * math.sin(new_angle)
	x = x0 + x1r
	y = y0 + y1r
	return x,y

class BoundingBox(GObject.GObject):
	def __init__(self,x0o,y0o,x1o,y1o):
		GObject.GObject.__init__(self)
		if x0o<x1o:
			self.x0 = x0o - GAP
			self.x1 = x1o + GAP
		else:
			self.x0 = x1o - GAP
			self.x1 = x0o + GAP
		if y0o<y1o:
			self.y0 = y0o - GAP
			self.y1 = y1o + GAP
		else:
			self.y0 = y1o - GAP
			self.y1 = y0o + GAP

	def move(self,x,y):
		self.x0 += x
		self.y0 += y
		self.x1 += x
		self.y1 += y
		
	def isin(self,x,y):
		if self.x0 <= x and x <= self.x1 and self.y0 <= y and y <= self.y1:
			return True
		return False
		
class TextBoundingBox(GObject.GObject):
	def __init__(self,x0,y0,text,rotation_angle,font,size):
		GObject.GObject.__init__(self)
		self.x0 = x0
		self.y0 = y0
		self.text = text
		self.font = font
		self.size = size
		self.rotation_angle = rotation_angle

	def move(self,x,y):
		self.x0 += x
		self.y0 += y
		
	def calc_bounds(self,context):
		context.save()
		context.select_font_face(self.font)
		context.set_font_size(self.size)
		x,y,width,height,xa,ya = context.text_extents(self.text)
		context.restore()
		
		x0o = self.x0 + x*comun.RESOLUTION
		y0o = self.y0 + y*comun.RESOLUTION
		x1o = x0o + width*comun.RESOLUTION
		y1o = y0o + height*comun.RESOLUTION
		x0o,y0o = rotate(self.rotation_angle*math.pi/2.0,self.x0,self.y0,x0o,y0o)
		x1o,y1o = rotate(self.rotation_angle*math.pi/2.0,self.x0,self.y0,x1o,y1o)
		if x0o<x1o:
			x0 = x0o - GAP
			x1 = x1o + GAP
		else:
			x0 = x1o - GAP
			x1 = x0o + GAP
		if y0o<y1o:
			y0 = y0o - GAP
			y1 = y1o + GAP
		else:
			y0 = y1o - GAP
			y1 = y0o + GAP
		return x0,y0,x1,y1
		
	def isin(self,x,y,context):
		x0,y0,x1,y1 = self.calc_bounds(context)
		if x0 <= x and x <= x1 and y0 <= y and y <= y1:
			return True
		return False
		
class Drawing(GObject.GObject):
	def __init__(self):
		GObject.GObject.__init__(self)
		self.selected = False
		self.inside = False

	def draw(self, cr):
		pass
		
class DrawingLine(Drawing):
	def __init__(self,x0,y0,x1,y1,color = BLACK,width=1):
		Drawing.__init__(self)
		self.x0 = x0
		self.y0 = y0
		self.x1 = x1
		self.y1 = y1
		self.color = color
		self.width = width
		self.bbox = BoundingBox(x0,y0,x1,y1)

	def move(self,x,y):
		self.x0 += x
		self.y0 += y
		self.x1 += x
		self.y1 += y
		self.bbox.move(x,y)

	def draw(self, cr):
		width = self.width
		x0 = self.x0
		y0 = self.y0
		x1 = self.x1
		y1 = self.y1
		cr.set_line_width(width)
		cr.set_source_rgba(self.color.r,self.color.g,self.color.b,self.color.a)
		cr.move_to(x0,y0)
		cr.line_to(x1,y1)
		cr.stroke()
		if self.selected:
			cr.rectangle(self.bbox.x0, self.bbox.y0, self.bbox.x1-self.bbox.x0, self.bbox.y1-self.bbox.y0)
			cr.set_source_rgba(HIGHLIGHT.r,HIGHLIGHT.g,HIGHLIGHT.b,HIGHLIGHT.a)
			cr.fill()
		elif self.inside:
			cr.rectangle(self.bbox.x0, self.bbox.y0, self.bbox.x1-self.bbox.x0, self.bbox.y1-self.bbox.y0)
			cr.set_source_rgba(SELECTION.r,SELECTION.g,SELECTION.b,SELECTION.a)
			cr.fill()
			
	
class DrawingRectangle(Drawing):
	def __init__(self,x0,y0,x1,y1,bordercolor = BLACK,fillcolor = None,width=1):
		Drawing.__init__(self)
		self.x0 = x0
		self.y0 = y0
		self.x1 = x1
		self.y1 = y1
		self.bordercolor = bordercolor
		self.fillcolor = fillcolor
		self.width = width
		self.bbox = BoundingBox(x0,y0,x1,y1)

	def move(self,x,y):
		self.x0 += x
		self.y0 += y
		self.x1 += x
		self.y1 += y
		self.bbox.move(x,y)

	def draw(self, cr):
		width = self.width
		x0 = self.x0
		y0 = self.y0
		x1 = self.x1
		y1 = self.y1
		cr.set_line_width(width)
		cr.rectangle(x0, y0, x1-x0, y1-y0)
		cr.set_source_rgba(self.bordercolor.r,self.bordercolor.g,self.bordercolor.b,self.bordercolor.a)
		cr.stroke()
		if self.fillcolor:
			cr.rectangle(x0, y0, self.x1-self.x0, self.y1-self.y0)
			cr.set_source_rgba(self.fillcolor.r,self.fillcolor.g,self.fillcolor.b,self.fillcolor.a)
			cr.fill()
		if self.selected:
			cr.rectangle(self.bbox.x0, self.bbox.y0, self.bbox.x1-self.bbox.x0, self.bbox.y1-self.bbox.y0)
			cr.set_source_rgba(HIGHLIGHT.r,HIGHLIGHT.g,HIGHLIGHT.b,HIGHLIGHT.a)
			cr.fill()
		elif self.inside:
			cr.rectangle(self.bbox.x0, self.bbox.y0, self.bbox.x1-self.bbox.x0, self.bbox.y1-self.bbox.y0)
			cr.set_source_rgba(SELECTION.r,SELECTION.g,SELECTION.b,SELECTION.a)
			cr.fill()
			
class DrawingCircle(Drawing):
	def __init__(self,x0,y0,x1,y1,bordercolor = BLACK,fillcolor = None,width=1):
		Drawing.__init__(self)
		self.x0 = x0
		self.y0 = y0
		self.x1 = x1
		self.y1 = y1
		self.bordercolor = bordercolor
		self.fillcolor = fillcolor
		self.width = width
		radius = math.sqrt(math.pow(x0-x1,2.0)+math.pow(y0-y1,2.0))
		self.bbox = BoundingBox(x0-radius,y0-radius,x0+radius,y0+radius)

	def move(self,x,y):
		self.x0 += x
		self.y0 += y
		self.x1 += x
		self.y1 += y
		self.bbox.move(x,y)

	def draw(self, cr):
		cr.save()		
		width = self.width
		x0 = self.x0
		y0 = self.y0
		x1 = self.x1
		y1 = self.y1
		radius = math.sqrt(math.pow(x0-x1,2.0)+math.pow(y0-y1,2.0))
		cr.move_to(x0+radius, y0)
		cr.set_line_width(width)
		cr.set_source_rgba(self.bordercolor.r,self.bordercolor.g,self.bordercolor.b,self.bordercolor.a)
		cr.arc(x0, y0, radius, 0.0, 2.0*math.pi)
		cr.stroke()
		if self.fillcolor:
			cr.set_source_rgba(self.fillcolor.r,self.fillcolor.g,self.fillcolor.b,self.fillcolor.a)
			cr.arc(x0, y0, radius, 0.0, 2.0*math.pi)
			cr.fill()
		if self.selected:
			cr.rectangle(self.bbox.x0, self.bbox.y0, self.bbox.x1-self.bbox.x0, self.bbox.y1-self.bbox.y0)
			cr.set_source_rgba(HIGHLIGHT.r,HIGHLIGHT.g,HIGHLIGHT.b,HIGHLIGHT.a)
			cr.fill()
		elif self.inside:
			cr.rectangle(self.bbox.x0, self.bbox.y0, self.bbox.x1-self.bbox.x0, self.bbox.y1-self.bbox.y0)
			cr.set_source_rgba(SELECTION.r,SELECTION.g,SELECTION.b,SELECTION.a)
			cr.fill()
		cr.restore()

class DrawingEllipse(Drawing):
	def __init__(self,x0,y0,x1,y1,bordercolor = BLACK,fillcolor = None,width=1):
		Drawing.__init__(self)
		self.x0 = x0
		self.y0 = y0
		self.x1 = x1
		self.y1 = y1
		self.bordercolor = bordercolor
		self.fillcolor = fillcolor
		self.width = width
		self.bbox = BoundingBox(x0,y0,x1,y1)

	def move(self,x,y):
		self.x0 += x
		self.y0 += y
		self.x1 += x
		self.y1 += y
		self.bbox.move(x,y)

	def draw(self, cr):
		width = self.x1-self.x0
		height = self.y1-self.y0
		if width<height:
			minimo = width
		else:
			minimo = height
		try:
			if abs(width)>0.0 and abs(height) > 0.0:			
				cr.save()
				cr.translate(self.x0 + width / 2., self.y0 + height / 2.);
				cr.scale(1. * (width / 2.), 1. * (height / 2.));
				cr.arc(0., 0., 1., 0., 2 * math.pi);
				if self.fillcolor:
					cr.set_source_rgba(self.fillcolor.r,self.fillcolor.g,self.fillcolor.b,self.fillcolor.a)
					cr.fill_preserve()
				cr.set_source_rgba(self.bordercolor.r,self.bordercolor.g,self.bordercolor.b,self.bordercolor.a)
				cr.set_line_width(self.width/minimo)
				cr.stroke()
				cr.restore()
				if self.selected:
					cr.rectangle(self.bbox.x0, self.bbox.y0, self.bbox.x1-self.bbox.x0, self.bbox.y1-self.bbox.y0)
					cr.set_source_rgba(HIGHLIGHT.r,HIGHLIGHT.g,HIGHLIGHT.b,HIGHLIGHT.a)
					cr.fill()
				elif self.inside:
					cr.rectangle(self.bbox.x0, self.bbox.y0, self.bbox.x1-self.bbox.x0, self.bbox.y1-self.bbox.y0)
					cr.set_source_rgba(SELECTION.r,SELECTION.g,SELECTION.b,SELECTION.a)
					cr.fill()
				
		except Exception:
			pass
						
class DrawingText(Drawing):
	def __init__(self,x0,y0,rotation_angle=0.0,font = 'Sans', size = 12, color = BLACK, text = ''):
		Drawing.__init__(self)
		self.x0 = x0
		self.y0 = y0
		self.font = font
		self.size = size*comun.RESOLUTION
		self.color = color
		self.text = text
		self.rotation_angle = rotation_angle
		self.bbox = TextBoundingBox(x0,y0,text,rotation_angle,font,size)

	def move(self,x,y):
		self.x0 += x
		self.y0 += y
		self.bbox.move(x,y)
		
	def draw(self, cr):
		cr.save()
		cr.set_source_rgba(self.color.r,self.color.g,self.color.b,self.color.a)
		cr.select_font_face(self.font)
		cr.set_font_size(self.size)
		cr.move_to(self.x0, self.y0)
		cr.rotate(self.rotation_angle*math.pi/2.0)
		cr.show_text(self.text)
		cr.restore()
		cr.save()
		x0,y0,x1,y1 = self.bbox.calc_bounds(cr)
		if self.selected:			
			cr.set_source_rgba(HIGHLIGHT.r,HIGHLIGHT.g,HIGHLIGHT.b,HIGHLIGHT.a)
			cr.rectangle(x0, y0, x1-x0, y1-y0)
			cr.fill()
		elif self.inside:
			cr.set_source_rgba(SELECTION.r,SELECTION.g,SELECTION.b,SELECTION.a)
			cr.rectangle(x0, y0, x1-x0, y1-y0)
			cr.fill()
		cr.restore()
		
		
class DrawingImage(Drawing):
	def __init__(self,x0,y0,x1,y1,surface,rotation_angle=0.0):
		Drawing.__init__(self)
		self.x0 = x0
		self.y0 = y0
		self.x1 = x1
		self.y1 = y1	
		self.surface = surface
		self.rotation_angle = rotation_angle
		self.bbox = BoundingBox(x0,y0,x1,y1)

	def move(self,x,y):
		self.x0 += x
		self.y0 += y
		self.x1 += x
		self.y1 += y
		self.bbox.move(x,y)

	def draw(self, cr):		
		zoomx = abs(self.x0 - self.x1)/self.surface.get_width()
		zoomy = abs(self.y0 - self.y1)/self.surface.get_height()
		if zoomx<zoomy:
			zoom = zoomx
		else:
			zoom = zoomy
		cr.save()
		cr.translate(self.x0, self.y0)
		mtr = cairo.Matrix()		
		mtr.scale(zoom,zoom)
		cr.transform(mtr)
		cr.rotate(self.rotation_angle*math.pi/2.0)
		cr.set_source_surface(self.surface)
		cr.paint()		
		cr.restore()
		if self.selected:
			cr.rectangle(self.bbox.x0, self.bbox.y0, self.bbox.x1-self.bbox.x0, self.bbox.y1-self.bbox.y0)
			cr.set_source_rgba(HIGHLIGHT.r,HIGHLIGHT.g,HIGHLIGHT.b,HIGHLIGHT.a)
			cr.fill()
		elif self.inside:
			cr.rectangle(self.bbox.x0, self.bbox.y0, self.bbox.x1-self.bbox.x0, self.bbox.y1-self.bbox.y0)
			cr.set_source_rgba(SELECTION.r,SELECTION.g,SELECTION.b,SELECTION.a)
			cr.fill()
		
		
if __name__ == '__main__':
	print(UBUNTU)
	print(rotate(math.pi,1.0,1.0,2.0,0.0))
