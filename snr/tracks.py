#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import pickle
import helper
from pykalman import *
from tifffile import *
from munkres import Munkres
from model import Track, timestep, ndim, poslim

# Parameters
ring_hough_file = '../data/rings_hough_sample_b.txt'

# load rings
rings = helper.read_rings(ring_hough_file, cols=(0,1))
fr_num = len(rings)
print 'Frame numbers: ', fr_num

# tracking
def init_tracks(track_id, observation):
    return Track(0, track_id, observation)
def plot(active_tracks, dead_tracks):
    _ax = plt.gca()
    _ax.cla()
    _ax.set_xlim(*poslim)
    _ax.set_ylim(*poslim[::-1])

    for t in active_tracks:
        _,x,y = t().T
        _ax.plot(x,y,'b-', linewidth=2)
    for t in dead_tracks:
        _,x,y = t().T
        _ax.plot(x,y,'g-', linewidth=2)



active_tracks = [ init_tracks(i, o) for i, o in enumerate(rings[0]) ]
dead_tracks = []
m = Munkres()
fig,axes = plt.subplots()


for _n, _obs in enumerate(rings[1:]):

    _n += 1

    kf = [t._filter for t in active_tracks ]
    mean = np.array([ t._mean[-1] for t in active_tracks ])
    covar = np.array([ t._covariance[-1] for t in active_tracks ])
    pred = np.array([ t.prediction(_n) for t in active_tracks ])

    # use Euclidean distance between prediction and observation as costs
    # for assignment algorithm
    cost = [[ np.linalg.norm(p[:ndim] - x) for x in _obs ] for p in pred ]

    for row, column in m.compute(cost):

        if cost[row][column] > 20:
            active_tracks.append( Track(_n, len(active_tracks), _obs[column]) )

        else:
            # Kalman filter update
            newmean, newcovar = kf[row].filter_update(mean[row], covar[row], _obs[column])

            active_tracks[row]._frame.append(_n)
            active_tracks[row]._mean.append(newmean)
            active_tracks[row]._covariance.append(newcovar)

    # move inactive tracks to dead_tracks
    for i in range(len(active_tracks)-1,0,-1):
        if _n - active_tracks[i]._frame[-1] > 20:
            t = active_tracks.pop(i)
            dead_tracks.append(t)

    # plotting
    if False:
        plot(active_tracks, dead_tracks)
        fig.show()
        plt.pause(1)

plot(active_tracks, dead_tracks)
fig.savefig('figs/tracks.png')

tracks = [ t() for t in  active_tracks + dead_tracks ]
tracks = [ t for t in tracks if len(t) > 5 ]
with open('tracks.pkl', 'wb') as f:
    pickle.dump(tracks, f)

