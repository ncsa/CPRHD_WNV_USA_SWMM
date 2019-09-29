import rasterio  # For interacting with geotiff files

import numpy as np  # For interacting with the numpy array
import pandas as pd  # Dataframes
import glob  # For finding geotiff files

from tqdm import tqdm  # Progress bar
from tqdm import trange  # Progress bar with built in 'range' function

import os

# Plotting modules
import rasterio.plot as rplot
from matplotlib import pyplot as plt

from osgeo import gdal  # For translating NETCDF to geotiff
gdal.UseExceptions()  # Force gdal to terminate program with exceptions instead of warnings




def warp_netcdf_to_geotiff(netcdf_file, subdataset, proj4, output_directory):
    # Warps and converts NetCDF to GeoTIFF
    #   netcdf_file: Directory of the NetCDF file you are warping
    #   subdataset: The subdataset of the NetCDF file (can be found by running gdalinfo on the file (ex. air, evap))
    #   proj4: The proj4 string of the desired projection
    #   output_directory: Where to save the output file (include file name!)

    warp_options = gdal.WarpOptions(options='-t_srs \"' + proj4 + '\" -of GTiff ')  # Set warp options with command line-like flags
    ds = gdal.Warp(srcDSOrSrcDSTab='NETCDF:' + netcdf_file + ':' + subdataset, destNameOrDestDS=output_directory, options=warp_options)  # Warp the NetCDF, and store the output in the output directory
    ds = None  # Save, close


def extract_bands(geotiff, output_destination):
    # Extracts individual bands from a geotiff file (use with warp_netcdf_to_geotiff)
    #   geotiff: directory to the warped geotiff file
    #   output_destination: directory to the folder which will contain the individual geotiff files

    in_ds = gdal.Open(geotiff)
    raster_count = in_ds.RasterCount  # Obtain the number of bands to loop through
    year = 1979  # Start year
    month = 1  # Start month

    for i in trange(1, raster_count + 1):  # gdal indices start at 1
        filename = str(year) + '_' + str(month)  # File name format: YYYY_MM
        if month < 10:  # Prepend a '0' to the month to keep consistent filename lengths (ex. 1979_1 --> 1979_01)
            filename = str(year) + '_0' + str(month)

        translate_options = gdal.TranslateOptions(options='-b ' + str(i) + ' -of GTiff')  # similar to command-line flags: -b represents band number, -of represents the driver
        gdal.Translate(destName=(output_destination + filename + '.geotiff'), srcDS=in_ds, options=translate_options)

        # Increment year and month
        if i % 12 == 0:
            year += 1
        if month >= 12:
            month = 0
        month += 1


def create_plot(file, output_destination, type='image'):
    # Preconditions: A .geotiff file has been passed. Optional: A type of output has been selected (histogram or image) - default is image
    # Postconditions: A figure has been saved to either /histogram/figure.png or /image/figure.png

    with rasterio.open(file) as raster:
        file_name = file[-15:-8]  # File name (ex. 1979_01)
        figure = plt.figure(figsize=(5.0, 5.0))  # Create a 500x500 figure
        axes1 = figure.add_subplot(1, 1, 1)  # Create a subplot within the figure

        if type == 'image':
            rplot.show(raster, ax=axes1)  # Make an image, and store it in axes1
        elif type == 'histogram':
            rplot.show_hist(raster, ax=axes1)  # Make a histogram, and store it in axes1

        month = convert_int_to_month(int(file_name[-2:])-1)  # Subtract one since January is 01 but indices start at 0.
        axes1.set_title('Air Temperature 2m\n' + month + ' ' + file_name[:4])  # Set the title of the plot (ex. January 1979)
        plt.xticks([])
        plt.yticks([])
        plt.savefig(output_destination + file_name + '.png')  # Store image or histogram in ./data/evap/image or /histogram
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
    # TODO Make this a bit faster by filling the dataframe directly instead of array -> dataframe. https://stackoverflow.com/questions/17091769/python-pandas-fill-a-dataframe-row-by-row
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
    frame = pd.DataFrame(arr, columns=['x', 'y', 'year', 'month', 'value'])  # Set column names
    frame['year'] = frame['year'].apply(lambda x: x + 1979).astype(int)  # Convert [0-39] to [1979-2018]
    frame['x'] = frame['x'].astype(int)  # Convert float to int
    frame['y'] = frame['y'].astype(int)  # Convert float to int
    frame['month'] = frame['month'].apply(convert_int_to_month)  # Convert [0-11] to month name
    return frame


def get_average_evaporation(frame):
    # Preconditions: A frame generated by extract_evaporation_data has been passed.
    # Postconditions: Twelve files have been created, containing the average evaporation values for each month
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for month in months:
        print(month)
        sub_frame = frame.loc[(frame['month'] == month)]  # Select the month we are averaging over
        sub_frame.drop(labels='year', axis=1, inplace=True)  # Drop the 'year' column
        sub_frame = sub_frame.groupby(['x', 'y']).mean()  # Sum each coordinate's value for each year
        sub_frame.reset_index(inplace=True)
        return sub_frame


def average_to_ascii():
    # Preconditions: The average evaporation rate for each month in pandas pickle form exists in ./data/evap/average/month_number_average
    # Postconditions: An ASCII file has been created which can then be translated to GeoTIFF
    for month in tqdm(range(1, 13)):

        if month < 10: # If the month is 0-9, prepend a 0 to the front
            avg_frame = pd.read_pickle('./data/evap/average/0' + str(month) + '_average')
        else: # Just write the number
            avg_frame = pd.read_pickle('./data/evap/average/' + str(month) + '_average')

        with open('./data/evap/average/ascii/' + str(month) + '.txt', 'w') as file:  # Open a new ASCII file based on the month's number
            # Set Initial Parameters - from template GeoTIFF
            writeString = 'ncols\t\t388\n'
            writeString += 'nrows\t\t316\n'
            writeString += 'xllcorner\t-6121312.596054837108\n'
            writeString += 'yllcorner\t-3833307.251033219509\n'
            writeString += 'dx\t\t30002.267236048923\n'
            writeString += 'dy\t\t30079.792474384965\n'
            writeString += 'NODATA_value\t9.9692099683868690468e+36\n'
            file.write(writeString)

            writeString = ''

            for i in range(0, 316):  # Loop through the rows
                sub_frame = avg_frame.loc[(avg_frame['y'] == i)]  # Find all the values for the row number
                sub_frame.drop(labels=['x', 'y'], axis=1, inplace=True)  # Drop columns (we only need the value)
                sub_frame.reset_index(inplace=True, drop=True)  # Reset the index (not sure if necessary)
                series = sub_frame.squeeze()  # Convert Dataframe to Series

                for value in series:  # Loop through each value in the row
                    writeString += str(value) + ' '  # Add the value plus a space delimiter
                writeString += '\n'

            file.write(writeString)  # Write the data to the ASCII file


def format_neighbors(row):
    if row == 'nan':
        row = 'None'
    return row


# warp_netcdf_to_geotiff('../evap.mon.mean.nc', 'evap', '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +towgs84=1,1,-1,0,0,0,0 +units=m +no_defs', '../evap/evap.mon.mean.geotiff')
extract_bands('../evap/evap.mon.mean.geotiff', '../evap/unmasked_geotiff/')
