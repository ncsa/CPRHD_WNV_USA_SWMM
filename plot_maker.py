import matplotlib.pyplot as plt
import pandas as pd
from fips_converter import fips_conversion
import glob
from swmm import complete_process


def make_plot(csv_file):
    geoid = csv_file[7:19]
    geoid_data = fips_conversion(geoid)

    frame = pd.read_csv(csv_file, delimiter=',')
    print(frame)
    frame.columns = ['date', 'rainfall', 'evaporation', 'runoff', 'total_lat_inflow', 'flow_leaving_outfalls', 'evaporation_rate', 'potential_PET']
    frame['balance'] = frame['rainfall'] - frame['evaporation']

    date = []
    balance = []
    for x, y in frame.iterrows():
        date.append(x+1)
        balance.append(y['balance'])

    # monthly_balance = 0
    # for i in range(len(balance[:30])):
    #     monthly_balance += balance[i]
    # print(monthly_balance)

    plt.plot(date[:365], [a if a > 0 else 0 for a in balance[:365]])
    # plt.plot(date[:1825], balance[:1825])  # Negative plot

    plt.ylabel('Water Level (Inches)')
    plt.title('Water Level over Time in ' + geoid_data[1] + ' County, ' + geoid_data[0] + ' - ' + geoid)
    plt.tight_layout()
    plt.savefig('./data/' + geoid + '.svg')


