"""
    http://www.drdobbs.com/testing/unit-testing-with-python/240165163
    http://www.onlamp.com/pub/a/python/2004/12/02/tdd_pyunit.html
"""
from FlapPyBird.flappy import FlappyBirdApp

from modules.species import Species
from modules.config import *
from modules.pool import *

import numpy as np
np.random.seed()


class System(object):
    """
        SYSTEM
        ------
    """

    def __init__(self):
        self.pool = Pool()


    def run(self):
        """
            Run
            ---
        """
        while True:

            print("\n")
            print("="*60)
            print("\t\tGenerating Fitness")
            print("="*60)
            for species in self.pool:                                # Fitness
                print("\t Species: {}".format(species))
                self.fitness(species, self.pool.generation)

            # Culling and ranking
            self.pool.cull_and_rank_sequence()

            # SELECT
            self.pool.select()

            # REPLICATE
            self.pool.replicate()









    def fitness(self, species, generation):
        """
            Fitness
            -------
        """

        flappy = FlappyBirdApp(species, generation)                                         # Play Game to generate fitness
        flappy.play()

        dtype = [('id', int), ('fitness', float)]                               # Initialize items needed for numpy sorting
        unsorted_fitness_values = []                                            # Initialize items needed for numpy sorting
        organism_id_mapping = {}


        for bird_results in flappy.crash_info:
            organism = bird_results['network']                                  # Obtain pertinent info from game
            energy = bird_results['energy']
            distance = bird_results['distance']

            organism.fitness = distance - energy * 2.5                          # Assign fitness to network

            if organism.fitness > self.pool.max_fitness:
                self.pool.max_fitness = organism.fitness

            unsorted_fitness_values.append((organism.fitness, organism.ID))     # Append fitness to unsorted array for later sorting
            organism_id_mapping[organism.ID] = organism                             # Update network map to track ID with Network

        species_fitness = np.array(unsorted_fitness_values, dtype=dtype)        # Cast unsorted into np array for sorting
        sorted_species_fitness = np.sort(species_fitness, order='id')           # Sort species by fitness


        for rank, (fitness, organism_id) in enumerate(sorted_species_fitness[::-1]):    # Rank the sorted species
            organism = organism_id_mapping[organism_id]
            organism.fitness = fitness
            organism.intra_species_rank = rank









if __name__ == '__main__':
    driver = System()
    driver.run()
