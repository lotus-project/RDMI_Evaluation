from sys import argv
import rasterio
# from rasterio.enums import Resampling
import rasterio.transform as transform
import numpy as np
import pandas as pd
from datetime import datetime as dt


def extract_validvalues(data):
    value = []

    row_index = np.where(~data.mask)[0]
    col_index = np.where(~data.mask)[1]

    for i, j in zip(row_index, col_index):
        value.append(data.data[i][j])
    return value, row_index, col_index


def coord_df(RDM_dict, meta, fn, save=False, compress=False):
    """
    Creates a dataframe with the coordinates for the upper left and bottom right of the pixel for each non-zero pixel, as well as the value of the pixel, of a GeoTIFF.
    
    Parameters
    fn (str): File name of the GeoTIFF image, e.g. 'file_name.tif'. Please do not use relative file paths that start with './' or '../'
    save (Bool): If True, saves the created DataFrame as a csv file using the same file name as the GeoTIFF in the same directory. Set to False by default.
    compress (Bool): If True, saves the csv as a compressed zip file. This parameter only has an effect if save=True. Set to False by default.
    
    Returns
    df: Pandas DataFrame with coordinates and pixel value (this dataframe can also be saved as a csv file if parameters are set accordingly)
    """

    start_time = dt.now()

    key_list = list(RDM_dict.keys())
    value_list = []
    for i in key_list:
        values, row_index, col_index = extract_validvalues(RDM_dict[i])
        value_list.append(values)
    value_dict = dict(zip(key_list, value_list))

    ul_lon, ul_lat = transform.xy(meta['transform'], row_index, col_index, offset='ul')
    lr_lon, lr_lat = transform.xy(meta['transform'], row_index, col_index, offset='lr')
    c_lon, c_lat = transform.xy(meta['transform'], row_index, col_index, offset='center')

    # TL = top left; BR = bottom right
    data = {'Lat_TL': ul_lat, 'Lon_TL': ul_lon, 'Lat_BR': lr_lat, 'Lon_BR': lr_lon, 'Lat_C': c_lat, 'Lon_C': c_lon}
    data.update(value_dict)

    df = pd.DataFrame(data=data)

    if save:
        if compress:
            df.to_csv(fn + '.csv', index=False, compression='zip')
        else:
            df.to_csv(fn + '.csv', index=False)

    print('Time taken to run function: ', dt.now() - start_time)

    return df

# coord_df(*argv[1:])
