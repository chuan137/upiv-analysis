#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.path.realpath('../python'))

import numpy as np
import matplotlib.pyplot as plt
import pickle
import operator
import tifffile.tifffile as tif
from azimuthal import radial_profile_simple
from helper import print_stats, read_rings, loadtxt

#{{{ Function isin(), fcmvect(), calc_snr()
def iterneighbours(x, y, r=1):
    for _x in range(x-r, x+r+1):
        for _y in range(y-r, y+r+1):
            yield _x,_y

import operator
def isin(x, s, cmpfn=operator.eq):
    for _x in s:
        if cmpfn(x, _x):
            return 1
    return 0

def fcmpvect(x, y, fuzzyness=2):
    if len(x) == len(y):
        for i in range(len(x)):
            if abs(x[i]-y[i]) > fuzzyness:
                return 0
        return 1
    else:
        return 0

def calc_snr(img_data, cx, cy, est_r):
    plist = []
    for _x,_y in iterneighbours(cx, cy):
        _, r, peak = radial_profile_simple(img_data, (_x,_y), est_r)
        plist.append([r, peak, _x, _y])

    r, peak, x0, y0 = max(plist, key=operator.itemgetter(1))

    # noise
    r_, l = int(r), 20
    xs, ys = img_data.shape
    bkgrd = np.zeros((xs+2*r_+2*l, ys+2*r_+2*l))
    bkgrd[y0: y0+2*r_+2*l+1, x0:x0+2*r_+2*l+1] = 1
    bkgrd[y0+l-5: y0+2*r_+l+6, x0+l-5:x0+2*r_+l+6] = 0
    bkgrd = bkgrd[r_+l:r_+l+xs, r_+l:r_+l+ys]
    noise = img_data[bkgrd==1]

    snr = (peak - noise.mean()) / noise.std(ddof=1)
    if r > 0:
        return x0, y0, r, snr
#}}}


ring_frame = read_rings('../data/smp_c_hough.txt')
ring_gt = loadtxt('../data/smp_c_gt.txt')
est_radii = [10, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12,
             13, 13, 13, 13, 15, 15, 15, 15, 18, 18, 18, 18,
             20, 20, 20, 20, 23, 23, 23, 23, 26, 26, 26, 26,
             29, 29, 29, 29, 31, 31, 31, 31, 35, 35, 35, 35,
             38, 38, 38, 38, 41, 41, 41, 41, 45, 45, 45, 45,
             48, 48, 48, 48, 51, 51, 51, 51, 53, 53, 53, 53,
             59, 59, 59, 59, 62, 62, 62, 62, 65, 65, 65, 65,
             69, 69, 69, 69, 73, 73, 73, 73, 77, 77, 77, 77]


for i in range(0, len(ring_frame)):
    filenum = i + 28
    rings = ring_frame[i]

    img_path = '../data/raw/sample_c'
    img_file_name = '{:05d}.tif'.format(filenum)
    img = tif.imread(os.path.join(img_path, img_file_name))

    # fro detected rings
    # use estimated radius
    for cx, cy, est_r in rings:

        if isin((cx,cy), ring_gt, cmpfn=fcmpvect):
            try:
                x0, y0, r, snr = calc_snr(img, int(cx), int(cy), est_radii[i])
                print 1, x0, y0, r, snr
            except:
                pass

    # for not detected rings 
    # use estimated radius
    for cx, cy in ring_gt:

        if not isin((cx,cy), rings[:,:2], cmpfn=fcmpvect):
            try:
                x0, y0, r, snr = calc_snr(img, int(cx), int(cy), est_radii[i])
                print 0, x0, y0, r, snr
            except:
                pass

    print

