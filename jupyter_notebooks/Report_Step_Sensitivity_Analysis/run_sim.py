import glob
from pyswmm import Simulation

for sim_type in ['1', '3', '6', '12', '24']:
	files = glob.glob('./' + sim_type + '/*.inp')
	for file in files:
		sim = Simulation(file)
		sim.execute()
