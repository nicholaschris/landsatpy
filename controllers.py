# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 14:49:04 2014

@author: Nicholas
"""

from __future__ import print_function, division
import models
import views
from math import cos, radians

LC = 'LC8'
path = '171'
row = '084'
time = '2014279'
misc = 'LGN00'
band = '_B'
end = '.TIF'
mtl_end = '_MTL.txt'

DATA_DIR = "highroc/data/"  # 'D:\\Nicholas\\Data\\'
#FULL_DIR = DATA_DIR + LC + '\\' + path + '\\' + row + '\\' +LC+path+row+ time + misc + '\\'
##DIR = 'D:\\Nicholas\\Data\\LC8171084\\'
#tiff_file = FULL_DIR+LC+path+row+time+misc+band
#mtl_file = FULL_DIR+LC+path+row+time+misc


def dn_to_rtoa(band_no):
    bounds = (1000, 1000, 1000, 1000)
    band_no = str(band_no)
    TiffArray = models.GeotiffObject(DATA_DIR, path, row, time, band_no)
    TiffArray.setup()
    tiff_data = TiffArray.data(band_no, bounds)
    arr = tiff_data
    se = float(TiffArray.mtl_dict['IMAGE_ATTRIBUTES']['SUN_ELEVATION'])
    m_p = float(TiffArray.mtl_dict['RADIOMETRIC_RESCALING']['REFLECTANCE_MULT_BAND_'+band_no])
    a_p = float(TiffArray.mtl_dict['RADIOMETRIC_RESCALING']['REFLECTANCE_ADD_BAND_'+band_no])
    rho_prime = (arr * m_p) + a_p
    return rho_prime/cos(radians(se))
    
def get_red():
    return dn_to_rtoa(4)
    
def get_green():
    return dn_to_rtoa(3)
    
def get_blue():
    return dn_to_rtoa(2)
    
if __name__ == "__main__":
    img = views.create_rgb()