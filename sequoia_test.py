#!/usr/bin/python

from optparse import OptionParser
import sys
import datetime
from hp83711b import HP83711B
import numpy
import time

#corba class
from ifproc_corba import IFProc

def gpib_init():
    syn = HP83711B()
    if syn:
        print "Frequency: %.4f GHz; Power level: %.1f dBm; Multiplier: %d" % (syn.get_freq()/1e9, syn.get_power_level(), syn.get_mult())
        return syn

#class for multifrequency measurements 
class Sequoia(object):
    def __init__(self, frequencies, chans, syn):
        """
        frequencies is a list of frequencies
        chans is an integer array of IF channels to keep track of
        syn is a GPIB instance of the synthesizer
        """
        self.frequencies = frequencies
        self.syn = syn
        self.chans = chans
        self.ifproc = IFProc()
        
    def get_zero_offset(self):
        print "Obtaining zero offsets"
        self.zero_offsets = numpy.zeros((len(self.frequencies), 32), 
                                        dtype=float)
        raw_input("Hit Enter after turning off second IF chain > ")
        for i, freq in enumerate(self.frequencies):
            print "Setting frequency: %.4f" % freq
            self.syn.set_freq(freq*1e9)
            time.sleep(0.1)
            self.zero_offsets[i] = self.ifproc.get_all_voltages()

    def _set_optimal_attenuator(self, voltage, delta=3.0, chans=None, 
                                num_iterations=10):
        """
        Given a voltage sets the attenuator
        so that the voltage will be between voltage +/- delta
        for the specified chans
        """
        if chans is None:
            chans = self.chans
        opt_atten = {}
        for chan in chans:
            iterate = True
            inum = 0
            while iterate:
                time.sleep(0.5)  
                att = self.ifproc.get_atten(chan)
                time.sleep(0.1)
                v = self.ifproc.get_avg_voltage(chan)
                if inum == 0:
                    print "Starting atten for chan: %d is %d. Voltage: %.2f" % (chan, att, v)
                print "Chan: %d, Att: %d; Voltage: %.2f" % (chan, att, v)
                inum += 1
                if abs(v-voltage) <= delta or inum > num_iterations:
                    # let's be real sure, repeat one more time
                    time.sleep(0.2)
                    v = self.ifproc.get_avg_voltage(chan)
                    print "Chan: %d, Att: %d; Voltage: %.2f" % (chan, att, v)
                    if abs(v-voltage) <= delta or inum > num_iterations:
                        opt_atten[chan] = self.ifproc.get_atten(chan)
                        iterate = False
                else:
                    if v > 9.8:
                        # too high a voltage, first bring it down
                        new_att = att + 1
                        if new_att > 31:
                            #raise Exception("ATT", "atten needs to be greater than 31 dB for chan: %d" % chan)
                            print "\n\nAttenuator needs to be greater than 31 dB for chan %d\n\n" % chan
                            self.ifproc.set_atten(31, chan)
                            time.sleep(0.1)
                            opt_atten[chan] = self.ifproc.get_atten(chan)
                            iterate = False
                        else:
                            self.ifproc.set_atten(new_att, chan)
                    elif v < -9.8:
                        new_att = att - 1
                        if new_att < 0:
                            #raise Exception("ATT", "atten needs to be lesser than 0 dB for chan: %d" % chan)
                            print "\n\nAttenuator needs to be less than 0 dB for chan %d\n\n" % chan
                            self.ifproc.set_atten(0, chan)
                            time.sleep(0.1)
                            opt_atten[chan] = self.ifproc.get_atten(chan)
                            iterate = False
                        else:
                            self.ifproc.set_atten(new_att, chan)
                            
                    elif v > voltage:
                        # too high, let's bring it down 
                        new_att = att + 1
                        if new_att > 31:
                            #raise Exception("ATT", "atten needs to be greater than 31 dB for chan: %d" % chan)                            
                            print "\n\nAttenuator needs to be greater than 31 dB for chan %d\n\n" % chan
                            self.ifproc.set_atten(31, chan)
                            time.sleep(0.1)
                            opt_atten[chan] = self.ifproc.get_atten(chan)
                            iterate = False
                        else:
                            self.ifproc.set_atten(new_att, chan)
                    else:
                        # too little, bring it up
                        new_att = att - 1
                        if new_att < 0:
                            #raise Exception("ATT", "atten needs to be lower than 0 dB for chan: %d" % chan)
                            print "\n\nAttenuator needs to be less than 0 dB for chan %d\n\n" % chan
                            self.ifproc.set_atten(0, chan)
                            time.sleep(0.1)
                            opt_atten[chan] = self.ifproc.get_atten(chan)
                            iterate = False
                        else:
                            self.ifproc.set_atten(new_att, chan)
        return opt_atten

    def set_opt_atten(self, voltage, delta=3.0, chans=None, 
                      num_iterations=10, frequencies=None):
        raw_input("Hit Enter after putting in hot load for optimal attenuator measurement > ")
        if frequencies is None:
            frequencies = self.frequencies
        if chans is None:
            chans = self.chans
        self.optimal_attenuation = numpy.zeros((len(frequencies),
                                                len(chans)),
                                               dtype='int')
        for i, freq in enumerate(frequencies):
            print "Setting optimal attenuation for freq = %.2f GHz" % freq
            self.syn.set_freq(freq*1e9)
            if freq < 8.0:
                # turn on CO filter
                print "Setting CO filter on"
                self.ifproc.set_all_CO(1)
            else:
                self.ifproc.set_all_CO(0)
            time.sleep(0.5)
            opt_att = self._set_optimal_attenuator(voltage, delta, 
                                                   chans=chans,
                                                   num_iterations=num_iterations)
            self.optimal_attenuation[i] = [opt_att[c] for c in chans]
            print
            print

    def _get_voltages(self, frequencies=None, chans=None,
                     label='Offset'):
        if not hasattr(self, 'optimal_attenuation'):
            raise Exception('ATT', 'First run set_opt_atten first')
        if frequencies is None:
            frequencies = self.frequencies
        if chans is None:
            chans = self.chans
        voltages = numpy.zeros((len(frequencies), 
                                len(chans)),
                               dtype=float)
        raw_input("Hit Enter after getting ready for %s measurement > " % label)
        for i, freq in enumerate(frequencies):
            print "Setting frequency: %.4f" % freq
            self.syn.set_freq(freq*1e9)
            time.sleep(0.2) # sleep to allow synth to settle
            if freq < 8.0:
                # turn on CO filter
                print "Setting CO filter on"
                self.ifproc.set_all_CO(1)
            else:
                self.ifproc.set_all_CO(0)
            time.sleep(0.2)
            print "Setting optimal atten: %s" % self.optimal_attenuation[i,:]
            for j, chan in enumerate(chans):
                self.ifproc.set_atten(self.optimal_attenuation[i, j], chan)
                time.sleep(0.1)
            time.sleep(0.2)  # time to settle
            #vs = self.ifproc.get_all_voltages()
            vs = []
            for chan in chans:
                vs.append(self.ifproc.get_avg_voltage(chan))
            #voltages[i] = vs[chans]
            print "Voltages: %s" % vs
            voltages[i] = vs
        return voltages

    def get_zero_offset(self, frequencies=None, chans=None):
        self.zero_offset = self._get_voltages(frequencies=frequencies,
                                              chans=chans,
                                              label='Offset')
    
    def get_hot_voltages(self, frequencies=None, chans=None):
        self.hot_voltages = self._get_voltages(frequencies=frequencies,
                                               chans=chans,
                                               label='Hot')

    def get_cold_voltages(self, frequencies=None, chans=None):
        self.cold_voltages = self._get_voltages(frequencies=frequencies,
                                                chans=chans,
                                                label='Cold')


if __name__ == '__main__':
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--startfreq", dest="startfreq",
                      action="store", type="float",
                      default=5.0,
                      help="start frequency of sweep in GHz")
    parser.add_option("-e", "--endfreq", dest="endfreq",
                      action="store", type="float",
                      default=20.0,
                      help="end frequency of sweep in GHz")
    parser.add_option("-S", "--stepfreq", dest="stepfreq",
                      action="store", type="float",
                      default=0.5,
                      help="Step in frequency of sweep in GHz")
    parser.add_option("-f", "--filename",
                      action="store", type="string",
                      dest="filename", default="sequoia_test.txt",
                      help="Ascii Filename to store data into")
    parser.add_option("-c", "--startchan", dest="startchan",
                      action="store", type="int",
                      default=16,
                      help="starting IF channel for tests")
    parser.add_option("-n", "--numchans", dest="numchans",
                      action="store", type="int",
                      default=4,
                      help="number of IF channels for tests")
    parser.add_option("-N", "--numiters", dest="numiters",
                      action="store", type="int",
                      default=15,
                      help="number of iterations max in attenuator settings")
    parser.add_option("-l", "--lo", dest="lo",
                      action="store", type="float",
                      default=120.6,
                      help="LO frequency in GHz")
    parser.add_option("-v", "--voltage", dest="voltage",
                      action="store", type="float",
                      default=5.0,
                      help="Desired Hot Voltage when setting atten")
    parser.add_option("-d", "--delta", dest="delta",
                      action="store", type="float",
                      default=2.0,
                      help="Desired delta voltage about voltage when setting atten")
    parser.add_option("-i", "--sequoiaIF", dest="sequoia_pixel",
                      action="store", type="int",
                      default=1,
                      help="Start pixel of SEQUOIA")

    (options, args) = parser.parse_args()  

    fp = open(options.filename, 'w')
    fp.write("#Sequoia Test started at %s\n" % datetime.datetime.now())

    numfreqs = int((options.endfreq - options.startfreq)/options.stepfreq) + 1
    frequencies = numpy.linspace(options.startfreq, options.endfreq, numfreqs)
    chans = numpy.arange(options.startchan, options.startchan+options.numchans)
    seq_pixels = numpy.arange(options.sequoia_pixel, 
                              options.sequoia_pixel + options.numchans)
    # initialize GPIB
    syn = HP83711B()

    # initializing IF
    seq = Sequoia(frequencies, chans, syn)

    print "Performing attenuator adjustments on the hot load. Please put in hot load"

    seq.set_opt_atten(options.voltage, delta=options.delta, 
                      num_iterations=options.numiters)

    
    print "Getting hot voltages. Leave hot load on"

    seq.get_hot_voltages()

    print "Getting cold voltages. Prepare cold load"

    seq.get_cold_voltages()

    print "Performing offset measurements. Please turn off 2nd IF amplifiers"

    seq.get_zero_offset()

    fp.write("#RFFreq,IFFreq,IFChan,SeqPixel,Atten,Hot,Cold,Offset\n")
    for i, f in enumerate(frequencies):
        for j, c in enumerate(chans):
            if options.lo > 100.0:
                sky =  options.lo - f
            else:
                sky = options.lo + f
            print sky, f, c, seq.optimal_attenuation[i, j], seq.hot_voltages[i, j], seq.cold_voltages[i, j], seq.zero_offset[i, j]
            fp.write("%.3f,%.3f,%d,%d,%d,%.8f,%.8f,%.8f\n" % (sky, f, c, seq_pixels[j], seq.optimal_attenuation[i, j], seq.hot_voltages[i, j], seq.cold_voltages[i, j], seq.zero_offset[i, j]))

    fp.close()

