from modules.config import *
import numpy as np
import random
random.seed()

class Species(object):
	ID = 0

	def __init__(self, organisms=[], speciesID=None):

		for organism in organisms:
			organism.speciesID = Species.ID

		self.organisms = organisms

		if speciesID:
			self.ID = speciesID
		else:
			self.ID = Species.ID
			Species.ID += 1

		self.genome = None
		self._init_representative_genome()

	def __repr__(self):
		return "Species ID {}".format(self.ID)


	def _init_representative_genome(self):
		self.genome = self.organisms[0].synapse_network


	def is_compatible(self, organism):

		organism_genome = organism.synapse_network

		# print("\t\tOrganism Genome: {}".format(organism_genome))
		# print("\t\tSpecies Genome: {}".format(self.genome))


		# Calculate excess genes, E
		E, D, W, N = organism.compare_genomes(self.genome)


		# Calculate average weight differences of matching genes
		# Find length of larger genome, N
		DELTA = (C1 * E / N) + (C2 * D / N) + C3*W

		# New species!
		if DELTA >= DELTA_T:
			organism.species_matched = False

		# Same species
		else:
			# Check if species exists already
			#self.add(organism)
			organism.species_matched = True



	def add(self, new_organism):
		pass

	def remove(self, network_ID):
		pass
