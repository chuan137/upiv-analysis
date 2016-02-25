#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.path.realpath('../python'))

import numpy as np
import matplotlib.pyplot as plt
import pickle
import operator
import tifffile.tifffile as tif
from azimuthal import radial_profile_simple
from helper import print_stats, read_rings


with open('../data/smp_b_tracks.pkl', 'rb') as f:
    tracks = pickle.load(f)
rings = read_rings('../data/smp_b_hough.txt')


rings_per_frame = {}
for t in tracks:
    for n,x,y in t:
        # if n != 5:
        #     continue
        if n not in rings_per_frame.keys():
            rings_per_frame[n] = [(x,y)]
        else:
            rings_per_frame[n].append((x,y))


for f in sorted(rings_per_frame.keys()):

    img_path = '../data/raw/sample_b'
    img_file_name = '{:05d}.tif'.format(int(f))
    img_data = tif.imread(os.path.join(img_path, img_file_name))
    centers = rings_per_frame[f]

    for c in centers:

        cx, cy = map(int, c)

        for xx, yy, est_r in rings[int(f)]:
            if abs(xx-cx) < 5 and abs(yy-cy) < 5:
                break

        plist = []
        for _x in range(cx-1, cx+2):
            for _y in range(cy-1, cy+2):
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
            print f, (x0, y0), r, snr, est_r

