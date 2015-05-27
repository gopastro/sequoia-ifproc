import pandas as pd
import itertools
import math

#needs user input at lines w/ ####

marker = itertools.cycle((',', 'o', 'v', '^', '<',
                          '>', '1', '2', '3', '4',
                          's', 'p', '*', 'h', 'H',
                          '+', 'x', 'D'))
colors = itertools.cycle(('b', 'g', 'r', 'c', 
                          'm', 'y', 'k', 'coral', 
                          'aqua', 'brown', 'chocolate', 'crimson', 
                          'firebrick', 'hotpink', 'khaki', 'maroon',
                          ))

data = pd.read_csv('IFMod7_rev2_sidebandratio.txt', sep=',') ####
dg = data.groupby('P_in_adj')
dgpow = dg.get_group(-9.0)
fig = figure(figsize=(14, 8))
dgifs = dgpow.groupby('IF_freq')

for pixel in range(4):
	pixelplus = pixel + 24 ####
        ax = fig.add_subplot(2, 2, pixel+1)
        iffreqs = dgifs.groups.keys()
        iffreqs.sort()
        for iffreq in iffreqs:
            ifdata = dgifs.get_group(iffreq)	
	    ydata = getattr(ifdata, 'rat%d' %pixelplus)
            ax.plot(ifdata['LO_freq'], ydata, marker=marker.next(), linestyle='-',                      color=colors.next(),label='IF = %d MHz' % iffreq)
        ax.set_title('Pixel %d' % (pixelplus))
        if pixel == 2:
            ax.set_xlabel('LO Frequency (GHz)')
            ax.set_ylabel('LSB - USB (dBm)')
        ax.legend(loc='best', prop={'size':6})

draw()
show()
fig.savefig('ifmodule7_rev2_img_rej.png') ####

    
