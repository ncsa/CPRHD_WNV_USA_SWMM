import rasterstats as rs
import geopandas as gpd
import pandas as pd
from tqdm import tqdm
import glob
from multiprocessing import Pool
from functools import partial


def intersections(raster_file, shape_file, proj4='+proj=longlat +datum=WGS84 +no_defs', interpolation=False):
    # INPUTS:
    #   raster_file: path to the raster file
    #   shape_file: path to the shape file
    #   proj4 (optional): PROJ.4 string of your projection (default is EPSG 4326)
    #   interpolation (optional): Whether or not the program should interpolate missing data values based on nearest neighbors, or leave them blank (default False)

    # OUTPUT:
    #   frame: pandas dataframe that contains the min, max, and mean values for each feature in the shape file

    shape_frame = gpd.read_file(shape_file)
    shape = shape_frame.to_crs(proj4)  # Change the projection using the input proj4 string

    output_columns = ['count', 'min', 'max', 'mean']
    stats = rs.zonal_stats(shape, raster_file, stats=output_columns, all_touched=True)
    frame = pd.DataFrame.from_dict(stats)

    if 'GEOID' in shape_frame.columns:  # If the shapefile has GEOID in its attributes
        shape_frame['GEOID'] = shape_frame['GEOID'].astype(str)  # Convert to string to keep the leading zeroes
        frame = frame.join(shape_frame['GEOID'])  # Add the GEOID's to the zonal_stats frame

    elif 'GEOID10' in shape_frame.columns:  # If the shapefile has GEOID10 ID's, do the same but with different column name
        shape_frame['GEOID10'] = shape_frame['GEOID10'].astype(str)
        frame = frame.join(shape_frame['GEOID10'])

    frame = frame.join(shape_frame['NAME'])  # Add the county name to the zonal_stats frame

    #############################################################
    # Data interpolation for polygons which have no raster data #
    #############################################################
    if interpolation:
        neighbors_frame = pd.read_csv('urban_counties_shapefile_neighbors.csv')  # Get a frame containing each feature's neighbors

        bad_features = frame.loc[frame['count'] < 1]  # Identify the bad counties based on the count of raster pixels touching it
        for feature in bad_features['NAME']:
            neighbors = neighbors_frame.loc[neighbors_frame['NAME'] == feature]['NEIGHBORS'].iloc[0].split(',')  # Get a list of the county's neighbors

            min = max = mean = area = 0

            for neighbor in neighbors:
                neighbor_data = frame.loc[frame['NAME'] == neighbor].join(neighbors_frame.loc[neighbors_frame['NAME'] == neighbor]['ALAND']).iloc[0]  # Get a dataframe of the neighbor's min, max, mean, and area.

                # Weighted average calculation
                min += neighbor_data['min'] * neighbor_data['ALAND']
                max += neighbor_data['max'] * neighbor_data['ALAND']
                mean += neighbor_data['mean'] * neighbor_data['ALAND']
                area += neighbor_data['ALAND']

            min /= area
            max /= area
            mean /= area

            # Insert the averaged data into the original frame
            frame.loc[frame['NAME'] == feature, 'min'] = min
            frame.loc[frame['NAME'] == feature, 'max'] = max
            frame.loc[frame['NAME'] == feature, 'mean'] = mean

    return frame


def multithread_helper(raster_file, shape_file, output_destination, proj4='+proj=longlat +datum=WGS84 +no_defs', interpolation=False):
    # Multithread helper function so each thread can save the frame to disk as a csv
    filename = raster_file[-22:-8]
    print(filename)
    frame = intersections(raster_file, shape_file, proj4, interpolation)
    frame.to_csv(output_destination + filename + '.csv')


# SINGLE THREADED OPERATION
shape_file = '../narr_data_fix/urban_counties/urban_counties_wnv_4326.shp'
# file_list = glob.glob('../narr_data_fix/air.2m_geotiff/*.geotiff')
# for file in tqdm(file_list):
#     frame = intersections(file, shape_file)


# # MULTI THREADED OPERATION
# if __name__ == '__main__':
#     file_list = glob.glob('../narr_data_fix/rhum.2m_geotiff/*.geotiff')
#     pool = Pool()
#     pool.map(partial(multithread_helper, shape_file=shape_file, projection='4326'), file_list)
