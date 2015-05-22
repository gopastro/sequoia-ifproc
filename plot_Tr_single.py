#!/usr/bin/python

from optparse import OptionParser
import sys
import pandas as pd
import itertools
import pylab
import datetime

marker = itertools.cycle(('o', 'v', '^', '<',
                          '>', '1', '2', '3', '4',
                          's', 'p', '*', 'h', 'H',
                          '+', 'x', 'D'))
colors = itertools.cycle(('b', 'g', 'r', 'c', 
                          'm', 'y', 'k', 'coral', 
                          'aqua', 'brown', 'chocolate', 'crimson', 
                          'firebrick', 'hotpink', 'khaki', 'maroon',
                          ))

def plot_single(fname, item='Tr', title=None,
                chans=[],
                plot_file=None):
    #fname1 = 'sequoia_80.4GHz_nov18__seqA_c1_16_rpt2.txt'
    #fname2 = 'sequoia_120.6GHz_nov18__seqA_c1_16_rpt2.txt'
    if item not in ('Tr', 'Atten', 'Hot', 'Cold', 'Offset'):
        print "Item to plot should be one of Tr, Atten, Hot, Cold or Offset"
        return

    df = pd.read_table(fname, sep=',', 
                       header=1)

    dg = df.groupby('SeqPixel')
    fig = pylab.figure()
    ax = fig.add_subplot(1,1,1)
    if not chans:
        chans = dg.groups.keys()
    chans = [int(c) for c in chans]
    for chan in dg.groups.keys():
        if chan in chans:
            pix = dg.get_group(chan)
            if item == 'Tr':
                pix['y'] = (pix['Hot']-pix['Offset'])/(pix['Cold']-pix['Offset'])
                pix['Tr'] = (290. - pix['y']*77.)/(pix['y'] - 1)
            zero_atten_idx = pix.Atten == 0
            ax.plot(pix[zero_atten_idx]['#RFFreq'], pix[zero_atten_idx][item],
                    marker='o', linestyle='None', markerfacecolor='white', 
                    color='red', markersize=18, label='_nolegend_')
            ax.plot(pix['#RFFreq'], pix[item], marker=marker.next(),
                    linestyle='-', color=colors.next(),
                    label='Pix %d' % (int(pix.SeqPixel.head(1))))

    ax.legend(loc='best')
    #ax.set_ylim(0, 150)
    ax.set_xlabel('Frequency (GHz)')
    #ax.set_ylabel('TR (K)')
    ax.set_ylabel(item)
    x1, x2 = ax.get_xlim()
    ax.set_xlim(x1, x2+(x2-x1)*0.2)
    
    if title is not None:
        ax.set_title(title)
    fig.canvas.draw()
    if plot_file is not None:
        fig.savefig(plot_file)
    pylab.show()

def get_comma_separated_args(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

if __name__ == '__main__':
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--filename",
                      action="store", type="string",
                      dest="filename",
                      help="ascii filename")
    parser.add_option("-i", "--item",
                      action="store", type="string",
                      dest="item",
                      help="Item to plot, one of Tr, Atten, Hot, Cold or Offset")
    parser.add_option("-c", "--chans",
                      type="string",
                      dest="chans",
                      action="callback",
                      callback=get_comma_separated_args,
                      help="Comma separated channel list to plot")
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
    if options.chans is None:
        chans = []
    else:
        chans = options.chans
    print chans
    plot_single(options.filename, item=options.item,
                chans=chans,
                title=options.title, 
                plot_file=options.plot_file)
    sys.exit(0)
