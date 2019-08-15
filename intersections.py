import rasterstats as rs
import geopandas as gpd
import pandas as pd
from tqdm import tqdm
import glob
# from multiprocessing import Pool
# from functools import partial


def intersections(raster_file, shape_file):
    # Preconditions: A shape file and raster file have been passed, each having the same projection.
    # Postconditions: A pandas dataframe has been returned, holding the min, max, mean, and count for each polygon in the shape file.
    shape_frame = gpd.read_file(shape_file)

    shape = shape_frame.to_crs({'init': 'epsg:5070', 'no_defs': True})

    output = ['min', 'max', 'mean', 'count']
    stats = rs.zonal_stats(shape, raster_file, stats=output, all_touched=True)
    frame = pd.DataFrame.from_dict(stats)
    shape_frame['GEOID10'] = shape_frame['GEOID10'].astype(str)
    print(shape_frame['GEOID10'])
    frame = frame.join(shape_frame['GEOID10'])
    return frame


# SINGLE THREADED
# for file in tqdm(file_list):
#     frame = intersections('./data/evap/shape_files/county/tl_2017_us_county.shp', file)
#     frame.to_csv('./data/evap/rohan/air.2m/intersection/' + file[-15:-8] + '.csv')


# MULTI THREADED
# if __name__ == '__main__':
#
#     file_list = []
#     for i in range(1999, 2016):
#         file_list.extend(glob.glob('./data/evap/rohan/rhum.2m/geotiff/' + str(i) + '*.geotiff'))
#
#     arg_list = ['./data/evap/shape_files/county/tl_2017_us_county.shp', ] * len(file_list)
#     arg_list = tuple(zip(arg_list, file_list))
#     print(arg_list[0][0], arg_list[0][1])
#     pool = Pool()
#     # pool.map(intersections, ['./data/evap/shape_files/county/tl_2017_us_county.shp', arg_list])
#     pool.map(partial(intersections, shape_file='./data/evap/shape_files/urban_county/2017_us_urban_county.shp'), file_list)
