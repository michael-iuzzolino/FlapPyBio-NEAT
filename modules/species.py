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

	ID = 0

	def __init__(self, organisms=[]):

		# Define species ID
		self.ID = Species.ID
		Species.ID += 1

		# Initialize parent generation number
		self.current_generation_index = 0

		if not organisms:
			organisms = [Organism() for _ in range(ORGANISMS)]

		self.generations = [organisms]

		# Determine representative genome
		# This should be a random genome from the PREVIOUS generation of the species
		self.representative_genome = organisms[0].genome



		# Initialize other useful parameters
		self.generation_total_fitness = 0.0
		self.cull = False
		self.improvement = 0.0
		self.number_progeny = None



	def is_compatible(self, organism):
		# Calculate excess genes, E
		E, D, W, N = organism.compare_genomes(self.representative_genome)

		# Calculate average weight differences of matching genes
		# Find length of larger genome, N
		DELTA = (C1 * E / N) + (C2 * D / N) + C3*W

		# New species!
		if DELTA < DELTA_T:
			return True
		else:
			return False



	def generations_total_fitness(self):
		previous_fitness = self.generation_total_fitness
		new_fitness = 0.0
		for organism in self.generations[self.current_generation_index]:
			new_fitness += organism.fitness

		self.generation_total_fitness = new_fitness

		fitness_change = new_fitness - previous_fitness

		self.improvement += fitness_change

		# Determine culling and improvement
		if self.current_generation_index % ROUNDS_BEFORE_CULLING == ROUNDS_BEFORE_CULLING-1:
			self.cull = True


	def current_generation(self):
		return self.generations[self.current_generation_index]


	def prime_new_generation(self, survived_organisms):

		# Normalize fitness of survived organisms
		for organism in survived_organisms:
			organism.normalized_fitness = organism.fitness / len(survived_organisms)    # Normalize fitness to species

		self.survived_organisms = survived_organisms

		self.next_generation = []


	def update_next_generation(self, new_organism):
		self.next_generation.append(new_organism)



	def set_next_generation(self):

		# Set next generation's representative genome randomly from this set
		current_generation = self.generations[self.current_generation_index]
		random_genome_index = np.random.randint(len(current_generation))
		self.representative_genome = current_generation[random_genome_index].genome

		# Move to next generation
		self.current_generation_index += 1
		self.generations.append(self.next_generation)



	def __repr__(self):
		return "Species ID: {} -- Generation {} -- Rep Genome: {}".format(self.ID, self.current_generation_index, self.representative_genome)
