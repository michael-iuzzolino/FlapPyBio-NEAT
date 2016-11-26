from modules.organism import Organism
from modules.config import *

import numpy as np
np.random.seed()

class Species(object):
	"""
		The species contains all of the organisms that are genetically similar. This protects novel structures from immediate extinction.
		The key elements of the class are:
			1. List of organisms
			2. Representative genome against which organisms are compared to determine species membership
			3. Species ID
			4. CULLING - removes unfit organisms from the species (this may also include species that evolve towards other speices)
	"""

	def __init__(self, species_id=None, organisms=[]):
		if not organisms:
			organisms = [Organism() for _ in range(ORGANISMS)]
		self.organisms = organisms

		self.ID = species_id

		self.representative_genome = self.organisms[0].genome # Set to genome of first species, since all species will be the same on init


	def is_compatible(self, organism):

		organism_genome = organism.genome

		# print("\t\tOrganism Genome: {}".format(organism_genome))
		# print("\t\tSpecies Genome: {}".format(self.genome))


		# Calculate excess genes, E
		E, D, W, N = organism.compare_genomes(self.representative_genome)


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


	def __repr__(self):
		return "Species ID: {}".format(self.ID)
