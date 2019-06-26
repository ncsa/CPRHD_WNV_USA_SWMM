from osgeo import gdal  # For translating NETCDF to geotiff
from os import path  # For checking if files already exist
import rasterio  # For reading geotiff files into numpy arrays
import numpy as np  # For interacting with the numpy array
import glob  # For finding geotiff files
import pandas as pd  # Dataframes
from tqdm import tqdm  # Progress bar

# Plotting modules
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
        name = file[-15:-8]  # File name (ex. 1979_01)
        figure = plt.figure(figsize=(5.0, 5.0))  # Create a 500x500 figure
        axes1 = figure.add_subplot(1, 1, 1)  # Create a subplot within the figure

        if out == 'image':
            rplot.show(raster, ax=axes1)  # Make an image, and store it in axes1
        elif out == 'histogram':
            rplot.show_hist(raster, ax=axes1)  # Make a histogram, and store it in axes1

        month = convert_int_to_month(int(name[-2:])-1)  # Subtract one since January is 01 but indices start at 0.
        print(month)
        axes1.set_title(month + ' ' + name[:4])  # Set the title of the plot (ex. January 1979)

        plt.savefig('./data/evap/' + out + '/' + name + '.png')  # Store image or histogram in ./data/evap/image or /histogram
        plt.close()


def print_raster(data):  # Loop through the raster and print each data point
    for i in range(len(data)):
        for j in range(len(data[0])):
            print(data[i][j], end=', ')
        print()


def convert_int_to_month(number):  # Convert 0-11 integers to their respective month
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    return months[int(number)]


def extract_evaporation_data(geotiff_files):
    # Preconditions: A list of .geotiff files has been passed
    # Postconditions: A pickled pandas dataframe file has been created, containing all of the data from the .geotiff files

    evap_array = np.zeros((349, 277, 40, 12))  # Create a 4-D array (Rows x Columns x Months x Years)

    year = 0  # Begin the year at 0
    month = 0  # Begin the month at 0

    for geotiff_file in tqdm(geotiff_files):  # TQDM gives us a progress bar

        with rasterio.open(geotiff_file) as raster:

            # print('Month:', month+1, 'Year:', year+1979, 'File:', geotiff_file)  # Info message
            data = raster.read()  # Convert the .geotiff file to a 3-D numpy array
            data = np.squeeze(data)  # Remove one of the dimensions as it is a singleton dimension (1, 277, 349) -> (277, 349)

            # Loop through the 2-D raster array
            for i in range(raster.width):
                for j in range(raster.height):
                    evap_array[i][j][year][month] = data[j][i]  # Insert the .geotiff data into the corresponding spot in our array. data[j][i] because data is [height][width], but our array is [width][height]

        # Increment the month (or year)
        if month == 11:
            month = 0
            year += 1
            if year == 40:  # The data for 2019 is incomplete, so end early
                break
        else:
            month += 1

    arr = np.column_stack(list(map(np.ravel, np.meshgrid(*map(np.arange, evap_array.shape), indexing="ij"))) + [evap_array.ravel()])  # https://stackoverflow.com/questions/45422898/how-can-i-efficiently-convert-a-4d-numpy-array-into-a-pandas-dataframe-with-indi
    frame = pd.DataFrame(arr, columns=['x', 'y', 'year', 'month', 'value'])
    frame['year'] = frame['year'].apply(lambda x: x + 1979).astype(int)  # Convert [0-39] to [1979-2018]
    frame['x'] = frame['x'].astype(int)  # Convert 0.0 to 1 since we're representing image pixels
    frame['y'] = frame['y'].astype(int)  # Convert 0.0 to 1
    frame['month'] = frame['month'].apply(convert_int_to_month)  # Convert [0-11] to month name
    frame.to_pickle('./data/evap/pickled_array')


# geotiff_files = glob.glob('./data/evap/geotiff/*.geotiff')
# extract_evaporation_data(geotiff_files)

frame = pd.read_pickle('./data/evap/pickled_array')

# Negative values example
# sub_frame = frame.loc[(frame['x'] == 140) & (frame['y'] == 140) & (frame['month'] == 'January')]
# print(sub_frame)

x_count = frame.loc[(frame['y'] == 1) & (frame['year'] == 1979) & (frame['month'] == 'January')].shape[0]  # Isolate X to get the count
y_count = frame.loc[(frame['x'] == 1) & (frame['year'] == 1979) & (frame['month'] == 'January')].shape[0]  # Isolate Y to get the count
for x in range(x_count):
    for y in range(y_count):
        sub_frame = frame.loc[(frame['x'] == x) & (frame['y'] == y) & (frame['month'] == 'January')]
        print(sub_frame)
        print('X:', x, 'Y:', y, 'Average value:', sub_frame['value'].mean())
