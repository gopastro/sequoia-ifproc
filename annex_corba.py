# CORBA imports
import CORBA
import sys
import IfprocDataModule
import numpy
import time

class IFProcAnnex(object):
    def __init__(self):
        self.ifproc = None
        self.setup_corba()
        self.atten = {}
	self.lpf = {}

    def setup_corba(self):
        orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)
        obj = orb.string_to_object("corbaloc:iiop:rs-ppc1:1099/Ifproc")
        self.ifproc = obj._narrow(IfprocDataModule.IfprocDataORB)
        if self.ifproc is None:
            raise Exception("CORBA Error", "Object reference is None")
        print "%s initialized" % self.ifproc.getObjectName()

    def set_atten(self, atten, chan):
        self.ifproc.setAnnexAttenuatorIndexed(atten, chan)
        self.atten[chan] = atten
        time.sleep(0.1)

    def set_lpf(self, fil, chan):
	self.ifproc.setAnnexLpfIndexed(fil, chan)
	self.lpf[chan] = fil
	time.sleep(0.1)

    def get_lpf(self, chan):
	filt = self.ifproc.getAnnexLpfIndexed(chan)
	self.lpf[chan] = filt
	return filt

    def get_atten(self, chan):
        att = self.ifproc.getAnnexAttenuatorIndexed(chan)
        self.atten[chan] = att
        return att

    def get_voltage(self, chan):
        return self.ifproc.getAnnexVoltsIndexed(chan)

    def get_avg_voltage(self, chan, nmeas=5):
        voltages = numpy.zeros(nmeas, dtype='float')
        for i in xrange(nmeas):
            voltages[i] = self.get_voltage(chan)
            time.sleep(0.2)
        return voltages.mean()

    #def get_rawlevel(self, chan):
    #    return self.ifproc.getPlatformRawLevelIndexed(chan)

    def get_level(self, chan):
        return self.ifproc.getAnnexRawLevelIndexed(chan)

    def get_all_atten(self):
        all_att = self.ifproc.getAnnexAttenuator()
        self.atten = dict((i, all_att[i]) for i in range(len(all_att)))

    #def set_all_CO(self, value):
    #    if value in (0, 1):
    #        allCO = [value] * 32
    #        self.ifproc.setPlatformCoFilter(allCO)
    
    #def get_all_CO(self):
    #    return numpy.array(self.ifproc.getPlatformCoFilter())

    #def get_all_voltages(self):
    #    return numpy.array(self.ifproc.getPlatformVolts())

    #def get_all_rawlevels(self):
    #   return numpy.array(self.ifproc.getPlatformRawLevel())

    def get_all_levels(self):
        return numpy.array(self.ifproc.getAnnexIfLevel())
    
    
