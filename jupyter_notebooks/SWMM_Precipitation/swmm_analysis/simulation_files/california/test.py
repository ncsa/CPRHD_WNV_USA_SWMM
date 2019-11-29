from pyswmm import Simulation
import glob

if __name__ == '__main__':
	files = glob.glob('./*.inp')
	for file in files:
		print(file)
		sim = Simulation(file)
		sim.execute()
