#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# dialogs.py
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
from gi.repository import Gtk
from gi.repository import Poppler
import os
import comun
from comun import _
from miniview import MiniView


def get_num(chain):
	try:
		chain = chain.strip() # removing spaces
		return int(float(chain))
	except:
		return None
def from_ranges_get_pages(chain, reverse = False):
	ranges = get_ranges(chain)
	pages =[]
	for rang in ranges:
		if len(rang)>1:
			for i in range(rang[0],rang[1]+1):
				if not i in pages:
					pages.append(i)
		else:
			if not rang[0] in pages:
				pages.append(rang[0])
	if len(pages)>0:
		pages = sorted(pages,reverse=reverse)
	return pages

def get_ranges(chain):
	ranges = []
	if chain.find(',') > -1:
		for part in chain.split(','):
			if part.find('-') > -1:
				parts = part.split('-')
				if len(parts) > 1:
					f = get_num(parts[0])
					t = get_num(parts[1])
					if f != None and t !=None:
						ranges.append([f,t])
			else:
				el = get_num(part)
				if el:
					ranges.append([el])
	elif chain.find('-') > -1:
		parts = chain.split('-')
		if len(parts) > 1:
			f = get_num(parts[0])
			t = get_num(parts[1])
			if f != None and t !=None:
				ranges.append([f,t])
	else:
		el = get_num(chain)
		if el:
			ranges.append([el])
	return ranges
		
class InsertPagesDialog(Gtk.Dialog):
	def __init__(self, parent=None):
		Gtk.Dialog.__init__(self,_('Insert pages'),parent,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL))
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_size_request(300, 120)
		self.set_resizable(False)
		self.set_icon_from_file(comun.ICON)
		self.set_icon_name('application-pdf')
		self.connect('destroy', self.close_application)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		notebook = Gtk.Notebook()
		vbox0.add(notebook)
		#
		frame1 = Gtk.Frame()
		notebook.append_page(frame1,tab_label = Gtk.Label(_('Select Pages')))
		#
		table1 = Gtk.Table(rows = 3, columns = 3, homogeneous = False)
		table1.set_border_width(5)
		table1.set_col_spacings(5)
		table1.set_row_spacings(5)
		frame1.add(table1)
		#
		label1 = Gtk.Label(_('Selectd pdf file')+':')
		label1.set_tooltip_text(_('Select pdf file from which insert pages'))
		label1.set_alignment(0,.5)
		table1.attach(label1,0,1,0,1, xoptions = Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.button1 = Gtk.Button(_('Select file'))
		self.button1.set_tooltip_text(_('Select pdf file'))
		self.button1.connect('clicked',self.on_self_button1_clicked)
		table1.attach(self.button1,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label2 = Gtk.Label(_('Pages')+':')
		label2.set_tooltip_text(_('Type page number and/or page\nranges separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
		label2.set_alignment(0,.5)
		table1.attach(label2,0,1,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.entry2 = Gtk.Entry()
		self.entry2.set_tooltip_text(_('Type page number and/or page\nranges separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
		table1.attach(self.entry2,1,2,1,2, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.option1 = Gtk.RadioButton(group=None, label=_('Before current page'))
		table1.attach(self.option1,0,1,2,3, xoptions = Gtk.AttachOptions.EXPAND| Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		self.option2 = Gtk.RadioButton(group=self.option1, label=_('After current page'))
		table1.attach(self.option2,1,2,2,3, xoptions = Gtk.AttachOptions.EXPAND| Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.show_all()
		#
		self.filename = None
class InsertPagesDialog(Gtk.Dialog):
	def __init__(self, parent=None):
		Gtk.Dialog.__init__(self,_('Insert pages'),parent,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL))
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_size_request(300, 120)
		self.set_resizable(False)
		self.set_icon_from_file(comun.ICON)
		self.set_icon_name('application-pdf')
		self.connect('destroy', self.close_application)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		notebook = Gtk.Notebook()
		vbox0.add(notebook)
		#
		frame1 = Gtk.Frame()
		notebook.append_page(frame1,tab_label = Gtk.Label(_('Select Pages')))
		#
		table1 = Gtk.Table(rows = 3, columns = 3, homogeneous = False)
		table1.set_border_width(5)
		table1.set_col_spacings(5)
		table1.set_row_spacings(5)
		frame1.add(table1)
		#
		label1 = Gtk.Label(_('Selectd pdf file')+':')
		label1.set_tooltip_text(_('Select pdf file from which insert pages'))
		label1.set_alignment(0,.5)
		table1.attach(label1,0,1,0,1, xoptions = Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.button1 = Gtk.Button(_('Select file'))
		self.button1.set_tooltip_text(_('Select pdf file'))
		self.button1.connect('clicked',self.on_self_button1_clicked)
		table1.attach(self.button1,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label2 = Gtk.Label(_('Pages')+':')
		label2.set_tooltip_text(_('Type page number and/or page\nranges separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
		label2.set_alignment(0,.5)
		table1.attach(label2,0,1,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.entry2 = Gtk.Entry()
		self.entry2.set_tooltip_text(_('Type page number and/or page\nranges separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
		table1.attach(self.entry2,1,2,1,2, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.option1 = Gtk.RadioButton(group=None, label=_('Before current page'))
		table1.attach(self.option1,0,1,2,3, xoptions = Gtk.AttachOptions.EXPAND| Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		self.option2 = Gtk.RadioButton(group=self.option1, label=_('After current page'))
		table1.attach(self.option2,1,2,2,3, xoptions = Gtk.AttachOptions.EXPAND| Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.show_all()
		#
		self.filename = None			
	def on_self_button1_clicked(self,widget):
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
			ans = os.path.split(filename)
			if len(ans)>1:
				self.filename = filename				
				self.button1.set_label(ans[1])
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
		except Exception,e:
			print(e)
		file_chooser.set_preview_widget_active(have_preview)
		return		
		
	def close_application(self,widget):
		self.hide()

	def get_filename(self):
		return self.filename

	def get_before(self):
		return self.option1.get_active()
	
	def get_pages(self):
		return from_ranges_get_pages(self.entry2.get_text())

class InsertBlankPagesDialog(Gtk.Dialog):
	def __init__(self, parent=None):
		Gtk.Dialog.__init__(self,_('Insert blank pages'),parent,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL))
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_size_request(300, 120)
		self.set_resizable(False)
		self.set_icon_from_file(comun.ICON)
		self.set_icon_name('application-pdf')
		self.connect('destroy', self.close_application)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		notebook = Gtk.Notebook()
		vbox0.add(notebook)
		#
		frame1 = Gtk.Frame()
		notebook.append_page(frame1,tab_label = Gtk.Label(_('Select Pages')))
		#
		table1 = Gtk.Table(rows = 3, columns = 3, homogeneous = False)
		table1.set_border_width(5)
		table1.set_col_spacings(5)
		table1.set_row_spacings(5)
		frame1.add(table1)
		#
		label1 = Gtk.Label(_('Number of pages')+':')
		label1.set_tooltip_text(_('Select the number of blank pages to insert'))
		label1.set_alignment(0,.5)
		table1.attach(label1,0,1,0,1, xoptions = Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		adj = Gtk.Adjustment(value=1, lower=1, upper=100,step_incr=1, page_incr=5, page_size=1)
		self.entry1 = Gtk.SpinButton()
		self.entry1.set_adjustment(adj)
		self.entry1.set_tooltip_text(_('The number of blank pages to insert'))
		table1.attach(self.entry1,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label2 = Gtk.Label(_('Paper size')+':')
		label2.set_tooltip_text(_('Select the paper size'))
		label2.set_alignment(0,.5)
		table1.attach(label2,0,1,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		liststore = Gtk.ListStore(str, float, float)
		liststore.append([_('4A0'),4768.0,6741.0])
		liststore.append([_('2A0'),3370.0,4768.0])
		liststore.append([_('A0'),2384.0,3370.0])
		liststore.append([_('A1'),1684.0,2384.0])
		liststore.append([_('Elephant'),1656.0,2016.0])
		liststore.append([_('Royal'),1440.0,1800.0])
		liststore.append([_('Broadsheet'),1296.0,1728.0])
		liststore.append([_('A2'),1191.0,1684.0])
		liststore.append([_('Medium'),1296.0,1656.0])
		liststore.append([_('Crown'),1080.0,1440.0])
		liststore.append([_('Post'),1116.0,1404.0])
		liststore.append([_('Tabloid'),792.0,1224.0])
		liststore.append([_('Ledger'),792.0,1224.0])
		liststore.append([_('A3'),842.0,1191.0])
		liststore.append([_('Legal'),612.0,1008.0])
		liststore.append([_(' Folio'),595.0,936.0])
		liststore.append([_('Fanfold'),612.0,864.0])
		liststore.append([_('A4'),595.0,842.0])
		liststore.append([_('Letter'),612.0,792.0])
		liststore.append([_('Quarto'),648.0,792.0])
		liststore.append([_('A5'),420.0,595.0])
		liststore.append([_('Junior Legal'),360.0,576.0])
		liststore.append([_('A6'),297.0,420.0])
		liststore.append([_('A7'),210.0,297.0])
		liststore.append([_('A8'),148.0,210.0])
		liststore.append([_('A9'),105.0,148.0])
		liststore.append([_('A10'),73.0,105.0])
		self.entry2 = Gtk.ComboBox.new_with_model(model=liststore)
		renderer_text = Gtk.CellRendererText()
		self.entry2.pack_start(renderer_text, True)
		self.entry2.add_attribute(renderer_text, "text", 0)
		self.entry2.set_active(17)
		table1.attach(self.entry2,1,2,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.option1 = Gtk.RadioButton(group=None, label=_('Before current page'))
		table1.attach(self.option1,0,1,2,3, xoptions = Gtk.AttachOptions.EXPAND| Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		self.option2 = Gtk.RadioButton(group=self.option1, label=_('After current page'))
		table1.attach(self.option2,1,2,2,3, xoptions = Gtk.AttachOptions.EXPAND| Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.show_all()
		#
		self.filename = None			
		
	def close_application(self,widget):
		self.hide()

	def get_number_of_pages(self):
		return self.entry1.get_value()

	def get_paper_size(self):
		tree_iter = self.entry2.get_active_iter()
		if tree_iter != None:
			model = self.entry2.get_model()
			w = model[tree_iter][1]
			h = model[tree_iter][2]
			return w,h
		return None

	def get_before(self):
		return self.option1.get_active()	

class SelectPagesToRotateDialog(Gtk.Dialog):
	def __init__(self,parent=None):
		Gtk.Dialog.__init__(self,_('Set pages to rotate'),parent,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL))
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_size_request(300, 120)
		self.set_resizable(False)
		self.set_icon_from_file(comun.ICON)
		self.connect('destroy', self.close_application)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		notebook = Gtk.Notebook()
		vbox0.add(notebook)
		#
		frame1 = Gtk.Frame()
		notebook.append_page(frame1,tab_label = Gtk.Label(_('Select Pages')))
		#
		table1 = Gtk.Table(rows = 3, columns = 3, homogeneous = False)
		table1.set_border_width(5)
		table1.set_col_spacings(5)
		table1.set_row_spacings(5)
		frame1.add(table1)
		#
		label1 = Gtk.Label(_('Pages')+':')
		label1.set_tooltip_text(_('Type page number and/or page\nranges separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
		label1.set_alignment(0,.5)
		table1.attach(label1,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.entry1 = Gtk.Entry()
		self.entry1.set_tooltip_text(_('Type page number and/or page\nranges separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
		table1.attach(self.entry1,1,3,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.option1 = Gtk.RadioButton(group=None, label=_('Clockwise'))
		table1.attach(self.option1,0,1,2,3, xoptions = Gtk.AttachOptions.EXPAND| Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		self.option2 = Gtk.RadioButton(group=self.option1, label=_('Counterclockwise'))
		table1.attach(self.option2,1,2,2,3, xoptions = Gtk.AttachOptions.EXPAND| Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		
		self.show_all()
		
	def close_application(self,widget):
		self.hide()

	def get_pages(self):
		return from_ranges_get_pages(self.entry1.get_text())		

	def get_clockwise(self):
		return self.option1.get_active()

class RemovePagesDialog(Gtk.Dialog):
	def __init__(self, parent=None):
		Gtk.Dialog.__init__(self,_('Remove pages from document'),parent,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL))
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_size_request(300, 120)
		self.set_resizable(False)
		self.set_icon_from_file(comun.ICON)
		self.connect('destroy', self.close_application)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		notebook = Gtk.Notebook()
		vbox0.add(notebook)
		#
		frame1 = Gtk.Frame()
		notebook.append_page(frame1,tab_label = Gtk.Label(_('Select Pages')))
		#
		table1 = Gtk.Table(rows = 3, columns = 3, homogeneous = False)
		table1.set_border_width(5)
		table1.set_col_spacings(5)
		table1.set_row_spacings(5)
		frame1.add(table1)
		#
		label1 = Gtk.Label(_('Pages')+':')
		label1.set_tooltip_text(_('Type page number and/or page\nranges separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
		label1.set_alignment(0,.5)
		table1.attach(label1,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.entry1 = Gtk.Entry()
		self.entry1.set_tooltip_text(_('Type page number and/or page\nranges separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
		table1.attach(self.entry1,1,3,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.show_all()
	def close_application(self,widget):
		self.hide()

	def get_pages(self):
		return from_ranges_get_pages(self.entry1.get_text())
class ExtractPagesDialog(Gtk.Dialog):
	def __init__(self, parent=None):
		Gtk.Dialog.__init__(self,_('Extract pages from document'),parent,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL))
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_size_request(300, 120)
		self.set_resizable(False)
		self.set_icon_from_file(comun.ICON)
		self.connect('destroy', self.close_application)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		notebook = Gtk.Notebook()
		vbox0.add(notebook)
		#
		frame1 = Gtk.Frame()
		notebook.append_page(frame1,tab_label = Gtk.Label(_('Select Pages')))
		#
		table1 = Gtk.Table(rows = 3, columns = 3, homogeneous = False)
		table1.set_border_width(5)
		table1.set_col_spacings(5)
		table1.set_row_spacings(5)
		frame1.add(table1)
		#
		label1 = Gtk.Label(_('Pages')+':')
		label1.set_tooltip_text(_('Type page number and/or page\nranges separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
		label1.set_alignment(0,.5)
		table1.attach(label1,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.entry1 = Gtk.Entry()
		self.entry1.set_tooltip_text(_('Type page number and/or page\nranges separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
		table1.attach(self.entry1,1,3,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.option1 = Gtk.CheckButton(label=_('Remove from document'))
		table1.attach(self.option1,0,1,1,2, xoptions = Gtk.AttachOptions.EXPAND| Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)

		self.show_all()
	def close_application(self,widget):
		self.hide()

	def get_pages(self):
		return from_ranges_get_pages(self.entry1.get_text())

	def get_remove(self):
		return self.option1.get_active()

if __name__ == '__main__':
	ibpd = InsertBlankPagesDialog()
	ibpd.run()
	print ibpd.get_number_of_pages()
	print ibpd.get_paper_size()
	print ibpd.get_before()
	'''
	ExtractPagesDialog().run()
	InsertPagesDialog().run()
	RemovePagesDialog().run()
	SelectPagesToRotateDialog().run()
	'''
	exit(0)
