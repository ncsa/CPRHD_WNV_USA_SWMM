# Computational Program for Racial Health Disparities - West Nile Virus - USA - Storm Water Management Model Tools
# Setup
## Directory Setup
```
Project_base
|   README.md
|   swmm.py
|   create_input_file.py
|   extract_data.py
|   US_FIPS_Codes.csv
|   move_report_files.py
└── data
     └─── binary_csv
          | .csv files
     └─── input_file_data
          | Selected_BG_inputs_20180208.csv (Group characteristics data)
          └─── weather_data
              | individual weather .csv files
     └─── input_files
          | .inp files
     └─── report_files
          | .rpt files
```

#### Legend: 
   File: | 
   
   Folder: └───
  
# Documentation 
## Main Modules
### [swmm.py](https://github.com/ncsa/CPRHD_WNV_USA_SWMM/blob/master/swmm.py)
Using [pyswmm](https://github.com/OpenWaterAnalytics/pyswmm), this module converts .inp files to .out and .rpt files, then, using [swmmtoolbox](https://github.com/timcera/swmmtoolbox), extracts the data from the binary .out file and stores it in a .csv file.
Make sure your file path is set up such that the .inp files are in ./data. There should also be a directory inside ./data with the path ./data/binary_csv.

    
### [create_input_file.py](https://github.com/ncsa/CPRHD_WNV_USA_SWMM/blob/master/create_input_file.py)
This module creates an input file for the SWMM Model.

## Supporting Modules


### [extract_data.py](https://github.com/ncsa/CPRHD_WNV_USA_SWMM/blob/master/extract_data.py)

#### process_output(output_file)
This function extracts the data from the binary SWMM file and writes it to a [.csv file]((https://github.com/mataslauzadis/SWMM/blob/master/data/binary_csv/Chicago_U_NoGI.csv)).
    
    from extract_data import process_output
    process_output('./data/input_files/Chicago_U_NoGI.inp') 
    * Chicago_U_NoGI.csv has been created *
    
### [fips_converter.py](https://github.com/ncsa/CPRHD_WNV_USA_SWMM/blob/master/fips_converter.py)
#### fips_to_dict()
Using US_FIPS_Codes.csv, this function creates a dictionary with keys of state code and county code.

Example: dictionary[state_code][county_code] will return a tuple containing the state name and county name.
    
    from fips_converter import fips_to_dict
    dictionary = fips_to_dict()
    dictionary[17][43] --> ['Illinois','Du Page']
    
#### fips_conversion(fips_code)
This function accepts 12-digit GEOIDs and returns a list with the state name, county name, census tract ID, and census block group ID.

    from fips_converter import fips_conversion 
    fips_conversion(170438466033) --> ['Illinois', 'Du Page', '8466', '033']
    


    
### [move_report_files.py](https://github.com/ncsa/CPRHD_WNV_USA_SWMM/blob/master/move_report_files.py)
This module moves all .rpt files from ./data to ./data/report_files.

### [netcdf.py](https://github.com/ncsa/CPRHD_WNV_USA_SWMM/blob/master/netcdf.py)
This module is used to manipulate the NetCDF file provided by [NARR](https://www.esrl.noaa.gov/psd/data/gridded/data.narr.html) for obtaining evaporation rate data.
#### netcdf_to_geotiff(netcdf_file, overwrite=False)
This function accepts a directory to a NetCDF file, warps it to the North American Lambert Conformal Conic projection, and then extracts each band into an individual image. If overwrite is true (default false), it will overwrite existing extracted data.

    from netcdf import netcdf_to_geotiff
    netcdf_to_geotiff('./path/to/file', overwrite=True)
    * GeoTIFF files have been created * 
#### create_evaporation_plot(geotiff_file, type='image')
This function accepts a .geotiff file and creates either an image or a histogram (default is image).

[Histogram](https://raw.githubusercontent.com/ncsa/CPRHD_WNV_USA_SWMM/master/docs/1999_03_histogram.png)

[Image](https://raw.githubusercontent.com/ncsa/CPRHD_WNV_USA_SWMM/master/docs/1993_03_image.png)
    
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

# About / Contact
#### Worked on by [Matas Lauzadis](https://github.com/mataslauzadis) during Summer 2019's REU-INCLUSION for NCSA's [Computational Program for Racial Health Disparities](https://wiki.ncsa.illinois.edu/display/CPRHD).  

