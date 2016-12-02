from modules.config import *
from modules.species import Species
import numpy as np


class Pool(object):

    def __init__(self):

        LUCA = Species()
        self.species = [LUCA]

        self.generation = 0
        self.max_fitness = 0.0



    def __repr__(self):
        return "{}".format(self.generation)


    def __iter__(self):
        for species in self.species:
            yield species

    def __prime_selection(self):
        self.cull()

        # 2. Rank globally
        self.rank_globally()

        # 3. Remove stale species
        self.remove_stale_species()

        # 4. Rank globally
        self.rank_globally()

        # 5. Remove weak species
        self.remove_weak_species()



    def cull(self, cull_to_one=False):
        """
            Cull
            ----
        """

        for species in self.species:
            number_to_survive = int(np.ceil(len(species) / 2.0)) if not cull_to_one else 1
            survived_organisms = [organism for organism in species if organism.intra_species_rank < number_to_survive]
            species.organisms = survived_organisms



    def rank_globally(self):

        # Generate list of all organisms in pool
        global_organisms = []
        for species in self.species:
            global_organisms += species.organisms

        # Get unsorted ranks
        dtype = [('id', int), ('fitness', float)]                               # Initialize items needed for numpy sorting

        organism_id_mapping = { organism.ID : organism for organism in global_organisms }
        unsorted_rankings = [ (organism.ID, organism.fitness) for organism in global_organisms ]              # Initialize items needed for numpy sorting

        species_fitness = np.array(unsorted_rankings, dtype=dtype)              # Cast unsorted into np array for sorting
        sorted_rankings = np.sort(species_fitness, order='fitness')[::-1]             # Sort species by fitness


        for rank, (organism_id, fitness) in enumerate(sorted_rankings):   # Rank the sorted species
            organism_id_mapping[organism_id].global_rank = rank


    def remove_stale_species(self):
        survived_species = []
        for species in self.species:

            for organism in species:
                if organism.intra_species_rank == 0:
                    top_organism = organism
                    break

            if top_organism.fitness > species.top_fitness:
                species.top_fitness = top_organism.fitness
                species.stale_index = 0
            else:
                species.stale_index += 1

            if (species.stale_index < SPECIES_STALE_INDEX_THRESHOLD) or (species.top_fitness >= self.max_fitness):
                survived_species.append(species)

        del self.species
        self.species = survived_species




    def remove_weak_species(self):
        survived_species = []

        total_average_fitness = self.total_average_fitness()

        for species in self.species:
            breed = int(np.floor(species.average_fitness / total_average_fitness * POPULATION))
            print("BREED: {}".format(breed))
            if breed >= WEAK_BREED_THRESHOLD:
                survived_species.append(species)

        self.species = survived_species


    def total_average_fitness(self):
        total = 0.0
        for species in self.species:
            species.generate_average_fitness()
            total += species.average_fitness
        return total


    def selection(self):

        self.__prime_selection()

        total_average_fitness = self.total_average_fitness()
        self.progeny = []

        for species in self.species:
            breeds = int(np.floor(species.average_fitness / total_average_fitness * POPULATION) - 1.0)
            print("\tSpecies {} -- Breeds: {}".format(species.ID, breeds))
            for breed in range(breeds):
                self.progeny.append(species.mate())
            print("\n")
        # cull
        self.cull(True)



    def replicate(self):
        print("len progeny: {}\t----\tlen species: {}".format(len(self.progeny), len(self.species)) )
        while len(self.progeny) + len(self.species) < POPULATION:
            random_species_index = np.random.randint(len(self.species))
            random_species = self.species[random_species_index]
            self.progeny.append(random_species.mate())

        for new_organism in self.progeny:
            self.add_to_species(new_organism)


        self.generation += 1


    def add_to_species(self, new_organism):
        for species in self.species:
            if species.is_compatible(new_organism):
                species.organisms.append(new_organism)
                return

        new_species = Species(new_species=True, initial_organism=new_organism)
        self.species.append(new_species)
