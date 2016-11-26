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
        self.species_list = [Species(species_id=initial_species_ID, generation_number=0)]

    def run(self):

        while True:

            # Fitness
            print("="*60)
            print("\t\tFITNESS")
            print("="*60)
            print('\n')
            for species in self.species_list:
                print("\tGenerating Fitness for Species #{}".format(species.ID))
                self.fitness(species)
            print("\n")

            # Cull species
            if self.cull():
                continue

            # Selection
            self.selection()

            # Replication
            self.replication()

            # Check Speciation
            self.speciation()


    def cull(self):
        for index, species in enumerate(self.species_list):
            if species.cull:
                print("="*60)
                print("\t\tCULLING")
                print("="*60)
                print('\n')
                if species.improvement < IMPROVEMENT_THRESHOLD:
                    if len(self.species_list) > 1:
                        print("\tCulling Species {}\n".format(species.ID))
                        del self.species_list[index]
                    else:
                        print("\tOnly Species in environment. Reinitialize.\n")
                        initial_species_ID = 0
                        self.species_list = [Species(species_id=initial_species_ID, generation_number=0)]
                        return True
                    species.cull = False
        return False


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


        # Adjust fitness for species
        self.intra_species_fitness(unsorted_fitness_values, network_id_map)


        # Sort species by fitness
        species_fitness = np.array(unsorted_fitness_values, dtype=dtype)
        sorted_species_fitness = np.sort(species_fitness, order='id')


        # Create sorted fitness results
        for rank, (fitness, id_) in enumerate(sorted_species_fitness[::-1]):
            network_id_map[id_].intra_species_rank = rank




    def intra_species_fitness(self, unsorted_fitness_values, network_id_map):
        for fitness, organism_id in unsorted_fitness_values:
            adjusted_fitness = fitness / len(unsorted_fitness_values)

            fitness = adjusted_fitness
            network_id_map[organism_id].fitness = adjusted_fitness



    def generate_species_fitness(self):
        population_fitness_total = 0.0
        for species in self.species_list:
            species.species_fitness_sum()
            population_fitness_total += species.total_fitness

        return population_fitness_total



    def selection(self):
        print("="*60)
        print("\t\tSELECTION")
        print("="*60)
        print('\n')
        # Fix this section to remove unfit organisms from species: 'cull the species'
        self.top_species = {}

        # Generate total population fitness from each species fitness sum
        # These ratios will be used for determining number of replication organisms per species
        total_population_fitness = self.generate_species_fitness()
        print("Total population fitness: {:.2f}".format(total_population_fitness))
        print("-"*50)

        # Iterate through the species within the environment
        for species in self.species_list:
            print("Species ID {} -- Generation {}".format(species.ID, species.generation_number, species.total_fitness, species.cull))

            print("\tSpecies fitness sum: {:.2f}".format(species.total_fitness))
            print("\tFitness improvement from last generation: {:.2f}".format(species.improvement))
            # Determine number of organisms in species
            # "Assigned a number of organims proportional to the sum of the adjusted fitnesses of its member organisms"
            number_progeny = self.get_progeny_number(species, total_population_fitness)

            print("\tNumber of Progeny: {}\n\n".format(number_progeny))
            # Initialize new key for top species dictionary inidicating current species
            self.top_species[(species.ID, species.generation_number, species.total_fitness, species.cull)] = []

            # Iterate through organisms within the current species
            for organism in species.organisms:
                organism.number_progeny = int(number_progeny / 4)
                # Get oragnism's intra species rank
                rank = organism.intra_species_rank

                # Check if rank is less than the cutoff; if so, append organism to top list within species
                if rank < RANK_CUTOFF:
                    self.top_species[(species.ID, species.generation_number, species.total_fitness, species.cull)].append(organism)


    def get_progeny_number(self, species, total_population_fitness):
        species_fitness_sum = species.total_fitness
        ratio = species_fitness_sum / total_population_fitness
        return int(ORGANISMS * ratio)


    def replication(self):

        # Initialize new generation of species list (must contain Species-class objects)
        new_species_generation = []

        # Iterate through the species in top_species
        for (species_ID, generation, total_fitness, cull), organisms in self.top_species.items():

            # Initialize new list to hold the progeny of 2 species
            new_organisms_list = []

            # Iterate through organisms by 2 up until the second-to-last organism
            for index, parent_organism_1 in enumerate(organisms[:int(len(organisms)/2):2]):

                # Define second parent in list
                parent_organism_2 = organisms[index+1]


                # Replicate
                number_progeny = parent_organism_1.number_progeny
                for progeny_index in range(number_progeny):

                    # Mate parent 1 with parent 2 to produce progeny
                    progeny = parent_organism_1.mate(parent_organism_2)

                    # Append progeny to list
                    new_organisms_list.append(progeny)

            # Create new generation of species from the progeny
            new_species = Species(species_id=species_ID,
                                  generation_number=generation+1,
                                  organisms=new_organisms_list,
                                  total_fitness=total_fitness,
                                  cull=cull)

            # Append to new species generation list
            new_species_generation.append(new_species)

        # Redefine species_list
        self.species_list = new_species_generation




    def speciation(self):
        print("="*60)
        print("\t\tSPECIATION")
        print("="*60)
        print('\n')

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
            print("\tNew Species! ID {}".format(new_species_ID))
            new_species_list = [Species(species_id=new_species_ID, generation_number=0, organisms=[new_organisms[0]])]
            del new_organisms[0]
            self.species_list.append(new_species_list[0])

        if new_organisms:
            for new_organism in new_organisms:
                for new_species in new_species_list:
                    new_species.is_compatible(new_organism)

                if not new_organism.species_matched:
                    new_species_ID += 1
                    print("\tNew Species! ID {}".format(new_species_ID))
                    new_species_list.append(Species(species_id=new_species_ID, generation_number=0, organisms=[new_organism]))

            for new_species in new_species_list[1:]:
                self.species_list.append(new_species)

        print("\n")

if __name__ == '__main__':
    driver = System()
    driver.run()
