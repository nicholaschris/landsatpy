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

bqa_cloud = np.logical_or.reduce((bqa==61440, bqa==59424, bqa==57344, bqa==56320, bqa==53248))


def make_cloud_list():
    cloud_list = []
    for i in range(2**16):
        if bin(i)[2:4] == '11':
            print(i)
            cloud_list.append(i)
    return cloud_list
