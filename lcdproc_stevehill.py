#!/usr/bin/env python

# lcdproc client class library
# Copyright (C) 2006 Steve Hill <steve@nexusuk.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import socket
import string

HIDDEN='hidden'
BACKGROUND='background'
INFO='info'
FOREGROUND='foreground'
ALERT='alert'
INPUT='input'
ON='on'
OFF='off'
GREY='gray'
OPEN='open'
TOGGLE='toggle'
BLINK='blink'
FLASH='flash'
UNDER='under'
BLOCK='block'

STRING='string'
TITLE='title'
HBAR='hbar'
VBAR='vbar'
ICON='icon'
SCROLLER='scroller'
FRAME='frame'
NUM='num'

HORIZONTAL='h'
VERTICAL='v'
MARQUEE='m'

EXCLUSIVE='excl'
SHARED='shared'

ACTION='action'
CHECKBOX='checkbox'
RING='ring'
SLIDER='slider'
NUMERIC='numeric'
ALPHA='alpha'
IP='ip'
MENU='menu'

NONE='none'
CLOSE='close'
QUIT='quit'

class widget:
	"""A widget on the LCD.

	Do not construct this directly - use the screen.widget_add() method instead."""

	def __init__(self,screen,id,type,parent_frame):
		self.id = id
		self.screen = screen
		self.parent_frame = parent_frame
		if (self.parent_frame != None):
			self.screen.lcd.send_command('widget_add',str(self.screen.id),str(self.id),type,'-in',self.parent_frame.id)
		else:
			self.screen.lcd.send_command('widget_add',str(self.screen.id),str(self.id),type)
	
	def __del__(self):
		self.screen._del_widget(self)
		self.screen.lcd.send_command('widget_del',str(self.screen.id),str(self.id))


class widget_string(widget):
	def __init__(self,screen,id,parent_frame):
		widget.__init__(self,screen,id,STRING,parent_frame)
	
	def set(self,x,y,text):
		"""Set some text to display at a certain position."""
		self.x = x
		self.y = y
		self.text = text
		self.screen.lcd.send_command('widget_set',str(self.screen.id),str(self.id),str(self.x),str(self.y),self.text)


class widget_title(widget):
	def __init__(self,screen,id,parent_frame):
		widget.__init__(self,screen,id,TITLE,parent_frame)
	
	def set(self,text):
		"""Set some text as a title."""
		self.text = text
		self.screen.lcd.send_command('widget_set',str(self.screen.id),str(self.id),self.text)


class widget_hbar(widget):
	def __init__(self,screen,id,parent_frame):
		widget.__init__(self,screen,id,HBAR,parent_frame)
	
	def set(self,x,y,length):
		"""Set a bar display at a certain position."""
		self.x = x
		self.y = y
		self.length = length
		self.screen.lcd.send_command('widget_set',str(self.screen.id),str(self.id),str(self.x),str(self.y),str(self.length))


class widget_vbar(widget_hbar):
	def __init__(self,screen,id,parent_frame):
		widget.__init__(self,screen,id,VBAR,parent_frame)


class widget_icon(widget_string):
	def __init__(self,screen,id,parent_frame):
		widget.__init__(self,screen,id,ICON,parent_frame)


class widget_scroller(widget):
	def __init__(self,screen,id,parent_frame):
		widget.__init__(self,screen,id,SCROLLER,parent_frame)

	def set(self,left,top,right,bottom,direction,speed,text):
		"""Set a scroller to display at a certain position.
		
		direction is: HORIZONTAL | VERTICAL | MARQUEE"""
		self.left = left
		self.right = right
		self.top = top
		self.bottom = bottom
		self.direction = direction
		self.speed = speed
		self.text = text
		self.screen.lcd.send_command('widget_set',str(self.screen.id),str(self.id),str(self.left),str(self.top),str(self.right),str(self.bottom),self.direction,str(self.speed),self.text)


class widget_frame(widget):
	def __init__(self,screen,id,parent_frame):
		widget.__init__(self,screen,id,FRAME,parent_frame)
		self.children = []
	
	def __del__(self):
		del self.children
		widget.__del__(self)
	
	def set(self,left,top,right,bottom,width,height,direction,speed):
		"""Set a frame to display at a certain position.
		
		direction is: HORIZONTAL | VERTICAL | MARQUEE"""
		self.left = left
		self.right = right
		self.top = top
		self.bottom = bottom
		self.width = width
		self.height = height
		self.direction = direction
		self.speed = speed
		self.screen.lcd.send_command('widget_set',str(self.screen.id),str(self.id),str(self.left),str(self.top),str(self.right),str(self.bottom),str(self.width),str(self.height),self.direction,str(self.speed))
	
	def widget_add(self,type):
		"""Add a new widget.

		Returns a widget_* object.
		Type can be: STRING | TITLE | HBAR | VBAR | ICON | SCROLLER | FRAME | NUM"""
		widget =  self.screen._add_widget(type,self)
		self.children.append(widget)
		return widget
	
	def _del_widget(self,widget):
		self.screen._del_widget(widget)
		self.children.remove(widget)


class widget_num(widget):
	def __init__(self,screen,id,parent_frame):
		widget.__init__(self,screen,id,NUM,parent_frame)

	def set(self,x,text):
		"""Set some text in large numbers."""
		self.x = x
		self.text = text
		self.screen.lcd.send_command('widget_set',str(self.screen.id),str(self.id),str(self.x),self.text)


class screen:
	"""A single screen on the LCD.
	
	Do not construct this directly - use the lcd.screen_add() method instead."""

	def __init__(self,lcd,id):
		self.id = id
		self.lcd = lcd
		self.lcd.send_command('screen_add',str(self.id))
		self.widgets = {}
	
	def __del__(self):
		self.lcd._del_screen(self)
		del self.widgets
		self.lcd.send_command('screen_del',str(self.id))
	
	def set_name(self,name):
		"""Set the screen's name."""
		self.name = name
		self.lcd.send_command('screen_set',str(self.id),'-name',self.name)

	def set_width(self,width):
		"""Set the screen's width."""
		self.width = width
		self.lcd.send_command('screen_set',str(self.id),'-wid',str(self.width))

	def set_height(self,height):
		"""Set the screen's height."""
		self.height = height
		self.lcd.send_command('screen_set',str(self.id),'-hgt',self(self.height))

	def set_priority(self,priority):
		"""Set the screen's priority: [1-255] | HIDDEN | BACKGROUND | INFO | FOREGROUND | ALERT | INPUT."""
		self.priority = priority
		self.lcd.send_command('screen_set',str(self.id),'-priority',str(self.priority))

	def set_heartbeat(self,heartbeat):
		"""Set the screen's heartbeat setting: ON | OFF | OPEN."""
		self.heartbeat = heartbeat
		self.lcd.send_command('screen_set',str(self.id),'-heartbeat',self.heartbeat)

	def set_backlight(self,backlight):
		"""Set the screen's backlight: ON | OFF | TOGGLE | OPEN | BLINK | FLASH."""
		self.backlight = backlight
		self.lcd.send_command('screen_set',str(self.id),'-backlight',self.backlight)

	def set_duration(self,duration):
		"""Set the screen's display duration in 8ths of a second."""
		self.duration = duration
		self.lcd.send_command('screen_set',str(self.id),'-duration',str(self.duration))

	def set_timeout(self,timeout):
		"""Set the screen's timeout in 8ths of a second."""
		self.timeout = timeout
		self.lcd.send_command('screen_set',str(self.id),'-timeout',str(self.timeout))

	def set_cursor(self,cursor):
		"""Set the screen's cursor: ON | OFF | UNDER | BLOCK."""
		self.cursor = cursor
		self.lcd.send_command('screen_set',str(self.id),'-cursor',self.cursor)

	def set_cursor_x(self,cursor_x):
		"""Set the cursor's X coordinate."""
		self.cursor_x = cursor_x
		self.lcd.send_command('screen_set',str(self.id),'-cursor_x',str(self.cursor_x))

	def set_cursor_y(self,cursor_y):
		"""Set the cursor's Y coordinate."""
		self.cursor_y = cursor_y
		self.lcd.send_command('screen_set',str(self.id),'-cursor_y',sstr(elf.cursor_y))

	def _add_widget(self,type,parent_frame):
		id = 0
		while (self.widgets.has_key(id)):
			id += 1
		if (type == STRING):
			newwidget = widget_string(self,id,parent_frame)
		elif (type == TITLE):
			newwidget = widget_title(self,id,parent_frame)
		elif (type == HBAR):
			newwidget = widget_hbar(self,id,parent_frame)
		elif (type == VBAR):
			newwidget = widget_vbar(self,id,parent_frame)
		elif (type == ICON):
			newwidget = widget_icon(self,id,parent_frame)
		elif (type == SCROLLER):
			newwidget = widget_scroller(self,id,parent_frame)
		elif (type == FRAME):
			newwidget = widget_frame(self,id,parent_frame)
		elif (type == NUM):
			newwidget = widget_num(self,id,parent_frame)
		self.widgets[id] = newwidget
		return newwidget

	def widget_add(self,type):
		"""Add a new widget.

		Returns a widget_* object.
		Type can be: STRING | TITLE | HBAR | VBAR | ICON | SCROLLER | FRAME | NUM"""
		return self._add_widget(type,None)
	
	def _del_widget(self,widget):
		if (self.widgets[widget.id] != widget):
			raise Exception	# Eek, not the same widget!
		del self.widgets[widget.id]
	
	def listen(self):
		print 'Got listen event'
	
	def ignore(self):
		print 'Got ignore event'


class menu:
	def _parentstring(self):
		if (self.parent != None):
			return str(id(self.parent))
		else:
			return ''
	
	def _set_init(self,key,default,func):
		self.data[key] = default
		self.set_funcs.append({'func': func, 'default': default, 'key': key})
		

	def __init__(self):
		self.data = {}
		self.lcd = None
		self.parent = None
		self.set_funcs = []
		self._set_init('text','',self.__set_text)
		self._set_init('hidden','0',self.__set_hidden)
		self._set_init('next',None,self.__set_next)
		self._set_init('prev',None,self.__set_prev)

	def _add(self,lcd,parent):
		self.lcd = lcd
		self.parent = parent
		self.lcd.send_command('menu_add_item',self._parentstring(),id(self),self.type,'')
		for i in self.set_funcs:
			key = i['key']
			if (i['default'] != self.data[key]):
				i['func']()

	def _del(self):
		if (self.parent != None):
			_parentstring = str(self.parent.id)
		else:
			_parentstring = ''
		self.lcd.send_command('menu_del_item',self._parentstring(),id(self))
		self.lcd = None
		self.parent = None
	
	def __del__(self):
		pass

	def __set_text(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-text',self.data['text'])
	
	def set_text(self,text):
		self.data['text'] = text
		self.__set_text()

	def __set_hidden(self):
		if (self.lcd != None):
			if (self.data['hidden']):
				opt = 'true'
			else:
				opt = 'false'
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-is_hidden',opt)
	
	def set_hidden(self,boolean):
		self.data['hidden'] = boolean
		self.__set_hidden()

	def __set_next(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-next',id(self.data['next']))
	
	def set_next(self,next_menu):
		self.data['next'] = next_menu
		self.__set_next()

	def __set_prev(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-prev',id(self.data['prev']))
	
	def set_prev(self,prev_menu):
		self.data['prev'] = prev_menu
		self.__set_prev()
	
	def event_enter(self,value):
		print 'Enter event:',value

	def event_leave(self,value):
		print 'Leave event:',value


class menu_action(menu):
	def __init__(self):
		self.type = ACTION
		menu.__init__(self)
		self._set_init('result',NONE,self.__set_result)

	def __set_result(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-menu_result',self.data['result'])

	def set_result(self,action):
		"""Set an action: NONE | CLOSE | QUIT."""
		self.data['result'] = action
		self.__set_result()
	
	def event_select(self,value):
		print 'Select event:',value


class menu_checkbox(menu):
	def __init__(self):
		self.type = CHECKBOX
		menu.__init__(self)
		self._set_init('value',OFF,self.__set_value)
		self._set_init('allow_grey',0,self.__set_allow_grey)

	def __set_value(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-value',self.data['value'])

	def set_value(self,value):
		"""Set the value: ON | OFF | GREY."""
		self.data['value'] = value
		self.__set_value()

	def __set_allow_grey(self):
		if (self.lcd != None):
			if (self.data['allow_grey']):
				opt = 'true';
			else:
				opt = 'false';
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-value',opt)
		
	def set_allow_grey(self,boolean):
		"""Set the value: TRUE | FALSE."""
		self.data['allow_grey'] = boolean
		self.__set_allow_grey()
	
	def event_update(self,value):
		print 'Update event:',value


class menu_ring(menu):
	def __init__(self):
		self.type = RING
		menu.__init__(self)
		self._set_init('value',0,self.__set_value)
		self._set_init('strings',[],self.__set_strings)

	def __set_value(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-value',self.data['value'])
	
	def set_value(self,value):
		"""Set the index of the selected string."""
		self.data['value'] = value
		self.__set_value()

	def __set_strings(self):
		if (self.lcd != None):
			tab_delimited = join(self.data['strings'],'\t')
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-strings',tab_delimited)

	def set_strings(self,strings):
		"""Set the strings from a list."""
		self.data['strings'] = strings
		self.__set_strings()

	def event_update(self,value):
		print 'Update event:',value


class menu_slider(menu):
	def __init__(self):
		self.type = SLIDER
		menu.__init__(self)
		self._set_init('value',0,self.__set_value)
		self._set_init('mintext','',self.__set_mintext)
		self._set_init('maxtext','',self.__set_maxtext)
		self._set_init('minvalue',0,self.__set_minvalue)
		self._set_init('maxvalue',100,self.__set_maxvalue)
		self._set_init('stepsize',1,self.__set_stepsize)

	def __set_value(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-value',self.data['value'])
	
	def set_value(self,value):
		"""Set the current value."""
		self.data['value'] = value
		self.__set_value()

	def __set_mintext(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-mintext',self.data['mintext'])
	
	def set_mintext(self,value):
		self.data['mintext'] = value
		self.__set_mintext()

	def __set_maxtext(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-maxtext',self.data['maxtext'])
	
	def set_maxtext(self,value):
		self.data['maxtext'] = value
		self.__set_maxtext()

	def __set_minvalue(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-minvalue',self.data['minvalue'])
	
	def set_minvalue(self,value):
		self.data['minvalue'] = value
		self.__set_minvalue()

	def __set_maxvalue(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-maxvalue',self.data['maxvalue'])
	
	def set_maxvalue(self,value):
		self.data['maxvalue'] = value
		self.__set_maxvalue()

	def __set_stepsize(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-stepsize',self.data['stepsize'])
	
	def set_stepsize(self,value):
		self.data['stepsize'] = value
		self.__set_stepsize()

	def event_plus(self,value):
		print 'Plus event:',value
	
	def event_minus(self,value):
		print 'Minus event:',value



class menu_numeric(menu):
	def __init__(self):
		self.type = NUMERIC
		menu.__init__(self)
		self._set_init('value',0,self.__set_value)
		self._set_init('minvalue',0,self.__set_minvalue)
		self._set_init('maxvalue',100,self.__set_maxvalue)

	def __set_value(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-value',self.data['value'])
	
	def set_value(self,value):
		"""Set the current value."""
		self.data['value'] = value
		self.__set_value()

	def __set_minvalue(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-minvalue',self.data['minvalue'])
	
	def set_minvalue(self,value):
		self.data['minvalue'] = value
		self.__set_minvalue()

	def __set_maxvalue(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-maxvalue',self.data['maxvalue'])
	
	def set_maxvalue(self,value):
		self.data['maxvalue'] = value
		self.__set_maxvalue()


	def event_update(self,value):
		print 'Update event:',value


class menu_alpha(menu):
	def __init__(self):
		self.type = ALPHA
		menu.__init__(self)
		self._set_init('value','',self.__set_value)
		self._set_init('password_char','',self.__set_password_char)
		self._set_init('minlength',0,self.__set_minlength)
		self._set_init('maxlength',10,self.__set_maxlength)
		self._set_init('allow_caps',1,self.__set_allow_caps)
		self._set_init('allow_noncaps',0,self.__set_allow_noncaps)
		self._set_init('allow_numbers',0,self.__set_allow_numbers)
		self._set_init('allowed_extra_string','',self.__set_allowed_extra_string)

	def __set_value(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-value',self.data['value'])
	
	def set_value(self,value):
		"""Set the current value."""
		self.data['value'] = value
		self.__set_value()

	def __set_minlength(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-minlength',self.data['minlength'])
	
	def set_minlength(self,value):
		self.data['minlength'] = value
		self.__set_minlength()

	def __set_maxlength(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-maxlength',self.data['maxlength'])
	
	def set_maxlength(self,value):
		self.data['maxlength'] = value
		self.__set_maxlength()


	def __set_allow_caps(self):
		if (self.lcd != None):
			if (self.data['allow_caps']):
				opt = 'true'
			else:
				opt = 'false'
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-allow_caps',opt)

	def set_allow_caps(self,boolean):
		"""Set: TRUE | FALSE."""
		self.data['allow_caps'] = boolean
		self.__set_allow_caps()

	def __set_allow_noncaps(self):
		if (self.lcd != None):
			if (self.data['allow_noncaps']):
				opt = 'true'
			else:
				opt = 'false'
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-allow_noncaps',opt)

	def set_allow_noncaps(self,boolean):
		"""Set: TRUE | FALSE."""
		self.data['allow_noncaps'] = boolean
		self.__set_allow_noncaps()

	def __set_allow_numbers(self):
		if (self.lcd != None):
			if (self.data['allow_numbers']):
				opt = 'true'
			else:
				opt = 'false'
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-allow_numbers',opt)

	def set_allow_numbers(self,boolean):
		"""Set: TRUE | FALSE."""
		self.data['allow_numbers'] = boolean
		self.__set_allow_numbers()

	def set_allow_extra(self,value):
		self.data['allow_extra'] = value
		self.__set_allow_extra()

	def __set_allow_extra(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-allow_extra',self.data['allow_extra'])
	
	def set_allow_extra(self,value):
		self.data['allow_extra'] = value
		self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-allow_extra',self.data['allow_extra'])

	def event_update(self,value):
		print 'Update event:',value


class menu_ip(menu):
	def __init__(self):
		self.type = IP
		menu.__init__(self)
		self._set_init('value','',self.__set_value)
		self._set_init('v6',0,self.__set_v6)

	def __set_value(self):
		if (self.lcd != None):
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-value',self.data['value'])
	
	def set_value(self,value):
		"""Set the current value."""
		self.data['value'] = value
		self.__set_value()

	def __set_v6(self):
		if (self.lcd != None):
			if (self.data['v6']):
				opt = 'true'
			else:
				opt = 'false'
			self.lcd.send_command('menu_set_item',self._parentstring(),id(self),'-v6',opt)

	def set_v6(self,boolean):
		"""Set: TRUE | FALSE."""
		self.data['v6'] = boolean
		self.__set_v6()


class menu_menu(menu):
	def __init__(self):
		self.type = MENU
		self.menus = {}
		menu.__init__(self)

	def __del__(self):
		menus = self.menus.values()
		for i in menus:
			self.menu_del_item(i)
		menu.__del__(self)
	
	def menu_add_item(self,menu):
		"""Add a new sub-menu item."""
		self.menus[str(id(menu))] = menu
		self.lcd.allmenus[str(id(menu))] = menu
		menu._add(self.lcd,self)

	def menu_del_item(self,menu):
		"""Delete a sub-menu item."""
		del self.menus[str(id(menu))]
		del self.lcd.allmenus[str(id(menu))]




class lcd:
	"""Interface class for controlling lcdproc's LCDd."""

	def run_events(self):
		old_commands_before_flush = self.commands_before_flush
		self.commands_before_flush = 1
		if (self.expected_successes > 0):
			self.flush_successes()
		while (len(self.queued_events) > 0):
			i = self.queued_events.pop(0)
			response = i.split(' ')
			resplen = len(response);
			if (resplen >= 1):
				if (response[0] == 'listen'):
					id = string.atoi(response[1])
					if (self.screens.has_key(id)):
						self.screens[id].listen()
				elif (response[0] == 'ignore'):
					id = string.atoi(response[1])
					if (self.screens.has_key(id)):
						self.screens[id].ignore()
				elif (response[0] == 'key'):
					id = string.atoi(response[1])
					if (self.keys.has_key(id)):
						self.keys[id].event()
				elif (response[0] == 'menuevent'):
					type = response[1]
					try:
						id = response[2]
					except:
						id = None
					if (resplen > 3):
						value = response[3]
					else:
						value = None
					menu = None
					if (id != None):
						if (self.allmenus.has_key(id)):
							menu = self.allmenus[id]
					else:
						menu = self
					if (menu != None):
						if (type == 'select'):
							menu.event_select(value)
						elif (type == 'update'):
							menu.event_update(value)
						elif (type == 'plus'):
							menu.event_plus(value)
						elif (type == 'minus'):
							menu.event_minus(value)
						elif (type == 'enter'):
							menu.event_enter(value)
						elif (type == 'leave'):
							menu.event_leave(value)
		self.commands_before_flush = old_commands_before_flush

	def get_data(self):
		"""Returns the next line of data from LCDd."""
		data = self.sock.recv(1024)
		data = data.split('\n')
		if (len(data) <= 0):
			return []
		partiallen = len(self.partial_data)
		if (partiallen > 0):
			self.partial_data[partiallen - 1] += data.pop(0)
		self.partial_data.extend(data)
		
		retdata = []
		while (len(self.partial_data) > 1):
			i = self.partial_data.pop(0)
			response = i.split(' ')
			resplen = len(response);
			if (resplen >= 1):
				if ((response[0] == 'listen') or (response[0] == 'ignore') or (response[0] == 'key') or (response[0] == 'menuevent')):
					self.queued_events.append(i)
					continue
			retdata.append(i)

		return retdata
					
	def flush_successes(self):
		while (self.expected_successes > 0):
			data = None
			while (data == None):
				data = self.get_data()
				for i in data:
					if (i != 'success'):
						print 'LCDd returned:',i
						raise Exception
					self.expected_successes -= 1
		self.run_events()
	
	def send_command(self,command,*params):
		"""Sends a string to the LCD and expects "success" back in response."""
		for i in params:
			command += ' "'+str(i).replace('\\','\\\\').replace('"','\\"')+'"'
		self.sock.send(command+'\n')
		self.expected_successes += 1
		if (self.expected_successes >= self.commands_before_flush):
			self.flush_successes()
	
	def __init__(self,client_name,host,port):
		"""Connects to the LCDd process on localhost."""
		self.screens = {}
		self.keys = {}
		self.menus = {}
		self.allmenus = {}
		self.expected_successes = 0
		self.commands_before_flush = 1
		self.partial_data = []
		self.queued_events = []
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except:
			self.sock = None
			raise Exception
		try:
			self.sock.connect((host,port))
			self.sock.send('hello')
			data = self.sock.recv(1024)
			data = data.strip()
			response = data.split(' ')
			resplen = len(response);
			if ((resplen < 1) or (response[0] != 'connect')):
				print 'LCDd returned',data
				raise Exception
			i = 1
			while (i < resplen):
				if (response[i] == 'LCDproc'):
					i += 1
					self.lcdproc_version = response[i]
				elif (response[i] == 'protocol'):
					i += 1
					self.lcdproc_protocol = response[i]
				elif (response[i] == 'wid'):
					i += 1
					self.width = response[i]
				elif (response[i] == 'hgt'):
					i += 1
					self.height = response[i]
				elif (response[i] == 'cellwid'):
					i += 1
					self.cellwidth = response[i]
				elif (response[i] == 'cellhgt'):
					i += 1
					self.cellheight = response[i]
				i += 1
			self.send_command('client_set -name',client_name)
		except:
			self.sock.close()
			raise
	
	def __del__(self):
		del self.screens
		del self.keys
		menus = self.menus.values()
		for i in menus:
			self.menu_del_item(i)

		try:
			self.sock.close()
		except:
			pass
	
	def screen_add(self):
		"""Add a new screen.

		Returns a screen object."""
		id = 0
		while (self.screens.has_key(id)):
			id += 1
		newscreen = screen(self,id)
		self.screens[id] = newscreen
		return newscreen

	def _del_screen(self,screen):
		if (self.screens[screen.id] != screen):
			raise Exception	# Eek, not the same screen!
		del self.screens[screen.id]

	def client_add_key(self,keyname,excl,callback):
		"""Ask the server for notifications of a key press.

		excl can be: EXCLUSIVE | SHARED
		
		When the key is pressed, callback.event() will be called"""
		self.send_command('client_add_key -'+excl+'',keyname)
		self.keys[keyname] = callback
	
	def client_del_key(self,key):
		"""Ask the server not to send notifications of a key press."""
		self.send_command('client_del_key',key)
		del self.keys[keyname]

	def menu_add_item(self,menu):
		"""Add a new menu item at the top level."""
		self.menus[str(id(menu))] = menu
		self.allmenus[str(id(menu))] = menu
		menu._add(self,None)

	def menu_del_item(self,menu):
		"""Delete a menu item at the top level."""
		del self.menus[str(id(menu))]
		del self.allmenus[str(id(menu))]

	def menu_goto(self,menu):
		self.send_command('menu_goto',str(menu.id))
		
	def menu_set_main(self,menu):
		if (menu == None):
			menstr = ''
		else:
			menstr = str(menu.id)
		self.send_command('menu_set_main',menstr)
	
	def set_backlight(self,backlight):
		"""Set the screen's backlight: ON | OFF | TOGGLE | OPEN | BLINK | FLASH."""
		self.backlight = backlight
		self.send_command('backlight',self.backlight)
		
	def set_output(self,output):
		"""Set the GPIO outputs"""
		self.output = output
		self.send_command('output',str(self.output))

	def event_enter(self,value):
		print 'Enter top menu event:',value

	def event_leave(self,value):
		print 'Leave top menu event:',value

