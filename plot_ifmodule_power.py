import pandas as pd
import itertools
import math
from optparse import OptionParser

marker = itertools.cycle((',', 'o', 'v', '^', '<',
                          '>', '1', '2', '3', '4',
                          's', 'p', '*', 'h', 'H',
                          '+', 'x', 'D'))
colors = itertools.cycle(('b', 'g', 'r', 'c', 
                          'm', 'y', 'k', 'coral', 
                          'aqua', 'brown', 'chocolate', 'crimson', 
                          'firebrick', 'hotpink', 'khaki', 'maroon',
                          ))

data = pd.read_csv('IFMod6_rev2_test.txt', sep=',')
dg = data.groupby('LO_freq')


for lofreq in dg.groups.keys():
    
    fig = figure(figsize=(14, 8))
    dfif = dg.get_group(lofreq)
    dgifs = dfif.groupby('IF_freq')
    for pixel in range(4):
	pixelplus = pixel + 20 ####
        ax = fig.add_subplot(2, 2, pixel+1)
        iffreqs = dgifs.groups.keys()
        iffreqs.sort()
        for iffreq in iffreqs:
            ifdata = dgifs.get_group(iffreq)
	    ydata = map(lambda x:(math.log(x+10)), 
			  getattr(ifdata, 'Dt_V%d' %pixelplus))
	    ydata2 = getattr(ifdata, 'P_out%d' %pixelplus)
            ax.plot(ifdata['P_in_adj'], ydata, marker=marker.next(), linestyle='-',                      color=colors.next(),label='IF = %d MHz' % iffreq) ####
        ax.set_title('Pixel %d; LO = %g GHz' % (pixelplus, lofreq))
        if pixel == 2:
            ax.set_xlabel('Input Power (dBm)')
            ax.set_ylabel('log(Det Voltage + 10V)') ####
        ax.legend(loc='best', prop={'size':6})
    draw()
    show()
    fig.savefig('ifmodule6_rev2_det_lo_%g_GHz.png' % lofreq)####

    
