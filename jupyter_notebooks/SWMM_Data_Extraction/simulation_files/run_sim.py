import glob
from pyswmm import Simulation

for file in glob.glob('./*.inp'):
	sim = Simulation(file)
	sim.execute()
