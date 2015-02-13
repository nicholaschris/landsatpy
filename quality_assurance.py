import models
import config as cfg
import imp
import numpy as np

import views

theCMG = views.create_cm_greys()
imp.reload(cfg)

bqa_str = 'bqa'

Scene = Scene = models.NetcdfVarModel(cfg.data_dir, cfg.path, cfg.row, cfg.time, bqa_str)
bqa = Scene.data(bqa_str)

qa_clouds = [61440, 59424, 57344, 56320, 53248, 39936, 36896, 36864]

min_cirrus = 32768 # '0b1000000000000000' in binary i.e probably a cirrus cloud
min_cloud = 49152 # '0b1100000000000000' in binary i.e probably a cloud

#bqa_cloud = np.logical_or.reduce((bqa==61440, bqa==59424, bqa==57344, bqa==56320, bqa==53248))
bqa_cloud = bqa > 32767


def make_cloud_list():
    cloud_list = []
    for i in range(2**16):
        if bin(i)[2:4] == '11':
            print(i)
            cloud_list.append(i)
    return cloud_list

def all_numbers_that_are_clouds():
    cloud_numbers = []
    for number in range(int('0b'+16*'1'), base=2):
        if bin(number)[2:4] == '11':
            cloud_numbers.append(number)
    return cloud_numbers