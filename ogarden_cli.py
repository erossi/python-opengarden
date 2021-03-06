#!/usr/bin/env python
# Copyright (C) 2011-2014 Enrico Rossi
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
parser.add_argument('--get-programs', type=argparse.FileType('w'), \
        metavar="<filename>", \
        help="Download device's programs to file.")
parser.add_argument('--send-programs', type=argparse.FileType('r'), \
        metavar="<filename>", \
        help="Use the file to program the device.")
parser.add_argument('--get-time', action='store_true', \
        help="Print the abstime from the device connected.")
parser.add_argument('--set-time', type=long, \
        metavar="<seconds>", \
        help="Set the abstime to the device connected.")
parser.add_argument('--alarm', action='store_true', \
        help="Print the alarm's lines status (ON/OFF).")
parser.add_argument('--alarm-level', nargs='?', const='get', \
        metavar="HIGH/LOW", help="get/set alarm trigger level.")
parser.add_argument('--get-version', action='store_true', \
        help="get the device's firmware version.")
parser.add_argument('--led', nargs='?', const='get', metavar="ON/OFF", \
        help="get/set led.")
parser.add_argument('--sunsite', nargs='?', const='get', \
        metavar="0..2", \
        help="get/set sunsite value where 0 is Full sun, 1 is Half sun \
        and 2 is Shadow.")
parser.add_argument('--temperature', action='store_true', \
        help="print the device's temperature.")
parser.add_argument('--queue', action='store_true', \
        help="Print the queue list.")
parser.add_argument('--valve', nargs='?', const='get', \
        metavar="monostable/bistable", help="get/set valve type.")
parser.add_argument('--device', default='/dev/ttyUSB0', required=True, \
        help="ex. /dev/ttyUSB0 or /dev/ttyS0")
args = parser.parse_args()

og = OpenGarden()
og.connect(args.device)

if og.version is None:
    print "No Open Garden device connected or problems!"
    raise "no device found error"
else:
    og.load()
    print "Open garden device found."
    print "Serial number:", og.serial
    print "Software version:", og.version

if args.temperature:
    temperature = og.temperature()
    print "temperature is: " + temperature[0]
    print "media 24h is: " + temperature[1]
    print "dfactor is: " + temperature[2]

if args.sunsite:
    if args.sunsite == 'get':
        print "susite setup to: " + og.rt_load_sunsite()
    elif args.sunsite in ('0', '1', '2'):
        og.rt_save_sunsite(args.sunsite)
        print "set sunsite to: " + og.rt_load_sunsite()
    else:
        print "Error: Sunsite value can be only 0, 1, 2!"

if args.valve:
    if args.valve == 'get':
        print "valve type is : " + og.rt_load_valve()
    elif args.valve in ("monostable", "bistable"):
        og.rt_save_valve(args.valve)
        print "set valve type to: " + og.rt_load_valve()
    else:
        print "Error: Valve type can be only monostable or bistable"

if args.alarm_level:
    if args.alarm_level == 'get':
        print "trigger level is: " + og.rt_load_alarm_level()
    elif args.alarm_level in ("HIGH", "LOW"):
        og.rt_save_alarm_level(args.alarm_level)
        print "set trigger level to: " + og.rt_load_alarm_level()
    else:
        print "Error: Alarm level can be only HIGH or LOW!"

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
    elif args.led in ("ON", "OFF"):
        og.rt_save_led_setup(args.led)
        print "Led setup to: " + og.rt_load_led_setup()
    else:
        print "Led can be only ON or OFF"

print "disconnecting the device"
og.disconnect()
del(og)
del(parser)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
