import sys
import numpy as np
import operator
import warnings

def crop_image(img, corner, xr=50, yr=50):
    x0, y0 = corner
    return np.array(img[y0:y0+yr, x0:x0+xr])


def crop_image_c(image, center, rad):
    xs, ys = image.shape
    y, x = center
    img_padded = np.zeros((xs+2*rad, ys+2*rad))
    img_padded[rad:-rad, rad:-rad] = image
    return img_padded[x:x+2*rad+1, y:y+2*rad+1]


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


def radial_profile_simple(image, center, r0=60):
    r0 = int(r0)
    maxr = r0 + 10
    minr = max(min(r0/2, r0-10), 2)

    cropped = crop_image_c(image, center, maxr)
    xx, yy = np.mgrid[-maxr:maxr+1, -maxr:maxr+1]
    rad = np.sqrt(xx**2 + yy**2)

    prof = []
    for rr in range(minr, maxr):
        s = cropped[np.logical_and(rad > rr,  rad <= rr+1)]
        prof.append(s[s>0].mean())
    prof = np.array(prof)

    try:
        r_peak, v_peak, _  = best_local_peak(prof)
        r_peak += minr + 0.5
    except TypeError as e:
        sys.stderr.write(e.message + '\n')
        r_peak, v_peak = 0, 0
    return r_peak, v_peak


