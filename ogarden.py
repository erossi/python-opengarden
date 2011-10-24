#!/usr/bin/env python

# This file is part of OpenGarden
# Copyright (C) 2011 Enrico Rossi
#
# OpenGarden is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenGarden is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import serial

class OpenGarden:
    """
    Some usefull docs.
    """

    _s = serial.Serial()
    _s.port = '/tmp/COM1'
    _s.timeout = 10
    programs = [(1530,30,0xff,1), (1600,45,0x10,2)]

    def _sendcmd(self, cmd):
        """
        Send the command to the serial port one char at a time.
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
        
        self._sendcmd("v\r")
        idt = self._s.readline()
    
        if idt[:10] == 'OpenGarden':
            return(idt[11:])
        else:
            return(None)
    
    def connect(self):
        self._s.open()
        self.id = self._id()
    
    def disconnect(self):
        self._s.close()

    def time(self, t=None):
        """
        Get or set the time of the device.
        """
        
        if t is None:
            cmd = "d\r"
        else:
            cmd = "d" + str(t) + "\r"
        
        self._sendcmd(cmd)
        idt = self._s.readline()
        print idt.strip()

    def sunsite(self, s=None):
        """ Read or set the sunsite """
        
        pass

    def load(self):
        """ load the programs from the device """
        pass

    def save(self):
        """ save the programs to the device """
        pass

if __name__ == "__main__":
    og = OpenGarden()
    og.connect()

    if og.id is None:
        print "No Open Garden device connected or problems!"
    else:
        print "The id is:" + og.id

    print "print the time"
    og.time()
    print "set the time to 123 sec. from the epoch"
    og.time(123)

    og.disconnect()
    del(og)
    
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
