def fips_to_dict(fips_csv_file):
    #Preconditions: None
    #Postconditions: A dictionary with keys of state code and county code has been returned.
    #                ex. dict[state_code][county_code] will give you the state name and county name
  

    data = {}  # Create an empty dictionary that we will fill later

    with open(fips_csv_file) as file:
        for line in file:
            # Remove quotes and new line characters
            tup = line.replace('"', '')\
                      .replace('\n','')\
                      .replace('\r','')\
                      .split(',')
            #exec('tup = (' + line + ')') # Alternative to .replace and .split

            # tup = (Alabama,Baldwin,01,003) # Example tuple after processing
            state_name = tup[0]
            county_name = tup[1]
            state_id = tup[2]
            county_id = tup[3]

            if state_id not in data:   # If the state is not already in the dictionary
                data[state_id] = {}  # Add the state
            if county_id not in data[state_id]:  # If the county is not in the state subset
                data[state_id][county_id] = [state_name, county_name]  # Add the county, and associate it with the names of both
    return data


def fips_conversion(fips_code):
    #Preconditions: A 12-digit GeoID has been passed (State (2 digits) + County (3 digits) + Tract (4 digits) + Block Group (3 digits))
    #Postconditoins: A list has been returned with the format of [State name, County name, Tract ID, Block Group ID]

    state_code = fips_code[:2]
    county_code = fips_code[2:5]
    converted_fips = _fips_dict[state_code][county_code]

    if len(fips_code) > 5:
        census_tract = fips_code[5:9]
        census_block_group = fips_code[9:]
        return [converted_fips[0], converted_fips[1], census_tract, census_block_group]
    return converted_fips


_fips_dict = fips_to_dict('../data/input_file_data/US_FIPS_Codes.csv')  # Create the dictionary for use in fips_conversion

