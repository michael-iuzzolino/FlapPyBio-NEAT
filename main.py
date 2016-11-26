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
    def __init__(self):
        initial_species_ID = 0
        self.species_list = [Species(initial_species_ID)]

    def run(self):

        while True:

            # Fitness
            for species in self.species_list:
                print("Generating Fitness for Species #{}".format(species.ID))
                self.fitness(species)

            # Selection
            self.selection()

            # Replication
            self.replication()

            # Check Speciation
            self.speciation()


    def fitness(self, species):
        # Play Game to generate fitness
        flappy = FlappyBirdApp(species.organisms)
        flappy.play()


        # Initialize items needed for numpy sorting
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
        # Fix this section to remove unfit organisms from species: 'cull the species'
        self.top_species = {}

        # Iterate through the species within the environment
        for species in self.species_list:

            # Initialize new key for top species dictionary inidicating current species
            self.top_species[species.ID] = []

            # Iterate through organisms within the current species
            for organism in species.organisms:

                # Get oragnism's intra species rank
                rank = organism.intra_species_rank

                # Check if rank is less than the cutoff; if so, append organism to top list within species
                if rank < RANK_CUTOFF:
                    self.top_species[species.ID].append(organism)

        print("Top Species")
        print("-----------")
        for species_ID, organisms in self.top_species.items():
            print("\tSpecies ID: {}")
            for organism in organisms:
                print("\t\tOrganism {} -- Rank: {}".format(organism.ID, organism.intra_species_rank))

            print("\n")




    def replication(self):

        # Initialize new generation of species list (must contain Species-class objects)
        new_species_generation = []

        # Iterate through the species in top_species
        for species_ID, organisms in self.top_species.items():

            # Initialize new list to hold the progeny of 2 species
            new_organisms_list = []

            # Iterate through organisms by 2 up until the second-to-last organism
            for index, parent_organism_1 in enumerate(organisms[:-1:2]):

                # Define second parent in list
                parent_organism_2 = organisms[index+1]

                # Since we cut original population in half during selection, 2 parents must create 4 progeny to return to original population size for next generation
                for progeny_index in range(4):

                    # Mate parent 1 with parent 2 to produce progeny
                    progeny = parent_organism_1.mate(parent_organism_2)

                    # Append progeny to list
                    new_organisms_list.append(progeny)

            # Create new generation of species from the progeny
            new_species = Species(species_ID, new_organisms_list)

            # Append to new species generation list
            new_species_generation.append(new_species)

        # Redefine species_list
        self.species_list = new_species_generation

        print("New species list")
        for species in self.species_list:
            print("species: {}".format(type(species)))






    def speciation(self):
        species_ID_list = []

        for species in self.species_list:
            species_ID_list.append(species.ID)
            for organism in species.organisms:
                species.is_compatible(organism)

        # Check for similarities in new species list for grouping into new species
        new_organisms = []
        for species in self.species_list:
            for organism in species.organisms:
                if not organism.species_matched:
                    new_organisms.append(organism)

        # Create new species
        if new_organisms:
            new_species_ID = max(species_ID_list)+1
            new_species_list = [Species(new_species_ID, [new_organisms[0]])]
            del new_organisms[0]
            self.species_list.append(new_species_list[0])

        if new_organisms:

            for new_organism in new_organisms:
                for new_species in new_species_list:
                    new_species.is_compatible(new_organism)

                if not new_organism.species_matched:
                    new_species_ID += 1
                    new_species_list.append(Species(new_species_ID, [new_organism]))

            for new_species in new_species_list[1:]:
                self.species_list.append(new_species)




if __name__ == '__main__':
    driver = System()
    driver.run()
