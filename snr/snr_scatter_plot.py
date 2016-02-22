#!/usr/bin/env python
import sys
sys.path.insert(0, '../python')

import numpy as np
import matplotlib.pyplot as plt
import re
from helper import loadtxt


fig, axes = plt.subplots()
axes.set_xlabel('Radius')
axes.set_ylabel('SNR')

data = loadtxt('./snr.txt', usecols=(3, 4))

for r, snr in data:
    snr_ind = 20 * np.log(snr) / np.log(10)
    axes.scatter(r, snr_ind)
plt.savefig('figs/snr_scatter.png')
