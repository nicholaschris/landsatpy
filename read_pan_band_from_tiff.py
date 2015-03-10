# read_pan_band_from_tiff.py
import sys
import models
import imp
imp.reload(models)


DATA_DIR = "/home/nicholas/Documents/data/"
path = sys.argv[1]
row = sys.argv[2]
time = sys.argv[3]

TiffArray = models.GeotiffBandModel(DATA_DIR, path, row, time, band_no=8)
# TiffArray.setup()
bounds = (1500, 1500, 4500, 4500)
bounds = (4500, 4500, 6500, 6500)
tiff_data = TiffArray.data(bounds)