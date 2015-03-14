#!/usr/bin/python
# Copyright (C) 2011-2015 Alessandro Dotti Contra <alessandro@hyboria.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" OpenGarden GUI Progam module.

This is a support module for the python OpenGarden GUI.
This module is part of the OpenGarden project.
"""

class program:
	"""
	This class implements a program the way it is used by OpenGarden GUI
	and OpenGarden appliance.
	"""

	_start	= "0000"	#Start time: the first two digits represent the hour
						#and the second two digits the minutes. The default
						#is midnight
	
	_length	= 0			#Lenght of the program in minutes (one minute by
						#default)

	_line	= 0			#Line which this program will work on.

	_days	= ()		#Days on which the program will run.

	def __init__(self):
		"""
		Default program initialization.

		Example: program = program()

		Create a meaningless program with default values, which are:
		start: 00:00
		length: 0 minutes
		line: 0
		days: none
		"""
		pass

	def startTime(self,time=None):
		"""
		Read or set program's start time.

		Examples:
			program.startTime()
			program.startTime('0130')
		"""
		if time:
			self._start = time
		else:
			return self._start

	def length(self,minutes=None):
		"""
		Read or set program's length in minutes.

		Examples:
			program.length()
			program.length(60)
		"""
		if minutes:
			self._length = minutes
		else:
			return self._length

	def line(self,line=None):
		"""
		Read or set the line on which the program will run.
		Line number is an integer.

		Examples:
			program.line()
			program.line(3)
		"""
		if line:
			self._line = line
		else:
			return self._line

	def days(self,days=None):
		"""
		Read or set the days on which the program will run.
		Days is an list.

		Examples:
			program.line()
			program.line(('mon','thu'))
		"""
		if days:
			self._days = days
		else:
			return self._days

	def asString(self):
		"""
		Prints program's data as a formatted string.

		Examples:
			program.asString()
		"""
		string = _("%s (%3s) - line %s ") % (self._start, self._length, self._line)
		string += "[ "
		for day in self._days:
			string += "%s " % (day)
		string += "]"
		return string


if __name__ == '__main__':
	
	print "Testing program class."

	program = program()

	print "===> Setting start time to 01:30"
	program.startTime('0130')
	print 'OK' if program.startTime() == '0130' else 'FAILED!!!'

	print "===> Setting length to 01:00"
	program.length(60)
	print 'OK' if program.length() == 60 else 'FAILED!!!'

	print "===> Setting line to 3"
	program.line(3)
	print 'OK' if program.line() == 3 else 'FAILED!!!'

	print "===> Setting day to mon and thu"
	program.days(('mon','thu'))
	print 'OK' if program.days() == ('mon','thu') else 'FAILED!!!'

	print "===> Printing data as string:"
	print program.asString()
