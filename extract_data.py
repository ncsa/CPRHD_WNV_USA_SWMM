from swmmtoolbox import swmmtoolbox  # Used to extract data from the binary .out file
import pandas as pd  # Used to create dataframes


def extract_data(output_file):

    catalogList = swmmtoolbox.catalog(output_file)  # Get a list of catalog variables
    variableList = ['Evaporation_infiltration', 'Runoff', 'Total_lateral_inflow', 'Flow_leaving_outfalls', 'Evaporation_rate', 'Potential_PET']  # Which catalog variables we want to extract (Rainfall is included below)
    all_dataframe = swmmtoolbox.extract(output_file, 'system,Rainfall,Rainfall')  # Create an initial data-frame with the Rainfall data

    for line in catalogList:  # Loop through each catalog variable
        if line[0] == 'system' and line[1] in variableList:  # Check if the catalog variable matches our variableList
            input_parameter = line[0] + ',' + line[1] + ',' + line[2]  # Construct our string parameter for the extract function (ex. 'system,Runoff,Runoff')
            print('Processing : ', input_parameter)
            new_data = swmmtoolbox.extract(output_file, input_parameter)
            all_dataframe = all_dataframe.join(new_data)

    with open('extract_system_all.csv', 'w') as file:
        pd.DataFrame.to_csv(all_dataframe, file)  # Write the dataframe to a .csv file
