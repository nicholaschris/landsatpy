from osgeo import gdal

# Assume this retrieves the dataset from a GeoTIFF file.
dataset = getDataSet(tiffFileLocation)      

saveOptions = []
saveOptions.append("QUALITY=75")

# Obtains a JPEG GDAL driver
jpegDriver = gdal.GetDriverByName("JPEG")   

# Create the .JPG file
jpegDriver.CreateCopy("imageFile.jpg", dataset, 0, saveOptions) 