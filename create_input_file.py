import fips_converter
import csv

with open('./data/input_data/group_characteristics/Selected_BG_inputs_20180208.csv') as characteristics_file:
    reader = csv.reader(characteristics_file)
    next(reader)
    for line in reader:
        # print(line[0])
        print(fips_converter.fips_conversion(line[0]))


