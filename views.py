# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 14:37:40 2014

@author: Nicholas
"""
import controllers
import numpy as np
from numpy import ma
from matplotlib import pyplot as plt
from matplotlib import cm

from scipy.misc import bytescale
from utils import calculate_percentile


#from skimage import data, img_as_float
from skimage import exposure


def scale_band_for_rgb(in_array, p_max):
    input_array = np.array(in_array)
    cmin = np.percentile(input_array, 0.01)
    cmax = p_max
    return bytescale(input_array, cmin=cmin, cmax=cmax)
    
def get_mean_percentile():
    p98_red = calculate_percentile(ma.masked_values(controllers.get_red(), 0), 98)
    p98_green = calculate_percentile(ma.masked_values(controllers.get_green(), 0), 98)
    p98_blue = calculate_percentile(ma.masked_values(controllers.get_blue(), 0), 100)
    p98_mean = (p98_red + p98_green + p98_blue) / 3
    print(p98_red, p98_green, p98_blue, p98_mean)
    return p98_red, p98_green, p98_blue, p98_mean
    
def create_rgb():
    p98_red, p98_green, p98_blue, p98_mean = get_mean_percentile()
    img_dim = controllers.get_red().shape
    img = np.zeros((img_dim[0], img_dim[1], 3), dtype=np.uint8)
    img[:,:,0] = scale_band_for_rgb(controllers.get_red(), p98_mean)
    img[:,:,1] = scale_band_for_rgb(controllers.get_green(), p98_mean)
    img[:,:,2] = scale_band_for_rgb(controllers.get_blue(), p98_mean)

#    return bytescale(img, cmax=calculate_percentile(ma.masked_values(img, 0), 98))
    return img
    
def create_composite(red, green, blue):
    img_dim = red.shape
    img = np.zeros((img_dim[0], img_dim[1], 3), dtype=np.float)
    img[:,:,0] = red
    img[:,:,1] = green
    img[:,:,2] = blue
    p2, p98 = np.percentile(img, (2, 98))
    img_rescale = exposure.rescale_intensity(img, in_range=(0, p98))
    return bytescale(img_rescale)

def create_cm_orange():
    from matplotlib import cm
    import numpy as np
    theCM = cm.get_cmap('Oranges')
    theCM._init() # this is a hack to get at the _lut array, which stores RGBA vals
    alphas = np.abs(np.linspace(0, .9, theCM.N))
    theCM._lut[:-3,-1] = alphas
    return theCM

def create_cm_greys():
    from matplotlib import cm
    import numpy as np
    theCM = cm.get_cmap('Greys')
    theCM._init() # this is a hack to get at the _lut array, which stores RGBA vals
    alphas = np.abs(np.linspace(0, .9, theCM.N))
    theCM._lut[:-3,-1] = alphas
    return theCM

def show_rgb():
    rgb = create_rgb()
    plt.imshow(rgb)
    return rgb
    
if __name__ == "__main__":
    plt.close('all')
#    img = create_rgb()
