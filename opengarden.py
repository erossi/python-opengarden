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
        2 is shadowed site.
        1 half-sun site.
        0 full-sun site.

    Known Bugs:
    - self.id name is too common, change it to something else.
    """

    _s = serial.Serial()
    _s.port = None
    _s.baudrate = 9600
    _s.bytesize = 8
    _s.parity = 'N'
    _s.stopbits = 1
    _s.timeout = 10

    id = None
    programs = None
    sunsite = None
    valve = None
    alarm = None
    led = None

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
                raise NameError('ComError')

    def _get_ok(self):
        ok = self._s.readline()

        if ok.strip() != "OK":
            raise NameError('NOOK')

    def _id(self):
        """
        Get the id of a device connected.
        """
        
        self._sendcmd("v\n")
        idt = self._s.readline()
    
        if idt[:10] == 'OpenGarden':
            self.id = idt[11:].strip()
        else:
            raise NameError('NoConnect')
    
    def _save_sunsite(self):
        """ Send the sunsite value to the device.

        Note: It does not save the value in the EEPROM,
        just in RAM.
        """

        self._sendcmd("y" + str(self.sunsite) + "\n")
        self._get_ok()
        return(True)

    def _load_sunsite(self):
        """ Load the sunsite value from the device.

        Note: It takes the value from the RAM not from
        the EEPROM.
        """
        self._sendcmd("y\n")
        self.sunsite = self._s.readline()
        self.sunsite = self.sunsite[0]
    
    def _save_valve(self):
        """
        Set the valve type into the RAM of the device.
        """

        if self.valve == 'monostable':
            cmd = "V1\n"
        else:
            cmd = "V2\n"

        self._sendcmd(cmd)
        self._get_ok()
        return(True)

    def _load_valve(self):
        """
        Load the valve type from the device RAM.
        """
        self._sendcmd("V\n")

        if (self._s.readline().find("1")) != -1:
            self.valve = 'monostable'
        else:
            self.valve = 'bistable'

    def _log_disable(self):
        """
        Disable log event.
        """

        self._sendcmd("L0\n")
        self._get_ok()

    def _load_alarm_level(self):
        """
        Load from the device the level (high, low) which triggers
        the alarm.
        """

        self._sendcmd("a\n")
        self.alarm = self._s.readline()

    def _save_alarm_level(self):
        """
        Store the alarm level to the device.
        """

        if self.alarm == "HIGH":
            self._sendcmd("aH\n")
        else:
            self._sendcmd("aL\n")

        self._get_ok()

    def _load_led_setup(self):
        """
        Load led's enable/disable (ON/OFF).
        """

        self._sendcmd("e\n")
        self.led = self._s.readline()

    def _save_led_setup(self):
        """
        Send the led setup attribute self.led to the device.
        """

        if self.led == "ON":
            self._sendcmd("e1\n")
        else:
            self._sendcmd("e0\n")

        self._get_ok()

    def _send_eepromload_cmd(self):
        """
        Restore the EEPROM memory to RAM of the device.
        """

        self._sendcmd("r\n")
        self._get_ok()

    def _load_programs(self):
        """ Read the programs in RAM from the device. """

        self._sendcmd("l\n")
        ans = self._s.readline()

        if ans[:10] != "Programs [":
            raise NameError('ErrProgNo')

        nprog = int(ans[10:12])
        self.programs = []

        for i in range(nprog):
            ans = self._s.readline().strip()
            self.programs.append(ans)

    def _save_programs(self):
        """ Store the programs in the device's RAM """

        # Clear RAM
        self._sendcmd('C\n')
        self._get_ok()

        for i in self.programs:
            self._sendcmd('p' + i[3:].strip() + '\n')

    def _send_eepromsave_cmd(self):
        """
        Write the RAM contents to EEPROM of the device.
        """

        self._sendcmd("s\n")
        self._get_ok()

    def connect(self, device):
        """
        Connect to the device and set the device id. 
        """

        if device is None:
            raise "A device MUST be given!"

        self._s.port = device
        self._s.open()
        self._log_disable()
        self._id()
        self._load_sunsite()
    
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
        self._load_valve()
        self._load_programs()
        self._load_alarm_level()
        self._load_led_setup()
        
    def save(self):
        """
        save programs and sunsite attributes to the device.
        """

        self._save_led_setup()
        self._save_alarm_level()
        self._save_programs()
        self._save_valve()
        self._save_sunsite()
        self._send_eepromsave_cmd()

    def temperature(self):
        """
        Read the temperature from the device's thermometer.

        Return:
            a list composed by the temperature [now, media 24h, dfactor]

        Example:
            print og.temperature()
        """

        self._sendcmd("g\n")
        temp = self._s.readline()
        temp = temp[12:].strip().split(',')
        return(temp)

if __name__ == "__main__":
    print "This is a module"

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
