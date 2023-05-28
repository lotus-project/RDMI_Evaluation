import rasterio
from rasterio.merge import merge
import glob
import os

def stitch(in_dir, out_dir, description):
	"""
	Creates a global tif file from individual tif files stored in a directory.

	Parameters:
	in_dir (str): takes the directory path where all the tif images to be stitched are stored
	out_dir (str): takes the directory path where the final global tif image is to be stored
	description (str): the type of images, e.g. NDVI, night_light

	Returns:
	String message to signify successful completion of the function
	"""

	images = glob.glob(in_dir+'/*.tif')

	src_to_mosaic = []

	for image in images:
		open_img = rasterio.open(image)
		src_to_mosaic.append(open_img)

	mosaic, out_trans = merge(src_to_mosaic)

	with rasterio.open(images[0]) as src:
		out_meta = src.meta.copy()

	out_meta.update({
		'driver': 'GTiff',
		'height': mosaic.shape[1],
		'width': mosaic.shape[2],
		'transform': out_trans
		})

	with rasterio.open(out_dir+'/'+description+'_stitch.tif', 'w', **out_meta) as dest:
		dest.write(mosaic)

	return 'Images successfully merged'