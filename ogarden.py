#!/usr/bin/env python
# Copyright (C) 2011 Enrico Rossi
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

""" Python-OpenGarden module API

This module contains the python API to an opengarden device.
"""
__author__ = "Enrico Rossi <e.rossi@tecnobrain.com>"
__date__ = "27 October 2011"
__version__ = "$Revision: 0.1b $"
__credits__ = """Nicola Galliani, the "On the field" beta tester.
Andrea Marabini, the electronic designer.
Alessandro Dotti Contra, GUI developer.
"""

import serial

class OpenGarden:
    """
    The basic class definition

    Some usefull docs.

    Examples:

    myobj = OpenGarden       # define the object
    myobj.connect()          # connect to the device.
    print myobj.id           # print the id.
    og.load()
    print og.sunsite         # print the sunsite attribute.
    for i in og.programs:
        print i
    og.disconnect()
    del(og)

    Formats:
    - self.programs = [(1530,30,0xff,1), (1600,45,0x10,2)]
    - self.sunsite is device phisical installation where:
        0 is shadowed site.
        1 half-sun site.
        2 full-sun site.

    Known Bugs:
    - Serial port must not be hardcoded here.
    - self.id name is too common, change it to something else.
    """

    _s = serial.Serial()
    _s.port = '/tmp/COM1'
    _s.baudrate = 9600
    _s.bytesize = 8
    _s.parity = 'N'
    _s.stopbits=1
    _s.timeout = 10

    id = None
    programs = None
    sunsite = None

    def _sendcmd(self, cmd):
        """
        Send the command to the serial port one char at a time.

        Keyword arguments:
        cmd -- the command string to send.
        """

        self._s.flushInput()

        for i in cmd[:]:
            self._s.write(i)
            j = self._s.read()

            if i != j:
                print "Error RX"

    def _id(self):
        """
        Get the id of a device connected.
        """
        
        self._sendcmd("v\n")
        idt = self._s.readline()
    
        if idt[:10] == 'OpenGarden':
            return(idt[11:])
        else:
            return(None)
    
    def _save_sunsite(self):
        """ Send the sunsite value to the device.

        Note: It does not save the value in the EEPROM,
        just in RAM.
        """

        self._sendcmd("y" + str(self.sunsite) + "\n")
        ok = self._s.readline()
    
        if ok == 'OK':
            return(True)
        else:
            return(False)

    def _load_sunsite(self):
        """ Load the sunsite value from the device.

        Note: It takes the value from the RAM not from
        the EEPROM.
        """
        self._sendcmd("y\n")
        self.sunsite = self._s.readline()
        self.sunsite = self.sunsite[0]
    
    def _send_eepromload_cmd(self):
        """ Restore the EEPROM memory to RAM of the device.
        """
        pass

    def _load_programs(self):
        """ Read the programs in RAM from the device. """

        if self.programs is None:
            self.programs = [(1530,30,0xff,1), (1600,45,0x10,2)]

    def _save_programs(self):
        """ Store the programs in the device's RAM """
        pass

    def _send_eepromsave_cmd(self):
        """ Write the RAM contents to EEPROM of the device. """
        pass

    def connect(self):
        """
        Connect to the device and set the device id. 
        """

        self._s.open()
        self.id = self._id()
    
    def disconnect(self):
        """
        Close the connection.
        """
        self._s.close()

    def time(self, t=None):
        """
        Get or set the time of the device.

        Keyword arguments:
            t -- time_t value of the updated timer.

        Example:
            print og.time()     # print the time (format time_t)
            og.time(1319724362) # set the time to 2011-10-27 04:06:02 PM
        """
        
        if t is None:
            cmd = "d\n"
        else:
            cmd = "d" + str(t) + "\n"
        
        self._sendcmd(cmd)
        idt = self._s.readline()
        return(idt.strip())

    def load(self):
        """
        loads programs and sunsite attributes from the device.
        """

        self._send_eepromload_cmd()
        self._load_sunsite()
        self._load_programs()
        
    def save(self):
        """
        save programs and sunsite attributes to the device.
        """

        self._save_programs()
        self._save_sunsite()
        self._send_eepromsave_cmd()

    def temperature(self):
        """
        Read the temperature from the device's thermometer.

        Example:
            print og.temperature()
        """

        self._sendcmd("g\n")
        temp = self._s.readline()
        return(temp.strip())

if __name__ == "__main__":
    og = OpenGarden()
    og.connect()

    if og.id is None:
        print "No Open Garden device connected or problems!"
    else:
        print "The id is:" + og.id

    print "the temperature is: "
    print og.temperature()

    print "the time is:"
    print og.time()

    print "set the time to 123 sec. from the epoch"
    print og.time(123)

    print "load programs from the device"
    og.load()
    print "the sunsite is:"
    print og.sunsite
    print "programs loaded:"

    for i in og.programs:
        print i

    print "disconnecting the device"
    og.disconnect()
    del(og)
    
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
