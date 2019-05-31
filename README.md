# SWMM
### [swmm.py](https://github.com/mataslauzadis/SWMM/blob/master/swmm.py)
Using [pyswmm](https://github.com/OpenWaterAnalytics/pyswmm), this module converts .inp files to .out and .rpt files, then, using [swmmtoolbox](https://github.com/timcera/swmmtoolbox), extracts the data from the binary .out file and stores it in a .csv file.
Make sure your file path is set up such that the .inp files are in ./data. There should also be a directory inside ./data with the path ./data/binary_csv.

    Sample output: 
    
    Processing .\data\Chicago_U_RG3A.inp 
    ... SWMM Version 5.2.0.dev1
    ... Run Complete
    Deleted .\data\Chicago_U_RG3A.out 
 
### [move_report_files.py](https://github.com/mataslauzadis/SWMM/blob/master/move_report_files.py)
This module moves all .rpt files from ./data to ./data/report_files. Make sure the path exists before trying to run this.

### fips_converter.py
This module converts 12-digit GEOID codes to State and County names. It also provides a dictionary containing each state / county code pair.
    
    Sample output:
    ['Illinois', 'Du Page', '8466', '033']


