# import models 
# import utils
# import views
# import numpy as np
# from numpy import ma
# import config



# imp.reload(config)
# imp.reload(models)
# imp.reload(utils)
import numpy as np
import bands
import imp
imp.reload(bands)


# data_dir = config.data_dir
# path = config.path
# row = config.row
# time = '2014251' # config.time

# band_option = config.band_option
# b = band_option

rhow_raw = bands.get_var_before_mask('rhow_655')
rhow = np.ma.masked_where(rhow_raw<0, rhow_raw)
rhow = rhow[3000:6000, 1500:4500]

lat = bands.get_var_before_mask('lat')[3000:6000, 1500:4500]
lon = bands.get_var_before_mask('lon')[3000:6000, 1500:4500]

# Nechad 2009
A_t = 235.32
B_t = 0.33
turbidity_first = A_t * rhow

# Vanhellemont and Ruddick 2014
A = 289.29 # g*m**(-3)
C = 0.1686
SPM = (A * rhow) / (1 - (rhow / C))

turbidity =  (A_t * rhow) / (1 - (rhow / C)) + B_t

def reject_outliers(data, m = 2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s<m]

def mask_outliers(data):
    output_data = np.ma.masked_where(data>np.percentile(data, 95), data)
    output_data = np.ma.masked_where(data<-np.percentile(data, 95), output_data)
    return output_data

turbidity_clean = mask_outliers(turbidity)
SPM_clean = mask_outliers(SPM)
rhow_nan_mask = np.ma.masked_where(rhow==np.nan, rhow)

def average_pixels(input, res):
    output = np.zeros((input.shape))
    for i in range(0, input.shape[0], res):
        for j in range(0, input.shape[0], res):
            output[i:i+res, j:j+res] = np.mean(input[i:i+res, j:j+res])
    return output

def stdev_pixels(input, res):
    output = np.zeros((input.shape))
    for i in range(0, input.shape[0], res):
        for j in range(0, input.shape[0], res):
            output[i:i+res, j:j+res] = np.std(input[i:i+res, j:j+res])
    return output

modis_mean = average_pixels(rhow_nan_mask, 10)
seviri_mean = average_pixels(rhow_nan_mask, 100)

modis_stdev = stdev_pixels(rhow_nan_mask, 10)
seviri_stdev = stdev_pixels(rhow_nan_mask, 100)


s_y_inds = np.where(seviri_stdev==seviri_stdev.max())[0]
s_x_inds = np.where(seviri_stdev==seviri_stdev.max())[1]
s_y_start = s_y_inds[0]
s_x_start = s_x_inds[0]

m_y_inds = np.where(modis_stdev==modis_stdev.max())[0]
m_x_inds = np.where(modis_stdev==modis_stdev.max())[1]
m_y_start = m_y_inds[0]
m_x_start = m_x_inds[0]

max_m_stdev = rhow_nan_mask[m_y_start:m_y_start+10, m_x_start:m_x_start+10]
max_s_stdev = rhow_nan_mask[s_y_start:s_y_start+100, s_x_start:s_x_start+100]

rhow_nan_mask_loc_seviri = np.array(rhow_nan_mask)
rhow_nan_mask_loc_modis = np.array(rhow_nan_mask)

rhow_nan_mask_loc_modis[m_y_start:m_y_start+10, m_x_start:m_x_start+10] = 9999
rhow_nan_mask_loc_seviri[s_y_start:s_y_start+100, s_x_start:s_x_start+100] = 9999

