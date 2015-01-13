import operator
import pandas as pd
import numpy as np
from numpy import ma
from scipy.misc import imresize
import scipy.ndimage as ndimage
from skimage.morphology import disk, dilation

def get_truth(input_one, input_two, comparison): # too much abstraction
    ops = {'>': operator.gt,
           '<': operator.lt,
           '>=': operator.ge,
           '<=': operator.le,
           '=': operator.eq}
    return ops[comparison](input_one, input_two)
    
def convert_to_celsius(brightness_temp_input):
    return brightness_temp_input - 272.15
    
def calculate_percentile(input_masked_array, percentile): 
    flat_fill_input = input_masked_array.filled(np.nan).flatten()
    df = pd.DataFrame(flat_fill_input)
    percentile = df.quantile(percentile/100.0)
    return percentile[0]
     
def save_object(obj, filename):
    import pickle
    with open(filename, 'wb') as output:
        pickle.dump(obj, output)

def downsample(input_array, factor=4):
    output_array = input_array[::2, ::2] / 4 + input_array[1::2, ::2] / 4 + input_array[::2, 1::2] / 4 + input_array[1::2, 1::2] / 4
    return output_array

def dilate_boolean_array(input_array, disk_size=3):
    selem = disk(disk_size)
    dilated = dilation(input_array, selem)
    return dilated

def get_resized_array(img, size):
    lena = imresize(img, (size, size))
    return lena

def interp_and_resize(array, new_length):
    orig_y_length, orig_x_length = array.shape

    interp_factor_y = new_length / orig_y_length
    interp_factor_x = new_length / orig_x_length


    y = round(interp_factor_y * orig_y_length)
    x = round(interp_factor_x * orig_x_length)
    # http://docs.scipy.org/doc/numpy/reference/generated/numpy.mgrid.html
    new_indicies = np.mgrid[0:orig_y_length:y * 1j, 0:orig_x_length:x * 1j]
    # order=1 indicates bilinear interpolation.
    interp_array = ndimage.map_coordinates(array, new_indicies, 
                                           order=1, output=array.dtype)
    interp_array = interp_array.reshape((y, x))
    return interp_array

def parse_mtl(in_file):
    awesome = True
    f = open(in_file, 'r')
    print(in_file)
    mtl_dict = {}
    with open(in_file, 'r') as f:
        while awesome:
            line = f.readline()
            if line.strip() == '' or line.strip() == 'END':
                return mtl_dict
            elif 'END_GROUP' in line:
                pass
            elif 'GROUP' in line:
                curr_group = line.split('=')[1].strip()
                mtl_dict[curr_group] = {}
            else:
                attr, value = line.split('=')[0].strip(), line.split('=')[1].strip()
                mtl_dict[curr_group][attr] = value
                