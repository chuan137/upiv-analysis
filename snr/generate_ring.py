#!/usr/bin/env python
import numpy as np
import numpy.random as rand
import matplotlib.pyplot as plt 
import cv


# {{{ Helper Functions
def draw_circle(imgsize, rad, thickness=2):
    w, h = imgsize
    xx, yy = np.mgrid[:w, :h]
    circle = (xx - w/2)**2 + (yy - h/2)**2
    rmin, rmax = rad - thickness/2, rad + thickness/2
    return np.logical_and(circle < rmax**2, circle > rmin**2)
def draw_fuzzy_circle(imgsize, rad, width):
    width = 0.5 * thickness
    idx = np.arange(min(imgsize))
    kernel = np.exp(-(idx - rad)**2/(2*width**2))

    w, h = imgsize
    xx, yy = np.mgrid[:w, :h]
    circle = np.floor(np.sqrt((xx - w/2)**2 + (yy - h/2)**2))

    f = np.vectorize(lambda x: kernel[x])
    return f(circle)
def stats(arr):
    return arr.size, arr.sum(), arr.mean(), arr.std(), arr.min(), arr.max()
# }}}


# seperation between noise and circle
alpha = 5
# variance of gaussian noise
noise = 1.0


imgsize = (64, 64)
background = rand.normal(0.0, noise, imgsize)


rad = 20
thickness = 6
circle = draw_fuzzy_circle(imgsize, rad, 0.1*thickness)
image = alpha * circle + background
# print stats(circle)
# print stats(circle[circle>0.6])
# print stats(image)


# signal noise ratio
snr =  alpha * circle[circle > np.exp(-.5)].mean() / noise
snr_ind = 20 * np.log(snr) / np.log(10)
print 'SNR :', snr
print 'Industrial SNR: %.3f db' % snr_ind


fig, ax = plt.subplots()
ax.imshow(image, cmap='gray')
#plt.pause(-1)
plt.savefig('figs/ring.png')

