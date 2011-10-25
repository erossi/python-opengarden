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
    programs = None
    sunsite = None

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
    
    def _save_sunsite(self):
        """ Send the sunsite value to the device.

        Note: It does not save the value in the EEPROM,
        just in RAM.
        """

        self._sendcmd("y" + str(self.sunsite) + "\r")
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
        if self.sunsite is None:
            self.sunsite = 1

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
        return(idt.strip())

    def load(self):
        """ load the programs from the device """
        self._send_eepromload_cmd()
        self._load_sunsite()
        self._load_programs()
        
    def save(self):
        """ save the programs to the device """
        self._save_programs()
        self._save_sunsite()
        self._send_eepromsave_cmd()

    def temperature(self):
        """ Read the temperature from the device. """

        self._sendcmd("g\r")
        temp = self._s.readline()
        return(temp.strip())

if __name__ == "__main__":
    og = OpenGarden()
    og.connect()

    if og.id is None:
        print "No Open Garden device connected or problems!"
    else:
        print "The id is:" + og.id

    print "the time is:"
    print og.time()

    print "set the time to 123 sec. from the epoch"
    print og.time(123)

    print "the temperature is: "
    print og.temperature()

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
