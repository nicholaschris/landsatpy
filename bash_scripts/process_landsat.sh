#! /bin/bash

# Convert Landsat 8 GeoTIFF images into RGB pan-sharpened JPEGs.

# Requirements:
#              * gdal (homebrew)
#              * convert (image-magick)

###############################
### MAPBOX tutorial version ###
###############################

# #establish an id variable
id=$1
DIRECTORY=$2
mkdir ./tmp/

if [[ -z "$1" ]]; then
	echo "Landsat image processing"
	echo ""
	echo "Converts to 8-bit, merges RGB, pan-sharpens, colour corrects and converts to JPG"
	echo "Example: process_landsat $1"
	echo "Output: $DIRECTORY"
	exit 0
fi

#use a for loop to reproject each of the bands you will be working with.
for BAND in {8,4,3,2}; do
 gdalwarp -t_srs EPSG:3857 $id"_B"$BAND.tif ./tmp/$BAND-projected.tif;
done

#translate each of your bands into the 8-bit format with default settings of -ot and -scale
echo "translating to 8-bit"
gdal_translate -ot Byte -scale 0 65535 0 255 ./tmp/4-projected{,-scaled}.tif
gdal_translate -ot Byte -scale 0 65535 0 255 ./tmp/3-projected{,-scaled}.tif
gdal_translate -ot Byte -scale 0 65535 0 255 ./tmp/2-projected{,-scaled}.tif

gdal_translate -ot Byte -scale 0 65535 0 255 ./tmp/8-projected{,-scaled}.tif

#merge the three reprojected band images into a single composite image
echo "merge into composite"
gdal_merge.py -v -ot Byte -separate -of GTiff -co PHOTOMETRIC=RGB -o ./tmp/$id-RGB-scaled.tif ./tmp/4-projected-scaled.tif ./tmp/3-projected-scaled.tif ./tmp/2-projected-scaled.tif

# ~ merge not reprojected stuff
echo "merge not reprojected stuff into composite"
gdal_merge.py -o ./tmp/$id-RGB.tif -separate "$id"_B4.TIF "$id"_B3.TIF "$id"_B2.TIF -co PHOTOMETRIC=RGB -co COMPRESS=LZW

# ~ pansharpen the not reprojected merged image
echo "pansharpen the not reprojected merged image"
gdal_pansharpen.py "$id"_B8.TIF ./tmp/$id-RGB.tif ./tmp/$id-RGB-pan.tif -r bilinear -co COMPRESS=LZW -co PHOTOMETRIC=RGB

# ~ pansharpen the reprojected merged image
echo "pansharpen the reprojected merged image"
gdal_pansharpen.py ./tmp/8-projected-scaled.tif ./tmp/$id-RGB-scaled.tif ./tmp/$id-RGB-scaled-pan.tif -r bilinear -co COMPRESS=LZW -co PHOTOMETRIC=RGB

# ~ pansharpen the not reprojected merged image
echo "Get a subset of the pansharpened image"
gdal_translate -srcwin 4600 1500 6000 6000 ./tmp/$id-RGB-scaled-pan.tif ./tmp/$id-RGB-scaled-pan-subset.tif

#color correct blue bands to deal with haze and correct across all brands for brightness, contrast and saturation
echo "color correct blue bands"
convert -channel B -gamma 1.05 -channel RGB -sigmoidal-contrast 20,20% -modulate 100,150 ./tmp/$id-RGB-scaled.tif ./tmp/$id-RGB-scaled-cc.tif
convert -channel B -gamma 1.05 -channel RGB -sigmoidal-contrast 20,20% -modulate 100,150 ./tmp/$id-RGB-scaled-pan-subset.tif ./tmp/$id-RGB-scaled-pan-cc-subset.tif


#use a cubic downsampling method to add overview
echo "use a cubic downsampling"
gdaladdo -r cubic ./tmp/$id-RGB-scaled-cc.tif 2 4 8 10 12

#call the TIFF worldfile for the requested image
echo "call the TIFF worldfile for the requested image"
listgeo -tfw ./tmp/3-projected.tif

#change name of file to match file needing georeference
echo "change name of file to match file needing georeference"
mv ./tmp/3-projected.tfw ./tmp/$id-RGB-scaled-cc.tfw

#georeference the image
echo "georeference the image"
gdal_edit.py -a_srs EPSG:3857 ./tmp/$id-RGB-scaled-cc.tif

#remove black background
echo "remove black background"
gdalwarp -srcnodata 0 -dstalpha ./tmp/$id-RGB-scaled-cc.tif ./tmp/$id-RGB-scaled-cc-2.tif

# Do the subsetting stuff
for BAND in {7,5,4,3,2}; do
  gdal_translate -srcwin 2300 750 3000 3000 $id"_B"$BAND.tif ./tmp/$BAND-subset.tif;
done

# create rgb
convert -combine ./tmp/{4,3,2}-subset.TIF ./tmp/"$id"-rgb-subset.tif

# create optimised rgb
convert -channel B -gamma 0.925 -channel R -gamma 1.03 \
-channel RGB -sigmoidal-contrast 50x16% ./tmp/"$id"-rgb-subset.tif ./tmp/"$id"-rgb-cc-subset.tif


# gdal_translate -srcwin 2300 750 3000 3000 $id"_B8".tif ./tmp/8-subset.tif
gdal_translate -srcwin 4600 1500 6000 6000 $id"_B8".tif ./tmp/8-subset.tif
# gdal_translate -srcwin 2300 750 3000 3000 ./tmp/$id-RGB.tif ./tmp/$id-RGB-subset.tif;
gdal_pansharpen.py ./tmp/8-subset.tif ./tmp/"$id"-rgb-subset.tif ./tmp/$id-pan-subset.tif

# convert -channel B -gamma 0.925 -channel R -gamma 1.03 \
# -channel RGB -sigmoidal-contrast 50x16% ./tmp/$id-pan-subset.tif ./tmp/$id-cc-pan-subset.tif

convert ./tmp/$id-pan-subset.tif ./tmp/$id-pan-subset.jpg
convert -verbose -channel B -gamma 0.8 -quality 95 ./tmp/$id-pan-subset.tif ./tmp/final-pan-rgb-corrected.jpg

#Move the tmp folder
echo "Move the tmp folder"
rsync -a ./tmp/ $DIRECTORY/$1/
rm -rf ./tmp

#########################
### Old version below ###
#########################

# Requirements:
#              * gdal http://www.mapbox.com/tilemill/docs/guides/gdal/
#              * convert (image-magick)
#
# Reference info:
#                 http://www.mapbox.com/blog/putting-landsat-8-bands-to-work/
#                 http://www.mapbox.com/tilemill/docs/guides/gdal/
#                 http://www.mapbox.com/blog/processing-landsat-8/
#                 http://earthexplorer.usgs.gov/

# DIRECTORY="$2"
# mkdir tmp

# if [[ -z "$1" ]]; then
# 	echo "Landsat image processing"
# 	echo ""
# 	echo "Converts to 8-bit, merges RGB, pan-sharpens, colour corrects and converts to JPG"
# 	echo "Example: process_landsat LC82010242013198LGN00"
# 	echo ""
# 	exit 0
# fi

# if [ ! -f ./"$1"_B2.TIF ]; then
# 	echo "File not found!"
# 	exit 0
# fi

# if [ ! -d "$DIRECTORY" ]; then
# 	mkdir tmp
# fi	

# # Convert 16-bit images into 8-bit and tweak levels
# for BAND in {8,4,3,2}; do
# 	gdalwarp -t_srs EPSG:3857 "$1"_B"$BAND".TIF ./tmp/b"$BAND"-projected.tif;
# 	gdal_contrast_stretch -ndv 0 -linear-stretch 70 30 ./tmp/b"$BAND"-projected.tif ./tmp/b"$BAND"-8bit.tif;
# done

# # Merge RGB bands into one image
# gdal_merge_simple -in ./tmp/b4-8bit.tif -in ./tmp/b3-8bit.tif -in ./tmp/b2-8bit.tif -out ./tmp/rgb.tif

# # Pan-sharpen RGB image
# gdal_landsat_pansharp -rgb ./tmp/rgb.tif -lum ./tmp/rgb.tif 0.25 0.23 0.52 -pan ./tmp/b3-8bit.tif -ndv 0 -o ./tmp/pan.tif

# # Colour correct and convert to JPG
# convert -verbose -channel B -gamma 0.8 -quality 95 ./tmp/pan.tif final-pan-rgb-corrected.jpg

# mv ./tmp "$DIRECTORY"/"$1"

# echo "Finished."