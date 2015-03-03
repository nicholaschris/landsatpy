import cloud_detection_new as cloud_detection
import utils 
import numpy as np
from numpy import ma
from skimage import morphology
from skimage.morphology import reconstruction

nir = cloud_detection.get_nir()
red = cloud_detection.get_red()
green = cloud_detection.get_green()
blue = cloud_detection.get_blue() # or use coastal
coastal = cloud_detection.get_coastal()
marine_shadow_index = (green-blue)/(green+blue)

water = cloud_detection.water_test()
pcp = cloud_detection.calc_pcp()
pcl = cloud_detection.calc_pcl(pcp)
bpcl = utils.dilate_boolean_array(pcl)
clear_sky_land = np.logical_and(np.invert(bpcl), np.invert(water))
csl_nir = ma.masked_where(np.invert(clear_sky_land), nir)

def shadow_morphology_land(image, csl_nir=csl_nir):
    image_shape = image.shape
    _image = np.zeros((image_shape[0]+2, image_shape[1]+2))
    _image[1:-1, 1:-1] = image
    print(image_shape, _image.shape)
    seed = np.copy(_image)
    seed[1:-1, 1:-1] = image.max()
    nir_low, nir_high = utils.calculate_percentile(csl_nir, 17.5), utils.calculate_percentile(csl_nir, 82.5)
    print(image.max(), image.mean(), nir_low, image.min())
    seed[0:1, :] = image.mean() # nir_low
    seed[-1:, :] = image.mean() # nir_low
    seed[:, 0:1] = image.mean() # nir_low
    seed[:, -1:] = image.mean() # nir_low
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

shadows_land = shadow_morphology_land(nir, csl_nir=csl_nir)
shadows_water = shadow_morphology_water(marine_shadow_index, csl_nir=csl_nir)

land_shadow_mask = np.logical_and(shadows_land>0.02, clear_sky_land)
water_shadow_mask = np.logical_and(shadows_water>0.02, water)

from views import create_composite, create_cm_greys, create_cm_orange, create_cm_blues
from skimage import exposure
from matplotlib import pyplot as plt
import matplotlib as mpl
plt.style.use('ggplot')
mpl.rcParams.update({'font.weight': 'light'})
mpl.rcParams.update({'font.family': 'Arial'})
mpl.rcParams.update({'font.size': 10})

img = create_composite(red, green, blue)
img = exposure.rescale_intensity(img, in_range=(0, 95))

output_dir = '/home/nicholas/Documents/highroc/output/'

scene = cloud_detection.path+cloud_detection.row+cloud_detection.time

theCMB = create_cm_blues()
theCMO = create_cm_orange()
theCMG = create_cm_greys()

plt.close('all')
plt.imshow(img)
plt.savefig(output_dir+scene+'-rgb.png', dpi=600)

plt.close('all')
plt.imshow(clear_sky_land, cmap=theCMG, alpha=0.4)
plt.imshow(water_shadow_mask, cmap=theCMB)
plt.imshow(land_shadow_mask, cmap=theCMG)
plt.imshow(bpcl, cmap=theCMO)

plt.savefig(output_dir+scene+'-mask.png', dpi=600)