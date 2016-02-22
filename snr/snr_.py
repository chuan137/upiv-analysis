from azimuthal import radial_profile, smooth_array, best_local_peak, crop_image
from helper import print_stats
import numpy as np
import operator

def coordinates(x, y):
    from itertools import product
    if type(x) is int:
        x = (0, x)
    if type(y) is int:
        y = (0, y)
    return list(product(xrange(*x), xrange(*y)))


def image_psnr(img_data, center, radius):
    center = map(int, center)

    r_e = radius
    r_min = max(r_e / 2, r_e - 20)
    r_max = r_e + 20

    def psnr(image, px, py, h, size):
        iw, ih = r_max, r_max
        iw2, ih2 = iw/2, ih/2
        orig = (pp[0]-iw2, pp[1]-ih2)
        img = crop_image(image, orig, iw, ih)
        sigma = ((img-img.mean())**2).sum()/img.size
        return 10 * np.log10(h0*h0/sigma)

    peaks = []
    profiles = []

    for _x, _y in coordinates((center[0] - 1, center[0] + 2),
                              (center[1] - 1, center[1] + 2)):

        # extract local peak from radial profile
        bins, profile = radial_profile(img_data, _x, _y, minr=r_min, maxr=r_max)
        profile = smooth_array(profile)
        p = best_local_peak(profile)

        if p is not None:
            peaks.append(((_x,_y), bins[p[0]], p[1], p[2]))
            profiles.append(smooth_array(profile))

    if len(peaks):
        # use the best peak for detected ring
        pp, r0, h0, c0 = max(peaks, key=operator.itemgetter(2))
        #print "Ring:", (pp, r0, h0, c0)

        _snr = psnr(img_data, pp[0], pp[1], h0, r_max)
        #print "SNR: ", _snr

        return r0, _snr

