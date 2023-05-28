import rasterio
import fiona
import shutil
import urllib.request as request
from contextlib import closing
import os

data_path=''
def getWindData(country):
    #Input: Enter ISO3 Country Code (https://unstats.un.org/unsd/tradekb/knowledgebase/country-code)
    #Output: File name of the retrieved tif file, tif file is stored at the data path defined above
    url = "https://globalwindatlas.info/api/gis/country/"+str(country)+"/power-density/200"
    filename = data_path+str(country)+".tif"
    with closing(request.urlopen(url)) as r:
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r, f)
    print(country+" is done, with file size = "+str(os.stat(filename).st_size))
    return filename