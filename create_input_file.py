from fips_converter import fips_conversion
import csv
from multiprocessing import Pool
import pandas as pd
import time


def create_input_file(row):
    with open('./data/input_files/' + row['GEOID10'] + '.inp', 'w') as file:

        print('Processing', row['GEOID10'])

        # Write [TITLE] Header
        file.write('[TITLE]\n;; ' + row['GEOID10'] + ' ' + fips_conversion(row['GEOID10'])[0] + ', ' + fips_conversion(row['GEOID10'])[1] + ' County\n\n')

        # [OPTIONS]

        # [OPTIONS] data
        optionsVariableList = [['FLOW_UNITS', 'CFS'], ['INFILTRATION', 'GREEN_AMPT'], ['FLOW_ROUTING', 'KINWAVE'],
                               ['LINK_OFFSETS', 'DEPTH'], ['MIN_SLOPE', '0'], ['ALLOW_PONDING', 'NO'], ['SKIP_STEADY_STATE', 'NO\n'],

                               ['START_DATE', '01/01/1981'], ['START_TIME', '00:00:00'], ['REPORT_START_DATE', '01/01/1981'],
                               ['REPORT_START_TIME', '00:00:00'], ['END_DATE', '12/31/1985'], ['END_TIME', '23:59:59'],
                               ['SWEEP_START', '01/01'], ['SWEEP_END', '12/31'], ['DRY_DAYS', '0'],
                               ['REPORT_STEP', '01:00:00'], ['WET_STEP', '00:06:00'], ['DRY_STEP', '00:06:00'],
                               ['ROUTING_STEP', '00:06:00\n'],

                               ['INERTIAL_DAMPING', 'PARTIAL'], ['NORMAL_FLOW_LIMITED', 'BOTH'], ['FORCE_MAIN_EQUATION', 'H-W'], ['VARIABLE_STEP', '0.75'],
                               ['LENGTHENING_STEP', '0'], ['MIN_SURFAREA', '12.557'], ['MAX_TRIALS', '8'], ['HEAD_TOLERANCE', '0.005'],
                               ['SYS_FLOW_TOL', '5'], ['LAT_FLOW_TOL', '5'], ['MINIMUM_STEP', '0.5'], ['THREADS', '1\n']]

        optionsString = ''

        # Write [OPTIONS] header
        optionsString += '[OPTIONS]\n;;Option\t\tValue\n'
        # Write [OPTIONS] block
        for variable in optionsVariableList:
            optionsString += writeVariable(variable[0], variable[1])
        file.write(optionsString)

        # [EVAPORATION]
        evaporationString = ''
        # Write [EVAPORATION] header
        evaporationString += '[EVAPORATION]\n;;DATA\tSource\tParameters\n;;-----------------------------\n\n'
        file.write(evaporationString)

        # [TIMESERIES]


def writeVariable(name, value):
    tabs = ''
    tab_count = 2
    if len(name) > 15:
        tab_count = 1
    elif len(name) < 8:
        tab_count = 3

    tabs += '\t' * tab_count
    return name + tabs + value + '\n'


if __name__ == '__main__':
    with open('./data/input_file_data/group_characteristics/Selected_BG_inputs_20180208.csv') as characteristics_file:
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
