"""
    http://www.drdobbs.com/testing/unit-testing-with-python/240165163
    http://www.onlamp.com/pub/a/python/2004/12/02/tdd_pyunit.html
"""
from FlapPyBird.flappy import FlappyBirdApp
from modules.organism import Organism
from modules.species import Species
from modules.config import *

import numpy as np
import random
random.seed()


class System(object):
    def __init__(self):
        self.species = [Species([Organism() for _ in range(ORGANISMS)])]

    def run(self):

        while True:
            # Fitness
            for species in self.species:
                print("Running species {}".format(species.ID))
                self.fitness(species)

            # Selection
            self.selection()

            # Replication
            self.replication()

            # Check Speciation
            self.speciation()


    def fitness(self, species):
        flappy = FlappyBirdApp(species.organisms)
        flappy.play()

        dtype = [('id', int), ('fitness', float)]
        unsorted_fitness_values = []

        network_id_map = {}

        for bird_results in flappy.crash_info:
            # Obtain pertinent info from game
            organism = bird_results['network']
            organism_id = organism.ID
            energy = bird_results['energy']
            distance = bird_results['distance']

            # Fitness recalculation
            fitness = distance - energy * 1.5

            # Assign fitness to network
            organism.fitness = fitness

            # Append fitness to unsorted array for later sorting
            unsorted_fitness_values.append((fitness, organism_id))

            # Update network map to track ID with Network
            network_id_map[organism_id] = organism


        # Sort species by fitness
        species_fitness = np.array(unsorted_fitness_values, dtype=dtype)
        sorted_species_fitness = np.sort(species_fitness, order='id')

        # Create sorted fitness results
        for rank, (fitness, id_) in enumerate(sorted_species_fitness[::-1]):
            network_id_map[id_].intra_species_rank = rank



    def selection(self):
        self.top_species = {}
        for species in self.species:
            species_ID = species.ID
            self.top_species[species_ID] = []
            for organism in species.organisms:
                rank = organism.intra_species_rank
                if rank < RANK_CUTOFF:
                    self.top_species[species_ID].append(organism)

            print("length: {}".format(len(self.top_species[species_ID])))



    def replication(self):
        print("\n")
        print("="*40)
        print("REPLICATION")
        print("=*40")
        print("\n")
        new_generation = {}
        for species, organisms in self.top_species.items():
            new_generation[species] = []
            for index, parent_organism_1 in enumerate(organisms[:-1:2]):
                parent_organism_2 = organisms[index+1]

                for progeny_index in range(4):
                    genes = parent_organism_1.mate(parent_organism_2)
                    progeny = Organism(genes)
                    new_generation[species].append(progeny)

        self.species = new_generation






    def speciation(self):
        print("\n")
        print("="*40)
        print("\tSpeciation")
        print("="*40)
        for species in self.species:
            print("{}".format(species))
            for organism in species.organisms:
                print("\t{}".format(organism))
                species.is_compatible(organism)


        # Check for similarities in new species list for grouping into new species
        new_organisms = []
        for species in self.species:
            for organism in species.organisms:
                if not organism.species_matched:
                    new_organisms.append(organism)

        # Create new species
        if new_organisms:
            new_species_list = [Species([new_organisms[0]])]
            del new_organisms[0]
            self.species.append(new_species_list[0])

        if new_organisms:
            for new_organism in new_organisms:
                print("\tNew organism: {}".format(new_organism))
                for new_species in new_species_list:
                    print("\t\tChecking if compatible with species: {}".format(new_species))
                    new_species.is_compatible(new_organism)

                if not new_organism.species_matched:
                    print("\t\tNot matched. Creating new species")
                    new_species_list.append(Species([new_organism]))
                else:
                    print("\t\tMatched!")
                print("\n")


            for new_species in new_species_list[1:]:
                self.species.append(new_species)



if __name__ == '__main__':
    driver = System()
    driver.run()
