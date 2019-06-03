import fips_converter
import csv

with open('./data/input_file_data/group_characteristics/Selected_BG_inputs_20180208.csv') as characteristics_file:
    reader = csv.reader(characteristics_file)
    next(reader)  # Skip the first line of the .csv since it contains headers
    for line in reader:
        print(fips_converter.fips_conversion(line[0]))  # line[0] represents the first column, the GEOID


