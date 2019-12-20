import glob
from pyswmm import Simulation
import pickle
from multiprocessing import Pool
import os


_sim_types = {'ng': 'no_green_infrastructure',
              'rb': 'rain_barrel',
              'rg': 'rain_garden'
              }


_batch_size = 32


def run_simulation(file):
    sim = Simulation(file)
    sim.execute()


def chonk(list, chonk_size):
    for i in range(0, len(list), chonk_size):
        yield list[i: i + chonk_size]


def main():
    # Specify Simulation Type
    sim_type = 'ng'

    chunk_file = '../data/input_files/' + sim_type + '_chunked'
    completed_chunk_file = '../data/input_files/' + sim_type + '_chunked_completed'
    path_to_input_files = '../input_files/' + _sim_types[sim_type] + '/*inp'

    if not os.path.exists(chunk_file):
	# Create and save the initial chunk list
        print('Chunk file not found, making a new one at:', chunk_file)
        files = glob.glob(path_to_input_files)
        chunks = list(chonk(files, _batch_size))
        pickle.dump(chunks, open(chunk_file, 'wb'))
    
    else: # Load the existing chunk list
        chunks = pickle.load(open(chunk_file, 'rb'))

    print('Number of batches:', len(chunks))
    print('Batch Size:', _batch_size)

    pool = Pool()
    while len(chunks) > 0:
        chunk = chunks[0]
        # Multiprocess the chunk
        pool.map(run_simulation, chunk)

        # Save the completed chunks
        try:
            completed_chunks = pickle.load(open(completed_chunk_file, 'rb'))
        except:  # if the file doesn't exist yet (first completed chunk)
            completed_chunks = []
        completed_chunks.append(chunk)
        pickle.dump(completed_chunks, open(completed_chunk_file, 'wb'))

        # Remove the completed chunk from the list
        chunks.remove(chunks[0])

        # Save
        pickle.dump(chunks, open(chunk_file, 'wb'))

    print('No more batches left to process')


if __name__ == '__main__':
    main()
