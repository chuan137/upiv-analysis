#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.path.realpath('../python'))

import cv
import getopt
import matplotlib.pyplot as plt
import numpy as np
import numpy.random as rand
import tifffile.tifffile as tif
from helper import stats


# {{{ Helper Functions
def snr_ind(snr):
    return 20 * np.log(snr) / np.log(10)
def draw_circle(imgsize, rad, thickness=2):
    w, h = imgsize
    xx, yy = np.mgrid[:w, :h]
    circle = (xx - w/2)**2 + (yy - h/2)**2
    rmin, rmax = rad - thickness/2, rad + thickness/2
    return np.logical_and(circle < rmax**2, circle > rmin**2)


def draw_fuzzy_circle(imgsize, rad, thickness):
    width = 0.5 * thickness
    idx = np.arange(min(imgsize))
    kernel = np.exp(-(idx - rad)**2/(2*width**2))

    w, h = imgsize
    xx, yy = np.mgrid[:w, :h]
    circle = np.floor(np.sqrt((xx - w/2)**2 + (yy - h/2)**2))

    f = np.vectorize(lambda x: kernel[x])
    return f(circle)


def gen_pattern(alpha, beta=0.01):
    '''
    generate pattern
    :param beta: signal threashold, ratio of the peak value
    '''
    fuzzy_circle = draw_fuzzy_circle(samplesize, rad, thickness)
    background = rand.normal(0.0, noise, samplesize)
    image = alpha * fuzzy_circle + background

    # signal noise ratio
    thred = beta * image.max()
    circle = draw_circle(samplesize, rad, 0.5*thickness)
    signal = image[np.logical_and(image>thred, circle)]
    snr = signal.mean() / noise
    return image, snr
# }}}


# seperation between noise and circle
alpha = 1.0
# variance of gaussian noise
noise = 1.0
# ring radius
rad = 25
# ring thickness
thickness = 6
# sample size
samplesize = (128, 128)
# full image size
fullsize = (1024, 1024)
# output format
fmt = 'tif'


"""
options:  [-a alpha] [-r radius] [-s fullsize] [-t fmt]
"""
optlist, args = getopt.getopt(sys.argv[1:], 'a:r:')
for o, a in optlist:
    if o == '-a':
        alpha = float(a)
    elif o == '-r':
        rad = float(a)
    elif o == '-f':
        fullsize = (float(a), float(a))
    elif o == '-t':
        fmt = a
    else:
        assert False, "unknown option"


image = np.zeros(fullsize)
xs, ys = samplesize
snr_ = []
for i in range(fullsize[0]/samplesize[0]):
    for j in range(fullsize[1]/samplesize[1]):

        sample, snr = gen_pattern(alpha)
        snr_.append(snr)
        print 'SNR : %.5f,' % snr,
        print 'Industrial SNR: %.3f db' % snr_ind(snr)

        image[i*xs:(i+1)*xs, j*xs:(j+1)*xs] = sample

snr_ = np.array(snr_)
print "Average SNR %.3f +/- %.3f  (%.2f db)" % \
    (snr_.mean(), snr_.std(), snr_ind(snr_.mean()))
# plt.imshow(image, cmap='gray')

if fmt == 'tif':
    tif.imsave('figs/ring.tif', image.astype(np.float32))
elif fmt == 'png':
    plt.savefig('figs/ring.png')
else:
    print 'Output format %s not supported' % fmt


