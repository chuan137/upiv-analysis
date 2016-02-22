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


ring_frame = read_rings('../data/smp_c_hough.txt')
ring_filter = loadtxt('../data/smp_c_gt.txt')
est_radii = [10, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12,
             13, 13, 13, 13, 15, 15, 15, 15, 18, 18, 18, 18,
             20, 20, 20, 20, 23, 23, 23, 23, 26, 26, 26, 26,
             29, 29, 29, 29, 31, 31, 31, 31, 35, 35, 35, 35,
             38, 38, 38, 38, 41, 41, 41, 41, 45, 45, 45, 45,
             48, 48, 48, 48, 51, 51, 51, 51, 53, 53, 53, 53,
             59, 59, 59, 59, 62, 62, 62, 62, 65, 65, 65, 65,
             69, 69, 69, 69, 73, 73, 73, 73, 77, 77, 77, 77]

# use estimated radius
for i,rings in enumerate(ring_frame):
    for r in rings:
        r[2] = est_radii[i]


def iterneighbours(x, y, r=1):
    for _x in range(x-r, x+r+1):
        for _y in range(y-r, y+r+1):
            yield _x,_y


for i,rings in enumerate(ring_frame):

    img_path = '../data/raw/sample_c'
    img_file_name = '{:05d}.tif'.format(int(i)+28)
    img_data = tif.imread(os.path.join(img_path, img_file_name))

    for cx, cy, est_r in rings:
        cx, cy = map(int, (cx,cy))

        plist = []
        for _x,_y in iterneighbours(cx, cy):
            r, peak = radial_profile_simple(img_data, (cx,cy), est_r)
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
            print i, (x0, y0), r, snr, est_r

