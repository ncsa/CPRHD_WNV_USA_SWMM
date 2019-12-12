# General Usage
import os
import glob
import numpy as np
import pandas as pd
import sys
from tqdm import tqdm

# Raster Data
import rasterstats as rs
import geopandas as gpd

# Plotting
import matplotlib.pyplot as plt
import calendar


def get_precipitation_timeseries_data(geoid, geotiffs, shape_frame):
    # Returns the precipitation data given a geoid and a list of masked GeoTIFFs
    # shape = gpd.read_file(shape_file)
    shape = shape_frame[shape_frame['GEOID10'] == geoid].reset_index()

    # Specify output statistics for zonal_stats
    output_stats = ['mean']

    # initialize the frame with the first GeoTIFF file
    name = geotiffs[0][geotiffs[0].rfind('/')+1:geotiffs[0].rfind('.')]
    stats = rs.zonal_stats(shape, geotiffs[0], stats=output_stats, all_touched=True)
    frame = pd.DataFrame.from_dict(stats)
    frame = frame.join(shape['GEOID10'])
    frame = frame.rename(columns={'mean':name})
    frame = frame[['GEOID10', name]]


    # loop through all the GeoTIFFs and join onto the original frame
    for file in geotiffs[1:]:
        name = file[file.rfind('/')+1:file.rfind('.')]
        stats = rs.zonal_stats(shape, file, stats=output_stats, all_touched=True)
        sub_frame = pd.DataFrame.from_dict(stats)
        sub_frame = sub_frame.rename(columns={'mean':name})
        frame = frame.join(sub_frame)


    # Convert to inches
    data = frame.iloc[0, 1:]
    data = data.apply(lambda x: x / 25.40)

    # Sort smallest to largest (1, 2, 3, ..., 365)
    data.index = data.index.astype(int)
    data = data.sort_index()

    return data.to_numpy()


def create_input_file_no_gi(row, evap, shape_frame, outfile, type='daily'):
    # outfile = './data/input_files/no_green_infrastructure/' + row['GEOID10'] + '_ng.inp'
    outfile = outfile

    if os.path.exists(outfile):
        print('File already exists!', outfile)
        return

    with open(outfile, 'w') as file:
        # Write [TITLE] Header
        writeString = '[TITLE]\n'
        writeString += ';; No Green Infrastructure\n'
        writeString += ';; ' + row['GEOID10'] + ' ' + row['STATE'] + ', ' + row['COUNTY'] + ' County\n'
        writeString += ';; Tract: ' + row['TRACT'] + '\tBlock Group: ' + row['BG_ID'] + '\n\n'
        file.write(writeString)

        # [OPTIONS]
            # User Input
        start_date = '01/01/2014'  # MM/DD/YYYY Format
        end_date = '12/31/2014'

        optionsVars = [['FLOW_UNITS', 'CFS'], ['INFILTRATION', 'GREEN_AMPT'], ['FLOW_ROUTING', 'KINWAVE'],
                       ['LINK_OFFSETS', 'DEPTH'], ['MIN_SLOPE', '0'], ['ALLOW_PONDING', 'NO'], ['SKIP_STEADY_STATE', 'NO\n'],

                       ['START_DATE', start_date], ['START_TIME', '00:00:00'], ['REPORT_START_DATE', start_date],
                       ['REPORT_START_TIME', '00:00:00'], ['END_DATE', end_date], ['END_TIME', '23:59:59'],
                       ['SWEEP_START', start_date[:-5]], ['SWEEP_END', end_date[:-5]], ['DRY_DAYS', '0'],
                       ['REPORT_STEP', '01:00:00'], ['WET_STEP', '00:06:00'], ['DRY_STEP', '00:06:00'],
                       ['ROUTING_STEP', '00:01:00\n'],

                       ['INERTIAL_DAMPING', 'PARTIAL'], ['NORMAL_FLOW_LIMITED', 'BOTH'], ['FORCE_MAIN_EQUATION', 'H-W'], ['VARIABLE_STEP', '0.75'],
                       ['LENGTHENING_STEP', '0'], ['MIN_SURFAREA', '12.557'], ['MAX_TRIALS', '8'], ['HEAD_TOLERANCE', '0.005'],
                       ['SYS_FLOW_TOL', '5'], ['LAT_FLOW_TOL', '5'], ['MINIMUM_STEP', '0.5'], ['THREADS', '1\n']]

        writeString = '[OPTIONS]\n;;Option\t\tValue\n'    # Write [OPTIONS] header

        for variable in optionsVars:
            writeString += writeVariable(variable[0], variable[1])  # Variable, Value
        file.write(writeString)

        # [EVAPORATION]
        writeString = '[EVAPORATION]\n;;DATA\tSource\tParameters\n;;------------------------\n'

        writeString += 'MONTHLY\t'
        for val in evap[1:]:
            writeString += str(val) + '\t'

        writeString += '\nDRY_ONLY\tYES\n\n'
        file.write(writeString)

        # [RAINGAGES]
        writeString = '[RAINGAGES]\n'
        writeString += ';;Name\tFormat\tInterval\tSCF\tSource\n'
        writeString += ';;--------------------------------------------\n'
        if type == 'daily':
            writeString += 'RainGage2\tVOLUME\t24:00:00\t1\tTIMESERIES NARR_DAILY\n\n'
        elif type == 'hourly':
            writeString += 'RainGage2\tVOLUME\t03:00:00\t1\tTIMESERIES NARR_3HR\n\n'
        file.write(writeString)

        # [SUBCATCHMENTS]
        writeString = '[SUBCATCHMENTS]\n'
        writeString += ';;Name\tRain Gage\tOutlet\tArea\t%Imperv\tWidth\t%Slope\tCurbLen\tSnowPack\n'
        writeString += ';;------------------------------------------------------------------------------\n'
        writeString += 'Subcatch1\tRainGage2\tOutfall1\t' + row['Area_acre_30m'] + '\t' + row['PCT_I_adj_30m'] + '\t' + row['WIDTH_30m'] + '\t' + row['pctslope_avg_30m'] + '\t0\n'
        writeString += 'Subcatch2\tRainGage2\tOutfall1\t0\t100\t0\t0\t0\n'
        writeString += 'Subcatch3\tRaingage2\tOutfall1\t0.000\t100\t0\t0\t0\n'
        writeString += 'Subcatch4\tRainGage2\tCisterns\t0.000\t100\t0\t0\t0'
        file.write(writeString)

        # [SUBAREAS]
        writeString = '\n\n[SUBAREAS]'
        writeString += '\n;;Subcatch\tN-Imperv\tN-Perv\tS-Imperv\tS-Perv\tPctZero\tRouteTo\tPctRouted'
        writeString += '\n;;---------------------------------------------------------------------------------------'
        writeString += '\nSubcatch1\t0.01\t' + row['ROUGH_NI_30m'] + '\t0.05\t' + row['DEPRESS_NI_30m'] + '\t0\tOUTLET'
        writeString += '\nSubcatch2\t0\t0\t0\t0\t0\tOUTLET'
        writeString += '\nSubcatch3\t0\t0\t0\t6\t0\tOUTLET'
        writeString += '\nSubcatch4\t0\t0\t0\t0\t0\tOUTLET'
        file.write(writeString)

        # [INFILTRATION]
        g_ampt_params = [['Suction', row['GMSH_adj_BG_30m']], ['Ksat', row['Keff_adj_BG_30m']], ['IMD', row['AMEP_adj_BG_30m']]]
        writeString = '\n\n[INFILTRATION]'
        writeString += '\n;;Subcatchment\tSuction\tKsat\tIMD'
        writeString += '\n;;------------------------------------------------------'
        for i in range(1, 5):
            writeString += '\nSubcatch' + str(i) + '\t' + g_ampt_params[0][1] + '\t' + g_ampt_params[1][1] + '\t' + g_ampt_params[2][1]
        file.write(writeString)

        # [LID_CONTROLS]
        writeString = '\n\n[LID_CONTROLS]'
        writeString += '\n;;Name\tType/Layer\tParameters'
        writeString += '\n;;--------------------------------------------'

            # Rain Garden
        writeString += '\nRainGarden\tBC'
        writeString += '\nRainGarden\tSURFACE\t6\t0\t0\t0\t0'
        writeString += '\nRainGarden\tSOIL\t12\t0.45\t0.1\t0.05\t10\t10\t1.6'
        writeString += '\nRainGarden\tSTORAGE\t0\t0\t0.4\t0'
        writeString += '\nRainGarden\tDRAIN\t0\t0.5\t6\t6'

            # Green Roof
        writeString += '\n\nGreenRoof\tBC'
        writeString += '\nGreenRoof\tSURFACE\t0\t0\t0\t0\t0'
        writeString += '\nGreenRoof\tSOIL\t4\t0.45\t0.1\t0.05\t10\t10\t1.6'
        writeString += '\nGreenRoof\tSTORAGE\t3\t0.75\t0\t0'
        writeString += '\nGreenRoof\tDRAIN\t10\t0.5\t0\t0'

            # Street Planter
        writeString += '\n\nStreetPlanter\tBC'
        writeString += '\nStreetPlanter\tSURFACE\t6\t0\t0\t0\t0'
        writeString += '\nStreetPlanter\tSOIL\t18\t0.45\t0.1\t0.05\t10\t10\t1.6'
        writeString += '\nStreetPlanter\tSTORAGE\t12\t0.75\t0.108\t0'

            # Porous Pavement
        writeString += '\n\nPorousPavement\tPP'
        writeString += '\nPorousPavement\tSURFACE\t0.05\t0\t0.01\t3\t0'
        writeString += '\nPorousPavement\tPAVEMENT\t6\t0.12\t0\t400\t0'
        writeString += '\nPorousPavement\tSTORAGE\t18\t0.75\t0.108\t0'
        file.write(writeString)

        # [LID_USAGE]
        writeString = '\n\n[LID_USAGE]'
        writeString += '\n;;Subcatchment\tLID\tProcess\tNumber\tArea\tWidth\tInitSat\tFromImp\tToPerv\tRptFile\tDrainTo'
        file.write(writeString)

        # [JUNCTIONS]
        writeString = '\n\n[JUNCTIONS]'
        writeString += '\n;;Name\tElevation\tMaxDepth\tInitDepth\tSurDepth\tAponded'
        writeString += '\n;;---------------------------------------------------------'
        writeString += '\nCisterns\t0\t0\t0\t0\t0'
        file.write(writeString)

        # [OUTFALLS]
        writeString = '\n\n[OUTFALLS]'
        writeString += '\n;;Name\tElevation\tType\tStage\tData\tGated\tRouted\tTo'
        writeString += '\n;;----------------------------------------------------------------------------'
        writeString += '\nOutfall1\t0\tFREE\tNO'
        file.write(writeString)

        # [STORAGE]
        writeString = '\n\n[STORAGE]'
        file.write(writeString)

        # [CONDUITS]
        writeString = '\n\n[CONDUITS]'
        file.write(writeString)

        # [XSECTIONS]
        writeString = '\n\n[XSECTIONS]'
        file.write(writeString)

        # [TIMESERIES]
        writeString = '\n\n[TIMESERIES]'
        writeString += '\n;;Name\tDate\tTime\tValue\n'
        writeString += ';;---------------------------\n'

        if type == 'daily':
            geotiffs = glob.glob('./daily/masked_geotiffs/*.geotiff')
            name = 'NARR_DAILY'
            frequency = 'D'
        elif type == 'hourly':
            geotiffs = glob.glob('./hourly/masked_geotiffs/*.geotiff')
            name = 'NARR_3HR'
            frequency = '3H'

        precipitation_data = get_precipitation_timeseries_data(row['GEOID10'], geotiffs, shape_frame)
        date_range = pd.date_range(start=start_date, end='1/1/2015', freq=frequency)[:-1]

        for i in range(len(precipitation_data)):
            date = date_range[i]
            writeString += name + '\t' + date.strftime('%m/%d/%Y') + '\t' + str(date.time()) + '\t' + str(precipitation_data[i]) + '\n'
        file.write(writeString)

        # [REPORT]
        reportVars = [['INPUT', 'NO'], ['CONTROLS', 'NO'], ['SUBCATCHMENTS', 'ALL'], ['NODES', 'ALL'], ['LINKS', 'ALL']]
        writeString = '\n[REPORT]\n;;Reporting\t\tOptions\n'
        for variable in reportVars:
            writeString += writeVariable(variable[0], variable[1])
        file.write(writeString)

        # [TAGS]
        file.write('\n[TAGS]')

        # [MAP]
        mapString = '\n\n[MAP]\n'
        dimension = '10000000000.000'
        mapString += 'DIMENSIONS\t' + dimension + '\t' + dimension + '\t-' + dimension + '\t-' + dimension
        mapString += '\nUnits\t\tNone'
        file.write(mapString)

        # [COORDINATES]
        writeString = '\n\n[COORDINATES]'
        writeString += '\n;;Node\t\t X-Coord\t\tY-Coord'
        writeString += '\n;;---------------------------------------------'
        file.write(writeString)

        # [VERTICES]
        writeString = '\n\n[VERTICES]'
        writeString += '\n;;Link\t\t X-Coord\t\tY-Coord'
        writeString += '\n;;---------------------------------------------'
        file.write(writeString)

        # [POLYGONS]
        writeString = '\n\n[POLYGONS]'
        writeString += '\n;;Subcatchment\t X-Coord\t\tY-Coord'
        writeString += '\n;;---------------------------------------------'
        file.write(writeString)

        # [SYMBOLS]
        writeString = '\n\n[SYMBOLS]'
        writeString += '\n;;Gage\t\t X-Coord\t\tY-Coord'
        writeString += '\n;;---------------------------------------------'
        file.write(writeString)


def writeVariable(name, value):
    tabs = ''
    tab_count = 2
    if len(name) > 15:
        tab_count = 1
    elif len(name) < 8:
        tab_count = 3

    tabs += '\t' * tab_count
    return name + tabs + value + '\n'


def main():
    # Load Block Group Characteristics
    characteristics_file = '../../data/input_file_data/Selected_BG_inputs_20191212.csv'
    characteristics_frame = pd.read_csv(characteristics_file, skip_blank_lines=True, low_memory=False, dtype=str)  # Read the green infrastructure data to a pandas dataframe

    # Load Evaporation Data
    evap = pd.read_pickle('../../data/input_file_data/evaporation_converted.pkl')

    # Load Block Group Shape File
    shape_frame = gpd.read_file('./shape_file/SelectBG_all_land_BGID_final.gpkg')

    # List of GeoID's we want to create input files for
    geoids = ['260810146022', '060375508003', '170319800001', '080310034021', '482019801001', '120110502083', '360470220002']

    for geoid in tqdm(geoids):
        for type in ['daily', 'hourly']:
            row = characteristics_frame.loc[characteristics_frame['GEOID10'] == geoid].reset_index(drop=True).iloc[0]  # Select the block group's information
            evap_data = evap.loc[row['GEOID10']]  # Select the block group's evaporation data

            name = row['STATE'].lower()
            outfile = './' + type + '/simulation_files/' + name + '_ng_' + type + '.inp'
            print(outfile)
            create_input_file_no_gi(row, evap_data, shape_frame, outfile, type=type)

if __name__ == '__main__':
    main()
