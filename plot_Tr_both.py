#!/usr/bin/python

from optparse import OptionParser
import sys
import pandas as pd
import itertools
import pylab
import datetime

marker = itertools.cycle((',', 'o', 'v', '^', '<',
                          '>', '1', '2', '3', '4',
                          's', 'p', '*', 'h', 'H',
                          '+', 'x', 'D'))
colors = itertools.cycle(('b', 'g', 'r', 'c', 
                          'm', 'y', 'k', 'coral', 
                          'aqua', 'brown', 'chocolate', 'crimson', 
                          'firebrick', 'hotpink', 'khaki', 'maroon',
                          ))

def plot_both(fname1, fname2, title=None,
              plot_file=None):
    #fname1 = 'sequoia_80.4GHz_nov18__seqA_c1_16_rpt2.txt'
    #fname2 = 'sequoia_120.6GHz_nov18__seqA_c1_16_rpt2.txt'

    df1 = pd.read_table(fname1, sep=',', 
                       header=1)
    df2 = pd.read_table(fname2, sep=',', 
                        header=1)

    dg1 = df1.groupby('SeqPixel')
    dg2 = df2.groupby('SeqPixel')
    fig = pylab.figure()
    ax = fig.add_subplot(1,1,1)
    for chan in dg1.groups.keys():
        pix1 = dg1.get_group(chan)
        pix2 = dg2.get_group(chan)
        #pix2['#RFFreq'] = 120.6 - (pix2['#RFFreq'] - 120.4)
        pix = pix1.append(pix2.sort('#RFFreq'), ignore_index=True)
        pix['y'] = (pix['Hot']-pix['Offset'])/(pix['Cold']-pix['Offset'])
        pix['Tr'] = (290. - pix['y']*77.)/(pix['y'] - 1)
        zero_atten_idx = pix.Atten == 0
        ax.plot(pix[zero_atten_idx]['#RFFreq'], pix[zero_atten_idx]['Tr'],
                marker='o', linestyle='None', markerfacecolor='white', 
                color='red', markersize=18, label='_nolegend_')        
        ax.plot(pix['#RFFreq'], pix['Tr'], marker=marker.next(),
                linestyle='-', color=colors.next(),
                label='Pix %d' % (chan))

    ax.legend(loc='best')
    ax.set_ylim(0, 150)
    ax.set_xlabel('Frequency (GHz)')
    ax.set_ylabel('TR (K)')
    if title is not None:
        ax.set_title(title)
    fig.canvas.draw()
    if plot_file is not None:
        fig.savefig(plot_file)
    pylab.show()

if __name__ == '__main__':
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-1", "--filename1",
                      action="store", type="string",
                      dest="filename1",
                      help="80.4 GHz ascii filename")
    parser.add_option("-2", "--filename2",
                      action="store", type="string",
                      dest="filename2",
                      help="120.6 GHz ascii filename")
    parser.add_option("-p", "--plotfile",
                      action="store", type="string",
                      dest="plot_file",
                      help="Output png file")
    parser.add_option("-t", "--title",
                      action="store", type="string",
                      help="Title for plot")
    (options, args) = parser.parse_args()
    print "Plotting ...."
    print "Kill plot window(s) to exit..."
    plot_both(options.filename1, options.filename2,
              options.title, options.plot_file)
    sys.exit(0)
