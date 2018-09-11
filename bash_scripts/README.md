See this link

Google Cloud SDK
https://cloud.google.com/sdk/docs/

Landsat
https://cloud.google.com/storage/docs/public-datasets/landsat

gsutil
https://cloud.google.com/storage/docs/quickstart-gsutil

sentinel
https://cloud.google.com/storage/docs/public-datasets/sentinel-2

List all objects in a bucket
gsutil ls gs://gcp-public-data-landsat

Cape Town is:
Lat: -33.9249
Lon: 18.4241
Path: 175
Row: 84

So gs://gcp-public-data-landsat/LC08/PRE/175/084/ will list all the scenes
e.g.
gsutil ls gs://gcp-public-data-landsat/LC08/01/175/084/ > LC08-01-175-084-list.txt

T1, T2, and RT tiers. T1 is the best.
L1TP is the highest quality

Landsat Collection 1 product identifier includes the updated processing levels, processing date, Collection number, and Collection tier category

https://stackoverflow.com/questions/44051852/how-to-read-jpg2000-with-python

UTM Zone for Cape Town
34H

Tools:
https://github.com/sentinelsat/sentinelsat
https://github.com/mapbox/sentinel-tiler

# Download a dataset from google cloud
gsutil cp -r gs://gcp-public-data-landsat/LC08/01/175/084/LC08_L1TP_175084_20180826_20180830_01_T1/

This copies the folder LC08_L1TP_175084_20180826_20180830_01_T1 into you're local folder ./LC08/01/175/084/
Then you need to start processing it.

# How to view the JPG version
https://medium.com/@nick_pringle/how-to-use-free-satellite-images-to-learn-about-our-world-86d1bcab45fe

# Install GDAL
brew install gdal

# Mapbox info
https://www.mapbox.com/help/processing-satellite-imagery/