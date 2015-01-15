import io

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np 

# filename = '/home/nicholas/Documents/data/LC8/196/030/LC81960302014022LGN00/LC81960302014022LGN00_RGB_RCO.jpg's
# filename = '/home/nicholas/Documents/data/LC8/199/024/LC81990242013232LGN00/LC81990242013232LGN00_RGB_RCO.jpg'
filename = '/home/nicholas/Documents/data/LC8/199/024/LC81990242013280LGN00/LC81990242013280LGN00_RGB_RCO.jpg'

img = mpimg.imread(filename)

# with open('/home/nicholas/Documents/data/LC8/196/030/LC81960302014022LGN00_RGB_RCO.jpg', 'rb') as inf:
#     jpgdata = inf.read()
 
# if jpgdata.startswith(b'\xff\xd8'):
#     text = u'This is a jpeg file (%d bytes long)\n'
# else:
#     text = u'This is a random file (%d bytes long)\n'
 
# with io.open('summary.txt', 'w', encoding='utf-8') as outf:
#     outf.write(text % len(jpgdata))