import os
import pandas as pd
import glob
import geopandas as gpd  # For NARR Precipitation Data
import rasterstats as rs  # For NARR Precipitation Data

# No Green Infrastructure: https://docs.google.com/document/d/1_rnpjv8CfboOivYl6W7affA1tcGYJgd-x4SOpYENsFo/edit
# Rain Garden: https://docs.google.com/document/d/1rpHAjt9MIGfQ17Wkbi4D-vHnY5gNW7pggtyGmI2G1RM/edit
# Rain Barrel: https://docs.google.com/document/d/1Ur0nB_N8GKZwqgg1X6mtUibkHuTgYJ7tisg-DyexPRM/edit


# Whether to replace existing input files or not
overwrite = True

# Define the absolute path to the Repository (used for path to precipitation and evaporation files)
_repo_path = '/home/matas/Desktop/CPRHD_WNV_USA_SWMM/'


class InputFile:
    def __init__(self, row, outfile, evap_data, sim_type='ng'):
        self.sim_type = str(sim_type)  # Simulation type (ng = No Green Infrastructure, rb = Rain Barrel, rg = Rain Garden)
        self.data = row  # Row of the block group characteristics spreadsheet
        self.evap = evap_data  # Numpy array containing the GEOID's evaporation data

        # Make sure there is some evaporation data
        assert not self.evap.size == 0, 'No Evaporation Data Found for GEOID ' + self.data['GEOID10']

        # Make sure the file does not already exist
        if os.path.exists(outfile) and not overwrite:
            print('File already exists!', outfile)
            exit(1)

        self.file = open(outfile, 'w')
        self.start = '01/01/1981'
        self.end = '12/31/2014'
        self.precipitation_data_type = 'PRISM'  # other options are narr_daily, narr_hourly
        self.evaporation_type = 'file'  # other option is 'average'

        if self.sim_type == 'rb':
            self.rb_type = 'subcatchment'  # other option is 'lid', using LID Controls instead of subcatchment


    def set_evaporation_type(self, value):
        self.evaporation_type = value


    def set_rainbarrel_type(self, value):
        self.rb_type = value


    def set_precipitation_data_type(self, data_type):
        self.precipitation_data_type = str(data_type)


    def set_start_date(self, date):
        self.start = str(date)


    def set_end_date(self, date):
        self.end = str(date)


    def get_sim_name(self):
        if self.sim_type == 'ng':
            return 'No Green Infrastructure'
        elif self.sim_type == 'rb':
            return 'Rain Barrel'
        elif self.sim_type == 'rg':
            return 'Rain Garden'
        else:
            print('Unknown Simulation Input! (ng = No Green Infrastructure, rb = Rain Barrel, rg = Rain Garden')
            exit(1)


    def title(self):
        self.file.write('[TITLE]\n')
        self.file.write(';; ' + self.get_sim_name() + '\n')
        self.file.write(
            ';; ' + self.data['GEOID10'] + ' ' + self.data['STATE'] + ', ' + self.data['COUNTY'] + ' County\n')
        self.file.write(';; Tract: ' + self.data['TRACT'] + '\tBlock Group: ' + self.data['BG_ID'] + '\n\n')


    def options(self):
        self.file.write('[OPTIONS]\n')

        optionVariables = {#'FLOW_UNITS': 'CFS',  # Default unit
                           'INFILTRATION': 'GREEN_AMPT',
                           #'FLOW_ROUTING': 'KINWAVE',  # Default
                           #'LINK_OFFSETS': 'DEPTH',  # Default
                           #'MIN_SLOPE': '0',  # Default
                           #'ALLOW_PONDING': 'NO',  # Default
                           #'SKIP_STEADY_STATE': 'NO\n',  # Default

                           'START_DATE': self.start,
                           #'START_TIME': '00:00:00',  # Default
                           #'REPORT_START_DATE': self.start,  # Default
                           #'REPORT_START_TIME': '00:00:00',  # Default
                           'END_DATE': self.end,
                           'END_TIME': '24:00:00',
                           'SWEEP_START': self.start[:-5],
                           'SWEEP_END': self.end[:-5] + '\n',

                           #'DRY_DAYS': '0',  # Default
                           'REPORT_STEP': '24:00:00',
                           'WET_STEP': '00:06:00',
                           'DRY_STEP': '00:06:00',
                           'ROUTING_STEP': '00:01:00\n',

                           #'INERTIAL_DAMPING': 'PARTIAL',  # Only used for Dynamic Wave Flow_Routing
                           #'NORMAL_FLOW_LIMITED': 'BOTH',  # Default
                           #'FORCE_MAIN_EQUATION': 'H-W',  # Default
                           #'VARIABLE_STEP': '0.75',  # Only used for Dynamic Wave Flow_Routing
                           #'LENGTHENING_STEP': '0',  # Default
                           #'MIN_SURFAREA': '12.557',  # Only used for Dynamic Wave Flow_Routing
                           #'MAX_TRIALS': '8',  # Default
                           #'HEAD_TOLERANCE': '0.005',  # Default
                           #'SYS_FLOW_TOL': '5',  # Default
                           #'LAT_FLOW_TOL': '5',  # Default
                           #'MINIMUM_STEP': '0.5',  # DEfault
                           #'THREADS': '1',  # Default
                           'IGNORE_ROUTING': 'YES'  # Ignore's routing information and just gets runoff data
                           }

        for key, value in optionVariables.items():
            if len(key) > 15:
                tabs = 1
            elif len(key) > 7:
                tabs = 2
            else:
                tabs = 3

            self.file.write(key + tabs * '\t' + value + '\n')

        self.file.write('\n')


    def evaporation(self):
        self.file.write('[EVAPORATION]\n')

        if self.evaporation_type == 'file':  # Monthly Evaporation in an External Timeseries File
            assert os.path.exists(_repo_path + 'data/input_file_data/evaporation_data_timeseries/' + self.data['GEOID10'] + '_EVAP.txt'), 'Failed to find external evaporation file'
            self.file.write('TIMESERIES ' + self.data['GEOID10'] + '_EVAP\n')

        elif self.evaporation_type == 'average':  # Code for Average Monthly Evaporation
            self.file.write('MONTHLY\t')
            for value in self.evap.values:
                self.file.write(str(value) + ' ')
            self.file.write('\n')
        else:
            raise Exception('Failed to parse evaporation type!')
        self.file.write('DRY_ONLY\tYES\n')


    def raingages(self):
        self.file.write('[RAINGAGES]\n')
        self.file.write(';;Name\tFormat\tInterval\tSCF\tSource\n')

        raingage_parameters_file =       {'Name': 'RainGage2',  # name of raingage variable
                                          'Form': 'VOLUME',  # form of recorded rainfall
                                          'Interval': '24:00:00',  # time interval between gage readings
                                          'SCF': '1.0',  # snow catch deficiency correction factor (use 1.0 for no adjustment)
                                          'FILE': 'FILE ' + _repo_path + 'data/input_file_data/weather_data_swmm_format/' + self.data['PRISM_ID'] + '.txt',
                                          'Sta': self.data['PRISM_ID'],
                                          'Units': 'IN'
                                          }

        raingage_parameters_timeseries = {'Name': 'RainGage2',  # name of raingage variable
                                          'Form': 'VOLUME',  # form of recorded rainfall
                                          'Interval': '24:00:00',  # time interval between gage readings
                                          'SCF': '1.0',  # snow catch deficiency correction factor (use 1.0 for no adjustment)
                                          'Tseries': 'TIMESERIES ' + self.precipitation_data_type.upper()
                                          }
        if self.precipitation_data_type == 'narr_hourly':
            raingage_parameters_timeseries['Interval'] = '03:00:00'

        if self.precipitation_data_type == 'PRISM': # Use External File for Data Input
            # Check that the precipitation file exists
            assert os.path.exists(_repo_path + 'data/input_file_data/weather_data_swmm_format/' + self.data['PRISM_ID'] + '.txt'), 'Failed to find external weather file'

            for key in raingage_parameters_file:
                self.file.write(raingage_parameters_file[key] + '\t')
            self.file.write('\n\n')

        else:  # Data will be written in [TIMESERIES] Section
            for key in raingage_parameters_timeseries:
                self.file.write(raingage_parameters_timeseries[key] + '\t')
            self.file.write('\n\n')


    def subcatchments(self):
        self.file.write('[SUBCATCHMENTS]\n')
        self.file.write(';;Name\tRain_Gage\tOutlet\tArea\t%Imperv\tWidth\t%Slope\tCurbLen\tSnowPack\n')

        slope_pct = self.data['pctslope_avg_30m']
        subcatchment_area = self.data['Area_acre_30m']
        subcatchment_imperv = self.data['PCT_I_adj_30m']
        subcatchment_width = self.data['WIDTH_30m']

        if self.sim_type == 'rb' and self.rb_type == 'subcatchment':
            # Subcatchment 1
            subcatchment_area = self.data['RB_SC1_ACRE_30m']
            subcatchment_imperv = self.data['RB_SC1_PCT_I_30m']
            subcatchment_width = self.data['RB_SC1_WIDTH_30m']
            # Subcatchment 4
            rainbarrel_area = self.data['SCA_ROOF_ACRE']
            rainbarrel_width = self.data['SCA_ROOF_WIDTH']


        elif self.sim_type == 'rg':
            subcatchment_imperv = self.data['RG1_PCT_I_adj_30m']

        self.file.write(
            'Subcatch1\tRainGage2\tOutfall1\t' + subcatchment_area + '\t' + subcatchment_imperv + '\t' + subcatchment_width + '\t' + slope_pct + '\t0\n')

        if self.sim_type == 'rb' and self.rb_type == 'subcatchment':
            self.file.write(
                'Subcatch4\tRainGage2\tBarrel\t' + rainbarrel_area + '\t100\t' + rainbarrel_width + '\t' + slope_pct + '\t0\n')
        self.file.write('\n')


    def subareas(self):
        self.file.write('[SUBAREAS]\n')
        self.file.write(';;Subcatch\tN-Imperv\tN-Perv\tS-Imperv\tS-Perv\tPctZero\tRouteTo\tPctRouted\n')

        n_perv = self.data['ROUGH_NI_30m']
        s_perv = self.data['DEPRESS_NI_30m']

        self.file.write('Subcatch1\t0.01\t' + n_perv + '\t0.05\t' + s_perv + '\t0\tOUTLET\n')

        if self.sim_type == 'rb' and self.rb_type == 'subcatchment':
            self.file.write('Subcatch4\t0.01\t' + n_perv + '\t0.05\t' + s_perv + '\t0\tOUTLET\n')
        self.file.write('\n')


    def infiltration(self):
        g_ampt_params = {
            'Suction': self.data['GMSH_adj_BG_30m'],
            'Ksat': self.data['Keff_adj_BG_30m'],
            'IMD': self.data['AMEP_adj_BG_30m']
        }

        self.file.write('[INFILTRATION]\n')
        self.file.write(';;Subcatchment\tSuction\tKsat\tIMD\n')

        self.file.write('Subcatch1\t' + g_ampt_params['Suction'] + '\t' + g_ampt_params['Ksat'] + '\t' + g_ampt_params['IMD'] + '\n')
        if self.sim_type == 'rb' and self.rb_type == 'subcatchment':
            self.file.write('Subcatch4\t' + g_ampt_params['Suction'] + '\t' + g_ampt_params['Ksat'] + '\t' + g_ampt_params['IMD'] + '\n')

        self.file.write('\n')


    def lid_controls(self):
        # Define the LID parameters for Rain Garden, Rain Barrel
        self.file.write('[LID_CONTROLS]\n')
        self.file.write(';;Name\tType\tParameters\n')

        if self.sim_type == 'rg':  # LID Control for Rain Garden
            self.file.write('RainGarden\tBC\n')

            # SURFACE
            surface_params = {'StorHt': '6',  # maximum depth of ponded water before overflow (inches)
                              'VegFrac': '0',  # fraction of storage volume filled with vegetation
                              'Rough': '0',  # Manning's n (EPA Manual recommends 0)
                              'Slope': '0',  # Slope of the surface (EPA Manual recommends 0)
                              'Xslope': '0'}  # Slope of side walls of vegetative swale (EPA Manual recommends 0)
            self.file.write(
                'RainGarden\tSURFACE\t' + surface_params['StorHt'] + '\t' + surface_params['VegFrac'] + '\t' +
                surface_params['Rough'] + '\t' + surface_params['Slope'] + '\t' + surface_params['Xslope'] + '\n')

            # SOIL
            soil_params = {'Thick': '12',  # thickness of soil layer (inches)
                           'Por': self.data['RG1_POROSITY'],  # soil porosity
                           'FC': self.data['RG1_FIELDCAP'],  # soil field capacity
                           'WP': self.data['RG1_WILTPT'],  # soil wilting point
                           'Ksat': self.data['RG1_Ks'],  # soil's saturated hydraulic conductivity (inches / hr)
                           'Kcoeff': self.data['RG1_Ks_SLOPE'], # slope of the curve of log(conductivity) vs. soil moisture content
                           'Suct': self.data['RG1_SH']  # soil capillary suction (inches)
                           }
            self.file.write(
                'RainGarden\tSOIL\t' + soil_params['Thick'] + '\t' + soil_params['Por'] + '\t' + soil_params[
                    'FC'] + '\t' + soil_params['WP'] + '\t' + soil_params['Ksat'] + '\t' + soil_params[
                    'Kcoeff'] + '\t' + soil_params['Suct'] + '\n')

            # STORAGE
            storage_params = {'Height': '0',  # height of the rain garden (inches)
                              'Vratio': '0',  # void ratio
                              'Seepage': self.data['RG1_SEEPAGE'],
                              # rate at which water seeps from the layer into the underlying layer
                              'Vclog': '0'}  # number of void volumes of runoff it takes to clog (use 0 to ignore clogging)
            self.file.write(
                'RainGarden\tSTORAGE\t' + storage_params['Height'] + '\t' + storage_params['Vratio'] + '\t' +
                storage_params['Seepage'] + '\t' + storage_params['Vclog'] + '\n')

        elif self.sim_type == 'rb' and self.rb_type == 'lid':  # LID Control for Rain Barrel
            self.file.write('RainBarrel\tRB\n')

            # STORAGE
            storage_params = {
                                'Height': '48',  # height of the rain barrel storage (inches)
                                # "values for Vratio, Seepage, and Vclog are ignored for Rain Barrels"
                                'Vratio': '0.75',  # void ratio
                                'Seepage': '10',  # rate at which water seeps from the layer into the underlying layer (inches / hour)
                                'Vclog': '0'  # number of void volumes of runoff it takes to clog (use 0 to ignore clogging)
                             }

            self.file.write('RainBarrel\tSTORAGE\t')
            for key in storage_params:
                self.file.write(storage_params[key] + '\t')
            self.file.write('\n')

            # DRAIN
            drain_params = {'Coeff': '0',  # rate of flow through drain as a function of height of water to drain bottom
                            'Expon': '0.5',  # rate of flow through the drain as a function of height of water to drain outlet
                            'Offset': '0',  # height of the drain line above the bottom of the rain barrel
                            'Delay': '0',  # number of dry weather hours that elapse before drain line is opened
                            # 'Unknown_Var': '0',
                            # 'Unknown_Var2': '0'
                            }

            self.file.write('RainBarrel\tDRAIN\t')
            for key in drain_params:
                self.file.write(drain_params[key] + '\t')
            self.file.write('\n')
        self.file.write('\n')


    def lid_usage(self):
        # Apply the LID parameters to a subcatchment

        self.file.write('[LID_USAGE]\n')
        self.file.write(
            ';;Subcatchment\tLID_Process\tNumber\tArea\tWidth\tInitSat\tFromImp\tToPerv\tRptFile\tDrainTo\n')
        if self.sim_type == 'rg':
            usage_parameters = {'Name': 'Subcatch1',  # Name of Subcatchment
                                'LID': 'RainGarden',  # Name of LID Control (defined above)
                                'Number': '1',  # Number of units
                                'Area': self.data['RG1_AREA_SQRFT'],  # Area of each replicate unit
                                'Width': '0',  # Recommended 0 for Bio-retention cells, Rain Gardens, Rain Barrels
                                'InitSat': '0',  # Initial saturation of soil
                                'FromImp': self.data['RG1_PCT_I_TREAT_30m'],  # Percentage of impervious runoff diverted to this LID (recommended 0 for direct rainfall only)
                                'ToPerv': '0',  # 1 is recommended for rain barrel, possibly green roof
                                'RptFile': '',  # Specify if you want an individual report file for this LID
                                'DrainTo': '',  # Name of subcatchment that receives flow from this unit's drain line, if different than the outlet of the Subcatchment it is placed in
                                }

            for key in usage_parameters:
                self.file.write(usage_parameters[key] + '\t')
            self.file.write('\n')

        elif self.sim_type == 'rb' and self.rb_type == 'lid':
            usage_parameters = {'Name': 'Subcatch1',  # Name of Subcatchment
                                'LID': 'RainBarrel',  # Name of LID Control (defined above)
                                # 'Number': '1',
                                'Number': self.data['NUM_RB_INTEGER'],  # Number of units
                                # 'Area': self.data['RB_STORE_SQRFT'],  # Area of each replicate unit
                                'Area': '500',
                                'Width': '0',  # Recommended 0 for Bio-retention cells, Rain Gardens, Rain Barrels
                                'InitSat': '0',  # Initial saturation of soil
                                # 'FromImp': str(float(self.data['SCA_ROOF_ACRE']) / float(self.data['Area_acre_30m']) * 100),  # Percentage of impervious runoff diverted to this LID (recommended 0 for direct rainfall only)
                                'FromImp': self.data['PCT_ISA_treated_RB_30'],
                                'ToPerv': '1',  # 1 is recommended for rain barrel, possibly green roof
                                'RptFile': '',  # Specify if you want an individual report file for this LID
                                'DrainTo': '',  # Name of subcatchment that receives flow from this unit's drain line, if different than the outlet of the Subcatchment
                                }
            for key in usage_parameters:
                self.file.write(usage_parameters[key] + '\t')
            self.file.write('\n')
        self.file.write('\n')


    def junctions(self):
        # This is not used from what I can tell
        return

        # if self.sim_type == 'rb':
        #     return

        self.file.write('[JUNCTIONS]\n')
        self.file.write(';;Name\tElevation\tMaxDepth\tInitDepth\tSurDepth\tAponded\n')

        junction_params = {'NAME': 'Barrel',
                           'Elev': '0',  # Elevation of junction invert
                           'Ymax': '0',  # depth from ground to invert elevation
                           'Y0': '0',  # water depth at start of simulation
                           'Ysur': '0',  # maximum additional head above ground elevation that junction can sustain
                           'Apond': '0'  # area subjected to surface ponding once water exceeds Ymax
                          }
        # if self.sim_type != 'rb':
        for key in junction_params:
            self.file.write(junction_params[key] + '\t')
        self.file.write('\n\n')


    def outfalls(self):
        self.file.write('[OUTFALLS]\n')
        self.file.write(';;Name\tElevation\tType\tGated\tRoute_To\n')

        outfalls_parameters = {'Name': 'Outfall1',  # Name of outfall
                               'Elevation': '0',  # Invert elevation of outfall
                               'Type': 'FREE',
                               'Gated': 'NO',  # If a flap gate is present to prevent reverse flow
                               'Route_To': ''  # Which subcatchment to route the outfall's discharge to
                               }

        for key in outfalls_parameters:
            self.file.write(outfalls_parameters[key] + '\t')
        self.file.write('\n\n')


    def storage(self):
        # This is only called for the Rain Barrel Scenario
        if self.sim_type != 'rb' or self.rb_type == 'lid':
            return

        self.file.write('[STORAGE]\n')
        self.file.write(';;Name\tElevation\tMaxDepth\tAcurve\tA1\tA2\tA0\tApond\tFevap\tPsi\tKsat\tIMD\n')

        storage_params = {'Name': 'Barrel',
                          'Elev': '0',  # Rain barrel invert elevation
                          'Ymax': '4',  # Rain barrel height, feet (maximum depth possible)
                          'Y0': '0',  # Initial water depth

                          'Acurve': 'FUNCTIONAL',  # Area = A0 + A1 * Depth^(A2)
                          'A1': '0',
                          'A2': '0',
                          'A0': self.data['RB_STORE_SQRFT'],  # Area of rain barrel, square feet

                          'Apond': '0',  # This variable has been deprecated, use 0
                          'Fevap': '0',  # Fraction of potential evaporation from surface realized (default 0)
                          'Psi': '2.4',  # Suction head of seepage loss of barrel (fixed at 2.4 inches)
                          'Ksat': '0.182',  # Seepage rate (0.182 for 5 gal / day, 0.545 for 15 gal / day)
                          'IMD': '0'  # Initial soil moisture deficit (fixed at 0)
                          }

        for val in storage_params:
            self.file.write(storage_params[val] + '\t')
        self.file.write('\n\n')


    def conduits(self):
        # This is only called for the Rain Barrel scenario
        if self.sim_type != 'rb' or self.rb_type == 'lid':
            return

        self.file.write('[CONDUITS]\n')
        self.file.write(';;Name\tNode1\t\tNode2\tConduit_Length\tN\tZ1\tZ2\tQ0\n')
        conduit_params = {'Name': 'Dummy2',
                          'Node1': 'Barrel',  # name of upstream node
                          'Node2': 'Outfall1',  # name of downstream node
                          'Conduit Length': '400',  # Conduit length (fixed at 400)
                          'N': '0.01',  # Manning Roughness coefficient for conduit (fixed at 0.01)

                          # See EPA SWMM 5.1 Manual, Page 306 for figure describing Z1 and Z2 variables
                          'Z1': '0',
                          # Offset of downstream end of conduit invert above invert elevation of it's downstream node
                          'Z2': '0',
                          # Offset of downstream end of conduit invert above the invert elevation of its downstream node

                          'Q0': '0',  # Flow in conduit at start of simulation
                          'Qmax': '',  # Maximum flow allowed in the conduit (default is no limit)
                          }

        for val in conduit_params:
            self.file.write(conduit_params[val] + '\t')
        self.file.write('\n\n')


    def xsections(self):
        # Provides cross-section geometric data for [CONDUITS]
        # This is only called for the Rain Barrel scenario
        if self.sim_type != 'rb' or self.rb_type == 'lid':
            return

        self.file.write('[XSECTIONS]\n')
        self.file.write(';;Name\tShape\tGeom1\tGeom2\tGeom3\tGeom4\tBarrels\n')

        xsections_params = {'Name': 'Dummy2',  # Name of conduit defining the cross-section of
                            'Shape': 'DUMMY',  # Cross section shape
                            'Geom1': '0',  # Full height of cross-section
                            'Geom2': '0',  # Auxiliary parameter
                            'Geom3': '0',  # Auxiliary parameter
                            'Geom4': '0',  # Auxiliary parameter
                            'Barrels': '1'  # Number of barrels in the conduit
                           }

        for key in xsections_params:
            self.file.write(xsections_params[key] + '\t')
        self.file.write('\n\n')


    def timeseries(self):
        self.file.write('[TIMESERIES]\n')
        self.file.write(';;Name\t\tDate\t\tTime\t\tValue\n')

        # File Evaporation Data
        if self.evaporation_type == 'file':
            self.file.write(self.data['GEOID10'] + '_EVAP ' + 'FILE ' + _repo_path + 'data/input_file_data/evaporation_data_timeseries/' + self.data['GEOID10'] + '_EVAP.txt\n')

        # NARR Precipitation Data
        if self.precipitation_data_type[:5] == 'narr':
            if self.precipitation_data_type == 'narr_hourly':
                masked_geotiffs = glob.glob('../data/input_file_data/narr_masked_geotiffs/hourly/*.geotiff')
            if self.precipitation_data_type == 'narr_daily':
                masked_geotiffs = glob.glob('../data/input_file_data/narr_masked_geotiffs/daily/*.geotiff')
            shape_file = '../data/input_file_data/SelectBG_all_land_BGID_final.gpkg'
            # data = self.get_narr_precipitation_data(shape_file, masked_geotiffs)  # Uncomment to calculate the data on the fly

            # The NARR data has been pre-calculated for the 7 block groups we have been considering
            data = pd.read_pickle('/home/matas/Desktop/CPRHD_WNV_USA_SWMM/jupyter_notebooks/SWMM_Precipitation/' + self.precipitation_data_type[5:] + '/timeseries/' + self.data['STATE'].lower() + '.pkl')
            data.to_csv(self.file, sep='\t', index=False, header=None)
            self.file.write('\n')
        self.file.write('\n')


    def report(self):
        self.file.write('[REPORT]\n')
        self.file.write(';;Reporting Options\n')

        report_params = {'INPUT': 'YES',
                         'CONTROLS': 'NO',
                         'SUBCATCHMENTS': 'ALL',
                         'NODES': 'NONE',
                         'LINKS': 'NONE'
                        }

        if self.sim_type == 'rb' and self.rb_type == 'subcatchment':
            report_params['NODES'] = 'Barrel'

        for key, val in report_params.items():
            self.file.write(key + '\t' + val + '\n')
        self.file.write('\n\n')


    def write(self):
        self.title()
        self.options()
        self.evaporation()
        self.raingages()
        self.subcatchments()
        self.subareas()
        self.infiltration()
        self.lid_controls()
        self.lid_usage()
        self.junctions()
        self.outfalls()
        self.storage()
        self.conduits()
        self.xsections()
        self.timeseries()
        self.report()
        self.file.close()


    def get_narr_precipitation_data(self, shape_file, masked_geotiffs):
        assert self.start == '01/01/2014' and self.end =='12/31/2014'  # We only have NARR data for 2014

        shape = gpd.read_file(shape_file)

        shape = shape[shape['GEOID10'] == self.data['GEOID10']].reset_index()
        output_stats = 'mean'

        # initialize the frame with the first GeoTIFF file
        name = masked_geotiffs[0][masked_geotiffs[0].rfind('/') + 1:masked_geotiffs[0].rfind('.')]
        stats = rs.zonal_stats(shape, masked_geotiffs[0], stats=output_stats, all_touched=True)
        frame = pd.DataFrame.from_dict(stats)
        frame = frame.join(shape['GEOID10'])
        frame = frame.rename(columns={'mean': name})
        frame = frame[['GEOID10', name]]

        # loop through all the GeoTIFFs and join onto the original frame
        for file in masked_geotiffs[1:]:
            name = file[file.rfind('/') + 1:file.rfind('.')]
            stats = rs.zonal_stats(shape, file, stats=output_stats, all_touched=True)
            sub_frame = pd.DataFrame.from_dict(stats)
            sub_frame = sub_frame.rename(columns={'mean': name})
            frame = frame.join(sub_frame)

        # Convert to inches
        data = frame.iloc[0, 1:]
        data = data.apply(lambda x: x / 25.40)

        # Sort smallest to largest (1, 2, 3, ..., 365)
        data.index = data.index.astype(int)
        data = data.sort_index().to_frame('VALUE')

        if self.precipitation_data_type == 'narr_hourly':
            date_range = pd.date_range(start=self.start, end=pd.to_datetime(self.end) + pd.Timedelta('1 days'), freq='3H')[:-1]
        else:
            date_range = pd.date_range(start=self.start, end=pd.to_datetime(self.end) + pd.Timedelta('1 days'), freq='D')[:-1]

        time = date_range.strftime('%H:%M:%S')

        date_range = date_range.strftime('%m/%d/%Y')

        data = data.set_index(date_range, drop=True)
        data = data.reset_index()
        data = data.rename(columns={'index': 'DATE'})
        data['TIME'] = time
        data['NAME'] = 'NARR_HOURLY'

        data = data[['NAME', 'DATE', 'TIME', 'VALUE']]
        return data
