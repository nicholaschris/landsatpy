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
phi0 = pi - phi_0

def max_x_y_offset(th0, phi0):
    d = 12000/30 # cloud_height(label_no)/30
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

def iter_cloud_shift(th0, phi0, cloud_height, x_inds, y_inds, tmp_shape, amxn, amxp, amyn, amyp):
    cloud_height = int((cloud_height*33) / 4)
    _tmp = np.zeros(tmp_shape)
    _tmp[y_inds, x_inds] = 1
    for height_iteration in range(0, cloud_height, 2):
        x_offset_neg, x_offset_pos, y_offset_neg, y_offset_pos = offset_sign((- (1/1)*height_iteration*tan(th0)*sin(phi0)), ( - (1/1)*height_iteration*tan(th0)*cos(phi0)))
        xon, xop, yon, yop = np.int(x_offset_neg), np.int(x_offset_pos), np.int(y_offset_neg), np.int(y_offset_pos)
        x_shifted = x_inds + xon + xop
        y_shifted = y_inds + yon + yop
        _tmp_tmp = np.zeros(tmp_shape)
        _tmp_tmp[y_shifted, x_shifted] = 1
        _tmp[y_shifted, x_shifted] = 1
    return _tmp

def iter_shadowmaker(labels, nbr_objects):
    x_offset, y_offset = max_x_y_offset(th0, phi0)
    amxn, amxp, amyn, amyp  = offset_sign(x_offset, y_offset)
    amxn, amxp, amyn, amyp = np.int(amxn), np.int(amxp), np.int(amyn), np.int(amyp)
    _tmp_shape = -amyn+labels.shape[0]+amyp, -amxn+labels.shape[1]+amxp
    shadowy = np.zeros(_tmp_shape)
    
    for label_no in range(1, (nbr_objects+1)):
        cloud_object_inds = np.where(labels==label_no)
        cloud_h = 3
        x_inds = cloud_object_inds[1] - amxn
        y_inds = cloud_object_inds[0] - amyn
        tmp = iter_cloud_shift(th0, phi0, cloud_h, x_inds, y_inds, _tmp_shape, amxn, amxp, amyn, amyp)
        shadowy += tmp
        tmp = None
    return shadowy[-amyn:_tmp_shape[0]-amyp, -amxn:_tmp_shape[1]-amxp ]

if __name__ == "__main__":
    the_shadows = iter_shadowmaker(labels, nbr_objects)