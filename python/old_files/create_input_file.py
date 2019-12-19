from fips_converter import fips_conversion  # Converting Fips Codes for [TITLE] block
import csv  # Reading data files
from multiprocessing import Pool, Manager  # Multithreading
import pandas as pd  # Data-frame
import time  # Time analysis
import os
from functools import partial


def writeVariable(name, value):
    tabs = ''
    tab_count = 2
    if len(name) > 15:
        tab_count = 1
    elif len(name) < 8:
        tab_count = 3

    tabs += '\t' * tab_count
    return name + tabs + value + '\n'


def create_input_file_rain_garden(row, namespace):
    with open('./data/input_files/rain_garden/' + row['GEOID10'] + '_rg.inp', 'w') as file:
        print(row['GEOID10'], '- Rain Garden')

        # Write [TITLE] Header
        location = fips_conversion(row['GEOID10'])  # Convert the GeoID10 to State / County / Tract / Block Group

        writeString = '[TITLE]\n'
        writeString += ';; Rain Garden\n'
        writeString += ';; ' + row['GEOID10'] + ' ' + location[0] + ', ' + location[1] + ' County\n;; Tract: ' + location[2] + '\tBlock Group: ' + location[3] + '\n\n'
        file.write(writeString)

        # [OPTIONS]
            # User Input
        start_date = '01/01/1981'  # MM/DD/YYYY Format
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
            writeString += writeVariable(variable[0], variable[1])  # Variable, Value
        file.write(writeString)

        # [EVAPORATION]
        writeString = '[EVAPORATION]\n;;DATA\tSource\tParameters\n;;------------------------\n'  # Write [EVAPORATION] header

        values = namespace.evap.loc[row['GEOID10']].values.T.tolist()

        writeString += 'MONTHLY\t'
        for val in values[1:]:
            writeString += str(val) + '\t'
        writeString += '\nDRY_ONLY\tYES\n\n'
        file.write(writeString)

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

        slope_percent = row['pctslope_avg_30m']
        subcatchment_area = row['Area_acre_30m']
        imperv_percent = row['PCT_I_adj_30m']
        width = row['WIDTH_30m']

        writeString += 'Subcatch1\tRainGage2\tOutfall1\t' + subcatchment_area + '\t' + imperv_percent + '\t' + width + '\t' + slope_percent + '\t0\n'
        writeString += 'Subcatch2\tRainGage2\tOutfall1\t0\t100\t0\t0\t0\n'
        writeString += 'Subcatch3\tRaingage2\tOutfall1\t0.000\t100\t0\t0\t0\n'
        writeString += 'Subcatch4\tRainGage2\tCisterns\t0.000\t100\t0\t0\t0\n'
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
        porosity = row['RG1_POROSITY']
        field_capacity = row['RG1_FIELDCAP']
        wilting_point = row['RG1_WILTPT']
        conductivity = row['RG1_Ks']
        conductivity_slope = row['RG1_Ks_SLOPE']
        suction_head = row['RG1_SH']

        seepage = row['RG1_SEEPAGE']

        writeString += '\nRainGarden\tBC'
        writeString += '\nRainGarden\tSURFACE\t6\t0\t0\t0\t0'
        writeString += '\nRainGarden\tSOIL\t12\t' + porosity + '\t' + field_capacity + '\t' + wilting_point + '\t' + conductivity + '\t' + conductivity_slope + '\t' + suction_head + '\n'
        writeString += '\nRainGarden\tSTORAGE\t0\t0\t' + seepage + '\t0'
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
        writeString += '\nSubcatch1\tRainGarden\t1\t' + row['RG1_AREA_SQRFT'] + '\t0\t0\t' + row['RG1_PCT_I_TREAT_30m'] + '\t0\n'
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

        with open('./data/input_file_data/weather_data/' + row['PRISM_ID'] + '.csv', 'r', newline='') as weather_file:
            reader = csv.reader(weather_file)
            start_date_compare = start_date[-4:] + '-' + start_date[:2] + '-' + start_date[3:5]  # Convert to YYYY-MM-DD (for <=, >= support)
            end_date_compare = end_date[-4:] + '-' + end_date[:2] + '-' + end_date[3:5]  # Convert to YYYY-MM-DD

            for line in reader:
                if line:
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


def create_input_file_rain_barrel(row, namespace):
    with open('./data/input_files/rain_barrel/' + row['GEOID10'] + '_rb.inp', 'w') as file:
        print(row['GEOID10'], '- Rain Barrel')

        # Write [TITLE] Header
        location = fips_conversion(row['GEOID10'])  # Convert the GeoID10 to State / County / Tract / Block Group

        writeString = '[TITLE]\n'
        writeString += ';; Rain Barrel\n'
        writeString += ';; ' + row['GEOID10'] + ' ' + location[0] + ', ' + location[1] + ' County\n;; Tract: ' + location[2] + '\tBlock Group: ' + location[3] + '\n\n'
        file.write(writeString)

        # [OPTIONS]
            # User Input
        start_date = '01/01/1981'  # MM/DD/YYYY Format
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
            writeString += writeVariable(variable[0], variable[1])  # Variable, Value
        file.write(writeString)

        # [EVAPORATION]
        writeString = '[EVAPORATION]\n;;DATA\tSource\tParameters\n;;------------------------\n'  # Write [EVAPORATION] header

        values = namespace.evap.loc[row['GEOID10']].values.T.tolist()

        writeString += 'MONTHLY\t'
        for val in values[1:]:
            writeString += str(val) + '\t'
        writeString += '\nDRY_ONLY\tYES\n\n'
        file.write(writeString)

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

        slope_percent = row['pctslope_avg_30m']

        # Rain Barrel Data
        rb_subcatchment_area = row['RB_SC1_ACRE_30m']  # Area of Subcatchment1
        rb_imperv_percent = row['RB_SC1_PCT_I_30m']  # Imperviousness of Subcatchment1
        rb_width = row['RB_SC1_WIDTH_30m']  # Width of Subcatchment1 area

        rb_roof_area = row['SCA_ROOF_ACRE']
        rb_roof_width = row['SCA_ROOF_WIDTH']

        writeString += 'Subcatch1\tRainGage2\tOutfall1\t' + rb_subcatchment_area + '\t' + rb_imperv_percent + '\t' + rb_width + '\t' + slope_percent + '\t0\n'
        writeString += 'Subcatch2\tRainGage2\tOutfall1\t0\t100\t0\t0\t0\n'
        writeString += 'Subcatch3\tRaingage2\tOutfall1\t0.000\t100\t0\t0\t0\n'
        writeString += 'Subcatch4\tRainGage2\tCisterns\t' + rb_roof_area + '\t' + '100' + '\t' + rb_roof_width + '\t' + slope_percent + '\t0\n'
        file.write(writeString)

        # [SUBAREAS]
        writeString = '\n\n[SUBAREAS]'
        writeString += '\n;;Subcatch\tN-Imperv\tN-Perv\tS-Imperv\tS-Perv\tPctZero\tRouteTo\tPctRouted'
        writeString += '\n;;---------------------------------------------------------------------------------------'
        writeString += '\nSubcatch1\t0.01\t' + row['ROUGH_NI_30m'] + '\t0.05\t' + row['DEPRESS_NI_30m'] + '\t0\tOUTLET'
        writeString += '\nSubcatch2\t0\t0\t0\t0\t0\tOUTLET'
        writeString += '\nSubcatch3\t0\t0\t0\t6\t0\tOUTLET'
        writeString += '\nSubcatch4\t0.01\t' + row['ROUGH_NI_30m'] + '\t0.05\t' + row['DEPRESS_NI_30m'] + '\t0\tOUTLET'
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
        file.write(writeString)

        # # [JUNCTIONS]
        # if gi_type != 'barrel':
        #     writeString = '\n\n[JUNCTIONS]'
        #     writeString += '\n;;Name\tElevation\tMaxDepth\tInitDepth\tSurDepth\tAponded'
        #     writeString += '\n;;---------------------------------------------------------'
        #     writeString += '\nCisterns\t0\t0\t0\t0\t0'
        #     file.write(writeString)

        # [OUTFALLS]
        writeString = '\n\n[OUTFALLS]'
        writeString += '\n;;Name\tElevation\tType\tStage\tData\tGated\tRouted\tTo'
        writeString += '\n;;----------------------------------------------------------------------------'
        writeString += '\nOutfall1\t0\tFREE\tNO'
        file.write(writeString)

        # [STORAGE]
        writeString = '\n\n[STORAGE]'

        rb_storage_area = row['RB_STORE_SQRFT']
        writeString += '\nCisterns\t0\t4\t0\tFUNCTIONAL\t0\t0\t' + rb_storage_area + '\t0\t0\t2.4\t0.182\t0'  # Replace 0.182 inches per hour with 0.545 to model high RB demand scenario (5 gallons per RB per day --> 15 gallons)
        file.write(writeString)

        # [CONDUITS]
        writeString = '\n\n[CONDUITS]'
        writeString += '\nDummy2\tCisterns\tOutfall1\t400\t0.01\t0\t0\t0'
        file.write(writeString)

        # [XSECTIONS]
        writeString = '\n\n[XSECTIONS]'
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
                if line:
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


def create_input_file_no_gi(row, namespace):
    file = './data/input_files/no_green_infrastructure/' + row['GEOID10'] + '_ng.inp'

    if os.path.exists(file):
        print('Skipped ' + row['GEOID10'])
        return

    with open('./data/input_files/no_green_infrastructure/' + row['GEOID10'] + '_ng.inp', 'w') as file:
        print(row['GEOID10'], '- No Green Infrastucture')

        # Write [TITLE] Header
        location = fips_conversion(row['GEOID10'])  # Convert the GeoID10 to State / County / Tract / Block Group

        writeString = '[TITLE]\n'
        writeString += ';; No Green Infrastructure\n'
        writeString += ';; ' + row['GEOID10'] + ' ' + location[0] + ', ' + location[1] + ' County\n;; Tract: ' + location[2] + '\tBlock Group: ' + location[3] + '\n\n'
        file.write(writeString)

        # [OPTIONS]
            # User Input
        start_date = '01/01/1981'  # MM/DD/YYYY Format
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
            writeString += writeVariable(variable[0], variable[1])  # Variable, Value
        file.write(writeString)

        # [EVAPORATION]
        writeString = '[EVAPORATION]\n;;DATA\tSource\tParameters\n;;------------------------\n'  # Write [EVAPORATION] header

        values = namespace.evap.loc[row['GEOID10']].values.T.tolist()

        writeString += 'MONTHLY\t'
        for val in values[1:]:
            writeString += str(val) + '\t'

        writeString += '\nDRY_ONLY\tYES\n\n'
        file.write(writeString)

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

        with open('../data/input_file_data/weather_data/' + row['PRISM_ID'] + '.csv', 'r', newline='') as weather_file:
            reader = csv.reader(weather_file)
            start_date_compare = start_date[-4:] + '-' + start_date[:2] + '-' + start_date[3:5]  # Convert to YYYY-MM-DD (to do <=, >=)
            end_date_compare = end_date[-4:] + '-' + end_date[:2] + '-' + end_date[3:5]  # Convert to YYYY-MM-DD

            for line in reader:
                if line:
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


def create_specific_input_file(row, namespace, type='no_gi'):
    if type is 'rain_barrel':
        create_input_file_rain_barrel(row, namespace)
    elif type is 'rain_garden':
        create_input_file_rain_garden(row, namespace)
    else:
        create_input_file_no_gi(row, namespace)


if __name__ == '__main__':
    characteristics_frame = pd.read_csv('../data/input_file_data/Selected_BG_inputs_20191212.csv', skip_blank_lines=True, low_memory=False, dtype=str)   # Read the green infrastructure data to a pandas dataframe

    # # Change the GeoID column name since it has some weird characters
    # temp_columns = list(characteristics_frame.columns)
    # temp_columns[0] = 'GEOID10'
    # characteristics_frame.columns = temp_columns
    #
    # # Load each row of the CSV into a list of dictionaries
    # characteristics_row_dict = characteristics_frame.T.to_dict().values()


    # Manager shares data between threads
    manager = Manager()
    namespace = manager.Namespace()

    evaporation_dataframe = pd.read_pickle('../data/input_file_data/evaporation_converted.pkl')
    namespace.evap = evaporation_dataframe

    # pool = Pool()
    # pool.map(partial(create_input_file_no_gi, namespace=namespace), characteristics_row_dict)