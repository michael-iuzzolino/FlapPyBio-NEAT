"""
    http://www.drdobbs.com/testing/unit-testing-with-python/240165163
    http://www.onlamp.com/pub/a/python/2004/12/02/tdd_pyunit.html
"""
from FlapPyBird.flappy import FlappyBirdApp

from modules.species import Species
from modules.config import *

import numpy as np
np.random.seed()


class System(object):
    """
        SYSTEM
        ------
    """

    def __init__(self):

        first_species = Species()
        self.population = [first_species]
        self.population_fitness = 0.0


    def run(self):
        """
            Run
            ---
        """

        while True:
            for species in self.population:                                     # Fitness
                print("Fitness Generation")
                print("------------------")
                print("\t{}\n".format(species))
                self.fitness(species)

            if self.cull():                                                     # Culling
                continue

            self.selection()                                                    # Selection
            self.replication()                                                  # Replication
            print("\n\n")



    def fitness(self, species):
        """
            Fitness
            -------
        """

        flappy = FlappyBirdApp(species)                                         # Play Game to generate fitness
        flappy.play()

        dtype = [('id', int), ('fitness', float)]                               # Initialize items needed for numpy sorting
        unsorted_fitness_values = []                                            # Initialize items needed for numpy sorting
        organism_id_mapping = {}


        for bird_results in flappy.crash_info:
            organism = bird_results['network']                                  # Obtain pertinent info from game
            energy = bird_results['energy']
            distance = bird_results['distance']

            organism.fitness = distance - energy * 1.5                          # Assign fitness to network
            unsorted_fitness_values.append((organism.fitness, organism.ID))     # Append fitness to unsorted array for later sorting
            organism_id_mapping[organism.ID] = organism                             # Update network map to track ID with Network

        species_fitness = np.array(unsorted_fitness_values, dtype=dtype)        # Cast unsorted into np array for sorting
        sorted_species_fitness = np.sort(species_fitness, order='id')           # Sort species by fitness


        for rank, (fitness, organism_id) in enumerate(sorted_species_fitness[::-1]):    # Rank the sorted species
            organism = organism_id_mapping[organism_id]
            organism.intra_species_rank = rank
            organism.normalized_fitness = organism.fitness / len(sorted_species_fitness)  # Normalize fitness

        # Generate species' generation fitness
        species.generations_total_fitness()




    def cull(self):
        """
            Cull
            ----
        """
        for index, species in enumerate(self.population):
            if not species.cull:
                return False

            if species.improvement < IMPROVEMENT_THRESHOLD:
                if len(self.population) > 1:
                    del self.population[index]
                    species.cull = False
                else:
                    self.__init__()
                    return True


    def selection(self):
        """
            Selection
            ---------
        """
        # Generate total fitness of population
        self.__population_total_fitness()

        for species in self.population:
            # Determine how many organisms this species will produce in next generation
            species.number_progeny = self.__calculate_progeny_number(species)

            survived_organisms = []
            for organism in species.current_generation():

                if organism.intra_species_rank <= species.number_progeny:
                    survived_organisms.append(organism)

            # Normalize organism fitness
            species.prime_new_generation(survived_organisms)


    def __population_total_fitness(self):
        """
            Generate Species Fitness
            ------------------------
        """
        population_fitness_total = 0.0
        for species in self.population:
            population_fitness_total += species.generation_total_fitness

        self.population_fitness = population_fitness_total


    def __calculate_progeny_number(self, species):
        """
            Calculate Progeny Number
            ------------------------
        """
        ratio = species.generation_total_fitness / self.population_fitness
        return int(ORGANISMS * ratio)




    def replication(self):
        """
            Replication
            -----------
            *** ISSUE: Need to track all new innovations in each species to ensure no double incrementing of
            innovation numbers for same structure. ***
        """

        new_organisms = []
        for species in self.population:
            # Get number of progeny for species

            for parent_index, parent_organism_1 in enumerate(species.survived_organisms[:-1:2]):
                parent_organism_2 = species.survived_organisms[parent_index+1]

                parents = [parent_organism_1, parent_organism_2]

                for progeny_index in range(2):
                    crossover_chance = np.random.uniform()

                    if crossover_chance <= CROSSOVER_CHANCE:
                        progeny = parents[0].mate(parents[1])                       # Mate parent 1 with parent 2 to produce progeny
                    else:
                        progeny = parents[np.random.randint(len(parents))].mitosis()            # No crossover - just mitosis

                    new_organisms.append(progeny)                              # Append progeny to list


        # Speciation
        self.__speciation(new_organisms)





    def __speciation(self, new_organisms):
        """
            Speciation
            ----------
        """
        new_population = []


        # Check each new organism for a match to the currently existing species
        # build list of unmatched organisms for speciation
        unmatched_organisms = []
        for species in self.population:

            for organism in new_organisms:
                if species.is_compatible(organism):
                    species.update_next_generation(organism)
                else:
                    unmatched_organisms.append(organism)
            species.set_next_generation()


            if len(species.current_generation()) >= 1:
                new_population.append(species)


        if unmatched_organisms:                                                       # Create new species
            print("New organism evolved!")
            new_species = Species(organisms=[unmatched_organisms[0]])

            # Create new species list
            new_species_list = [new_species]
            del unmatched_organisms[0]

            if unmatched_organisms:
                for organism in unmatched_organisms:
                    # Check all new species for match with organism
                    for new_species in new_species_list:
                        if new_species.is_compatible(organism):
                            current_generation = new_species.current_generation()
                            current_generation.append(organism)

                    # Organism wasn't matched to any new species - create new species
                    if not organism.species_matched:
                        new_species = Species(organism=[organism])
                        new_species_list.append(new_species)

                # Add all new species to the new population
                for new_species in new_species_list:
                    new_population.append(new_species)

        self.population = new_population




if __name__ == '__main__':
    driver = System()
    driver.run()
