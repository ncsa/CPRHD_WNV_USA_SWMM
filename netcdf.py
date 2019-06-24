from osgeo import gdal
from os import path
import rasterio
import numpy as np
import csv
from multiprocessing import Pool
import glob

# PLOT
import rasterio.plot as rplot
from matplotlib import pyplot as plt


def NETCDF_to_geotiff(netcdf):
    gdal.UseExceptions()  # Force gdal to terminate program with exceptions instead of warnings
    in_ds = gdal.Open('NETCDF:' + netcdf + ':evap')  # Open the file as NETCDF, and only take the evaporation data

    last_slash = (netcdf.rfind('/')) + 1  # Find the last occurrence of the slash in the file directory
    file_dir = (netcdf[:last_slash]) + 'geotiff/'  # Find the directory of the NETCDF file

    # print(gdal.Info(in_ds))  # Obtain metadata about bands

    raster_count = in_ds.RasterCount  # Obtain the number of bands to loop through
    year = 1979  # Start year
    month = 1  # Start month

    for i in range(1, raster_count + 1):  # gdal indices start at 1
        if month < 10:  # Prepend a '0' to the month (if needed) to keep consistent filename lengths
            string_month = '0' + str(month)
        else:
            string_month = str(month)
        filename = str(year) + '_' + string_month  # Format: YYYY_MM

        if path.exists(file_dir + filename + '.geotiff'):  # Check if the .geotiff already exists
            pass
        else:
            translate_options = gdal.TranslateOptions(options='-b ' + str(i) + ' -of GTiff', outputSRS='epsg:4326')  # 'options' represents command-line-like flags. ex. -b represents band number
            out_ds = gdal.Translate(file_dir + filename + '.geotiff', in_ds, options=translate_options)
            out_ds = None  # Save, close

        # Increment year / month
        if i % 12 == 0:
            year += 1
        if month >= 12:
            month = 0
        month += 1


def create_evaporation_plot(file, out='image'):
    with rasterio.open(file) as raster:
        name = file[-15:-8]

        figure = plt.figure(figsize=(5.0, 5.0))
        axes1 = figure.add_subplot(1, 1, 1)

        if out == 'image':
            rplot.show(raster, ax=axes1)
        elif out == 'histogram':
            rplot.show_hist(raster, ax=axes1)

        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        month = months[int(name[-2:])-1]  # Subtract one since January is 01 but indices start at 0.
        axes1.set_title(month + ' ' + name[:4])

        plt.savefig('./data/evap/' + out + '/' + name + '.png')  # Put files in ./data/evap/image or /histogram
        plt.close()


def print_raster(raster, data):
    for i in range(raster.height):
        for j in range(raster.width):
            print(data[i][j], end=', ')
        print()


def extract_evaporation_data(geotiff_file):
    with rasterio.open(geotiff_file) as raster:
        name = geotiff_file[-15:-8]
        data = raster.read()  # Convert the .geotiff file to a numpy ndarray
        data = np.squeeze(data)  # Remove one of the dimensions as it is a singleton dimension (1, 277, 349) -> (277, 349)
