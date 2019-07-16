import matplotlib.pyplot as plt
import pandas as pd
from swmm import complete_process

# Alabama, Autauga County
frame = pd.read_csv('./data/binary_csv/010010202001.csv', delimiter=',')
print(frame)
frame.columns = ['date', 'rainfall', 'evaporation', 'runoff', 'total_lat_inflow', 'flow_leaving_outfalls', 'evaporation_rate', 'potential_PET']
frame['balance'] = frame['rainfall'] - frame['evaporation']
# frame['date'] = frame['date'].to_datetime()
# frame = frame['date'].to_frame().join(frame['balance'])

# print(frame.resample('d').sum())


date = []
balance = []
for x, y in frame.iterrows():
    date.append(x+1)
    balance.append(y['balance'])

monthly_balance = 0
for i in range(len(balance[:30])):
    monthly_balance += balance[i]

print(monthly_balance)



plt.plot(date[:365], [a if a > 0 else 0 for a in balance[:365]])
plt.xlabel('Days since January 1st, 1981')
plt.ylabel('Water Level (Inches)')
plt.title('Water Level over Time in Autauga County, Alabama')
plt.tight_layout()
plt.savefig('./data/plot_spring.svg')


