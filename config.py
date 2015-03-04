# config.py
import sys
print("Trying to work out scene!")
try:
    scene_id = sys.argv[1]
    print(scene_id)
    input("Press Enter")
    path = scene_id[3:6]
    row = scene_id[6:9]
    time = scene_id[9:16]
    print(path, row, time)
except IndexError as e:
    print(e)
 
# defaults
data_dir = "Documents/data/"
band_option = 'rrc_'
resolution_global_var = False
ul = (1500,1500)
len_sq = 4000

# List of available scenes:

# path = '012'
# row = '054'
# time = '2013154'

# path = '199'
# row = '024'
# time = '2013280'
# time = '2013232'
# time = '2014251'

#path = '200'
#row = '024'
#time = '2014258'

### End of list

# data_dir = "Documents/data/"
# path = '170'
# row = '078'
# time = '2013269'

# data_dir = "Documents/data/"
# path = '176'
# row = '083'
# time = '2014010'

# data_dir = "Documents/data/"
# path = '176'
# row = '083'
# time = '2014218'


# data_dir = "Documents/data/"
# path = '199'
# row = '024'
# time = '2013232'

# data_dir = "Documents/data/"
# path = '199'
# row = '024'
# time = '2013280'

# data_dir = "Documents/data/"
# path = '196'
# row = '030'
# time = '2014022'

# data_dir = "Documents/data/"
# path = '012'
# row = '054'
# time = '2013154'

# data_dir = "Documents/data/"
# path = '200'
# row = '024'
# time = '2014258'

# data_dir = "Documents/data/"
# path = '199'
# row = '024'
# time = '2013280'
# band_option = 'rhow_'
# band_option = 'rrc_'
# resolution_global_var = False
# ul = (1500,1500)
# len_sq = 4000
# band_option = 'rrc_'
# band_option = 'rtoa_'
