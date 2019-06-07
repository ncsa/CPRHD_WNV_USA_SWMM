# SWMM
## Directory Setup
```
Project_base
|   README.md
|   swmm.py
|   create_input_file.py
|   extract_data.py
|   move_report_files.py
|   US_FIPS_Codes.csv
└── data
     └─── binary_csv
          | .csv files
     └─── input_file_data
          | PRISM_selectBG_dailyrain_raw_in_20170917.csv (Weather data)
          | Selected_BG_inputs_20180208.csv (Group characteristics)
     └─── input_files
          | .inp files created by create_input_file.py
     └─── report_files
          | .rpt files
```
## Main Modules
### [swmm.py](https://github.com/mataslauzadis/SWMM/blob/master/swmm.py)
Using [pyswmm](https://github.com/OpenWaterAnalytics/pyswmm), this module converts .inp files to .out and .rpt files, then, using [swmmtoolbox](https://github.com/timcera/swmmtoolbox), extracts the data from the binary .out file and stores it in a .csv file.
Make sure your file path is set up such that the .inp files are in ./data. There should also be a directory inside ./data with the path ./data/binary_csv.

    
### [create_input_file.py](https://github.com/mataslauzadis/SWMM/blob/master/create_input_file.py)
This module creates an input file for the SWMM Model.

## Supporting Modules


### [extract_data.py](https://github.com/mataslauzadis/SWMM/blob/master/extract_data.py)

#### process_output(output_file)
This function extracts the data from the binary SWMM file and writes it to a [.csv file]((https://github.com/mataslauzadis/SWMM/blob/master/data/binary_csv/Chicago_U_NoGI.csv)).
    
    from extract_data import process_output
    process_output('./data/input_files/Chicago_U_NoGI.inp') 
    * Chicago_U_NoGI.csv has been created *
    
### [fips_converter.py](https://github.com/mataslauzadis/SWMM/blob/master/fips_converter.py)
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
    


    
### [move_report_files.py](https://github.com/mataslauzadis/SWMM/blob/master/move_report_files.py)
This module moves all .rpt files from ./data to ./data/report_files.


