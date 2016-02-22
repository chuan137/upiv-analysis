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

try:
    snrfile = sys.argv[1]
except:
    snrfile = '../data/smp_b_snr.txt'
outfile = os.path.join('./figs', os.path.splitext(os.path.basename(snrfile))[0] + '.png')


fig, axes = plt.subplots()
axes.set_xlabel('Radius')
axes.set_ylabel('SNR')

data = loadtxt(snrfile, usecols=(3, 4))

for r, snr in data:
    snr_ind = 20 * np.log(snr) / np.log(10)
    axes.scatter(r, snr_ind)
plt.savefig(outfile)
