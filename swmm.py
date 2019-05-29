from pyswmm import Simulation  # Used to convert .inp files to .out and .rpt files using SWMM
from swmmtoolbox import swmmtoolbox  # Used to obtain variables from the binary .out file
import csv  # Used to write .csv file
import glob  # Used to find .inp and .out file(s)
import os  # Used to delete the .out file after it has been read into a .csv (save disk space)


def process_input(file):
    #  Preconditions: 'file' has been passed, containing the directory path for a .inp file
    #  Postconditions: The SWMM model has created a .out and .rpt file in the base_directory\data folder based on the parameters given in the .inp file.
    with Simulation(file) as sim:
        sim.execute()
        sim.close()


def process_output(file):
    #  Preconditions: 'file' has been passed, containing the directory path for a .out file
    #  Postconditions: TODO
    data = swmmtoolbox.listvariables(file)
    # TODO Find out what data is needed from .out and how to get it
    # csv_file = open('.\\data\\binary_csv' + file[6:-4] + '.csv', 'w')
    # csv_writer = csv.writer(csv_file)
    # csv_writer.writerow(['TYPE', 'DESCRIPTION', 'VARINDEX'])
    # csv_writer.writerows(data)
    # csv_file.close()


input_files = glob.glob('.\data\*.inp')

for file in input_files:

    #  Create .out and .rpt files from .inp file
    print('Processing', file, end='')
    process_input(file)

    # Print data to .csv
    output_file = glob.glob('.\data\*.out')[0]  # Since glob returns a list of files, we get the first (and only) file with [0].
    # print('\nWriting', output_file, 'to .\\data\\binary_csv' + file[6:-4] + '.csv')
    # process_output(output_file)

    #  Remove .out file
    os.remove(output_file)
    print('\nDeleted', output_file, '\n')



