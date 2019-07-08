from osgeo import gdal  # For translating NETCDF to geotiff
import rasterio  # For interacting with geotiff files

import numpy as np  # For interacting with the numpy array
import pandas as pd  # Dataframes
import glob  # For finding geotiff files


from tqdm import tqdm  # Progress bar
from tqdm import trange  # Progress bar with built in 'range' function

from os import path  # For checking if files already exist

# Plotting modules
import rasterio.plot as rplot
from matplotlib import pyplot as plt


def NETCDF_to_geotiff(netcdf_file, overwrite=False):
    gdal.UseExceptions()  # Force gdal to terminate program with exceptions instead of warnings

    last_slash = (netcdf_file.rfind('/')) + 1  # Find the last occurrence of the slash in the file directory
    file_dir = (netcdf_file[:last_slash]) + 'geotiff/'  # Find the directory of the NetCDF file

    if not path.exists('./data/evap/warped_netcdf.geotiff'):  # If the NetCDF has not been warped yet
        lambert_conformal_conic_proj = '+proj=lcc +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs'  # Define the projection we will use for the warp
        warp_options = gdal.WarpOptions(options='-t_srs \"' + lambert_conformal_conic_proj + '\" -of GTiff ')  # Set warp options with command line-like flags
        ds = gdal.Warp(srcDSOrSrcDSTab='NETCDF:./data/evap/evap.mon.mean.nc:evap', destNameOrDestDS='./data/evap/warped_netcdf.geotiff', options=warp_options)  # Warp the NetCDF, and store the output in warped_netcdf.geotiff
        ds = None  # Save, close


    in_ds = gdal.Open('./data/evap/warped_netcdf.geotiff')
    raster_count = in_ds.RasterCount  # Obtain the number of bands to loop through
    year = 1979  # Start year
    month = 1  # Start month

    for i in trange(1, raster_count + 1):  # gdal indices start at 1
        if month < 10:  # Prepend a '0' to the month (if needed) to keep consistent filename lengths
            string_month = '0' + str(month)
        else:
            string_month = str(month)
        filename = str(year) + '_' + string_month  # Format: YYYY_MM

        if path.exists(file_dir + filename + '.geotiff') and overwrite is False:  # Check if the .geotiff already exists
            pass
        else:
            translate_options = gdal.TranslateOptions(options='-b ' + str(i) + ' -of GTiff')  # similar to command-line flags: -b represents band number, -of represents the driver
            out_ds = gdal.Translate(destName=(file_dir + filename + '.geotiff'), srcDS=in_ds, options=translate_options)  # Do the translation

        # Increment year and month
        if i % 12 == 0:
            year += 1
        if month >= 12:
            month = 0
        month += 1


def create_evaporation_plot(file, type='image'):
    # Preconditions: A .geotiff file has been passed. Optional: A type of output has been selected (histogram or image) - default is image
    # Postconditions: A figure has been saved to either /histogram/figure.png or /image/figure.png

    with rasterio.open(file) as raster:
        name = file[-15:-8]  # File name (ex. 1979_01)
        figure = plt.figure(figsize=(5.0, 5.0))  # Create a 500x500 figure
        axes1 = figure.add_subplot(1, 1, 1)  # Create a subplot within the figure

        if type == 'image':
            rplot.show(raster, ax=axes1)  # Make an image, and store it in axes1
        elif type == 'histogram':
            rplot.show_hist(raster, ax=axes1)  # Make a histogram, and store it in axes1

        month = convert_int_to_month(int(name[-2:])-1)  # Subtract one since January is 01 but indices start at 0.
        axes1.set_title(month + ' ' + name[:4])  # Set the title of the plot (ex. January 1979)

        plt.savefig('./data/evap/' + type + '/' + name + '.png')  # Store image or histogram in ./data/evap/image or /histogram
        plt.close()  # Clean up


def print_raster(data):  # Loops through the raster and print each data point
    for i in range(len(data)):
        for j in range(len(data[0])):
            print(data[i][j], end=', ')
        print()


def convert_int_to_month(number):
    # Preconditions: A 0-11 integer has been passed
    # Postconditions: The corresponding month has been returned
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    return months[int(number)]


def extract_evaporation_data(geotiff_files):
    # Preconditions: A list of .geotiff files has been passed
    # Postconditions: A pickled pandas dataframe file has been created, containing all of the data from the .geotiff files

    with rasterio.open(geotiff_files[0]) as raster:
        width = raster.profile['width']  # Get width of raster
        height = raster.profile['height']  # Get height of raster

    evap_array = np.zeros((width, height, 40, 12))  # Create a 4-D array (Width x Height x Months x Years)

    year = 0  # Begin the year at 0
    month = 0  # Begin the month at 0

    for geotiff_file in tqdm(geotiff_files):  # TQDM gives us a progress bar
        with rasterio.open(geotiff_file) as raster:
            data = raster.read()  # Convert the .geotiff file to a numpy array
            data = np.squeeze(data)  # Remove one of the dimensions as it is a singleton dimension (1, 277, 349) -> (277, 349)

            # Loop through the 2-D raster array
            for i in range(raster.width):
                for j in range(raster.height):
                    evap_array[i][j][year][month] = data[j][i]  # Insert the .geotiff data into the corresponding spot in our array. data[j][i] because the raster data is [height][width], but our array is [width][height]

        # Increment the month (or year)
        if month == 11:
            month = 0
            year += 1
            if year == 40:  # The data for 2019 is incomplete, so end early
                break
        else:
            month += 1

    arr = np.column_stack(list(map(np.ravel, np.meshgrid(*map(np.arange, evap_array.shape), indexing="ij"))) + [evap_array.ravel()])  # Convert 4-D Array to Dataframe https://stackoverflow.com/questions/45422898/how-can-i-efficiently-convert-a-4d-numpy-array-into-a-pandas-dataframe-with-indi
    frame = pd.DataFrame(arr, columns=['x', 'y', 'year', 'month', 'value']) #  Set column names
    frame['year'] = frame['year'].apply(lambda x: x + 1979).astype(int)  # Convert [0-39] to [1979-2018]
    frame['x'] = frame['x'].astype(int)  # Convert float to int
    frame['y'] = frame['y'].astype(int)  # Convert float to int
    frame['month'] = frame['month'].apply(convert_int_to_month)  # Convert [0-11] to month name
    frame.to_pickle('./data/evap/pickled_array')  # Store the numpy array in 'pickled_array'


def get_average_evaporation(frame):
    x_count = frame.loc[(frame['y'] == 1) & (frame['year'] == 1979) & (frame['month'] == 'January')].shape[0]  # Isolate X to get the count
    y_count = frame.loc[(frame['x'] == 1) & (frame['year'] == 1979) & (frame['month'] == 'January')].shape[0]  # Isolate Y to get the count
    for x in range(100, 300):
        for y in range(120, 250):
            sub_frame = frame.loc[(frame['x'] == x) & (frame['y'] == y) & (frame['month'] == 'January')]
            print('X:', x, 'Y:', y, 'Average value:', sub_frame['value'].mean())
