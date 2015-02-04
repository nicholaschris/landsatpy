import models
import config
import utils
import imp
import numpy as np
from numpy import ma

imp.reload(config)
imp.reload(models)
imp.reload(utils)

data_dir = config.data_dir
path = config.path
row = config.row
time = '2014251' # config.time

band_option = config.band_option
b = band_option
def get_var_before_mask(var):
    Scene = models.NetcdfVarModel(data_dir, path, row, time, var)
    # return utils.interp_and_resize(Scene.data(var), 2048)
    return Scene.data(var)
    

def get_mask():
    mask = get_var_before_mask('BT_B10')
    # mask[np.where(mask!=0)] = 99

    mask[np.where(mask<200)] = 1e12
    mask[np.where(mask<1e10)] = 0
    mask[np.where(mask==1e12)] = 255
    # mask = ma.masked_where(mask==0, mask)
    # mask[np.where(mask==True)] = 0
    # mask[np.where(mask==False)] = 1
    return mask

def get_angles():
    Scene = models.NetcdfVarModel(data_dir, path, row, time, 'BT_B10')
    Scene.setup_file()
    Scene.connect_to_nc()
    scene_attributes = {}
    scene_attributes['dimensions'] = Scene.dimensions
    scene_attributes['theta_v'] = Scene.theta_v 
    scene_attributes['theta_0 '] = Scene.theta_0 
    scene_attributes['phi_v '] = Scene.phi_v 
    scene_attributes['phi_0'] = Scene.phi_0 
    return scene_attributes

# scene_attributes = get_angles()
mask = get_mask()

def get_var(var, mask=mask, resolution=2048):
    mask = utils.get_resized_array(mask, resolution) # get_mask()
    result = get_var_before_mask(var)

    result = utils.interp_and_resize(result, resolution)
    print(result.shape)
    result = ma.masked_where(mask==255, result)
    return result

def get_coastal():
    return get_var(b+'443')

def get_blue():
    return get_var(b+'483')

def get_green():
    return get_var(b+'561')

def get_red():
    return get_var(b+'655')

def get_nir():
    return get_var(b+'865')

def get_swir():
    return get_var(b+'1609')

def get_swir2():
    return get_var(b+'2201')

def get_cirrus():
    return get_var('rtoa_1373')

def get_temp():
    return get_var('BT_B10')

def get_bqa():
    return get_var('bqa')

# print(Scene.get_variables_list())

def calc_ndsi():
    green = get_green()
    swir = get_swir()
    return (green - swir)/(green + swir)

def calc_ndvi():
    nir = get_nir()
    red = get_red()
    return (nir - red)/(nir + red)