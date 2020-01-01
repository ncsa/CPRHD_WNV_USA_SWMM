import pandas as pd
from pandarallel import pandarallel  # Multiprocessing a pandas DataFrame
from InputFile import InputFile


def main():
    # Number of processes to create when multiprocessing
    num_processes = 4

    # Load the Block Group Characteristics Data
    characteristics_file = '../data/input_file_data/Selected_BG_inputs_20191212.csv'
    characteristics_frame = pd.read_csv(characteristics_file, skip_blank_lines=True, low_memory=False, dtype=str)  # Read the green infrastructure data to a pandas dataframe

    # Load the Evaporation Data
    evaporation_data = pd.read_pickle('../data/input_file_data/evaporation_converted.pkl')

    # Initialize pandarallel
    pandarallel.initialize(nb_workers=num_processes, progress_bar=True, verbose=1, use_memory_fs=True)

    # Set simulation type (ng = No Green Infrastructure, rb = Rain Barrel, rg = Rain Garden)
    sim_type = 'ng'

    # Apply the create_input_function to each GEOID in the block group characteristics frame
    characteristics_frame.parallel_apply(lambda x: create_input_file(x, evaporation_data.loc[x['GEOID10']], sim_type), axis=1)
    return


def create_input_file(row, evap, sim_type):
    out_dir = '/home/matas/Desktop/all_input_files/ng/'
    outfile = out_dir + row['GEOID10'] + '_' + sim_type + '.inp'
    file = InputFile(row, outfile, evap, sim_type)
    file.write()
    return


if __name__ == '__main__':
    main()
