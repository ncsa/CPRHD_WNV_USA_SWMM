from swmmtoolbox import swmmtoolbox  # Used to extract data from the binary .out file
import pandas as pd  # Used to create data-frames


def process_output(output_file, daily=True):
    # Preconditions: A binary .out file generated by SWMM has been passed
    # Postconditions: A .csv file containing data from all variables in variableList has been created in ./data/binary_csv

    variableList = ['Rainfall', 'Evaporation_infiltration', 'Runoff', 'Total_lateral_inflow', 'Flow_leaving_outfalls', 'Evaporation_rate', 'Potential_PET']  # Which catalog variables we want to extract

    input_parameter_list = []  # The extract function needs to have parameters in (system, variable, variable) form.
    for variable in variableList:  # Make a parameter list
        input_parameter_list.append('system,' + variable + ',' + variable)

    all_dataframe = swmmtoolbox.extract(output_file, *input_parameter_list)  # Extract all parameters

    filename = './data/binary_csv' + output_file[6:-4] + '.csv'  # Set the .csv file name

    if daily:
        all_dataframe = all_dataframe.resample('d').sum()  # Group by day ('d') and sum.
        with open(filename, 'w') as file:
            pd.DataFrame.to_csv(all_dataframe, file)  # Write to .csv file
    else:
        with open(filename, 'w') as file:
            pd.DataFrame.to_csv(all_dataframe, file)  # Write the entire data-frame to a .csv file

