from pyswmm import Simulation  # Used to convert .inp files to .out and .rpt files using SWMM
from swmmtoolbox import swmmtoolbox  # Used to obtain variables from the binary .out file
import csv  # Used to write .csv file
import glob  # Used to find .inp and .out file(s)
import os  # Used to delete the .out file after it has been read into a .csv (save disk space)
from extract_data import process_output


def process_input(file):
    #  Preconditions: 'file' has been passed, containing the directory path for a .inp file
    #  Postconditions: The SWMM model has created a .out and .rpt file in the base_directory\data folder based on the parameters given in the .inp file.
    with Simulation(file) as sim:
        sim.execute()
        sim.close()
    print()


input_files = glob.glob('.\data\*.inp')
for file in input_files:  # Loop through all input files

    #  Create .out and .rpt files from .inp file
    print('Processing', file, end='')
    process_input(file)

    #  Extract data to .csv
    output_file = glob.glob('.\data\*.out')[0]  # Since glob returns a list of files, we get the first (and only) file with [0].
    process_output(output_file)
    print('\nWriting data from', output_file, 'to .\\data\\binary_csv' + file[6:-4] + '.csv')

    #  Remove .out file
    os.remove(output_file)
    print('Deleted', output_file, '\n')