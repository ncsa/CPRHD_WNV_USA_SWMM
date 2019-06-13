from fips_converter import fips_conversion  # Converting Fips Codes for [TITLE] block
import csv  # Reading data files
from multiprocessing import Pool, Manager  # Multithreading
import pandas as pd  # Data-frame
import time  # Time analysis


def create_input_file(row):
    with open('./data/input_files/' + row['GEOID10'] + '.inp', 'w') as file:

        print('Processing', row['GEOID10'])
        # Write [TITLE] Header
        file.write('[TITLE]\n;; ' + row['GEOID10'] + ' ' + fips_conversion(row['GEOID10'])[0] + ', ' + fips_conversion(row['GEOID10'])[1] + ' County\n\n')

        # [OPTIONS]

        # [OPTIONS] data
        start_date = '01/01/1981'
        end_date = '12/31/2014'

        optionsVariableList = [['FLOW_UNITS', 'CFS'], ['INFILTRATION', 'GREEN_AMPT'], ['FLOW_ROUTING', 'KINWAVE'],
                               ['LINK_OFFSETS', 'DEPTH'], ['MIN_SLOPE', '0'], ['ALLOW_PONDING', 'NO'], ['SKIP_STEADY_STATE', 'NO\n'],

                               ['START_DATE', start_date], ['START_TIME', '00:00:00'], ['REPORT_START_DATE', start_date],
                               ['REPORT_START_TIME', '00:00:00'], ['END_DATE', end_date], ['END_TIME', '23:59:59'],
                               ['SWEEP_START', start_date[:-5]], ['SWEEP_END', end_date[:-5]], ['DRY_DAYS', '0'],
                               ['REPORT_STEP', '01:00:00'], ['WET_STEP', '00:06:00'], ['DRY_STEP', '00:06:00'],
                               ['ROUTING_STEP', '00:06:00\n'],

                               ['INERTIAL_DAMPING', 'PARTIAL'], ['NORMAL_FLOW_LIMITED', 'BOTH'], ['FORCE_MAIN_EQUATION', 'H-W'], ['VARIABLE_STEP', '0.75'],
                               ['LENGTHENING_STEP', '0'], ['MIN_SURFAREA', '12.557'], ['MAX_TRIALS', '8'], ['HEAD_TOLERANCE', '0.005'],
                               ['SYS_FLOW_TOL', '5'], ['LAT_FLOW_TOL', '5'], ['MINIMUM_STEP', '0.5'], ['THREADS', '1\n']]

        # Write [OPTIONS] header
        optionsString = '[OPTIONS]\n;;Option\t\tValue\n'
        # Write [OPTIONS] block
        for variable in optionsVariableList:
            optionsString += writeVariable(variable[0], variable[1])
        file.write(optionsString)

        # [EVAPORATION]

        evaporationString = '[EVAPORATION]\n;;DATA\tSource\tParameters\n;;-----------------------------\n\n'  # Write [EVAPORATION] header
        file.write(evaporationString)

        # [TIMESERIES]
        timeSeriesString = '[TIMESERIES]\n;;Name\tDate\tTime\tValue\n'  # Timeseries header
        timeSeriesString += ';;--------------------------------------------\n'

        with open('./data/input_file_data/rows/' + row['PRISM_ID'] + '.csv', 'r', newline='') as weather_file:
            reader = csv.reader(weather_file)
            start_date_compare = start_date[-4:] + '-' + start_date[:2] + '-' + start_date[3:5]  # Convert to YYYY-MM-DD (for <=, >= support)
            end_date_compare = end_date[-4:] + '-' + end_date[:2] + '-' + end_date[3:5]  # Convert to YYYY-MM-DD

            for line in reader:
                date = line[0][5:7] + '/' + line[0][-2:] + '/' + line[0][:4]  # Convert date from YYYY-MM-DD to MM/DD/YYYY (SWMM format)
                if start_date_compare <= line[0] <= end_date_compare:
                    timeSeriesString += (row['PRISM_ID'] + '\t\t' + date + '\t' + '0:00:00' + '\t' + line[1] + '\n')

        file.write(timeSeriesString)


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

        # for value in dictionary.values():
        #     geoid_list = []
        #     for geoid in value:
        #         geoid_list.append(geoid)
        #     geoids_list.append(geoid_list)
        # print(geoids_list)

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

        # for key, val in dictionary.items():
        #     dictionary[key][val] =

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
