
# coding: utf-8

# In[ ]:

import numpy as np
import operator
import re


# ### manuplating files

# In[ ]:

def ext_filter(path, extension):
    """ return file-[] with extension, in sorted order"""
    from os import listdir
    from os.path import isfile, join
    filtered_files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
    return sorted(filtered_files)

def read_raw(filename, xsize=1024, ysize=1024):
    import struct
    with open(filename, 'rb') as f:
        img_data = [ struct.unpack('>f', f.read(4)) for i in range(xsize * ysize) ]
        img_data = np.array(img_data).reshape(xsize, ysize)
    return img_data


def coordinates(x, y):
    from itertools import product
    if type(x) is int:
        x = (0, x)
    if type(y) is int:
        y = (0, y)
    return list(product(xrange(*x), xrange(*y)))


def reverse_enum(L):
    for index in reversed(range(len(L))):
        yield index, L[index]

        
def crop_image(img, corner, xr=50, yr=50):
    x0, y0 = corner
    return np.array(img[y0:y0+yr, x0:x0+xr])


def smooth_array(lst):
    res = np.zeros_like(lst)
    for ii in range(1, len(lst)-1):
        aa,bb,cc = lst[ii-1:ii+2]
        res[ii] = 0.5*bb + 0.25*aa + 0.25*cc
    res[0] = 0.75*lst[0] + 0.25*lst[1]
    res[-1] = 0.75*lst[-1] + 0.25*lst[-2]
    return np.array(res)
        

def azimu_hist(img, center_x, center_y):
    hist_x = np.arange(0, 50, 0.5)
    hist_n = np.zeros_like(hist_x)
    hist = np.zeros_like(hist_x)
    for i,j in coordinates(img.shape[0], img.shape[1]):
        dist = np.sqrt((i-center_x)**2 + (j-center_y)**2)
        hist[int(dist/0.5)] += img[i,j]
        hist_n[int(dist/0.5)] += 1
    return hist_x, hist/hist_n


def local_peak(data, window=5):
    """ Search local peak in data[].

    A peak is a series of values, that first monotonically increases
    to the middle point of the series, then monotonically decreases.
    The length of the series is given by *window*, that should be odd.

    @return (index[], contrast[])
        index:    of each local peak
        contrast: max subtract min of each peak series, normalized
                  by window
    """
    if window != 2 * (window / 2) + 1:
        warnings.warn("window (%d) is not an odd number. Increasing by 1" % window)
        window += 1
    win_half = window / 2
    
    index = []
    contrast = []

    for i in range(0, len(data)-win_half):
    #for i in range(len(data)-win_half, 0, -1):
        dd = data[i:i+window]
        if not np.isnan(dd).any():
            test = (dd[1:] - dd[:-1] > 0)
            if len(test) == 4:
                if (test == [True, True, False, False]).all():
                    index.append(i+win_half)
                    contrast.append( float(max(dd)-min(dd)) / window )
    return index, contrast


def best_local_peak(data, window=5):
    peaks, contrasts = local_peak(data, window)
    if len(peaks) > 0:
        peak_val = np.array([data[i] for i in peaks])
        return max(zip(peaks, peak_val, contrasts), key=operator.itemgetter(1))


# In[ ]:

def radial_profile(img, px=None, py=None, minr=5, maxr=50, bins=None):
    """ Calculate azimuthally averaged radial profile
    
    px:     coordinate x of center. if None, take the center of image.
    py:     coordinate y of center.
    maxr:   max radius in profile. if (px, py) is very close to border, change 
            maxr to the distance of (px,py) to bondary
    bins:   bins for histogram. if a list, histogram bins. if a integer, bins
            is number of bins. if None, histogram bins is arange(0, maxr, 0.5)
    """
    
    if px is None:
        centerx = int(img.shape[1]/2) - 1
    if py is None:
        py = img.shape[0]/2 - 1
    
    maxr_ = min(px, py, img.shape[1] - px, img.shape[0] - py)    
    if maxr + 2 > maxr_:
        maxr = maxr_ - 2
        
    if bins is None:
        bins = np.arange(0, maxr, 0.5)
    if type(bins) is int:
        bins = np.arange(0, maxr, float(marx/bins))
    
    # crop original image from (px - maxr, py - maxr) with size
    # (2*maxr + 1, 2*maxr + 1)
    crop_ = crop_image(img, (px-maxr, py-maxr), 2*maxr+1, 2*maxr+1)
    
    # calculate profile at (maxr, maxr)
    y, x = np.indices((crop_.shape))
    r = np.sqrt((x - maxr)**2 + (y - maxr)**2)

    hr = np.histogram(r.ravel(), bins=bins)
    h = np.histogram(r.ravel(), bins=bins, weights=crop_.ravel())
    
    bins = (0.5 * (bins[1:] + bins[:-1]))
    res = h[0] / hr[0]
    res[bins<minr] = float('NaN')
    return bins, res


# In[1]:
#
# def read_rings(fpath):
#     def ring_filter(r):
#         return tuple(map(float, r[:-1].split()[:3]))
#     
#     rings = []
#     
#     with open(fpath, 'r') as df:
#         for l in df.readlines():
#             if l[0] == '#':
#                 rings.append([])
#             else:
#                 rings[-1].append(l)
#
#     return [[ring_filter(item) for item in row] for row in rings]
#

def read_rings(ring_file, cols=(0,1,2)):
    '''
    :param cols: tuple of columns to return
    :returns: list of ring coordinates for each frame
    '''

    data = []
    with open(ring_file) as f:
        for line in f:
            if line.startswith('#'):
                data.append([])
            else:
                data[-1].append(map(float, line.split()))
    return [np.array(d)[:,cols] for d in data]


def loadtxt(fname, usecols=None):
    numeric_const_pattern = r"""
        [-+]? # optional sign
        (?:
            (?: \d* \. \d+ ) # .1 .12 .123 etc 9.1 etc 98.1 etc
            |
            (?: \d+ \.? ) # 1. 12. 123. etc 1 12 123 etc
        )
        # followed by optional exponent part if desired
        (?: [Ee] [+-]? \d+ ) ?
    """
    rx = re.compile(numeric_const_pattern, re.VERBOSE)
    data = []
    with open(fname, 'r') as f:

        for line in f:
            if line.startswith('#'):
                continue

            scan = rx.findall(line)
            scan = np.array(map(float, scan))

            if len(scan) == 0:
                continue

            if usecols:
                usecols = list(usecols)
                try:
                    data.append(scan[usecols])
                except IndexError as e:
                    print 'Warning: ', e.message
                    print '         ', scan
            else:
                data.append(scan)
    return np.array(data)


def print_stats(arr):
    print 'size: {}, sum: {}, mean: {}, std: {}, min: {}, max: {}'.format(\
        arr.size, arr.sum(), arr.mean(), arr.std(), arr.min(), arr.max())
