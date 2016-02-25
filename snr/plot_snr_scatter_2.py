#!/usr/bin/env python
import sys, os
sys.path.insert(0, '../python')

import numpy as np
import matplotlib.pyplot as plt
import re
from helper import loadtxt

'''
usage: ./snr_scatter_plot.py [snr_file]
'''

def snr_i(x):
    return 20 * np.log(x) / np.log(10)


try:
    snrfile = sys.argv[1]
except:
    snrfile = './snr.txt'
outfile = os.path.join('./figs', os.path.splitext(os.path.basename(snrfile))[0] + '.png')


data = loadtxt(snrfile, usecols=(0, 3, 4))
data_b = [ list(d) for d in data if d[0] == 1]
data_r = [ list(d) for d in data if d[0] == 0]


fig = plt.figure(figsize=(12, 12))
axes = fig.add_subplot(221)
axes.set_xlabel('Radius')
axes.set_ylabel('SNR')

for flag, r, snr in data_b:
    axes.scatter(r, snr_i(snr), c='b', alpha=0.4)
for flag, r, snr in data_r:
    axes.scatter(r, snr_i(snr), c='r', alpha=0.4)

bsize = 2
bins = np.arange(-40,30,bsize)
axes = fig.add_subplot(222)
axes.set_xlabel('SNR')
nb,_,_ = axes.hist([ snr_i(d[2]) for d in data_b ], bins=bins, color='b')

axes = fig.add_subplot(223)
axes.set_xlabel('SNR')
nr,bins,_ = axes.hist([ snr_i(d[2]) for d in data_r ], bins=bins, color='r')

pb = nb/(nb+nr)
# pb[np.isnan(pb)] = 0.0
bins = 0.5 * (bins[1:] + bins[:-1])
axes = fig.add_subplot(224)
axes.set_ylim(-10, 120)
axes.plot(bins, 100*pb, 'go')

plt.savefig(outfile)
