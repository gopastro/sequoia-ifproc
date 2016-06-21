#!/usr/bin/python

import sys
try:
    import CORBA
except ImportError:
    sys.path.insert(0, '/usr/local/omniORB-4.1.3/x86-linux/lib/python2.5/site-packages')
    import CORBA
import SequoiaDataModule
import time

class SequoiaChopper(object):
    def __init__(self):
        self.sequoia = None
        self.setup_corba()
        
    def setup_corba(self):
        orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)
        obj = orb.string_to_object("corbaloc:iiop:rs-ppc1:1099/Sequoia")
        self.sequoia = obj._narrow(SequoiaDataModule.SequoiaDataORB)
        if self.sequoia is None:
            raise Exception("CORBA Error", "Object reference is None")
        print "SEQUOIA initialized: %s" % self.sequoia.getObjectName()

    def get_chopper_status(self):
        if self.sequoia.getChopperStatus() == 0x3:
            print "Chopper is out"
            return 0
        else:
            print "Chopper is in"
            return 1
    
    def chopper_in(self):
        self.sequoia.setChopperCommand(1)
        print "Moving chopper in"
        time.sleep(1.)
        if self.get_chopper_status() != 1:
            raise Exception("Chopper Error", "Chopper not moving in")

    def chopper_out(self):
        self.sequoia.setChopperCommand(0)
        print "Moving chopper out"
        time.sleep(1.)
        if self.get_chopper_status() != 0:
            raise Exception("Chopper Error", "Chopper not moving out")


        


