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
from math import *
import imp

imp.reload(count_clouds)

pcl = cloud_detection.calc_pcl()
labels, nbr_objects = count_clouds.label_clouds(pcl,3,9)
label_no = 4

data_dir = config.data_dir
path = config.path
row = config.row
time = config.time

band_option = config.band_option
b = band_option

# Scene = models.NetcdfModel(data_dir, path, row, time)
# Scene.get_variables_list()
# btc = utils.convert_to_celsius(Scene.data('BT_B10'))
# btc[np.where(btc<0)] = 0
# btc[np.where(btc>27)] = 27

th0 = Scene.theta_0
phi0 = pi - (Scene.phi_0)
# _bpcl, pcs_buffer = cloud_shadow_morphology.main()
_bpcl = None

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

def calc_temp_percentiles():
    csl_bt = fmask.clear_sky_land_brightness_temp()
    t_low, t_high = utils.calculate_percentile(csl_bt, 17.5), utils.calculate_percentile(csl_bt, 82.5)
    return t_low, t_high

def create_zeros_array(input_array):
    new_shape = input_array.shape
    output_array = np.zeros(new_shape)
    return output_array


def calc_mean_water_pixel_btc():
    water_pixel_btc = ma.masked_where(np.invert(fmask.water_test()), btc)
    return ma.mean(water_pixel_btc)

def cloud_base_height(label_no):

    cloud_object_btc = ma.masked_where(labels!=label_no, btc)
    
    cloud_height_array = create_zeros_array(cloud_object_btc)

    area = ma.count(cloud_object_btc)
    radius = np.sqrt(area/(2*np.pi)) # confusion as to whether 2 should be included

    if radius >= 8:
        # print("Radius is: ", radius)
        t_cloudbase = utils.calculate_percentile(cloud_object_btc, (((radius- 8)**2)/radius**2))
        # print("Cloudbase temp is: ",t_cloudbase)
    else:
        t_cloudbase = cloud_object_btc.min()

    cloud_object_btc[np.where(cloud_object_btc>t_cloudbase)] = t_cloudbase

    # t_low, t_high = utils.calculate_percentile(cloud_object_btc, 17.5), utils.calculate_percentile(cloud_object_btc, 82.5)
    

    h_cloudbase = max(0.2, (t_low-4-t_cloudbase)/9.8), min(12, (t_high +4-t_cloudbase))

    t_cloudtop = np.percentile(cloud_object_btc, 12.5) # cloud_object_btc.min() # not clear in paper
    h_cloudtop = np.max(np.array(h_cloudbase)) # + 6.5*(t_cloudbase-t_cloudtop)
    h_cloud_top = 0.2+(t_high - t_cloudbase)/6.5
    # h_cloudtop_two = np.max(np.array(h_cloudbase)) + 6.5*(t_cloudbase-t_cloudtop)
    # print(h_cloudbase)
    # h_cloudtop = (h_cloudtop_one + h_cloudtop_two) / 2
    print(h_cloudbase, h_cloudtop, t_cloudtop, t_cloudbase-t_cloudtop)
    # return h_cloudbase, h_cloudbase[1], h_cloudtop, t_cloudtop, t_cloudbase-t_cloudtop
    # cloud_height_array[np.where(labels==label_no)] = h_cloudtop_two
    return h_cloudtop

def max_x_y_offset(th0, phi0):
    d = 12000/30 # cloud_height(label_no)/30
    x_offset = - d*tan(th0)*sin(phi0)
    y_offset = - d*tan(th0)*cos(phi0)
    return x_offset, y_offset

def create_expanded_zone():
    x_offset, y_offset = max_x_y_offset(th0, phi0)
    amxn, amxp, amyn, amyp  = offset_sign(x_offset, y_offset)
    amxn, amxp, amyn, amyp = np.int(amxn), np.int(amxp), np.int(amyn), np.int(amyp)
    _tmp_shape = -amyn+labels.shape[0]+amyp, -amxn+labels.shape[1]+amxp
    shadowy = np.zeros(_tmp_shape)
    return shadowy, _tmp_shape

def iter_cloud_x_y_offset(th0, phi0, cloud_height):
    x_offset = []
    y_offset = []
    cloud_height = cloud_height*1000/30
    for height_iteration in range(0, np.int(cloud_height)):
        x_offset.append(- (1/1)*height_iteration*tan(th0)*sin(phi0))
        y_offset.append( - (1/1)*height_iteration*tan(th0)*cos(phi0))
    return x_offset, y_offset


def iter_cloud_shift(th0, phi0, cloud_height, x_inds, y_inds, tmp_shape, amxn, amxp, amyn, amyp):
    cloud_height = cloud_height*33
    print(cloud_height)
    _tmp = np.zeros(tmp_shape)
    _tmp[y_inds, x_inds] = 1
    for height_iteration in range(0, np.int(cloud_height*0.9), 2):
        # print(height_iteration)
        x_offset_neg, x_offset_pos, y_offset_neg, y_offset_pos = offset_sign((- (1/1)*height_iteration*tan(th0)*sin(phi0)), ( - (1/1)*height_iteration*tan(th0)*cos(phi0)))
        xon, xop, yon, yop = np.int(x_offset_neg), np.int(x_offset_pos), np.int(y_offset_neg), np.int(y_offset_pos)
        x_shifted = x_inds + xon + xop
        y_shifted = y_inds + yon + yop
        # print(x_shifted, y_shifted)
        # _tmp[y_shifted, x_shifted] = 1 # put in if statement
        _tmp_tmp = np.zeros(tmp_shape)
        _tmp_tmp[y_shifted, x_shifted] = 1
        # mask = ma.masked_where(_tmp_tmp[-amyn:tmp_shape[0]-amyp, -amxn:tmp_shape[1]-amxp ]==1, pcs_buffer)
        # mask = np.logical_and(pcs_buffer, _tmp_tmp[-amyn:tmp_shape[0]-amyp, -amxn:tmp_shape[1]-amxp ]) # NB
        # mask = pcs_buffer + _tmp_tmp[-amyn:tmp_shape[0]-amyp, -amxn:tmp_shape[1]-amxp ]
        # mask = ma.masked_where(np.invert(mask), mask) # NB
        # print(ma.count(mask), np.count_nonzero(_tmp))
        # if ma.count(mask) > np.count_nonzero(_tmp)/4: #NB
        #     print("Match")
        #     _tmp[y_shifted, x_shifted] = 1
        _tmp[y_shifted, x_shifted] = 1
    return _tmp

def iter_shadowmaker(labels, nbr_objects):
    x_offset, y_offset = max_x_y_offset(th0, phi0)
    amxn, amxp, amyn, amyp  = offset_sign(x_offset, y_offset)
    amxn, amxp, amyn, amyp = np.int(amxn), np.int(amxp), np.int(amyn), np.int(amyp)
    _tmp_shape = -amyn+labels.shape[0]+amyp, -amxn+labels.shape[1]+amxp
    shadowy = np.zeros(_tmp_shape)
    
    for label_no in range(1, (nbr_objects+1)):
        print("Label No: ", label_no)
        cloud_object_inds = np.where(labels==label_no)
        cloud_h = 12 # cloud_base_height(label_no)
        cloud_h = 6 # Speed things up
        print("Cloud Height: ", cloud_h)
        
        x_inds = cloud_object_inds[1] - amxn
        y_inds = cloud_object_inds[0] - amyn
        
        tmp = iter_cloud_shift(th0, phi0, cloud_h, x_inds, y_inds, _tmp_shape, amxn, amxp, amyn, amyp)

        shadowy += tmp
        tmp = None
    return shadowy[-amyn:_tmp_shape[0]-amyp, -amxn:_tmp_shape[1]-amxp ]

print("There are %s clouds." % nbr_objects)
mean_water_pixel_btc = calc_mean_water_pixel_btc()
t_low, t_high = calc_temp_percentiles()
# cloud_height_array = create_zeros_array(labels)
# cloud_height_list=[]
# for label_no in range(1, nbr_objects+1):
#     print("Cloud Number ", label_no)
    # cloud_height_array += cloud_base_height(label_no)
    # cloud_height_list.append(cloud_base_height(label_no))

if __name__ == "__main__":
    shadowy = iter_shadowmaker(labels, nbr_objects)
    # utils.save_object(pcs_buffer, fmask.Scene.dir_name+ '/' + band_option +'shadowy.pkl')
    # os.chdir(os.path.dirname(__file__))
    # print(os.getcwd())
    # cur_dir = os.getcwd()
    # cur_dir = os.path.join(os.getcwd(), "")
    # fig_dir = cur_dir + 'results/figures/'
    # theCMG = views.create_cm_greys()
    # plt.close('all')
    # plt.imshow(shadowy, cmap = theCMG)
    # plt.show()
