import rasterstats as rs
import geopandas as gpd
import pandas as pd
from tqdm import tqdm
import glob
from multiprocessing import Pool
from functools import partial


def intersections(raster_file, shape_file, projection='4326'):
    # INPUTS:
    #   raster_file: path to the raster file
    #   shape_file: path to the shape file
    #   projection (optional): EPSG code of the projection of your shape file (default is 4326)

    # OUTPUT:
    #   frame: pandas dataframe that contains the min, max, and mean values for each feature in the shape file

    shape_frame = gpd.read_file(shape_file)
    shape = shape_frame.to_crs({'init': 'epsg:' + projection, 'no_defs': True})  # Change the projection to your input projection

    output_columns = ['min', 'max', 'mean']
    stats = rs.zonal_stats(shape, raster_file, stats=output_columns, all_touched=True)
    frame = pd.DataFrame.from_dict(stats)
    shape_frame['GEOID'] = shape_frame['GEOID'].astype(str)
    frame = frame.join(shape_frame['GEOID'])
    frame = frame.join(shape_frame['NAME'])
    return frame


def multithread_helper(raster_file, shape_file, projection='4326'):
    # Multithread helper function so each thread can save the frame to the disk as a csv
    filename = raster_file[-15:-8]
    print(filename)
    frame = intersections(raster_file, shape_file, projection)
    frame.to_csv('../narr_data_fix/rhum.2m/' + filename + '.csv')


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
