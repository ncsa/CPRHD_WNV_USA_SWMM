def fips_to_dict():
    #Preconditions: None
    #Postconditions: A dictionary with keys of state code and county code has been returned.

    data = {}  # Create an empty dictionary that we will fill later

    with open('US_FIPS_Codes.csv') as file:
        line = file.readline()
    
        while line:  # Loop through the file

            # Remove quotes and new line characters
            tup = line.replace('"', '')\
                      .replace('\n','')\
                      .replace('\r','')\
                      .split(',')
            #exec('tup = (' + line + ')') # Alternative to .replace and .split

            # tup = (Alabama,Baldwin,01,003) # Example tuple
            state_name = tup[0]
            county_name = tup[1]
            state_id = tup[2]
            county_id = tup[3]

            if state_id not in data:
                data[state_id] = {}
            if county_id not in data[state_id]:
                data[state_id][county_id] = [state_name, county_name]
            line = file.readline()
    return data


def fips_conversion(fips_code):
    #Preconditions: A 12-digit GeoID has been passed (State (2) + County (3) + Tract (4) + Block Group (3))
    #Postconditoins: A list has been returned with the format of [State name, County name, Tract ID, Block Group ID]

    state_code = fips_code[:2]
    county_code = fips_code[2:5]
    census_tract = fips_code[5:9]
    census_block_group = fips_code[9:]

    converted_fips = _fips_dict[state_code][county_code]
    return [converted_fips[0], converted_fips[1], census_tract, census_block_group]

_fips_dict = fips_to_dict()
