import cloud_detection as fmask
import utils
import os
# import models
# import config
import numpy as np
from numpy import ma as ma
from skimage import morphology
from skimage.morphology import reconstruction
import imp
import matplotlib.pyplot as plt
imp.reload(fmask)
# data_dir = config.data_dir #"Documents/data/"
# path = config.path #'176'
# row = config.row #'083'
# time = config.time #'2014010'

# band_option = config.band_option
# b = band_option

# Scene = models.NetcdfModel(data_dir, path, row, time)

# print(Scene.get_variables_list())

nir = fmask.Scene.data('rtoa_865')
blue = fmask.Scene.data('rtoa_483')
green = fmask.Scene.data('rtoa_561')
red = fmask.Scene.data('rtoa_655')
swir = fmask.Scene.data('rtoa_1609')
coastal = fmask.Scene.data('rtoa_443')


os.chdir(os.path.dirname(__file__))
print(os.getcwd())
cur_dir = os.getcwd()
cur_dir = os.path.join(os.getcwd(), "")
fig_dir = cur_dir + 'results/figures/'

new = nir/coastal+red/coastal+green/coastal
csigc = (green-coastal)/(green+coastal)
# utils.save_object(new, fmask.Scene.dir_name+ '/' +str(fmask.Scene.cropping)+fmask.band_option+'coastal_ratios.pkl')
plt.imshow(new, vmax=np.mean(new))
plt.savefig(fig_dir+fmask.Scene.file_name[:fmask.Scene.file_name.index('_')]+'-'+fmask.band_option+"coastal_ratios.png")


all_ave = (nir+blue+green+red) / 4
water = fmask.water_test()
pcl = fmask.calc_pcl()
bpcl = fmask.buffer_pcl(pcl)
clear_sky_land = np.logical_and(np.invert(bpcl), np.invert(water))
csl_nir = ma.masked_where(np.invert(clear_sky_land), nir)

def shadow_morphology_land(image, csl_nir=csl_nir):
    image_shape = image.shape
    _image = np.zeros((image_shape[0]+2, image_shape[1]+2))
    _image[1:-1, 1:-1] = image
    print(image_shape, _image.shape)
    seed = np.copy(_image)
    seed[1:-1, 1:-1] = image.max()
    # seed[1:-1, 1:-1] = image.max()
    # seed[2:-2, 2:-2] = image.max()
    nir_low, nir_high = utils.calculate_percentile(csl_nir, 17.5), utils.calculate_percentile(csl_nir, 82.5)
    print(image.max(), image.mean(), nir_low, image.min())
    seed[0:1, :] = image.mean() # nir_low
    seed[-1:, :] = image.mean() # nir_low
    seed[:, 0:1] = image.mean() # nir_low
    seed[:, -1:] = image.mean() # nir_low
    # _image[1:2, :] = 0.00005 # nir_low
    # _image[-2:-1:, :] = 0.00005 # nir_low
    # _image[:, 1:2] = 0.00005 # nir_low
    # _image[:, -2:-1] = 0.00005 # nir_low
    mask = _image

    filled = reconstruction(seed, mask, method='erosion')
    result = filled - _image
    return result[1:-1, 1:-1] #, result, seed, mask

def shadow_morphology_water(image, csl_nir=csl_nir):
    image_shape = image.shape
    _image = np.zeros((image_shape[0], image_shape[1]))
    _image = image
    seed = np.copy(_image)
    seed[1:-1, 1:-1] = image.max()
    mask = _image

    filled = reconstruction(seed, mask, method='erosion')
    result = filled - _image
    return result

def shadow_morphology(image):
    image_shape = image.shape
    _image = np.zeros((image_shape[0], image_shape[1]))
    _image = image
    seed = np.copy(_image)
    seed[1:-1, 1:-1] = image.max()
    mask = _image

    filled = reconstruction(seed, mask, method='erosion')
    result = filled - _image
    return result

def make_potential_cloud_shadow_mask(nir, water, bpcl, land_threshold, water_threshold):
    water_threshold = water_threshold + 0.0005
    nir_holes = shadow_morphology(nir)
    nir_holes_l = shadow_morphology_land(nir)
    nir_holes_w = shadow_morphology_water(nir)
    return np.logical_or.reduce((nir_holes, nir_holes_l, nir_holes_w))

def make_potential_cloud_shadow_mask_2(nir, water, bpcl, land_threshold, water_threshold):
    water_threshold = water_threshold + 0.0005
    nir_holes = shadow_morphology(nir)
    nir_holes_l = shadow_morphology_land(nir)
    nir_holes_w = shadow_morphology_water(blue/red)
    nir_holes_w2 = shadow_morphology_water(nir)
    # nir_holes_masked = ma.masked_where(np.logical_or(bpcl, np.invert(water)), nir_holes)
    nir_holes_bpcl_land = np.logical_and(np.invert(np.logical_or(bpcl, water)), (nir_holes_l>0.1))
    nir_holes_bpcl_water = np.logical_and(np.invert(np.logical_or(bpcl, np.invert(water))), (nir_holes_w>0.005))
    nir_holes_bpcl_water2 = np.logical_and(np.invert(np.logical_or(bpcl, np.invert(water))), (nir_holes_w2>0.005))
    green_blue_test = (green/blue<1.0)
    return np.logical_or.reduce((nir_holes_bpcl_land, nir_holes_bpcl_water, nir_holes_bpcl_water2, green_blue_test))

def buffer_mask(stuff):
    stuff_shape = stuff.shape
    stuff_buff = np.array(np.copy(stuff))
    for x in range(1,stuff_shape[0]):
        for y in range(1,stuff_shape[1]):
            if stuff[x,y] == False:
                if np.count_nonzero(stuff[x-1:x+2,y-1:y+2]) > 4:
                    # print x,y
                    stuff_buff[x,y] = True
    selem = morphology.disk(1)
    stuff_buff = morphology.opening(stuff_buff, selem)
    selem = morphology.disk(1)
    stuff_buff = morphology.closing(stuff_buff, selem)
    return stuff_buff

def main():
    _bpcl = buffer_mask(bpcl)
    selem = morphology.disk(2)
    _bpcl = morphology.dilation(_bpcl, selem)
    pcs = make_potential_cloud_shadow_mask(nir, water, _bpcl, 0.02, 0.0005)
    pcs_buff = buffer_mask(pcs)
    # pcs_buffer = buffer_mask(pcs_buff)
    pcs_buffer = morphology.dilation(pcs_buff, selem)
    return _bpcl, pcs_buffer

if __name__ == "__main__":
    _bpcl, pcs_buffer = main()
    _bpcl = None
    # utils.save_object(pcs_buffer, fmask.Scene.dir_name+ '/' +'pcs_buffer.pkl')