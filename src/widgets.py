#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# widgets.py
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
from gi.repository import Gtk, Gdk, GObject, GdkPixbuf
from gi.repository import Rsvg
import cairo
import drawing
import comun
from comun import _

def svg2Surface(filename,width=30,height=30):
	svg = Rsvg.Handle.new_from_file(filename)
	ims = cairo.SVGSurface(None, width, height)
	context = cairo.Context(ims)
	svg.render_cairo(context)
	return ims

class Separator(Gtk.DrawingArea):	
	def __init__(self,color=drawing.UBUNTU):
		Gtk.DrawingArea.__init__(self)
		self.backgroundcolor = color
		self.connect('draw', self.on_expose, None)

	def on_expose(self, widget, cr, data):
		cr.rectangle(0,0,40,40)
		cr.set_source_rgba(self.backgroundcolor.r,self.backgroundcolor.g,self.backgroundcolor.b,self.backgroundcolor.a)
		cr.fill()

class Separator(Gtk.DrawingArea):	
	def __init__(self,color=drawing.UBUNTU):
		Gtk.DrawingArea.__init__(self)
		self.backgroundcolor = color
		self.connect('draw', self.on_expose, None)

	def on_expose(self, widget, cr, data):
		cr.rectangle(0,0,40,40)
		cr.set_source_rgba(self.backgroundcolor.r,self.backgroundcolor.g,self.backgroundcolor.b,self.backgroundcolor.a)
		cr.fill()

class SeparatorToolButton(Gtk.ToolItem):
	def __init__(self):
		Gtk.ToolItem.__init__(self)
		s = Separator()
		s.set_size_request(20,40)
		self.add(s)

class ColorButton(Gtk.DrawingArea):
	def __init__(self,color=drawing.BLACK):
		Gtk.DrawingArea.__init__(self)
		self.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)
		self.connect('draw', self.on_expose, None)
		self.connect('enter-notify-event',self.mouse_in)
		self.connect('motion-notify-event',self.mouse_in)
		self.connect('leave-notify-event',self.mouse_out)
		self.connect('button-release-event',self.on_clicked)
		self.backgroundcolor = drawing.UBUNTU
		self.color = color
		self.sensitive = False		
		
	def on_clicked(self,widget,data):
		cdia = Gtk.ColorSelectionDialog(_('Select color'))
		colorsel = cdia.get_color_selection()
		colorsel.set_current_color(Gdk.Color(self.color.r*65535.0,self.color.g*65535.0,self.color.b*65535.0))
		colorsel.set_current_alpha(self.color.a*65535.0)
		colorsel.set_has_opacity_control(True)
		colorsel.set_has_palette(True)
		if cdia.run() == Gtk.ResponseType.OK:
			colorsel = cdia.get_color_selection()	
			color = colorsel.get_current_color()
			alpha = colorsel.get_current_alpha()			
			self.color = drawing.fromGdk2Color(color,alpha)
		cdia.destroy()		
		self.queue_draw()
		
	def mouse_in(self,widget,color):
		self.backgroundcolor = drawing.GREY
		self.queue_draw()

	def mouse_out(self,widget,color):
		self.backgroundcolor = drawing.UBUNTU
		self.queue_draw()
		
	def on_expose(self, widget, cr, data):
		cr.rectangle(0,0,40,40)
		cr.set_source_rgba(self.backgroundcolor.r,self.backgroundcolor.g,self.backgroundcolor.b,self.backgroundcolor.a)
		cr.fill()
		cr.rectangle(10,10, 20,20)
		if self.sensitive:
			cr.set_source_rgba(self.color.r,self.color.g,self.color.b,self.color.a)
		else:
			cr.set_source_rgba(drawing.GREY.r,drawing.GREY.g,drawing.GREY.b,drawing.GREY.a)
		cr.fill()		
		
	def set_sensistive(self,sensitive):
		self.sensitive = sensitive
		self.queue_draw()

	def get_color(self):
		return self.color

class ToolButtonColor(Gtk.ToolItem):
	def __init__(self):
		Gtk.ToolItem.__init__(self)
		self.colorbutton = ColorButton()
		self.colorbutton.set_can_focus(False)
		#self.colorbutton.set_use_alpha(True)
		self.colorbutton.set_size_request(40,40)
		self.add(self.colorbutton)

	def set_sensitive(self,sensitive):
		super(ToolButtonColor,self).set_sensitive(sensitive)
		self.colorbutton.set_sensistive(sensitive)
	def get_color(self):
		self.colorbutton.get_color()
		
class ImageButton(Gtk.DrawingArea):
	__gsignals__ = {
		'clicked' : (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,())
		}
	
	def __init__(self,filename=None,filename2=None,width=40.0,height=40.0,gap=5.0):
		Gtk.DrawingArea.__init__(self)
		self.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)
		self.connect('draw', self.on_expose, None)
		self.connect('enter-notify-event',self.mouse_in)
		self.connect('motion-notify-event',self.mouse_in)
		self.connect('leave-notify-event',self.mouse_out)
		self.connect('button-press-event',self.on_button_press)
		self.connect('button-release-event',self.on_button_release)		
		self.image_active = svg2Surface(filename,width-2.0*gap,height-2.0*gap)
		self.image_inactive = svg2Surface(filename2,width-2.0*gap,height-2.0*gap)
		self.sensitive = True
		self.selected = False
		self.mouse_inside = False
		self.height = height
		self.width = width
		self.gap = gap
		
	def on_button_press(self,widget,event):
		pass

	def on_button_release(self,widget,event):
		#self.set_selected(False)
		self.emit('clicked')
		
	def mouse_in(self,widget,color):
		self.mouse_inside = True
		self.queue_draw()

	def mouse_out(self,widget,color):
		self.mouse_inside = False
		self.queue_draw()
		
	def on_expose(self, widget, cr, data):
		cr.rectangle(0,0,self.width,self.height)
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
			cr.set_source_surface(self.image_active,self.gap,self.gap)
			cr.paint()
		else:
			cr.set_source_surface(self.image_inactive,self.gap,self.gap)
			cr.paint()

	def set_selected(self,selected):
		self.selected = selected
		self.queue_draw()
		
	def get_selected(self):
		return self.selected

	def set_sensitive(self,sensitive):
		self.sensitive = sensitive
		self.mouse_inside = False
		self.queue_draw()
	
class LabelButton(Gtk.DrawingArea):
	__gsignals__ = {
		'clicked' : (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,())
		}
	
	def __init__(self,text):
		Gtk.DrawingArea.__init__(self)
		self.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)
		self.connect('draw', self.on_expose, None)
		self.connect('enter-notify-event',self.mouse_in)
		self.connect('motion-notify-event',self.mouse_in)
		self.connect('leave-notify-event',self.mouse_out)
		self.connect('button-press-event',self.on_button_press)
		self.connect('button-release-event',self.on_button_release)
		self.text = text
		self.set_size_request(40,40)
		self.selected = False
		self.mouse_inside = False
		
	def on_button_press(self,widget,event):
		pass

	def on_button_release(self,widget,event):
		#self.set_selected(False)
		self.emit('clicked')
		
	def mouse_in(self,widget,color):
		self.mouse_inside = True
		self.queue_draw()

	def mouse_out(self,widget,color):
		self.mouse_inside = False
		self.queue_draw()
		
	def on_expose(self, widget, cr, data):		
		cr.select_font_face('Ubuntu')
		cr.set_font_size(14)
		x,y,width,height,xe,ye = cr.text_extents(self.text)
		cr.rectangle(0,0,width+10,40)
		self.set_size_request(width+10,40)
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
			cr.set_source_rgba(drawing.WHITE.r,drawing.WHITE.g,drawing.WHITE.b,drawing.WHITE.a)
		else:
			cr.set_source_rgba(drawing.UNACTIVE.r,drawing.UNACTIVE.g,drawing.UNACTIVE.b,drawing.UNACTIVE.a)
		rect = self.get_allocation()
		cr.move_to((rect.width-width)/2,(rect.height-height)/2-y)
		cr.show_text(self.text)

	def set_selected(self,selected):
		self.selected = selected
		self.queue_draw()
		
	def get_selected(self):
		return self.selected

	def set_sensitive(self,sensitive):
		self.sensitive = sensitive
		self.mouse_inside = False
		self.queue_draw()
		
class FontButton(Gtk.DrawingArea):
	__gsignals__ = {
		'clicked' : (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,())
		}
	
	def __init__(self,font,size):
		Gtk.DrawingArea.__init__(self)
		self.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)
		self.connect('draw', self.on_expose, None)
		self.connect('enter-notify-event',self.mouse_in)
		self.connect('motion-notify-event',self.mouse_in)
		self.connect('leave-notify-event',self.mouse_out)
		self.connect('button-press-event',self.on_button_press)
		self.connect('button-release-event',self.on_button_release)
		self.font = font
		self.size = size
		self.set_size_request(40,40)
		self.selected = False
		self.mouse_inside = False
		
	def on_button_press(self,widget,event):
		pass

	def on_button_release(self,widget,event):
		fdia = Gtk.FontChooserDialog(_('Select font name'))
		fdia.set_preview_text(_('One day I saw a cow wearing a military uniform'))
		fdia.set_font('%s %s'%(self.font,self.size))
		if fdia.run() == Gtk.ResponseType.OK:
			fontname = fdia.get_font()
			fdia.destroy()
			if fontname:
				values = fontname.split(' ')
				font = ' '.join(values[:-1])
				size = int(values[-1])
				self.set_font_and_size(font,size)
		fdia.destroy()
		self.emit('clicked')
		
	def mouse_in(self,widget,color):
		self.mouse_inside = True
		self.queue_draw()

	def mouse_out(self,widget,color):
		self.mouse_inside = False
		self.queue_draw()
		
	def on_expose(self, widget, cr, data):		
		cr.select_font_face(self.font)
		cr.set_font_size(14)
		text = '%s %s'%(self.font,self.size)
		x,y,width,height,xe,ye = cr.text_extents(text)
		cr.rectangle(0,0,width+10,40)
		self.set_size_request(width+10,40)
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
			cr.set_source_rgba(drawing.WHITE.r,drawing.WHITE.g,drawing.WHITE.b,drawing.WHITE.a)
		else:
			cr.set_source_rgba(drawing.UNACTIVE.r,drawing.UNACTIVE.g,drawing.UNACTIVE.b,drawing.UNACTIVE.a)
		rect = self.get_allocation()
		cr.move_to((rect.width-width)/2,(rect.height-height)/2-y)
		cr.show_text(text)

	def set_selected(self,selected):
		self.selected = selected
		self.queue_draw()
		
	def get_selected(self):
		return self.selected

	def set_font(self,font):
		self.font = font
		self.queue_draw()
		
	def get_font(self):
		return self.font
	def get_font_and_size(self):
		return self.font,self.size
		
	def set_size(self,size):
		self.size = size
		self.queue_draw()
	
	def get_size(self):
		return self.size
		
	def set_font_and_size(self,font,size):
		self.font = font
		self.size = size
		self.queue_draw()
	
	def set_sensitive(self,sensitive):
		self.sensitive = sensitive
		self.mouse_inside = False
		self.queue_draw()
				
class ImageToolButton(Gtk.ToolItem):
	__gsignals__ = {
		'clicked' : (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,())
		}
	
	def __init__(self,filename=None,filename2=None):
		Gtk.ToolItem.__init__(self)
		self.imagebutton = ImageButton(filename,filename2)
		self.imagebutton.set_can_focus(False)
		self.imagebutton.set_size_request(40,40)
		self.imagebutton.connect('clicked',self.on_clicked)
		self.add(self.imagebutton)

	def on_clicked(self,widget):
		self.emit('clicked')

	def set_sensitive(self,sensitive):
		self.imagebutton.set_sensitive(sensitive)
		super(ImageToolButton,self).set_sensitive(sensitive)		
			
class ImageToggleToolButton(Gtk.ToolItem):
	__gsignals__ = {
		'clicked' : (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,())
		}
	
	def __init__(self,filename=None,filename2=None):
		Gtk.ToolItem.__init__(self)
		self.imagebutton = ImageButton(filename,filename2)
		self.imagebutton.set_can_focus(False)
		self.imagebutton.set_size_request(40,40)
		self.imagebutton.connect('clicked',self.on_clicked)
		self.add(self.imagebutton)

	def on_clicked(self,widget):
		self.imagebutton.set_selected(not self.imagebutton.get_selected())
		self.emit('clicked')

	def set_sensitive(self,sensitive):
		super(ImageToggleToolButton,self).set_sensitive(sensitive)
		self.imagebutton.set_sensitive(sensitive)

	def set_selected(self,selected):
		self.imagebutton.set_selected(selected)

	def get_active(self):
		return self.imagebutton.get_selected()
		
	def set_active(self,active):
		self.imagebutton.set_selected(active)		
	
class ToolLabel(Gtk.ToolItem):
	def __init__(self,text=None):
		Gtk.ToolItem.__init__(self)
		self.label = Gtk.Label()
		self.add(self.label)
		self.label.set_use_markup(True)		
		self.set_text(text)
		
	def set_text(self,text):
		if text:
			self.label.set_markup("<span foreground='white'>%s</span>" % (text))
		else:
			self.label.set_text('')
class TemporalButton(Gtk.ToolItem):
	def __init__(self,text=None):
		Gtk.ToolItem.__init__(self)
		self.button = Gtk.Button()
		self.button.set_relief(Gtk.ReliefStyle.NONE)
		self.button.set_label('Temporal')
		self.add(self.button)
		
class ToolEntry(Gtk.ToolItem):		
	def __init__(self,text=None):
		Gtk.ToolItem.__init__(self)
		self.entry = Gtk.Entry()
		self.add(self.entry)
	def set_text(self,text):
		self.entry.set_text(text)
	def get_text(self):
		return self.entry.get_text()

class ToolButtonFont(Gtk.ToolItem):
	def __init__(self,font=None):
		Gtk.ToolItem.__init__(self)
		self.fontbutton = FontButton('Ubuntu',11)
		self.add(self.fontbutton)

	def set_font(self,font):
		self.fontbutton.set_font(font)
		
	def set_sensitive(self,sensitive):
		super(ToolButtonFont,self).set_sensitive(sensitive)		
		self.fontbutton.set_sensitive(sensitive)

class ToolSpinButton(Gtk.ToolItem):
	def __init__(self,text=None):
		Gtk.ToolItem.__init__(self)
		self.spinbutton = Gtk.SpinButton()
		self.spinbutton.set_can_focus(False)
		self.spinbutton.set_size_request(40,40)
		self.add(self.spinbutton)
		adjustment = Gtk.Adjustment(value=1, lower=1, upper=100, step_incr=1, page_incr=5, page_size=2.0)
		self.spinbutton.set_adjustment(adjustment)
	def get_value(self):
		return self.spinbutton.get_value()

	def set_value(self,value):
		self.spinbutton.set_value(value)

class ToolSpinButton2(Gtk.ToolItem):
	def __init__(self,text=None):
		Gtk.ToolItem.__init__(self)
		self.spinbutton = Gtk.VolumeButton(4, 1, 100, 1, icons=None)
		self.spinbutton.set_can_focus(False)
		self.spinbutton.set_size_request(40,40)
		self.add(self.spinbutton)
	def get_value(self):
		return self.spinbutton.get_value()

	def set_value(self,value):
		self.spinbutton.set_value(value)

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

	def set_value(self,value):
		self.scalebutton.set_value(value)

	def get_value(self):
		return self.scalebutton.get_value()
		
class ScaleButton(Gtk.DrawingArea):
	global MIN
	global MAX
	MIN = 1
	MAX = 100
	def __init__(self):
		Gtk.DrawingArea.__init__(self)
		self.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.SCROLL_MASK)
		self.connect('draw', self.on_expose, None)
		self.connect('enter-notify-event',self.mouse_in)
		self.connect('motion-notify-event',self.mouse_in)
		self.connect('leave-notify-event',self.mouse_out)
		self.connect('button-release-event',self.on_button_release)
		self.connect('scroll-event', self.wheel)  
		self.set_size_request(40,40)
		self.selected = False
		self.mouse_inside = False
		self.set_value(5)
		
	def wheel(self,widget,event):
		if event.direction == Gdk.ScrollDirection.UP:
			value = self.value + 1
			if value > MAX:
				value = MAX
		elif event.direction == Gdk.ScrollDirection.DOWN:
			value = self.value - 1
			if value < MIN:
				value = MIN
		self.set_value(value)
		
	def on_button_press(self,widget,event):
		pass			

	def on_button_release(self,widget,event):
		if event.button == 1:
			value = self.value + 1
			if value > MAX:
				value = MAX
			self.set_value(value)
		elif event.button == 3:
			value = self.value - 1
			if value < MIN:
				value = MIN
			self.set_value(value)

				
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
		h = int(30*self.value/MAX)		
		cr.rectangle(5,(40-h)/2,30,h)
		cr.fill()		

	def set_selected(self,selected):
		self.selected = selected
		self.queue_draw()
		
	def get_selected(self):
		return self.selected

	def set_sensitive(self,sensitive):
		self.sensitive = sensitive
		self.mouse_inside = False
		self.queue_draw()
		
	def set_value(self,value):
		self.value = int(value)
		self.set_tooltip_text(_('Value')+' %s'%(self.value))
		self.queue_draw()
		
	def get_value(self):
		return int(self.value)		
