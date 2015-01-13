import models 
import utils
import views
import numpy as np
from numpy import ma
import config
import imp

imp.reload(config)
imp.reload(models)
imp.reload(utils)

data_dir = config.data_dir
path = config.path
row = config.row
time = config.time

band_option = config.band_option
b = band_option

# Scene = models.NetcdfModel(data_dir, path, row, time)
# Scene = models.NetcdfVarModel(data_dir, path, row, time, 'rtoa_1373')

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

mask = get_mask()

def get_var(var, mask=mask):
    mask = utils.get_resized_array(mask, 2048) # get_mask()
    result = get_var_before_mask(var)

    result = utils.interp_and_resize(result, 2048)
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

coastal = get_coastal()
blue = get_blue()
green = get_green()
red = get_red()
nir = get_nir()
cirrus = get_cirrus()


