import glob

import sys
sys.path.insert(1, 'C:/Users/matas/Anaconda3/envs/SWMM/Lib/site-packages/GDAL-2.3.3-py3.7-win-amd64.egg-info/scripts/')
import gdal_calc


def apply_mask(raster_file, mask_file, output_destination):
    # INPUTS:
    #   raster_file: raster file you are masking
    #   mask_file: raster file you are using to mask
    #   output_destination: where to put the output geotiff (include file name!)

    gdal_calc.Calc('A*B', A=raster_file, B=mask_file, outfile=output_destination, NoDataValue=0, format='GTiff')
