#!/usr/bin/python

import socket

class GpibClientSocket:
    def __init__(self, host="128.119.51.8", port=7000, device='83711b'):
        self.host = host
        self.port = port
        self.device = device
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
        self.s.connect((self.host, self.port))

    def write(self, msg):
        return self.s.send("%s write %s" % (self.device, msg))

    def ask(self, msg):
        msgtxt = "%s ask %s" % (self.device, msg)
        if self.s.send(msgtxt) == len(msgtxt):
            return self.s.recv(1024)  #,socket.MSG_DONTWAIT)

    def read(self):
        return self.s.recv(1024)  #,socket.MSG_DONTWAIT)


    def set_freq(self, frequency):
        """frequency is in Hz"""
        if self.device == '8341b':
            ftxt = 'CW'
            unit_mhz = 'MZ'
            unit_ghz = 'GZ'
        else:
            ftxt = ':FREQ:CW'
            unit_mhz = 'MHZ'
            unit_ghz = 'GHZ'
        #if frequency < 1.e9:
        #    freqtext = ":FREQ:CW %.6f MHZ" % (frequency/1.e6)
        #else:
        #    freqtext = ":FREQ:CW %.6f GHZ" % (frequency/1.e9)
        if frequency < 1.e9:
            freqtext = "%s %.6f %s" % (ftxt, frequency/1.e6, unit_mhz)
        else:
            freqtext = "%s %.6f %s" % (ftxt, frequency/1.e9, unit_ghz)
        self.write(freqtext)

    def ask_freq(self):
        try:
            if self.device == '8341b':
                setfreq = float(self.ask("OK"))
            else:
                setfreq = float(self.ask(":FREQ:CW?"))
        except:
            setfreq = 0
        if setfreq:
            if setfreq>1.e9:
                return "%.6f GHz" % (setfreq/1.e9)
            else:
                return "%.6f MHz" % (setfreq/1.e6)
        else:
            return "No GPIB connection"
    

