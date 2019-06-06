from pyswmm import Simulation  # Used to convert .inp files to .out and .rpt files using SWMM
import glob  # Used to find .inp and .out file(s)
import os  # Used to delete the .out file after it has been read into a .csv (save disk space) and get thread identity
from extract_data import process_output  # Used to create the .csv file
from multiprocessing import Pool  # Used for multi-threading
import time  # Used for time analysis
import sys  # Used for suppressing output


def process_input(input_file):
    #  Preconditions: 'file' has been passed, containing the directory path for a .inp file
    #  Postconditions: The SWMM model has created a .out and .rpt file in the base_directory\data folder based on the parameters given in the .inp file.
    Simulation.execute = suppressOutput(Simulation.execute)  # Make it so that sim.execute() does not print anything
    with Simulation(input_file) as sim:
        sim.execute()
        sim.close()


def complete_process(input_file):
    #  Preconditions: An input file has been passed
    #  Postconditions: A .rpt file has been generated. A .csv file has been created containing data from the simulation.
    print('Processing', input_file[7:], ' Thread:', os.getpid())  # Print filename and thread number
    process_input(input_file)

    output_file = input_file[:-4] + '.out'  # Name formatting
    process_output(output_file)  # Create the .csv from the .out file
    #os.remove(output_file)  # Remove the .out file


def suppressOutput(func):  # This function temporarily redirects stdout to a null variable so it doesn't get printed
    def wrapper(*args, **kwargs):
        with open(os.devnull, 'w') as devNull:
            original = sys.stdout
            sys.stdout = devNull
            func(*args, **kwargs)
            sys.stdout = original
    return wrapper


if __name__ == '__main__':
    start_time = time.time()

    input_files = glob.glob('./data/*.inp')
    pool = Pool()
    pool.map(complete_process, input_files)
    print('Elapsed time with multi-threading:', '%.2f' % (time.time() - start_time), 'seconds.')
    # start_time = time.time()
    # for file in input_files:
    #     complete_process(file)
    # print('Elapsed time with single thread:', time.time() - start_time)

