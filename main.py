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
            for species in self.pool:                                           # Fitness
                print("\t{}".format(species))
                self.fitness(species, self.pool.generation)

            # SELECT
            self.pool.selection()

            # REPLICATE
            self.pool.replicate()



    def fitness(self, species, generation):
        """
            Fitness
            -------
        """

        flappy = FlappyBirdApp(species, generation)                             # Play Game to generate fitness
        flappy.play()

        for bird_results in flappy.crash_info:
            organism = bird_results['network']                                  # Obtain pertinent info from game
            energy = bird_results['energy']
            distance = bird_results['distance']

            fitness = distance - energy * 2.5
            organism.fitness = fitness if fitness > 0 else -1.0                 # Assign fitness to network

            if organism.fitness > self.pool.max_fitness:
                self.pool.max_fitness = organism.fitness

        species.set_intra_species_rank()




if __name__ == '__main__':
    random_pipes = False

    with open('FlapPyBird/resources/config.py', 'r') as infile:
        configure_file = infile.readlines()

    with open('FlapPyBird/resources/config.py', 'w') as outfile:
        for line in configure_file:
            if 'RANDOM_PIPES' in line:
                line = 'RANDOM_PIPES = {}\n'.format(random_pipes)
            outfile.write(line)


    driver = System()
    driver.run()
