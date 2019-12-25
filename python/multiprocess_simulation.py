import glob
import persistqueue
from pyswmm import Simulation
from multiprocessing import Process


_sim_types = {'ng': 'no_green_infrastructure',
              'rb': 'rain_barrel',
              'rg': 'rain_garden'
              }


_sim_type = 'ng'
_max_processes = 8


path_to_input_files = './' + _sim_types[_sim_type] + '/'
path_to_queue = path_to_input_files + _sim_types[_sim_type] + '_queue'
q = persistqueue.UniqueAckQ(path_to_queue, auto_commit=True, multithreading=True)


def main():
    if q.size == 0:
        input_files = glob.glob(path_to_input_files + '*.inp')
        print('Queue is empty, adding', len(input_files), 'files from', path_to_input_files)
        for file in input_files:
            q.put(file)

    print('Queue Size:', q.size)
    for i in range(_max_processes):
        p = Process(target=worker)
        p.start()
    return


def worker():
    while True:
        file = q.get(block=True)
        sim = Simulation(file)
        sim.execute()
        q.ack(file)


if __name__ == '__main__':
    main()
