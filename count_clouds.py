# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 08:35:11 2014

@author: Nicholas
"""

from __future__ import print_function, division

import numpy as np
from skimage import morphology
from scipy.ndimage import measurements
# from fmask import calc_pcp, calc_pcl, buffer_pcl
from cloud_detection import calc_pcp
from math import pi

def label_clouds(pcp, opening_selem, closing_selem):
    # img = buffer_pcl()
    # pcp = calc_pcp
    img = pcp
    _img = np.zeros((img.shape[0]+30, img.shape[1]+30))
    _img[15:-15, 15:-15] = img
    
    o_selem   = morphology.disk(opening_selem)
    _img = morphology.opening(_img, o_selem)
    c_selem   = morphology.disk(closing_selem)
    bin_im = morphology.closing(_img, c_selem)
    
    labels, nbr_objs = measurements.label(bin_im)
    print(nbr_objs)
    return labels[15:-15, 15:-15], nbr_objs

if __name__ == "__main__":
    labels, nbr_objs = label_clouds(pcp, 3, 9)