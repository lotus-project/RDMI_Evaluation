import rasterio
import fiona
import shutil
import urllib.request as request
from contextlib import closing
import os
import rasterio.mask
import numpy as np
import time

data_path = '' #Define Data Path here

def getShape(filename,countryName):
    #Input: Name of the TIFF File generated using the getWindData() function, and the name of the country
    #Output: geoJSON shape file
    s = "'"+countryName.lower()+"'" 
    url = 'https://opendata.arcgis.com/datasets/a21fdb46d23e4ef896f31475217cbb08_1.geojson?where=CNTRY_NAME%20%3D%20'+s
    file_n = countryName+'.geojson'
    time.sleep(10) # adding a 10 second delay before making the next request
    with closing(request.urlopen(url)) as r:
        with open(file_n, 'wb') as f:
            shutil.copyfileobj(r, f)
    print(countryName+" is done, with file size = "+str(os.stat(file_n).st_size))
    return file_n

def maskFile(shapefile,tiffile):
    #Input - Name of the shape file, and the tif file
    #Output - Masked tif file
    with fiona.open(shapefile, "r") as shapefile:
        shapes = [feature["geometry"] for feature in shapefile]
    with rasterio.open(tiffile) as src:
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta
    print(out_image)
    out_meta.update({"driver": "GTiff","height": out_image.shape[1],"width": out_image.shape[2],"transform": out_transform})
    with rasterio.open(tiffile, "w", **out_meta) as dest:
        dest.write(out_image)
        
def masks(tiffile):
    #Input - TIF Filename, after running the previous methods
    #The file returns a 2-D Numpy Array containing Boolean Values
    #A value of True indicates that the element at that index in the array contains invalid data - nan
    #A value of False indicates that the element at that index in the array contains valid data
    #https://rasterio.readthedocs.io/en/latest/topics/masks.html
    src = rasterio.open(tiffile)
    msk = src.read(1,masked=True)
    return msk.mask
