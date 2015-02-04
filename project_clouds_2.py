import os
import models
import views
import config
import count_clouds
import utils
import cloud_detection
# import cloud_shadow_morphology
import skimage
import numpy as np
from numpy import ma
from matplotlib import pyplot as plt
from math import pi, tan, cos, sin
import imp

imp.reload(cloud_detection)
imp.reload(config)
imp.reload(models)
imp.reload(utils)

data_dir = config.data_dir
path = config.path
row = config.row
time = config.time

band_option = config.band_option
b = band_option

pcp = cloud_detection.calc_pcp()
pcl = cloud_detection.calc_pcl(pcp)
pcp = None
bpcl = bpcl = utils.dilate_boolean_array(pcl)
pcl = None
bpcl = bpcl == 255
labels, nbr_objects = count_clouds.label_clouds(bpcl,1,2)

def get_meta(var):
    Scene = models.NetcdfVarModel(data_dir, path, row, time, var)
    bt_10 = Scene.data(var)
    dimensions=    Scene.dimensions
    theta_v =   Scene.theta_v
    theta_0=    Scene.theta_0
    phi_v =   Scene.phi_v
    phi_0=    Scene.phi_0
    return bt_10, dimensions, theta_v, theta_0, phi_v, phi_0

bt_10, dimensions, theta_v, theta_0, phi_v, phi_0 = get_meta('BT_B10')
th0 = theta_0
phi0 = pi - phi_0 # 180deg - azimuth angle

def max_x_y_offset(th0, phi0):
    d = 12000/30/4 # cloud_height(label_no)/30
    x_offset = - d*tan(th0)*sin(phi0)
    y_offset = - d*tan(th0)*cos(phi0)
    return x_offset, y_offset

def offset_sign(x_offset, y_offset):
    if x_offset <= 0:
        x_offset_neg, x_offset_pos = x_offset, 0
    if y_offset <= 0:
        y_offset_neg, y_offset_pos = y_offset, 0
    if x_offset > 0:
        x_offset_neg, x_offset_pos = 0, x_offset
    if y_offset > 0:
        y_offset_neg, y_offset_pos = 0, y_offset
    return x_offset_neg, x_offset_pos, y_offset_neg, y_offset_pos

def create_expanded_zone(labels=labels):
    x_offset, y_offset = max_x_y_offset(th0, phi0)
    amxn, amxp, amyn, amyp  = offset_sign(x_offset, y_offset)
    amxn, amxp, amyn, amyp = np.int(amxn), np.int(amxp), np.int(amyn), np.int(amyp)
    _tmp_shape = -amyn+labels.shape[0]+amyp, -amxn+labels.shape[1]+amxp
    shadowy = np.zeros(_tmp_shape)
    return shadowy, _tmp_shape

def iter_shadowmaker(labels, nbr_objects):
    x_offset, y_offset = max_x_y_offset(th0, phi0)
    amxn, amxp, amyn, amyp  = offset_sign(x_offset, y_offset)
    amxn, amxp, amyn, amyp = np.int(amxn), np.int(amxp), np.int(amyn), np.int(amyp)
    print(amxn, amxp, amyn, amyp)
    _tmp_shape = -amyn+labels.shape[0]+amyp, -amxn+labels.shape[1]+amxp
    shadowy = np.zeros(_tmp_shape)
    # test = np.zeros(_tmp_shape)
    
    for label_no in range(1, (nbr_objects+1)): # nbr_objects+1
        cloud_object_inds = np.where(labels==label_no)
        x_inds = cloud_object_inds[1] - amxn + amxn + amxp
        y_inds = cloud_object_inds[0] - amyn + amyn + amyp
        shadowy[y_inds, x_inds] = label_no
        # test[cloud_object_inds[0], cloud_object_inds[1]] = label_no
    # return shadowys
    return shadowy[-amyn:_tmp_shape[0]-amyp, -amxn:_tmp_shape[1]-amxp ]

if __name__ == "__main__":
    shad = iter_shadowmaker(labels, nbr_objects)

'''
for cloud in list of clouds:
    make a bigger area
    shift cloud required space

def shift cloud required space(th0, phi0):
    distance = 12*tan(th0) # the projection distance
    x_offset = - d*tan(th0)*sin(phi0)
    y_offset = - d*tan(th0)*cos(phi0) # the x and y coords in unit terms (check pos neg values)
    the x and y coords scaled to the projection distance
'''