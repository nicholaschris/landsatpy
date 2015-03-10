from netCDF4 import Dataset
import numpy as np

lat = list(range(100))
lon = list(range(100))
val = list(range(100))
t = list(range(100))
#create a netCDF4 file
rootgrp = Dataset('test.nc', 'w', format='NETCDF4')
print(rootgrp.data_model)
#create a group
rootgrp.createGroup('forecasts')
#create dimensions
lat_dim = rootgrp.createDimension('lat', len(lat))
lon_dim = rootgrp.createDimension('lon', len(lon))
value_dim = rootgrp.createDimension('value', len(val))
time = rootgrp.createDimension('time', None)
#create variables
latitudes = rootgrp.createVariable('latitude','f4',('lat',))
longitudes = rootgrp.createVariable('longitude','f4',('lon',))
values = rootgrp.createVariable('value','f4',('value',))
times = rootgrp.createVariable('time','f8',('time',))
temp = rootgrp.createVariable('temp','f4',('lat','lon','value','time'))
print(rootgrp.variables)
#write attributes
rootgrp.description = 'none'
history = "I don't know"
rootgrp.history = 'Created ' + history
rootgrp.source = 'geotiff2netcdf.py'
latitudes.units = 'degrees north'
longitudes.units = 'degrees east'
values.units = ''
temp.units = 'K'
times.units = 'hours since 0001-01-01 00:00:00.0'
times.calendar = 'gregorian'
#write data
latitudes[:] = lat
longitudes[:] = lon
values[:] = val
times[:] = t
print(type(temp))
temp.setncatts({'lat':lat,'lon':lon,'value':val,'time':t})
print('ncattrs LAT ',temp.getncattr('lat'))
print('ncattrs LON ',temp.getncattr('lon'))
print('ncattrs VALUE ',temp.getncattr('value'))
print('ncattrs TIME ',temp.getncattr('time'))
#close file
rootgrp.close()