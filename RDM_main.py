from Auto_Scaling import AutoScale
from TIF_Loading import TIF_Transform, maskTIF
import extract_coordinates

import rasterio as rio
import numpy.ma as ma
from scipy.special import expit
import numpy as np
import numpy.ma as ma
import os


def save_tif(file_path, data, meta):
    with rio.open(
            file_path,
            'w',
            **meta
    ) as dst:
        dst.write(data, 1)

def compute_RDM(TIFData_list, category_aggregation="median", rdm_aggregation='median', dim_weights=None):
    """Takes in list of TIFData instances and calculates RDM index. Make sure previous functions modifying the mask and scaling the data have been performed first.

    Args:
        TIFData_list (list) : list of TIF_Transform.TIFData instances.


    Returns:
        RDM_dict (dict): dictionary with keys for the category medians, and then the RDM index and its weighted version.
        weights_dict (dict): dictionary with keys as categories and values as their weights used to calculate the weighted version of the RDM index.
    """
    # take sigmoid of each dataset and get list of category names
    sigmoid_data = []
    category_list = []
    for tif_data in TIFData_list:
        category_list.append(tif_data.category)
        sigmoid_data.append(expit(tif_data.data))
    category_list_unique = list(set(category_list))

    # aggregate datasets with same categories and then aggregate over these
    agg_categories = []
    for i in range(len(category_list_unique)):
        indexes = [n for n, x in enumerate(category_list) if x == category_list_unique[i]]
        filtered_sigmoid = [sigmoid_data[i] for i in indexes]

        if category_aggregation == 'median':
            agg_category = ma.median(ma.array(filtered_sigmoid), axis=0)

        elif category_aggregation == 'average':
            agg_category = ma.mean(ma.array(filtered_sigmoid), axis=0)
            agg_category = agg_category.astype('float32')  
        
        else:
            agg_category = ma.max(ma.array(filtered_sigmoid), axis=0)           
    
        agg_categories.append(agg_category)

    if rdm_aggregation == 'median':
        RDM_index = ma.median(ma.array(agg_categories), axis=0)
    
    else:
        RDM_index = ma.average(ma.array(agg_categories), axis=0, weights=dim_weights)
        RDM_index = RDM_index.astype('float32')


    # calculate default weights for each category
    dif2 = np.zeros(shape=len(category_list_unique))
    for i in range(len(category_list_unique)):
        dif2[i] = ma.sum(ma.power(agg_categories[i] - RDM_index, 2))
    normalisation_factor = ma.sum(dif2)
    weights_categories = np.divide(dif2, normalisation_factor)
    RDM_index_weighted = ma.average(ma.array(agg_categories), axis=0, weights=weights_categories)

    weights_dict = dict(zip(category_list_unique, weights_categories.tolist()))
    RDM_dict = dict(zip(category_list_unique, agg_categories))
    RDM_dict['RDM'] = RDM_index
    RDM_dict['RDM_weighted'] = RDM_index_weighted
    for rdm_index_type in RDM_dict:
        ma.set_fill_value(RDM_dict[rdm_index_type], 0)

    return RDM_dict, weights_dict


class RDMCalculator():
    """
    Class which defines with attributes that define how the RDM is calculated. Attributes:
    data_dict (dict): dictionary with keys and values:
    'data_types': list containing any of the elements 'solar', 'NDVI', 'wind', 'popdensity' that
    controls which data is used to calculate the RDM. Must always contain 'popdensity'
    'polarities': list containing polarities for each element in 'data_types'. Each element of
    this list is either 'identity' or 'decreasing'
    'categories': list containing categories for each element in 'data_types'. Each element of
    this list is either 'environmental, geographical or social'
    """

    def __init__(self, data_dict):
        self.data_dict = data_dict

    def get_rdm(self, country_dict, category_agg='median', rdm_agg='median', dim_weights=None,
                save_df=False, compress_df=False, save_as_tif=False, tif_name = 'RDM.tif'):
        """
        Calculates RDM index for country using attributes in instance of RDMCalculator class
        Args:
        country_dict (dict): dictionary with keys 'code' which is the two letter codification for the country and
        'full_name' which is the full name of the country. Where ever there is a space in the country there should be a %20.
        save_df (bool): True if you want to save df as .csv. Default False.
        compress_df (bool): True if you want .zip of csv. Default False.
        save_as_tif (bool): True if you want to save RDM index as tif. Default False

        Returns:
        RDM_dict (dict): dictionary with keys for the category medians, and then the RDM index and its weighted version.
        weights_dict (dict): dictionary with keys as categories and values as their weights used to calculate the weighted version of the RDM index.
        df_RDM (pd.DataFrame): dataframe of coordinates with their RDM values from RDM_dict.
        """
        data_dict = self.data_dict

        data_paths = []
        for data_type in data_dict['data_types']:
            data_type_path = os.path.join('./Data/',
                                          country_dict['code'] + '/' + data_type + '_' + country_dict['code'] + '.tif')
            data_paths.append(data_type_path)
        data_dict['data_paths'] = data_paths

        # mask each TIF using maskFile to remove off shore values.
        shape_geojson = maskTIF.getShape(country_dict['code'], country_dict['full_name'])

        for data_path in data_dict['data_paths']:
            maskTIF.maskFile(shape_geojson, data_path)

        # use population density data as a reference point for the height, width and meta information for the remaining TIFs
        with rio.open(data_dict['data_paths'][0]) as raster:
            meta_ref = raster.profile
        height = meta_ref['height']
        width = meta_ref['width']
        dim = (height, width)

        # Define the pipeline for the scaling
        pipe_step0 = AutoScale.Scaler('selective_log', {'maxspan': 2, 'C': 1, 'log_base': 10})
        pipe_step1 = AutoScale.Scaler('zscore', {'ignore_value': 0})  # create second transformation
        pipeline = [pipe_step0, pipe_step1]  # define pipeline as a list of Scaler instance

        # create instances of the class TIFFile which is used to load the TIF file and resample so it has the same resolution and meta information as the reference.
        TIFDatas = []

        for i, data_path in enumerate(data_dict['data_paths']):
            TIF = TIF_Transform.TIFFile(data_path, data_dict['data_types'][i])
            data, meta = TIF.tif_load(dimensions=dim, dst_meta=meta_ref)
            scaled = AutoScale.scaler_pipeline(pipeline, data)
            scaled = AutoScale.polarity_transform(scaled, polarity_type=data_dict['polarities'][i], ignore_value=0)
            TIFData = TIF_Transform.TIFData(scaled, meta, data_dict['categories'][i])
            TIFDatas.append(TIFData)

        # Make sure masks are combined to do an OR operation between them all - that only pixels with values in all datasets are used.
        TIFDatas = TIF_Transform.strict_mask(TIFDatas)

        # calculate both versions of the index and return the aggregated category medians in RDM_dict. Weights are given in weights_dict
        RDM_dict, weights_dict = compute_RDM(TIFDatas, category_agg, rdm_agg, dim_weights)

        # Create dataframe with long and lat coordinates for top left and bottom right pixels with values of RDM index, weighted version and the category medians.
        df_RDM = extract_coordinates.coord_df(RDM_dict, meta_ref, 'RDM_index', save=save_df, compress=compress_df)

        meta_ref.update({'nodata':float(0)})
        if save_as_tif:
            save_tif(tif_name, RDM_dict['RDM'], meta_ref)

        return RDM_dict, weights_dict, df_RDM, meta_ref
