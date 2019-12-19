# West Nile Virus - USA - Storm Water Management Model 

This repository contains code related to the [Computational Program for Racial Health Disparities'](https://wiki.ncsa.illinois.edu/display/CPRHD) 
West Nile Virus USA project at the [National Center for Supercomputing Applications](http://www.ncsa.illinois.edu/). We create input files for the model using green infrastructure data, evaporation data, and precipitation data for ~150,000 census block groups across the United States.

We then run these input files using a Python port of SWMM, [pyswmm](https://github.com/OpenWaterAnalytics/pyswmm), and extract the timeseries data using [swmmtoolbox](https://pypi.org/project/swmmtoolbox/).
 
## Getting Started

1) Clone the Repository
2) [Download Requisite Files](https://uofi.app.box.com/folder/97076496992)
    1) Selected_BG_inputs_20191212.csv - Contains block group characteristics
    2) weather_data_swmm_format - Contains precipitation data, linked to the block groups by their PRISM ID
    3) evaporation_converted.pkl - Pickled pandas array containing evaporation data for each GEOID10
3) Place the files in /CPRHD_WNV_USA_SWMM/data/input_file_data/
4) Run [create_input_files.py](https://github.com/ncsa/CPRHD_WNV_USA_SWMM/blob/master/python/create_input_files.py), specifying which LID type you want to create the files for (ng = No Green Infrastructure, rb = Rain Barrel, rg = Rain Garden)

    
### Prerequisites
1) [PySWMM](https://github.com/OpenWaterAnalytics/pyswmm) - Running the Simulations
2) [SWMMToolbox](https://pypi.org/project/swmmtoolbox/) - Extracting Timeseries Data
3) [Pandarallel](https://github.com/nalepae/pandarallel) - Multiprocessing with pandas dataframes
```
pip install pyswmm
pip install swmmtoolbox
pip install pandarallel
```

## Documentation
### [create_input_file_class.py](https://github.com/ncsa/CPRHD_WNV_USA_SWMM/blob/master/python/create_input_file_class.py)
#### Constructor

    file = InputFile(row_of_characteristics_data, path_to_outfile, evaporation_data, sim_type)
    
Options for sim_type are 'ng', 'rb', or 'rg'.

#### set_start_date
Set the simulation start date (default 01/01/1981)
    
    file.set_start_date('01/01/2014')
   
#### set_end_date
Set the simulation end date (maximum/default is 12/31/2014)

    file.set_end_date('01/31/2014')

#### set_precipitation_data_type
Set the precipitation data type (default is PRISM), choices are PRISM, narr_hourly, narr_daily.

    file.set_precipitation_data_type('narr_hourly')
    
#### get_sim_name
Returns the LID Simulation Type

    file = InputFile(row, outfile, evap, 'rg')
    print(file.get_sim_name())
    >> Rain Garden

#### write
This function writes every section of the input file used in our analysis

    file.write()
    >> (Input file has been created)

### [netcdf.py](https://github.com/ncsa/CPRHD_WNV_USA_SWMM/blob/master/python/netcdf.py)
This module is used to manipulate the NetCDF file provided by [NARR](https://www.esrl.noaa.gov/psd/data/gridded/data.narr.html) for obtaining evaporation rate data.
#### netcdf_to_geotiff(netcdf_file, overwrite=False)
This function accepts a directory to a NetCDF file, warps it to the North American Lambert Conformal Conic projection, and then extracts each band into an individual image. If overwrite is true (default false), it will overwrite existing extracted data.

    from netcdf import netcdf_to_geotiff
    netcdf_to_geotiff('./path/to/file', overwrite=True)
    * GeoTIFF files have been created * 
    
#### create_evaporation_plot(geotiff_file, type='image')
This function accepts a .geotiff file and creates either an image or a histogram (default is image).
    
    from netcdf import create_evaporation_plot
    create_evaporation_plot('./path/to/geotiff/file', type='histogram')
    * A histogram has been created * 

#### extract_evaporation_data(geotiff_files)
This function accepts a list of .geotiff files (obtained with glob), and iterates through each, adding its data to a dataframe. The dataframe is then pickled and stored in a file for later access.
    
    from netcdf import extract_evaporation_data
    geotiff_files = glob.glob('./path/to/files/*.geotiff')
    extract_evaporation_data(geotiff_files)
    * A pickle file has been created *
  
#### get_average_evaporation(dataframe)
This function accepts a dataframe, and prints the average evaporation level across all years.
    
    from netcdf import get_average_evaporation
    import pandas as pd
    dataframe = pd.read_pickle('./path/to/pickle/file')
    get_average_evaporation(dataframe)

## Authors

* Matas Lauzadis - [GitHub](https://github.com/mataslauzadis)

## Acknowledgments

* [Aiman Soliman](https://aimansoliman.com/) - Mentor
* [Liudmila Mainzer](https://ccbgm.illinois.edu/people/liudmila-sergeevna-mainzer/) - CPRHD Lead
