#!/usr/bin/env python
import sys, os
sys.path.insert(0, '../python')

from helper import loadtxt
import matplotlib.pyplot as plt
import numpy as np
import re


fig, axes = plt.subplots()
axes.set_xlabel('SNR [db]')
axes.set_ylabel('Detections [%]')
axes.set_ylim(0,120)

# axes.set_xrange()

detects = np.array(loadtxt('../data/simu_detections_R15.txt'))
rates = 100*detects[:,2]/detects[:,1]
snr = detects[:,-1]
axes.plot(snr, rates, 'o-', label='r = 15')

detects = np.array(loadtxt('../data/simu_detections_R25.txt'))
rates = 100*detects[:,2]/detects[:,1]
snr = detects[:,-1]
axes.plot(snr, rates, 'o-', label='r = 25')

detects = np.array(loadtxt('../data/simu_detections_R35.txt'))
rates = 100*detects[:,2]/detects[:,1]
snr = detects[:,-1]
axes.plot(snr, rates, 'o-', label='r = 35')

detects = np.array(loadtxt('../data/simu_detections_R45.txt'))
rates = 100*detects[:,2]/detects[:,1]
snr = detects[:,-1]
axes.plot(snr, rates, 'o-', label='r = 45')

axes.legend(loc=2)
plt.savefig('./figs/simu_detctions.png')
