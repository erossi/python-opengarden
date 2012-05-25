#!/usr/bin/env python
# Copyright (C) 2011, 2012 Enrico Rossi
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

""" OpenGarden command line interface

This is the command line interface to the Open Garden device.
"""
__author__ = "Enrico Rossi <e.rossi@tecnobrain.com>"
__date__ = "23 January 2011"
__version__ = "$Revision: 0.2a $"
__credits__ = """Nicola Galliani, the "On the field" beta tester.
Andrea Marabini, the electronic designer.
Alessandro Dotti Contra, GUI developer.
"""

import argparse
import sys
from opengarden import OpenGarden

parser = argparse.ArgumentParser(description='OpenGarden CLI.')
parser.add_argument('--get-alarm-level', action='store_true', \
        help="Print the alarm's trigger level.")
parser.add_argument('--set-alarm-level', metavar="HIGHLOW", \
        help="Set the alarm's trigger level ['HIGH' or 'LOW'], \
        remeber it will not stored into the device unless \
        an upload of a program is performed.")
parser.add_argument('--get-programs', type=argparse.FileType('w'), \
        metavar="<filename>", \
        help="Download device's programs to file.")
parser.add_argument('--send-programs', type=argparse.FileType('r'), \
        metavar="<filename>", \
        help="Use the file to program the device.")
parser.add_argument('--get-sunsite', action='store_true', \
        help="Print the sunsite of the device.")
parser.add_argument('--set-sunsite', type=int, \
        metavar="SUNSITE", \
        help="Set the sunsite of the device, \
        remeber it will not stored into the device unless \
        an upload of a program is performed.")
parser.add_argument('--get-time', action='store_true', \
        help="Print the abstime from the device connected.")
parser.add_argument('--set-time', type=long, \
        metavar="<seconds>", \
        help="Set the abstime to the device connected.")
parser.add_argument('--get-valve', action='store_true', \
        help="Print the valve type of the device.")
parser.add_argument('--set-valve', metavar="VALVETYPE", \
        help="Set the valve type of the device ['monostable or 'bistable'], \
        remeber it will not stored into the device unless \
        an upload of a program is performed.")
parser.add_argument('--alarm', action='store_true', \
        help="Print the alarm's lines status (ON/OFF).")
parser.add_argument('--get-version', action='store_true', \
        help="get the device's firmware version.")
parser.add_argument('--led', nargs='?', const='get', metavar="ON/OFF", \
        help="get/set led.")
parser.add_argument('--temperature', action='store_true', \
        help="print the device's temperature.")
parser.add_argument('--queue', action='store_true', \
        help="Print the queue list.")
parser.add_argument('--device', default='/dev/ttyUSB0', required=True, \
        help="ex. /dev/ttyUSB0 or /dev/ttyS0")
args = parser.parse_args()

og = OpenGarden()
og.connect(args.device)

if og.id is None:
    print "No Open Garden device connected or problems!"
    raise "no device found error"
else:
    og.load()
    print "Open garden device [" + og.id + "] found."

if args.temperature:
    temperature = og.temperature()
    print "temperature is: " + temperature[0]
    print "media 24h is: " + temperature[1]
    print "dfactor is: " + temperature[2]

if args.get_sunsite:
    print "susite setup to: " + og.sunsite

if args.set_sunsite:
    og.sunsite = args.set_sunsite
    print "set sunsite to: " + str(og.sunsite)

if args.get_valve:
    print "valve type is : " + og.valve

if args.set_valve:
    og.valve = args.set_valve
    print "set valve type to: " + str(og.valve)

if args.get_alarm_level:
    print "trigger level is: " + og.alarm

if args.set_alarm_level:
    og.alarm = args.set_alarm_level
    print "set trigger level to : " + str(og.alarm)

if args.set_time:
    og.time(args.set_time)
    print "set time to: " + str(args.set_time)

if args.get_time:
    print "OG clock is: " + og.time()

if args.queue:
    print "Queue List: Not Yet Implemented"

if args.get_programs:
    if og.programs:
        # args.get_programs.open()

        for i in og.programs:
            args.get_programs.write(i)
            args.get_programs.write('\n')

        args.get_programs.close()
    else:
        print "No programs present in the device."

if args.send_programs:
    og.programs = args.send_programs.readlines()

    for i in og.programs:
        print i[3:].strip()

    og.save()
    args.send_programs.close()

if args.alarm:
    print "Alarm's lines: " + og.get_alarm()

if args.led:
    if args.led == 'get':
        print "Led setup is: " + og.rt_load_led_setup()
    elif (args.led == "ON") or (args.led == "OFF"):
        og.rt_save_led_setup(args.led)
        print "Led setup to: " + og.rt_load_led_setup()
    else:
        print "Led can be only ON or OFF"

print "disconnecting the device"
og.disconnect()
del(og)
del(parser)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
