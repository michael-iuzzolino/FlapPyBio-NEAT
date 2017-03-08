from modules.organism import Organism
from modules.config import *

import numpy as np
np.random.seed()

class Species(object):
    ID = 0

    def __init__(self, new_species=False, initial_organism=None, number_of_organisms=POPULATION):

        self.organisms = [initial_organism] if new_species else [Organism() for _ in range(number_of_organisms)]

        self.representative_genome = self.organisms[0].genome

        self.ID = Species.ID
        Species.ID += 1

        self.top_fitness = 0.0
        self.average_fitness = 0.0
        self.fitness_sum = 0
        self.stale_index = 0

        self.parents = []
        self.progeny = []


    def __repr__(self):
        return "Species: ID {} -- Average Fitness {:.0f} -- Top Fitness {:.0f} ".format(self.ID, self.average_fitness, self.top_fitness)

    def __len__(self):
        return len(self.organisms)

    def __iter__(self):
        for organism in self.organisms:
            yield organism



    def set_intra_species_rank(self):
        dtype = [('id', int), ('fitness', float)]                               # Initialize items needed for numpy sorting
        organism_map = { organism.ID : organism for organism in self.organisms }
        unsorted_fitness = [(organism.ID, organism.fitness) for organism in self.organisms]
        unsorted_fitness = np.array(unsorted_fitness, dtype=dtype)
        sorted_fitness = np.sort(unsorted_fitness, order='fitness')[::-1]

        sorted_organisms = []

        for rank, (organism_id, fitness) in enumerate(sorted_fitness):
            organism_map[organism_id].intra_species_rank = rank
            sorted_organisms.append(organism_map[organism_id])

        self.organisms = sorted_organisms


    def generate_average_fitness(self):
        self.fitness_sum = 0.0

        for organism in self.organisms:
            self.fitness_sum += organism.fitness

        self.average_fitness = self.fitness_sum / len(self.organisms)


    def mate(self):

        if np.random.uniform() < CROSSOVER_CHANCE:

            parent_1 = self.parents[np.random.randint(len(self.parents))]
            parent_2 = self.parents[np.random.randint(len(self.parents))]
            progeny = parent_1.mate(parent_2)

        else:
            parent = self.parents[np.random.randint(len(self.parents))]
            progeny = parent.clone()

        return progeny



    def is_compatible(self, organism):
        # Calculate excess genes, E
        E, D, W, N = organism.compare_genomes(self.representative_genome)

        # Calculate average weight differences of matching genes
        delta = (C1 * E / N) + (C2 * D / N) + C3*W

        # New species!
        if delta < DELTA_T:
            return True
        else:
            return False
