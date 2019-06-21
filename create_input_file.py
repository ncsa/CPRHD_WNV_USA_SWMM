from fips_converter import fips_conversion  # Converting Fips Codes for [TITLE] block
import csv  # Reading data files
from multiprocessing import Pool, Manager  # Multithreading
import pandas as pd  # Data-frame
import time  # Time analysis


def create_input_file(row, gi_type=None):
    with open('./data/input_files/' + row['GEOID10'] + '.inp', 'w') as file:
        print('Processing', row['GEOID10'])
        # Write [TITLE] Header
        file.write('[TITLE]\n;; ' + row['GEOID10'] + ' ' + fips_conversion(row['GEOID10'])[0] + ', ' + fips_conversion(row['GEOID10'])[1] + ' County\n\n')

        # [OPTIONS]
        # [OPTIONS] data
        start_date = '01/01/1981'
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

        for variable in optionsVars:    # Write [OPTIONS] block
            writeString += writeVariable(variable[0], variable[1])
        file.write(writeString)

        # [EVAPORATION]
        # TODO Get Evaporation data
        evaporationString = '[EVAPORATION]\n;;DATA\tSource\tParameters\n;;------------------------\n\n'  # Write [EVAPORATION] header
        file.write(evaporationString)

        # [RAINGAGES]
        writeString = '[RAINGAGES]\n'
        writeString += ';;Name\tFormat\tInterval\tSCF\tSource\n'
        writeString += ';;--------------------------------------------\n'
        writeString += 'RainGage2\tVOLUME\t24:00:00\t1\tTIMESERIES ' + row['PRISM_ID'] + '\n\n'
        file.write(writeString)

        # [SUBCATCHMENTS]
        writeString = '[SUBCATCHMENTS]\n'
        writeString += ';;Name\tRain Gage\tOutlet\tArea\t%Imperv\tWidth\t%Slope\tCurbLen\tSnowPack\n'
        writeString += ';;------------------------------------------------------------------------------\n'

        # There are three possible impervious percentages depending on the GI type
        imperv_percent = row['PCT_I_adj_30m']
        if gi_type == 'barrel':
            imperv_percent = row['RB_SC1_PCT_I_30m']
        elif gi_type == 'garden':
            imperv_percent = row['RG1_PCT_I_adj_30m']

        writeString += 'Subcatch1\tRainGage2\tOutfall1\t' + row['Area_acre_30m'] + '\t' + imperv_percent + '\t' + row['WIDTH_30m'] + '\t' + row['pctslope_avg_30m'] + '\t0\n'
        writeString += 'Subcatch2\tRainGage2\tOutfall1\t0\t100\t0\t0\t0\n'
        writeString += 'Subcatch3\tRaingage2\tOutfall1\t0.000\t100\t0\t0\t0\n'

        if gi_type == 'barrel':
            writeString += 'Subcatch4\tRainGage2\tCisterns\t' + row['RB_SC1_ACRE_30m'] + '\tFILL\tFILL\tFILL\t0\n'
        else:
            writeString += 'Subcatch4\tRainGage2\tCisterns\t0.000\t100\t0\t0\t0'
        file.write(writeString)

        # [SUBAREAS]
        writeString = '\n\n[SUBAREAS]'
        writeString += '\n;;Subcatch\tN-Imperv\tN-Perv\tS-Imperv\tS-Perv\tPctZero\tRouteTo\tPctRouted'
        writeString += '\n;;---------------------------------------------------------------------------------------'
        writeString += '\nSubcatch1\t0.01\t' + row['ROUGH_NI_30m'] + '\t0.05\t' + row['DEPRESS_NI_30m'] + '\t0\tOUTLET'
        writeString += '\nSubcatch2\t0\t0\t0\t0\t0\tOUTLET'
        writeString += '\nSubcatch3\t0\t0\t0\t6\t0\tOUTLET'
        if gi_type == 'barrel':
            writeString += '\nSubcatch4\t0.01\t' + row['ROUGH_NI_30m'] + '\t0.05\t' + row['DEPRESS_NI_30m'] + '\t0\tOUTLET'
        else:
            writeString += '\nSubcatch4\t0\t0\t0\t0\t0\tOUTLET'
        file.write(writeString)

        # [INFILTRATION]
        g_ampt_params = [['Suction', '5.1'], ['Ksat', '0.4'], ['IMD', '0.26']]
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
        writeString += '\nRainGarden\tSTORAGE\t0\t0\t0.108\t0'
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
        if gi_type == 'garden':
            writeString += '\nSubcatch1\tRainGarden\t1\tFILL\tFILL\tFILL\tFILL\tFILL'
        else:
            writeString += '\nSubcatch1\tRainGarden\t1\t0\t0\t0\t0\t0'
        file.write(writeString)

        # [JUNCTIONS]
        if gi_type != 'barrel':
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
        if gi_type == 'barrel':
            writeString += '\n0\t4\t0\tFUNCTION\t0\t0\tFILL\t0\t0\t2.4\tFILL\t0'
        file.write(writeString)

        # [CONDUITS]
        writeString = '\n\n[CONDUITS]'
        if gi_type == 'barrel':
            writeString += '\nDummy2\tCisterns\tOutfall1\t400\t0.01\t0\t0\t0'
        file.write(writeString)

        # [XSECTIONS]
        writeString = '\n\n[XSECTIONS]'
        if gi_type == 'barrel':
            writeString += '\nDummy2\tDUMMY\t0\t0\t0\t0\t1'
        file.write(writeString)

        # [TIMESERIES]
        writeString = '\n\n[TIMESERIES]'
        writeString += '\n;;Name\tDate\tTime\tValue\n'
        writeString += ';;---------------------------\n'

        with open('./data/input_file_data/weather_data/' + row['PRISM_ID'] + '.csv', 'r', newline='') as weather_file:
            reader = csv.reader(weather_file)
            start_date_compare = start_date[-4:] + '-' + start_date[:2] + '-' + start_date[3:5]  # Convert to YYYY-MM-DD (for <=, >= support)
            end_date_compare = end_date[-4:] + '-' + end_date[:2] + '-' + end_date[3:5]  # Convert to YYYY-MM-DD

            for line in reader:
                date = line[0][5:7] + '/' + line[0][-2:] + '/' + line[0][:4]  # Convert date from YYYY-MM-DD to MM/DD/YYYY (SWMM format)
                if start_date_compare <= line[0] <= end_date_compare:  # If the timeseries is within our start and end range
                    writeString += (row['PRISM_ID'] + '\t' + date + '\t' + '0:00:00' + '\t' + line[1] + '\n')
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


def createWeatherDictionary(characteristics_dict):
    dictionary = {}

    for chunk in pd.read_csv('./data/input_file_data/rotated_weather_data.csv', chunksize=1000, skiprows=[1, 2, 3, 4], nrows=250):
        print(chunk.shape)
        #chunk.set_index('date', inplace=True)
        for P_ID in chunk['date']:
            #print(chunk.loc[P_ID])
            if P_ID not in dictionary:
                dictionary[P_ID] = {}

        for row in characteristics_dict:
            prism_id = row['PRISM_ID']
            geoid = row['GEOID10']
            if prism_id in chunk['date'].values.tolist() and geoid not in dictionary[prism_id]:
                dictionary[prism_id][geoid] = '5'

        geoids_list = []

        for key in dictionary.items():
            geoid_list = []
            for geoid in key[1]:
                geoid_list.append(geoid)
            geoids_list.append(geoid_list)

        dictionary.clear()
        count = 0
        for P_ID in chunk['date']:
            if P_ID not in dictionary:
                dictionary[P_ID] = geoids_list[count]
                count += 1


    writer = csv.writer(open('dictionary.csv', 'w'))
    for key, val in dictionary.items():
        writer.writerow([key, val])


if __name__ == '__main__':
    with open('./data/input_file_data/Selected_BG_inputs_20180208.csv') as characteristics_file:
        start_time = time.time()
        # Convert the input characteristics data .csv to a pandas dataframe
        characteristics_frame = pd.read_csv(characteristics_file, skip_blank_lines=True, low_memory=False, dtype=str)

        # Change the GeoID column name since it has some weird characters
        temp_columns = list(characteristics_frame.columns)
        temp_columns[0] = 'GEOID10'
        characteristics_frame.columns = temp_columns

        # Load each row into a list of dictionaries
        characteristics_row_dict = characteristics_frame.T.to_dict().values()

        print('Setup time:', time.time() - start_time)

        # Send the threads to process the input files
        start_time = time.time()
        pool = Pool()
        pool.map(create_input_file, characteristics_row_dict)

        print('File processing elapsed time:', time.time() - start_time)
