import rasterio as rio
from rasterio.warp import reproject, Resampling
import numpy as np
import numpy.ma as ma
import pandas as pd


# This collection of functions are specific to the data. They convert array into masked array that masks incorrect data e.g. missing or not a pixel.
def _solar(data):
    """
    corrects for rasterio not masking nan in solar data.

    Parameters
    data (numpy ma array): numpy ma array for solar data
    """
    # rasterio doesn't mask nan values in solar data properly.
    data.mask[np.isnan(data.data)] = True
    return data


def _popdensity(data):
    """
    Corrects for rasterio not (sometimes) masking 0 or nan data properly.

    Parameters
    data (numpy ma array): numpy ma array for popdensity data
    """
    # rasterio seems to not mask 0 or nan values properly in some cases.
    #mask = np.logical_or(np.isnan(data), data == 0)
    #data = ma.array(data, mask=mask)

    return data


def _ndvi(data):
    """
    corrects for rasterio not masking nan or 0 in NDVI data. Also removes bottom 2.5% of data as they are outliers.

    Parameters
    data (numpy ma array): numpy ma array for NDVI data
    """
    # For some strange reason the rasterio doesn't mask the data properly, where there is 0 or nan create mask. Manually correct for this.
    mask = np.isnan(data)
    data = ma.array(data, mask=mask)

    # NDVI data has very small outliers - remove the bottom 2.5% of the data to account for this by adding this to the masked array.
    outlier_lower = pd.DataFrame(data.data[~data.mask].ravel()).quantile(0.025).to_numpy()
    outlier_bool = data < outlier_lower
    data.mask = outlier_bool.data | data.mask
    return data


def _wind(data):
    """
    For now there is no correction to mask for wind data

    Parameters
    data (numpy ma array): numpy ma array for wind data
    """
    # rasterio seems to mask data properly. Leaving this here in case this changes
    return data

def _no2(data):
    """
    For now there is no correction to mask for no2 data

    Parameters
    data (numpy ma array): numpy ma array for no2 data
    """
    # rasterio seems to mask data properly. Leaving this here in case this changes
    mask = np.isnan(data)
    data = ma.array(data, mask=mask)

    return data

def _nightlight(data):
    """
    corrects for rasterio not masking <= 0 values in nightlight data.

    Parameters
    data (numpy ma array): numpy ma array for nightlight data
    """
    data.mask = data.data <= 0
    return data

# dictionary defining which function of the above to pass input to.
data_dict = {
    'solar': _solar,
    'popdensity': _popdensity,
    'NDVI': _ndvi,
    'wind': _wind,
    'NO2_OFFL': _no2,
    'nightlight': _nightlight
}


class TIFFile():
    """
    Defines class TifFile which has attributes:
    path (str): full path of tif file
    which (str): indicates which data it is - 'solar', 'popdensity', 'NDVI', 'wind', 'NO2', 'nightlight' available.
    """

    def __init__(self, path, which):
        self.path = path
        self.which = which

    def tif_load(self, dimensions, dst_meta, resampling_method='bilinear'):
        """Loads tif from instance of class 'TIFFile'.

        Parameters
        dimensions (tuple): tuple of height and width desired for the tif.
        resampling_method (str): changes how resampling is done. 'bilinear' is default. Other options: 'nearest', 'bilinear', 'cubic', 'cubic_spline', 'lanczos', 'average', 'mode' available.
        dst_meta (dict): meta information for the destination that contains the transform attribute desired"""
        with rio.open(self.path) as raster:
            # resample data to target shape
            data = raster.read(1, masked=True, out_shape=(dimensions[0], dimensions[1]),
                               resampling=Resampling[resampling_method]
                               )
            meta = raster.profile
            # scale_image_transform
            transform = raster.transform * raster.transform.scale(
                (raster.width / data.shape[-1]),
                (raster.height / data.shape[-2])
            )
        meta.update({'height': dimensions[0], 'width': dimensions[1], 'transform': transform})
        data = data_dict[self.which](data)

        src_transform = meta['transform']
        src_crs = meta['crs']
        dst_transform = dst_meta['transform']
        dst_crs = dst_meta['crs']
        destination = ma.copy(data)
        reproject(
            data,
            destination=destination,
            src_transform=src_transform,
            src_crs=src_crs,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            resampling=Resampling[resampling_method])

        meta.update({'transform': dst_transform, 'crs': dst_crs})
        return data, meta

class TIFData():
    """Defines class which has attributes:
    data (numpy ma array): numpy masked array of scaled values (using AutoScale)
    meta (dictionary): dictionary of meta information from the tif_load
    category (string): name of category to which data belongs to. No restrictions on different names.
    """
    def __init__(self, data, meta, category):
        self.data = data
        self.meta = meta
        self.category = category


def strict_mask(TIFData_list):
    """
    Combines masks from list of TIFData instances to make sure OR is applied to all masks otherwise when aggregating value appears even if there is an unmasked value in at least one dataset.

    Parameters
    TIFData_list (list): List of TIFData instances. See that class for further explanation of attributes.
    """
    mask_tuple = []
    for i in range(len(TIFData_list)):
        mask_tuple.append(TIFData_list[i].data.mask)
    mask_tuple = tuple(mask_tuple)
    strict_mask = np.logical_or.reduce(mask_tuple)
    for i in range(len(TIFData_list)):
        TIFData_list[i].data.mask = strict_mask
    return TIFData_list
