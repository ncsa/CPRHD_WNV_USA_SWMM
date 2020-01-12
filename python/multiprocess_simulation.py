import glob
from pyswmm import Simulation
from multiprocessing import Pool
import shutil
import os
import sys


_sim_types = {'ng': 'no_green_infrastructure',
              'rb': 'rain_barrel',
              'rg': 'rain_garden'
              }


_sim_type = 'ng'
_max_processes = 8


path_to_input_files = '../input_files/' + _sim_type + '/'
path_to_output_files = '../output_files/' + _sim_type + '/'
path_to_report_files = '../report_files/' + _sim_type + '/'


def main():
    input_files = glob.glob(path_to_input_files + '*.inp')
    print('Input Files:', len(input_files))
    sys.stdout = open(os.devnull, 'w')
    print('hello')
    pool = Pool(_max_processes)
    pool.map(worker, input_files)
    return


def worker(file):
    name = file[file.rfind('/')+1:file.rfind('.')]
    sim = Simulation(file)
    sim.execute()
    try:
        os.remove(file)
        _ = shutil.move(path_to_input_files + name + '.out', path_to_output_files)  # move the output file to another folder
        _ = shutil.move(path_to_input_files + name + '.rpt', path_to_report_files)
    except:
        pass


if __name__ == '__main__':
    main()
