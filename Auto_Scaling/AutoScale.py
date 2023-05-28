import numpy as np
import numpy.ma as ma
from types import SimpleNamespace
from enum import Enum, auto
import pandas as pd


def log_bisymmetric(arr, C=1, log_base=10):
    """https://pdfs.semanticscholar.org/70d5/3d9f448e6f2c10bd87a4a058be64f5af7dbc.pdf"""
    sign = np.sign(arr)
    sign[sign == 0] = 0
    return sign * np.log(1 + np.abs(arr / C)) / np.log(log_base)


def log_bisymmetric_inv(arr, C=1, log_base=10):
    """https://pdfs.semanticscholar.org/70d5/3d9f448e6f2c10bd87a4a058be64f5af7dbc.pdf"""
    sign = np.sign(arr)
    sign[sign == 0] = 0
    return sign * C * (np.power(log_base, np.abs(arr)) - 1)


def log_span(arr, base=10):
    val = np.abs(arr)
    val[val == 0] = np.nan
    in_unit_circle = val <= 1
    try:
        in_span = log_b(np.nanmax(val[in_unit_circle]), base) - log_b(np.nanmin(val[in_unit_circle]), base)
    except ValueError:
        in_span = 0
    out_unit_circle = np.invert(in_unit_circle)
    try:
        out_span = log_b(np.nanmax(val[out_unit_circle]), base) - log_b(np.nanmin(val[out_unit_circle]), base)
    except ValueError:
        out_span = 0
    return in_span, out_span


def log_b(x, base=10):
    return np.log(x) / np.log(base)


def _zscore_transform(data, ignore_value=None):
    """Applies zscore to dataframe and ignores value stored in ignore_value if this is not None"""
    transf_parameters = SimpleNamespace()
    if ignore_value is not None:
        transf_parameters.mean = data[data != ignore_value].mean()
        transf_parameters.std = data[data != ignore_value].std()
        data[data != ignore_value] = (data[data != ignore_value] - transf_parameters.mean) / transf_parameters.std
    else:
        transf_parameters.mean = data.mean()
        transf_parameters.std = data.std()
        data = (data - transf_parameters.mean) / transf_parameters.std
    return data, transf_parameters


def _zscore_inverse(data, transf_parameters):
    data = data * transf_parameters.std + transf_parameters.mean
    return data


class _transf_kind(Enum):
    no_transf = auto()
    log_bisymmetric = auto()
    log = auto()


def _selective_log_transform_column(arr, maxspan=2, C=1, log_base=10):
    """rescales one column according to the criteria"""
    in_span, out_span = log_span(arr)
    # has_zeros = (arr == 0).sum()
    has_zeros = arr.eq(0).any().any()
    sign = set(np.sign(arr))
    both_signs = (-1 in sign) and (1 in sign)

    #if out_span > maxspan:
    #    if in_span > maxspan:
    #        if (not has_zeros) and (not both_signs):
    #            # apply log only
    #            which_transformation = _transf_kind.log
    #            arr = log_b(arr, log_base)
    #        else:
                # apply nothing
    #            which_transformation = _transf_kind.no_transf
    #    else:
    #        # apply bisymmetric
    #        which_transformation = _transf_kind.log_bisymmetric
    #        arr = log_bisymmetric(arr, C, log_base)
    #elif in_span > maxspan:
    #    # For case where metric is in fixed interval [0,1] but within this interval contains wide order of magnitudes
    #    which_transformation = _transf_kind.log_bisymmetric
    #    arr = log_bisymmetric(arr, C, log_base)
    #else:
    #    which_transformation = _transf_kind.no_transf

    if out_span > maxspan:
        if (not has_zeros) and (not both_signs):
            # apply log only
            which_transformation = _transf_kind.log
            arr = log_b(arr, log_base)
        else:
            # apply bisymmetric in cases where it has 0 or both signs
            which_transformation = _transf_kind.log_bisymmetric
            arr = log_bisymmetric(arr, C, log_base)
    elif in_span > maxspan:
        # For case where metric is in fixed interval [0,1] but within this interval contains wide order of magnitudes
        which_transformation = _transf_kind.log_bisymmetric
        arr = log_bisymmetric(arr, C, log_base)
    else:
        which_transformation = _transf_kind.no_transf

    return arr, which_transformation


def _selective_log_transform(data, maxspan=2, C=1, log_base=10):
    """rescales a dataframe"""
    transf_parameters = SimpleNamespace()
    transf_parameters.C = C
    transf_parameters.log_base = log_base
    transf_parameters.maxspan = 2
    if len(data.shape) == 2:
        transf_parameters.multicolumn = True
    elif len(data.shape) == 1:
        transf_parameters.multicolumn = False
    else:
        raise ValueError('data is neither 1-dimensional nor 2-dimensional')

    data, transf_parameters._transf_kind = _selective_log_transform_column(data, maxspan, C, log_base)
    return data, transf_parameters


def _selective_log_inverse(data, transf_parameters):
    assert len(transf_parameters._transf_kind) == data.shape[1]
    data = data.copy()
    if transf_parameters.multicolumn:
        for j, tkind in enumerate(transf_parameters._transf_kind):
            if tkind is _transf_kind.log_bisymmetric:
                data.iloc[:, j] = log_bisymmetric_inv(data.iloc[:, j], transf_parameters.C, transf_parameters.log_base)
            elif tkind is _transf_kind.log:
                data.iloc[:, j] = np.power(transf_parameters.log_base, data.iloc[:, j])
    else:
        if transf_parameters._transf_kind is _transf_kind.log_bisymmetric:
            data[:] = log_bisymmetric_inv(data, transf_parameters.C, transf_parameters.log_base)
        elif transf_parameters._transf_kind is _transf_kind.log:
            data[:] = np.power(transf_parameters.log_base, data)
    return data


transformation_dict = {
    'zscore': _zscore_transform,
    'selective_log': _selective_log_transform,
}
inverse_dict = {
    'zscore': _zscore_inverse,
    'selective_log': _selective_log_inverse
}


class Scaler():
    """wraps data rescaling functions for Pandas DataFrames and Series"""

    def __init__(self, kind='zscore', transf_arguments={}):
        self.kind = kind
        self.transf_arguments = transf_arguments  # optional args for rescaling function or zscore. Make sure appropriate arguments match the kind of transformation
        self.transf_parameters = None  # needed to compute inverse

    def scale(self, data):
        """scales data. all transformations must get a DataFrame or a Series as input, and output the tuple (transformed_data, transformation_parameters), where transformation_parameters is a SimpleNamespace containing the information necessary to compute the inverse."""
        scaled, transf_parameters = transformation_dict[self.kind](data, **self.transf_arguments)
        self.transf_parameters = transf_parameters
        return scaled

    def inverse(self, data):
        assert self.transf_parameters is not None
        return inverse_dict[self.kind](data, self.transf_parameters)



def scaler_pipeline(pipeline, data):
    """chain Scaler transformations. Input pipeline must be list of Scalar instances, data can either be dataframe series or numpy masked array"""
    if type(data).__name__ == 'MaskedArray':
        data_onlyunmask = data.data[~data.mask]
        df_data = pd.DataFrame(data_onlyunmask)
        for scaler in pipeline:
            df_data = scaler.scale(df_data)

        data_array = df_data.to_numpy()
        rowcol_mask = np.argwhere(~data.mask)
        data_scaled = ma.copy(data)
        for i in range(len(rowcol_mask[:, 0])):
            data_scaled.data[rowcol_mask[i, 0], rowcol_mask[i, 1]] = data_array[i]
        data = data_scaled
    else:
        for scaler in pipeline:
            data = scaler.scale(data)
    return data


def polarity_transform(data, polarity_type='identity', ignore_value=None):
    """changes polarity of data. Either applies identity or multiplies by -1 when decreasing option is selected. If ignore_value is not None it ignores anything with the same values when decreasing option is selected. E.g. ignores 0s in population density data so that they are not given too much weight (no people living there)."""
    if polarity_type == 'identity':
        data = data
    elif polarity_type == 'decreasing':
        if ignore_value is not None:
            data[data != ignore_value] = -data[data != ignore_value]
            data[data == ignore_value] = -1000 # set the ignore value to be quite small so that when sigmoid is applied to it the value here is also quite small.
        else:
            data = -data
    return data

# class ScalerPipeline():
#    """applies several Scaler transformations in a given order"""

#    def __init__(self, pipeline):
#        self.pipeline = pipeline

#    def scale(self, data):
#        for scaler in pipeline:
#            data = scaler.scale(data)
#        return data

#    def inverse(self, data):
#        for scaler in reversed(pipeline):
#            data = scaler.inverse(data)
#        return data
