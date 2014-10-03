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

#gir1.2-poppler
from gi.repository import Poppler, Gtk, Gdk, GObject, GdkPixbuf
import cairo
import math
import os
from view import View
from miniview import MiniView
from pdfview import PdfView
from progreso import Progreso
from dialogs import 	RemovePagesDialog,\
						InsertPagesDialog,\
						SelectPagesToRotateDialog,\
						ExtractPagesDialog,\
						InsertBlankPagesDialog
import drawing
import widgets
import webbrowser
import comun
import splashscreen
from comun import _

HEIGHT = 280

def clone_list(alist):
	newlist = []
	for element in alist:
		newlist.append(element)
	return newlist	
		
def add2menu(menu, text = None, icon = None, conector_event = None, conector_action = None):
	if text != None:
		if icon == None:
			menu_item = Gtk.MenuItem.new_with_label(text)
		else:
			menu_item = Gtk.ImageMenuItem.new_with_label(text)
			image = Gtk.Image.new_from_stock(icon, Gtk.IconSize.MENU)
			menu_item.set_image(image)
			menu_item.set_always_show_image(True)
	else:
		if icon == None:
			menu_item = Gtk.SeparatorMenuItem()
		else:
			menu_item = Gtk.ImageMenuItem()
			image = Gtk.Image.new_from_stock(icon, Gtk.IconSize.MENU)
			menu_item.set_image(image)
			menu_item.set_always_show_image(True)
	if conector_event != None and conector_action != None:				
		menu_item.connect(conector_event,conector_action)
	menu_item.show()
	menu.append(menu_item)
	return menu_item

class UPDF(Gtk.Window):
	def __init__(self,afile=None):
		Gtk.Window.__init__(self)
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_title('uPdf')
		self.set_default_size(750, 600)
		self.set_icon_from_file(comun.ICON)
		self.connect('destroy', self.on_close_application)	
		self.connect('key-press-event',self.on_view_key_pressed)
		self.connect('check-resize',self.on_resize,None)
		self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)		
		'''
		win_style_context = self.get_style_context()
		print win_style_context
		print win_style_context.lookup_color('bg_color')
		bg = win_style_context.lookup_color('bg_color')[1].to_string()
		# Then we set that as the background for GtkToolbar
		# We also make the boarder transparent
		css_provider = Gtk.CssProvider()
		toolbar_css = "GtkToolbar,VBox { background-color: transparent}"
		css_provider.load_from_data(toolbar_css.encode('UTF-8'))
		screen = Gdk.Screen.get_default()
		win_style_context.add_provider_for_screen(screen, css_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)			
'''
		
		#background = Gtk.Frame()
		#background.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
		#self.add(background)
		#
		vbox = Gtk.VBox()
		self.add(vbox)
		#
		#
		self.menubar = Gtk.MenuBar.new()
		vbox.pack_start(self.menubar,False,False,0)	
		################################################################
		self.filemenu = Gtk.Menu.new()
		self.filem = Gtk.MenuItem.new_with_label(_('File'))
		self.filem.set_submenu(self.filemenu)
		#
		self.menus = {}
		#
		self.menus['open'] = Gtk.MenuItem.new_with_label(_('Open'))
		self.menus['open'].connect('activate',self.on_button1_clicked)
		self.filemenu.append(self.menus['open'])
		#
		self.menus['close'] = Gtk.MenuItem.new_with_label(_('Close'))
		self.menus['close'].connect('activate',self.on_toolbar_clicked,'close')
		self.filemenu.append(self.menus['close'])
		#
		self.filemenu.append(Gtk.SeparatorMenuItem())
		#
		self.menus['save_as'] = Gtk.MenuItem.new_with_label(_('Save as'))
		self.menus['save_as'].connect('activate',self.on_button0_clicked)
		self.filemenu.append(self.menus['save_as'])	
		#
		self.filemenu.append(Gtk.SeparatorMenuItem())			
		#
		self.menus['exit'] = Gtk.MenuItem.new_with_label(_('Exit'))
		self.menus['exit'].connect('activate',self.on_close_application)
		self.filemenu.append(self.menus['exit'])
		#
		self.menubar.append(self.filem)
		################################################################
		self.fileedit = Gtk.Menu.new()
		self.filee = Gtk.MenuItem.new_with_label(_('Edit'))
		self.filee.set_submenu(self.fileedit)
		#
		self.menus['copy'] = Gtk.MenuItem.new_with_label(_('Copy'))
		self.menus['copy'].connect('activate',self.on_toolbar_clicked,'copy')
		self.fileedit.append(self.menus['copy'])	
		#
		self.menus['paste'] = Gtk.MenuItem.new_with_label(_('Paste'))
		self.menus['paste'].connect('activate',self.on_toolbar_clicked,'paste')
		self.fileedit.append(self.menus['paste'])	
		#
		'''
		self.pref = Gtk.ImageMenuItem.new_with_label(_('Preferences'))
		self.pref.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_PREFERENCES, Gtk.IconSize.MENU))		
		#self.pref.connect('activate',self.on_preferences_activate)
		self.pref.set_always_show_image(True)
		self.fileedit.append(self.pref)
		'''
		
		#
		self.menubar.append(self.filee)
		################################################################
		filetool = Gtk.Menu.new()
		filet = Gtk.MenuItem.new_with_label(_('Tools'))
		filet.set_submenu(filetool)
		#
		self.menus['first'] = Gtk.MenuItem.new_with_label(_('Go to first'))
		self.menus['first'].connect('activate',self.on_toolbar_clicked,'goto_first')
		filetool.append(self.menus['first'])
		#
		self.menus['back'] = Gtk.MenuItem.new_with_label(_('Go to back'))
		self.menus['back'].connect('activate',self.on_toolbar_clicked,'goto_back')
		filetool.append(self.menus['back'])
		#
		self.menus['forward'] = Gtk.MenuItem.new_with_label(_('Go to forward'))
		self.menus['forward'].connect('activate',self.on_toolbar_clicked,'goto_fordward')
		filetool.append(self.menus['forward'])
		#
		self.menus['last'] = Gtk.MenuItem.new_with_label(_('Go to last'))
		self.menus['last'].connect('activate',self.on_toolbar_clicked,'goto_last')
		filetool.append(self.menus['last'])
		#
		filetool.append(Gtk.SeparatorMenuItem())
		#
		self.menus['zoom_in'] = Gtk.MenuItem.new_with_label(_('Zoom in'))
		self.menus['zoom_in'].connect('activate',self.on_toolbar_clicked,'zoom_in')
		filetool.append(self.menus['zoom_in'])
		#
		self.menus['zoom_out'] = Gtk.MenuItem.new_with_label(_('Zoom out'))
		self.menus['zoom_out'].connect('activate',self.on_toolbar_clicked,'zoom_out')
		filetool.append(self.menus['zoom_out'])
		#
		self.menus['zoom_reset'] = Gtk.MenuItem.new_with_label(_('Reset zoom'))
		self.menus['zoom_reset'].connect('activate',self.on_toolbar_clicked,'zoom_reset')
		filetool.append(self.menus['zoom_reset'])
		#
		self.menus['zoom_fit'] = Gtk.MenuItem.new_with_label(_('Fit zoom'))
		self.menus['zoom_fit'].connect('activate',self.on_toolbar_clicked,'zoom_fit')
		filetool.append(self.menus['zoom_fit'])
		#
		filetool.append(Gtk.SeparatorMenuItem())
		#
		self.menus['rotate_pages'] = Gtk.MenuItem.new_with_label(_('Rotate pages'))
		self.menus['rotate_pages'].connect('activate',self.on_toolbar_clicked,'rotate_pages')
		filetool.append(self.menus['rotate_pages'])		
		#
		filetool.append(Gtk.SeparatorMenuItem())
		#
		self.menus['insert_pages'] = Gtk.MenuItem.new_with_label(_('Insert pages'))
		self.menus['insert_pages'].connect('activate',self.on_toolbar_clicked,'insert_pages')
		filetool.append(self.menus['insert_pages'])
		#
		self.menus['insert_blank_pages'] = Gtk.MenuItem.new_with_label(_('Insert blank pages'))
		self.menus['insert_blank_pages'].connect('activate',self.on_toolbar_clicked,'insert_blank_pages')
		filetool.append(self.menus['insert_blank_pages'])
		#
		self.menus['remove_pages'] = Gtk.MenuItem.new_with_label(_('Remove pages'))
		self.menus['remove_pages'].connect('activate',self.on_toolbar_clicked,'remove_pages')
		filetool.append(self.menus['remove_pages'])
		#
		self.menus['extract_pages'] = Gtk.MenuItem.new_with_label(_('Extract pages'))
		self.menus['extract_pages'].connect('activate',self.on_toolbar_clicked,'extract_pages')
		filetool.append(self.menus['extract_pages'])
		#		
		self.menubar.append(filet)
		################################################################
		self.filehelp = Gtk.Menu.new()
		self.fileh = Gtk.MenuItem.new_with_label(_('Help'))
		self.fileh.set_submenu(self.get_help_menu())
		#
		self.menubar.append(self.fileh)
		################################################################			
		#
		toolbar = Gtk.Toolbar()
		toolbar.set_property("visible",False)
		toolbar.set_property("can_focus",False)
		toolbar.set_property("toolbar_style",'icons')
		toolbar.set_property("icon_size",4)
		#toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
		'''
		color = Gdk.RGBA(0.242,0.242,0.242,1)
		toolbar.override_background_color(Gtk.StateFlags.NORMAL,color)		
		toolbar.override_background_color(Gtk.StateFlags.SELECTED, color)
		toolbar.override_background_color(Gtk.StateFlags.FOCUSED, color)
		'''
		vbox.pack_start(toolbar,False,False,0)
		#
		self.buttons = {}
		self.buttons['open'] = widgets.ImageToolButton(os.path.join(comun.ICONDIR,'new_active.svg'),os.path.join(comun.ICONDIR,'new_inactive.svg'))
		self.buttons['open'].set_can_focus(False)
		self.buttons['open'].set_tooltip_text(_('Open'))	
		self.buttons['open'].connect('clicked',self.on_button1_clicked)
		toolbar.add(self.buttons['open'])
		#
		self.buttons['save_as'] = widgets.ImageToolButton(os.path.join(comun.ICONDIR,'save_active.svg'),os.path.join(comun.ICONDIR,'save_inactive.svg'))
		self.buttons['save_as'].set_can_focus(False)	
		self.buttons['save_as'].set_tooltip_text(_('Save As'))	
		self.buttons['save_as'].connect('clicked',self.on_button0_clicked)
		toolbar.add(self.buttons['save_as'])
		#
		self.buttons['close'] = widgets.ImageToolButton(os.path.join(comun.ICONDIR,'close_active.svg'),os.path.join(comun.ICONDIR,'close_inactive.svg'))
		self.buttons['close'].set_can_focus(False)
		self.buttons['close'].set_tooltip_text(_('Close'))	
		self.buttons['close'].connect('clicked',self.on_toolbar_clicked,'close')
		toolbar.add(self.buttons['close'])
		#
		toolbar.add(widgets.SeparatorToolButton())
		#
		self.buttons['first'] = widgets.ImageToolButton(os.path.join(comun.ICONDIR,'goto_first.svg'),os.path.join(comun.ICONDIR,'goto_first_inactive.svg'))
		self.buttons['first'].set_can_focus(False)
		self.buttons['first'].set_tooltip_text(_('Go to first'))	
		self.buttons['first'].connect('clicked',self.on_toolbar_clicked,'goto_first')
		toolbar.add(self.buttons['first'])
		#
		self.buttons['back'] = widgets.ImageToolButton(os.path.join(comun.ICONDIR,'goto_back.svg'),os.path.join(comun.ICONDIR,'goto_back_inactive.svg'))
		self.buttons['back'].set_can_focus(False)
		self.buttons['back'].set_tooltip_text(_('Go to back'))	
		self.buttons['back'].connect('clicked',self.on_toolbar_clicked,'goto_back')
		toolbar.add(self.buttons['back'])
		#		
		self.entry1 = widgets.ToolEntry()
		self.entry1.entry.set_width_chars(6)
		self.entry1.entry.connect('key-press-event',self.on_entry1_key_pressed)
		toolbar.add(self.entry1)
		#
		self.label1 = widgets.ToolLabel()
		toolbar.add(self.label1)
		#
		self.buttons['forward'] = widgets.ImageToolButton(os.path.join(comun.ICONDIR,'goto_fordward.svg'),os.path.join(comun.ICONDIR,'goto_fordward_inactive.svg'))
		self.buttons['forward'].set_can_focus(False)
		self.buttons['forward'].set_tooltip_text(_('Go to forward'))	
		self.buttons['forward'].connect('clicked',self.on_toolbar_clicked,'goto_fordward')
		toolbar.add(self.buttons['forward'])
		#
		self.buttons['last'] = widgets.ImageToolButton(os.path.join(comun.ICONDIR,'goto_last.svg'),os.path.join(comun.ICONDIR,'goto_last_inactive.svg'))
		self.buttons['last'].set_can_focus(False)
		self.buttons['last'].set_tooltip_text(_('Go to last'))	
		self.buttons['last'].connect('clicked',self.on_toolbar_clicked,'goto_last')
		toolbar.add(self.buttons['last'])
		#
		toolbar.add(widgets.SeparatorToolButton())
		#
		self.buttons['zoom_in'] = widgets.ImageToolButton(os.path.join(comun.ICONDIR,'zoom_in.svg'),os.path.join(comun.ICONDIR,'zoom_in_inactive.svg'))
		self.buttons['zoom_in'].set_can_focus(False)
		self.buttons['zoom_in'].set_tooltip_text(_('Zoom in'))	
		self.buttons['zoom_in'].connect('clicked',self.on_toolbar_clicked,'zoom_in')
		toolbar.add(self.buttons['zoom_in'])
		#
		self.buttons['zoom_out'] =  widgets.ImageToolButton(os.path.join(comun.ICONDIR,'zoom_out.svg'),os.path.join(comun.ICONDIR,'zoom_out_inactive.svg'))
		self.buttons['zoom_out'].set_can_focus(False)
		self.buttons['zoom_out'].set_tooltip_text(_('Zoom out'))	
		self.buttons['zoom_out'].connect('clicked',self.on_toolbar_clicked,'zoom_out')
		toolbar.add(self.buttons['zoom_out'])
		#
		self.buttons['zoom_reset'] = widgets.ImageToolButton(os.path.join(comun.ICONDIR,'zoom_reset.svg'),os.path.join(comun.ICONDIR,'zoom_reset_inactive.svg'))
		self.buttons['zoom_reset'].set_can_focus(False)
		self.buttons['zoom_reset'].set_tooltip_text(_('Reset zoom'))	
		self.buttons['zoom_reset'].connect('clicked',self.on_toolbar_clicked,'zoom_reset')
		toolbar.add(self.buttons['zoom_reset'])
		#
		self.buttons['zoom_fit'] = widgets.ImageToolButton(os.path.join(comun.ICONDIR,'zoom_fit.svg'),os.path.join(comun.ICONDIR,'zoom_fit_inactive.svg'))
		self.buttons['zoom_fit'].set_can_focus(False)
		self.buttons['zoom_fit'].set_tooltip_text(_('Fit zoom'))			
		self.buttons['zoom_fit'].connect('clicked',self.on_toolbar_clicked,'zoom_fit')
		toolbar.add(self.buttons['zoom_fit'])
		#
		self.buttons['rotate_clockwise'] = widgets.ImageToolButton(os.path.join(comun.ICONDIR,'rotate_clockwise.svg'),os.path.join(comun.ICONDIR,'rotate_clockwise_inactive.svg'))
		self.buttons['rotate_clockwise'].set_can_focus(False)
		self.buttons['rotate_clockwise'].set_tooltip_text(_('Rotate'))	
		self.buttons['rotate_clockwise'].connect('clicked',self.on_toolbar_clicked,'rotate_clockwise')
		toolbar.add(self.buttons['rotate_clockwise'])
		#
		self.buttons['rotate_counter_clockwise'] = widgets.ImageToolButton(os.path.join(comun.ICONDIR,'rotate_counter_clockwise.svg'),os.path.join(comun.ICONDIR,'rotate_counter_clockwise_inactive.svg'))
		self.buttons['rotate_counter_clockwise'].set_can_focus(False)
		self.buttons['rotate_counter_clockwise'].set_tooltip_text(_('Rotate'))	
		self.buttons['rotate_counter_clockwise'].connect('clicked',self.on_toolbar_clicked,'rotate_counter_clockwise')
		toolbar.add(self.buttons['rotate_counter_clockwise'])
		#
		self.buttons['insert_pages'] = widgets.ImageToolButton(os.path.join(comun.ICONDIR,'insert_pages.svg'),os.path.join(comun.ICONDIR,'insert_pages_inactive.svg'))
		self.buttons['insert_pages'].set_can_focus(False)
		self.buttons['insert_pages'].set_tooltip_text(_('Insert pages'))	
		self.buttons['insert_pages'].connect('clicked',self.on_toolbar_clicked,'insert_pages')
		toolbar.add(self.buttons['insert_pages'])
		#
		self.buttons['remove_pages'] = widgets.ImageToolButton(os.path.join(comun.ICONDIR,'extract_pages.svg'),os.path.join(comun.ICONDIR,'extract_pages_inactive.svg'))
		self.buttons['remove_pages'].set_can_focus(False)
		self.buttons['remove_pages'].set_tooltip_text(_('Remove pages'))	
		self.buttons['remove_pages'].connect('clicked',self.on_toolbar_clicked,'remove_pages')
		toolbar.add(self.buttons['remove_pages'])
		#
		toolbar2 = Gtk.Toolbar()
		toolbar2.set_property("visible",True)
		toolbar2.set_property("can_focus",False)
		toolbar2.set_property("toolbar_style",'icons')
		toolbar2.set_property("icon_size",4)
		vbox.pack_start(toolbar2,False,False,0)
		#
		self.buttons['bordercolor'] = widgets.ToolButtonColor()
		self.buttons['bordercolor'].set_can_focus(False)
		self.buttons['bordercolor'].set_tooltip_text(_('Border color'))	
		toolbar2.add(self.buttons['bordercolor'])
		#
		self.buttons['fillcolor'] = widgets.ToolButtonColor()
		self.buttons['fillcolor'].set_can_focus(False)
		self.buttons['fillcolor'].set_tooltip_text(_('Fill color'))	
		toolbar2.add(self.buttons['fillcolor'])		
		#
		self.buttons['font'] = widgets.ToolButtonFont()
		self.buttons['font'].set_can_focus(False)
		self.buttons['font'].set_tooltip_text(_('Font'))	
		toolbar2.add(self.buttons['font'])		
		#
		self.buttons['size'] = widgets.ToolScaleButton()
		self.buttons['size'].set_can_focus(False)
		self.buttons['size'].set_tooltip_text(_('Size'))
		toolbar2.add(self.buttons['size'])
		#
		self.tools = {}
		self.tools['arrow'] = widgets.ImageToggleToolButton(os.path.join(comun.ICONDIR,'arrow_active.svg'),os.path.join(comun.ICONDIR,'arrow_inactive.svg'))
		self.tools['arrow'].set_tooltip_text(_('Select'))	
		self.tools['arrow'].connect('clicked',self.on_buttontool_clicked,'arrow')
		toolbar2.add(self.tools['arrow'])
		#
		self.tools['remove'] = widgets.ImageToggleToolButton(os.path.join(comun.ICONDIR,'remove_active.svg'),os.path.join(comun.ICONDIR,'remove_inactive.svg'))
		self.tools['remove'].set_tooltip_text(_('Remove'))	
		self.tools['remove'].connect('clicked',self.on_buttontool_clicked,'remove')
		toolbar2.add(self.tools['remove'])
		#
		self.tools['line'] = widgets.ImageToggleToolButton(os.path.join(comun.ICONDIR,'line.svg'),os.path.join(comun.ICONDIR,'line_inactive.svg'))
		self.tools['line'].set_tooltip_text(_('Draw a line'))	
		self.tools['line'].connect('clicked',self.on_buttontool_clicked,'line')
		toolbar2.add(self.tools['line'])
		#
		self.tools['rectangle'] = widgets.ImageToggleToolButton(os.path.join(comun.ICONDIR,'rectangle.svg'),os.path.join(comun.ICONDIR,'rectangle_inactive.svg'))
		self.tools['rectangle'].set_tooltip_text(_('Draw a rectangle'))	
		self.tools['rectangle'].connect('clicked',self.on_buttontool_clicked,'rectangle')
		toolbar2.add(self.tools['rectangle'])
		#
		self.tools['circle'] = widgets.ImageToggleToolButton(os.path.join(comun.ICONDIR,'circle.svg'),os.path.join(comun.ICONDIR,'circle_inactive.svg'))
		self.tools['circle'].set_tooltip_text(_('Draw a circle'))	
		self.tools['circle'].connect('clicked',self.on_buttontool_clicked,'circle')
		toolbar2.add(self.tools['circle'])
		#
		self.tools['ellipse'] = widgets.ImageToggleToolButton(os.path.join(comun.ICONDIR,'ellipse_active.svg'),os.path.join(comun.ICONDIR,'ellipse_inactive.svg'))
		self.tools['ellipse'].set_tooltip_text(_('Draw an ellipse'))	
		self.tools['ellipse'].connect('clicked',self.on_buttontool_clicked,'ellipse')
		toolbar2.add(self.tools['ellipse'])
		#
		self.tools['text'] = widgets.ImageToggleToolButton(os.path.join(comun.ICONDIR,'text.svg'),os.path.join(comun.ICONDIR,'text_inactive.svg'))
		self.tools['text'].set_tooltip_text(_('Write some text'))	
		self.tools['text'].connect('clicked',self.on_buttontool_clicked,'text')
		toolbar2.add(self.tools['text'])
		#
		self.tools['image'] = widgets.ImageToggleToolButton(os.path.join(comun.ICONDIR,'image.svg'),os.path.join(comun.ICONDIR,'image_inactive.svg'))
		self.tools['image'].set_tooltip_text(_('Add an image'))	
		self.tools['image'].connect('clicked',self.on_buttontool_clicked,'image')
		toolbar2.add(self.tools['image'])
		#
		self.tools['highlight'] = widgets.ImageToggleToolButton(os.path.join(comun.ICONDIR,'highlight_active.svg'),os.path.join(comun.ICONDIR,'highlight_inactive.svg'))
		self.tools['highlight'].set_tooltip_text(_('Highlight document'))	
		self.tools['highlight'].connect('clicked',self.on_buttontool_clicked,'highlight')
		toolbar2.add(self.tools['highlight'])
		#
		#
		panel1 = Gtk.Paned()
		vbox.pack_start(panel1,True,True,0)
		self.scrolledwindow1 = Gtk.ScrolledWindow()
		self.scrolledwindow1.set_size_request(200,200)
		self.scrolledwindow1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		self.scrolledwindow1.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)		
		self.scrolledwindow1.connect('scroll-event',self.scroll)
		panel1.add(self.scrolledwindow1)
		self.viewport0 = Gtk.Viewport()
		self.miniview = PdfView(width=200,height=HEIGHT)
		self.miniview.connect('selected',self.on_page_selected)
		self.miniview.connect('unselected',self.on_page_unselected)
		self.viewport0.add(self.miniview)
		self.scrolledwindow1.add(self.viewport0)		
		#
		self.scrolledwindow2 = Gtk.ScrolledWindow()
		self.scrolledwindow2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		self.scrolledwindow2.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)		
		panel1.add(self.scrolledwindow2)
		self.viewport = Gtk.Viewport()
		self.viewport.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
		self.scrolledwindow2.add(self.viewport)
		self.view = View(self.viewport,self)
		self.viewport.add(self.view)
		#
		
		#
		self.show_all()
		#
		self.set_focus(self.scrolledwindow2)
		self.text = ''
		self.miniview.reset()
		self.entry1.set_text('')
		self.label1.set_text('')
		self.set_tools_sensistive(sensitive=False)
		self.view.set_page(None,None,None,None,None)	
		
	def set_tools_sensistive(self,sensitive=False,all_elements=False):
		for key in self.menus.keys():
			self.menus[key].set_sensitive(sensitive)
		for key in self.buttons.keys():
			self.buttons[key].set_sensitive(sensitive)
		for key in self.tools.keys():
			self.tools[key].set_sensitive(sensitive)
		self.entry1.set_sensitive(sensitive)
		if all_elements==False:
			self.buttons['open'].set_sensitive(True)
			self.menus['open'].set_sensitive(True)
			self.menus['exit'].set_sensitive(True)				

	def get_help_menu(self):
		help_menu =Gtk.Menu()
		#		
		add2menu(help_menu,text = _('Web...'),conector_event = 'activate',conector_action = self.on_menu_project_clicked)
		add2menu(help_menu,text = _('Get help online...'),conector_event = 'activate',conector_action = self.on_menu_help_online_clicked)
		add2menu(help_menu,text = _('Translate this application...'),conector_event = 'activate',conector_action = self.on_menu_translations_clicked)
		add2menu(help_menu,text = _('Report a bug...'),conector_event = 'activate',conector_action = self.on_menu_bugs_clicked)
		add2menu(help_menu)
		add2menu(help_menu,text = _('About'),conector_event = 'activate',conector_action = self.on_about_activate)
		#
		help_menu.show()
		#
		return help_menu

	def on_menu_project_clicked(self,widget):
		webbrowser.open('https://launchpad.net/updf')
		
	def on_menu_help_online_clicked(self,widget):
		webbrowser.open('https://answers.launchpad.net/updf')
	
	def on_menu_translations_clicked(self,widget):
		webbrowser.open('https://translations.launchpad.net/updf')
	
	def on_menu_bugs_clicked(self,widget):
		webbrowser.open('https://bugs.launchpad.net/updf')		

	def on_about_activate(self,widget):
		ad=Gtk.AboutDialog()
		ad.set_name(comun.APPNAME)
		ad.set_version(comun.VERSION)
		ad.set_copyright('Copyright (c) 2012\nLorenzo Carbonell')
		ad.set_comments(_('An application to modify pdf files'))
		ad.set_license(''+
		'This program is free software: you can redistribute it and/or modify it\n'+
		'under the terms of the GNU General Public License as published by the\n'+
		'Free Software Foundation, either version 3 of the License, or (at your option)\n'+
		'any later version.\n\n'+
		'This program is distributed in the hope that it will be useful, but\n'+
		'WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY\n'+
		'or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for\n'+
		'more details.\n\n'+
		'You should have received a copy of the GNU General Public License along with\n'+
		'this program.  If not, see <http://www.gnu.org/licenses/>.')
		ad.set_website('http://www.atareao.es')
		ad.set_website_label('http://www.atareao.es')
		ad.set_authors(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
		ad.set_documenters(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
		ad.set_translator_credits(''+
		'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>\n')
		ad.set_program_name('uPdf')
		ad.set_logo(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
		ad.run()
		ad.destroy()
				
	def on_toolbar_clicked(self,widget,option):
		#self.miniview.update_current_page()
		if option == 'close':
			self.close_file()
		elif option == 'goto_first':
			self.goto_page(0)
		elif option == 'goto_back':
			self.goto_page(self.miniview.get_number_of_selected_page() - 1)
		elif option == 'goto_fordward':
			self.goto_page(self.miniview.get_number_of_selected_page() + 1)
		elif option == 'goto_last':
			self.goto_page(self.miniview.get_number_of_pages() - 1)
		elif option == 'zoom_in':
			self.view.zoom_in()
		elif option == 'zoom_out':
			self.view.zoom_out()
		elif option == 'zoom_reset':			
			self.view.zoom_reset()
		elif option == 'zoom_fit':
			self.view.zoom_fit()
		elif option == 'rotate_pages':
			spd = SelectPagesToRotateDialog(self)
			if spd.run() == Gtk.ResponseType.ACCEPT:
				clockwise = spd.get_clockwise()
				pages = spd.get_pages()
				spd.destroy()
				p = Progreso(_('Rotate pages'),self,len(pages))
				for number_of_page in pages:
					if number_of_page>0 and number_of_page < (self.miniview.get_number_of_pages()-1):
						if clockwise:
							self.miniview.get_page(number_of_page-1).rotate_clockwise()
						else:
							self.miniview.get_page(number_of_page-1).rotate_counter_clockwise()
					p.increase()
				self.goto_page(self.miniview.get_number_of_selected_page())
			spd.destroy()
		elif option == 'rotate_clockwise':
			self.view.rotate_clockwise()
			sp = self.miniview.get_selected_page().rotate_clockwise()
			if sp:
				sp.rotate_clockwise()
		elif option == 'rotate_counter_clockwise':
			self.view.rotate_counter_clockwise()
			sp = self.miniview.get_selected_page()
			if sp:
				sp.rotate_counter_clockwise()				
		elif option == 'insert_pages':
			ipd = InsertPagesDialog(self)
			if ipd.run() == Gtk.ResponseType.ACCEPT:
				filename = ipd.get_filename()
				is_before = ipd.get_before()
				pages = ipd.get_pages()
				ipd.destroy()
				if filename:
					uri = 'file://' + filename
					document = Poppler.Document.new_from_file(uri, None)
					total_pages = document.get_n_pages()
					p = Progreso(_('Load pdf'),self,len(pages))
					if is_before:
						insert_in = self.miniview.get_number_of_selected_page()						
					else:
						insert_in = self.miniview.get_number_of_selected_page() + 1
					old_selected_page = self.miniview.get_number_of_selected_page()
					self.unselect()
					for num_page in pages:					
						if num_page-1 < total_pages:
							page = document.get_page(num_page-1)
							self.miniview.insert_page(page,insert_in)
							p.increase()
					self.label1.set_text(_(' / %s ')%(str(self.miniview.get_number_of_pages())))
					self.goto_page(old_selected_page+1)
			ipd.destroy()
		elif option == 'insert_blank_pages':
			ibpd = InsertBlankPagesDialog()
			if ibpd.run() == Gtk.ResponseType.ACCEPT:
				number_of_pages = int(ibpd.get_number_of_pages())
				size = ibpd.get_paper_size()
				is_before = ibpd.get_before()
				ibpd.destroy()
				if number_of_pages>0:
					p = Progreso(_('Load pdf'),self,number_of_pages)
					if is_before:
						insert_in = self.miniview.get_number_of_selected_page()						
					else:
						insert_in = self.miniview.get_number_of_selected_page() + 1
					old_selected_page = self.miniview.get_number_of_selected_page()					
					self.unselect()
					for num_page in range(number_of_pages):
						self.miniview.insert_blank_page(size[0],size[1],insert_in)
						p.increase()
					self.label1.set_text(_(' / %s ')%(str(self.miniview.get_number_of_pages())))
					self.goto_page(old_selected_page+1)
			ibpd.destroy()			
		elif option == 'remove_pages':
			spd = RemovePagesDialog(self)
			if spd.run() == Gtk.ResponseType.ACCEPT:
				pages = spd.get_pages()
				spd.destroy()
				pages = sorted(pages,reverse = True)
				for num_page in pages:
					self.miniview.remove_page(num_page-1)
					self.label1.set_text(_(' / %s ')%(str(self.miniview.get_number_of_pages())))
			spd.destroy()
		elif option == 'extract_pages':
			spd = ExtractPagesDialog(self)
			if spd.run() == Gtk.ResponseType.ACCEPT:
				pages = spd.get_pages()
				option_remove = spd.get_remove()
				spd.destroy()
				pages = sorted(pages,reverse = False)
				self.save_pages_as_pdf(pages)
				if option_remove:
					pages = sorted(pages,reverse = True)
					for num_page in pages:
						self.miniview.remove_page(num_page-1)
						self.label1.set_text(_(' / %s ')%(str(self.miniview.get_number_of_pages())))
			spd.destroy()
		elif option == 'copy':
			if self.view.tool == 'arrow' and self.view.mouse_down == None and self.view.selection_end and self.view.selection_start:
				self.view.copy_to_pixbuf()
		elif option == 'paste':
			if self.view.tool == 'arrow':
				self.view.paste_from_pixbuf()
			
	
	def on_resize(self,widget,data):
		self.view.is_plotted = False
		self.view.queue_draw()
		
	def on_view_key_pressed(self,widget,event):
		if self.view.tool and self.view.tool == 'text' :
			if event.keyval >= 32 and event.keyval <= 126 or\
			event.keyval >= 127 and event.keyval <= 255:
				if event.keyval == 32:
					self.view.text +=' '
				else:
					self.view.text += unichr(Gdk.keyval_to_unicode(event.keyval))
				self.view.queue_draw()
			elif event.keyval == 65288: #backspace
				self.view.text = self.view.text[:-1]
				self.view.queue_draw()
			elif event.keyval == 65293 or event.keyval == 65421: # return
				self.view.write()
			elif event.keyval in range(65456,65466):
				self.view.text += str(event.keyval-65456)
				self.view.queue_draw()
			else:
				print(event.keyval)
				print(Gdk.keyval_name(event.keyval))
		else:
			if event.keyval == 65361: 
				self.goto_page(0)
			elif event.keyval == 65362 or event.keyval == 65360:
				self.goto_page(self.miniview.get_number_of_selected_page() - 1)
			elif event.keyval == 65363:
				self.goto_page(self.miniview.get_number_of_pages() - 1)
			elif event.keyval == 65364 or event.keyval == 65367:

				self.goto_page(self.miniview.get_number_of_selected_page() + 1)
			elif event.keyval == 65451 or event.keyval == 43:
				self.view.zoom_in()
			elif event.keyval == 65453 or event.keyval == 45:
				self.view.zoom_out()
			else:
				print(event.keyval)
				print(Gdk.keyval_name(event.keyval))
				
	def toInt(self,valor):
		try:
			if len(valor)>0:
				return int(float(valor))
			else:
				return 0		
		except:
			return self.miniview.get_selected_page() + 1
	
	def on_entry1_key_pressed(self,widget,event):
		if event.keyval == 65293 or event.keyval == 65421:
			if self.miniview.get_number_of_pages() >0 :
				page_to_go = self.toInt(self.entry1.get_text())-1
			else:
				page_to_go = 0
			self.goto_page(page_to_go)
				
	def on_button0_clicked(self,widget):
		dialog = Gtk.FileChooserDialog(_('Select a pdf file'),
										self,
									   Gtk.FileChooserAction.SAVE,
									   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
										Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		dialog.set_default_response(Gtk.ResponseType.OK)
		filter = Gtk.FileFilter()
		filter.set_name(_('Pdf files'))
		filter.add_mime_type('application/pdf')
		filter.add_pattern('*.pdf')
		dialog.add_filter(filter)
		preview = MiniView(200)
		dialog.set_use_preview_label(False)
		dialog.set_preview_widget(preview)
		dialog.connect('update-preview', self.update_preview_cb, preview)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			self.unselect()
			filename = dialog.get_filename()
			dialog.destroy()
			if not filename.endswith('.pdf'):
				filename += '.pdf'
			pdfsurface = cairo.PDFSurface(filename, 200, 200)
			context = cairo.Context(pdfsurface)
			progressdialog = Progreso(_('Save pdf'),self,len(self.miniview.get_children()))
			for page in self.miniview.get_children():
				context.save()
				if page.rotation_angle == 0.0 or page.rotation_angle == 2.0:
					width,height = page.get_size()
				else:
					height,width = page.get_size()
				pdfsurface.set_size(width,height)
				mtr = cairo.Matrix()
				mtr.rotate(page.rotation_angle*math.pi/2.0)
				context.transform(mtr)
				if page.rotation_angle == 1.0:
					context.translate(0.0,-width)
				elif page.rotation_angle == 2.0:
					context.translate(-width,-height)
				elif page.rotation_angle == 3.0:
					context.translate(-height,0.0)
				if page.page:
					page.page.render(context)
				context.restore()
				context.save()
				mtr = cairo.Matrix()
				mtr.rotate(page.rotation_angle*math.pi/2.0)
				mtr.scale(1.0/comun.RESOLUTION,1.0/comun.RESOLUTION)
				context.transform(mtr)
				if page.rotation_angle == 1.0:
					context.translate(0.0,-width*comun.RESOLUTION)
				elif page.rotation_angle == 2.0:
					context.translate(-width*comun.RESOLUTION,-height*comun.RESOLUTION)
				elif page.rotation_angle == 3.0:
					context.translate(-height*comun.RESOLUTION,0.0)
				for drawing in page.drawings:
					drawing.draw(context)
				context.restore()
				context.show_page()
				progressdialog.increase()
		dialog.destroy()
		
	def on_button1_clicked(self,widget):
		self.close_file()
		dialog = Gtk.FileChooserDialog(_('Select a pdf file'),
										self,
									   Gtk.FileChooserAction.OPEN,
									   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
										Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		dialog.set_default_response(Gtk.ResponseType.OK)
		filter = Gtk.FileFilter()
		filter.set_name(_('Pdf files'))
		filter.add_mime_type('application/pdf')
		filter.add_pattern('*.pdf')
		dialog.add_filter(filter)
		preview = MiniView(200,force=True)
		dialog.set_use_preview_label(False)
		dialog.set_preview_widget(preview)
		dialog.connect('update-preview', self.update_preview_cb, preview)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			filename = dialog.get_filename()		
			self.load_file(filename)			
		dialog.destroy()
	
	def update_preview_cb(self,file_chooser, preview):
		filename = file_chooser.get_preview_filename()
		have_preview = False
		try:
			if os.path.isfile(filename):
				uri = "file://" + filename
				document = Poppler.Document.new_from_file(uri, None)
				if document.get_n_pages() > 0:
					preview.set_page(document.get_page(0))
					have_preview = True
		except Exception as e:
			print(e)
		file_chooser.set_preview_widget_active(have_preview)
		return		
		
	def close_file(self):
		self.miniview.reset()
		self.entry1.set_text('')
		self.label1.set_text('')
		self.set_tools_sensistive(sensitive=False)
		self.view.set_page(None,None,None,None,None)	
		
	def on_buttontool_clicked(self,widget, tool):
		self.view.mouse_down = None
		self.view.selection_end = None
		self.view.selection_start = None		
		if tool == 'text':
			self.view.text =''
		if self.tools[tool].get_active():
			for atool in self.tools.keys():
				if atool != tool:
					self.tools[atool].set_active(False)
			self.view.set_tool(tool)
		else:
			self.view.set_tool(None)
	def on_close_application(self,widget):
		exit(0)
		
	def load_file(self,afile):
		uri = "file://" + afile
		try:
			document = Poppler.Document.new_from_file(uri, None)
			number_of_pages = document.get_n_pages()				
			if number_of_pages>0:
				p = Progreso(_('Load pdf'),self,number_of_pages)
				for number_of_page in range(number_of_pages):
					page = document.get_page(number_of_page)			
					self.miniview.insert_page(page)
					p.increase()		
			self.goto_page(0)
			can_do_anything = (self.miniview.get_number_of_pages() > 0)
			self.set_tools_sensistive(sensitive=can_do_anything)
		except(Exception,e):
			print(e)
			
	def on_page_unselected(self,widget,n):
		if self.view.drawings and n >-1 :
			self.miniview.get_page(n).drawings = clone_list(self.view.drawings)
			self.miniview.get_page(n).render()
			self.view.drawings = []
		
	def on_page_selected(self,widget,n):
		if n<0:
			n = 0
		if n >= self.miniview.get_number_of_pages():
			n = self.miniview.get_number_of_pages() - 1
		if self.miniview.get_number_of_pages() > 0:
			self.entry1.set_text(str(n+1))
			self.label1.set_text(_(' / %s ')%(str(self.miniview.get_number_of_pages())))
			rotation_angle = self.miniview.get_selected_page().rotation_angle
			width,height = self.miniview.get_selected_page().get_size()
			width = int(width*comun.RESOLUTION)
			height = int(height*comun.RESOLUTION)
			self.view.set_page(self.miniview.get_selected_page().get_image(),n,rotation_angle,width,height)
			self.view.drawings = clone_list(self.miniview.get_selected_page().drawings)
			self.scrolledwindow1.get_vadjustment().set_value(n*self.miniview.height)
			#
			rect = self.scrolledwindow1.get_allocation()
			after = rect.height/HEIGHT
			number_of_page =  int(self.scrolledwindow1.get_vadjustment().get_value()/HEIGHT)
			for i in range(-1,after+1):
				n = number_of_page + i
				if n > 0 and n < self.miniview.get_number_of_pages():
					self.miniview.get_page(number_of_page+1).render()
							
	def save_pages_as_pdf(self,pages):
		dialog = Gtk.FileChooserDialog(_('Select a pdf file'),
										self,
									   Gtk.FileChooserAction.SAVE,
									   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
										Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		dialog.set_default_response(Gtk.ResponseType.OK)
		filter = Gtk.FileFilter()
		filter.set_name(_('Pdf files'))
		filter.add_mime_type('application/pdf')
		filter.add_pattern('*.pdf')
		dialog.add_filter(filter)
		preview = MiniView(200)
		dialog.set_use_preview_label(False)
		dialog.set_preview_widget(preview)
		dialog.connect('update-preview', self.update_preview_cb, preview)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			filename = dialog.get_filename()
			dialog.destroy()
			if not filename.endswith('.pdf'):
				filename += '.pdf'
			pdfsurface = cairo.PDFSurface(filename, 200, 200)
			context = cairo.Context(pdfsurface)
			progressdialog = Progreso(_('Save pdf'),self,len(pages))
			for number_of_page in pages:
				if number_of_page >0 and number_of_page < len(self.miniview.get_children()):
					page = self.miniview.get_children()[number_of_page-1]
					context.save()
					if page.rotation_angle == 0.0 or page.rotation_angle == 2.0:
						width,height = page.get_size()
					else:
						height,width = page.get_size()
					pdfsurface.set_size(width,height)
					mtr = cairo.Matrix()
					mtr.rotate(page.rotation_angle*math.pi/2.0)
					context.transform(mtr)
					if page.rotation_angle == 1.0:
						context.translate(0.0,-width)
					elif page.rotation_angle == 2.0:
						context.translate(-width,-height)
					elif page.rotation_angle == 3.0:
						context.translate(-height,0.0)
					if page.page:
						page.page.render(context)
					context.restore()
					context.save()
					mtr = cairo.Matrix()
					mtr.rotate(page.rotation_angle*math.pi/2.0)
					mtr.scale(1.0/comun.RESOLUTION,1.0/comun.RESOLUTION)
					context.transform(mtr)
					if page.rotation_angle == 1.0:
						context.translate(0.0,-width*comun.RESOLUTION)
					elif page.rotation_angle == 2.0:
						context.translate(-width*comun.RESOLUTION,-height*comun.RESOLUTION)
					elif page.rotation_angle == 3.0:
						context.translate(-height*comun.RESOLUTION,0.0)
					for drawing in page.drawings:
						drawing.draw(context)
					context.restore()
					context.show_page()
				progressdialog.increase()
		dialog.destroy()
		
	def scroll(self,widget,data):
		rect = self.scrolledwindow1.get_allocation()
		after = rect.height/HEIGHT
		number_of_page =  int(self.scrolledwindow1.get_vadjustment().get_value()/HEIGHT)
		self.entry1.set_text(str(number_of_page+1))
		for i in range(-1,after+1):
			n = number_of_page + i
			if n > 0 and n < self.miniview.get_number_of_pages():
				self.miniview.get_page(number_of_page+1).render()						
		
	def goto_page(self,n):
		if n<0:
			n = 0
		if n >= self.miniview.get_number_of_pages():
			n = self.miniview.get_number_of_pages() - 1
		if self.miniview.get_number_of_pages() > 0:
			self.entry1.set_text(str(n+1))
			self.label1.set_text(_(' / %s ')%(str(self.miniview.get_number_of_pages())))
			self.miniview.select_page(n)	
			rotation_angle = self.miniview.get_selected_page().rotation_angle
			width,height = self.miniview.get_selected_page().get_size()
			width = int(width*comun.RESOLUTION)
			height = int(height*comun.RESOLUTION)
			self.view.set_page(self.miniview.get_selected_page().get_image(),n,rotation_angle,width,height)
			self.view.drawings = clone_list(self.miniview.get_selected_page().drawings)
			self.scrolledwindow1.get_vadjustment().set_value(n*self.miniview.height)
			#
			rect = self.scrolledwindow1.get_allocation()
			after = rect.height/HEIGHT
			number_of_page =  int(self.scrolledwindow1.get_vadjustment().get_value()/HEIGHT)
			for i in range(-1,after+1):
				n = number_of_page + i
				if n > 0 and n < self.miniview.get_number_of_pages():
					self.miniview.get_page(number_of_page+1).render()
	def unselect(self):
		if self.view.drawings and self.miniview.get_selected_page():
			self.miniview.get_selected_page().drawings = clone_list(self.view.drawings)
			self.miniview.get_selected_page().render()
			self.view.drawings = []
			self.miniview.unselect()

def main():
	ss = splashscreen.SplashScreen()
	splashscreen.wait(3)
	ss.destroy()
	main_without_splash_screen()

def main_without_splash_screen():
	screen = Gdk.Screen.get_default()
	css_provider = Gtk.CssProvider()
	css_provider.load_from_path(comun.CSSFILE)
	context = Gtk.StyleContext()
	context.add_provider_for_screen(screen, css_provider,Gtk.STYLE_PROVIDER_PRIORITY_USER)
	uPDF = UPDF()
	Gtk.main()

if __name__ == '__main__':
	main()
	#main_without_splash_screen()
	exit(0)
