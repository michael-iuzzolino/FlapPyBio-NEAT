from modules.config import *
from modules.species import Species
import numpy as np

from FlapPyBird.flappy import FlappyBirdApp

class Pool(object):

    def __init__(self):

        # Create the initial species
        initial_species = Species()

        # Set initial species into object list
        self.species = [initial_species]

        # Initialize pool genration to 0
        self.generation = 0

        # Initialize a dictionary to track the top organism
        self.max_fitness = {"organism" : {"object" : None, "fitness" : None}}


    def __repr__(self):
        return "{}".format(self.generation)


    def __iter__(self):
        for species in self.species:
            yield species


    def fitness(self):
        """
            Fitness
            -------
            Each species in the pool is iterated over.
            They are passed into the FlappyBird App,
                and the game is played for all organisms in that species simultaneously.

            Flappy generates "crash_info", from which we obtain the
                1. organism,
                2. its expended energy during play, and
                3. its distance traveled during play

            Using the organism's energy and distance, a fitness measure is generated and assigned to the organism

        """

        # Iterate through the species in the list
        for species in self.species:

            # ================ PLAY FLAPPYBIRD ====================
            flappy = FlappyBirdApp(species, self.generation)
            flappy.play()
            # =====================================================

            for bird_results in flappy.crash_info:

                # ====== Results per organism =======
                organism = bird_results['network']
                energy = bird_results['energy']
                distance = bird_results['distance']
                # ===================================

                # ======== INTERFACE WITH VIS ========

                print(organism)
                # ===================================

                # Determine the organism's fitness
                # ============ FITNESS FUNCTION ================
                fitness = distance - energy * 1.5
                # ==============================================

                # Assign the fitness to the organism
                organism.fitness = fitness if fitness > 0 else -1.0


                # =============== Pool's Max Fitness ===============
                # First, check if max fitness dict is empty.
                #   If so, assign the first organism and its fitness
                pool_max_organism = self.max_fitness['organism']
                if not pool_max_organism['fitness']:
                    pool_max_organism['object'] = organism
                    pool_max_organism['fitness'] = organism.fitness

                # Check if current organism has higher fitness than pool's all-time max
                elif organism.fitness > pool_max_organism['fitness']:
                    pool_max_organism['object'] = organism
                    pool_max_organism['fitness'] = organism.fitness
                # ==================================================

            # Set the species intra rank and reorder the species organism list from top rank to lowest rank (0 to x, x being the lowest)
            species.set_intra_species_rank()



    def selection(self):

        for species in self.species:
            # Determine number of organisms that will survive in the given species
            number_to_survive = int(np.ceil(len(species) * FRACTION_SELECTED))

            # Initialize species' parent list
            species.parents = []

            # Generate a list of the oranisms that survive
            for organism in species:
                if organism.intra_species_rank < number_to_survive:
                    species.parents.append(organism)


            # Generate average fitness for species
            species.generate_average_fitness()



    def replicate(self):

        self.new_species = []

        for species in self.species:

            # Initialize species' child list with top parent (save the best organism)
            species.progeny = [species.parents[0]]

            remaining_progeny = POPULATION - len(species.progeny)
            while remaining_progeny > 0:
                progeny = species.mate()
                self.__add_to_species(progeny)
                remaining_progeny -= 1

            print("Number of progeny: {}".format(len(species.progeny)))

        self.__increment_generation()





    def __increment_generation(self):
        self.generation += 1
        for species in self.species:
            species.organisms = species.progeny


        for new_species in self.new_species:
            self.species.append(new_species)



    def __cull_species(self):

        # Remove the stale species from the pool
        survived_species = []
        for species in self.species:

            # Determine CURRENT species' top organism
            for organism in species:
                if organism.intra_species_rank == 0:
                    top_organism = organism
                    break

            # Compare CURRENT species top organism with the species' global top fitness
            # Essentially, if a species is demonstrating improvement, keep it "fresh"
            if top_organism.fitness > species.top_fitness:
                species.top_fitness = top_organism.fitness
                species.stale_index = 0

            # Otherwise, if it decreases in performance, increase its stale index
            else:
                species.stale_index += 1

            # If the stale index is below threshold, save the species and pass to next gen
            pool_max_organism_fitness = self.max_fitness['organism']['fitness']
            if (species.stale_index < SPECIES_STALE_INDEX_THRESHOLD) or (species.top_fitness >= pool_max_organism_fitness):
                survived_species.append(species)

        # Delete the current list of species and update it with the survived species
        self.species = survived_species








    def __rank_globally(self):

        # Generate list of all organisms in pool
        global_organisms = []
        for species in self.species:
            for organism in species:
                global_organisms.append(organism)


        # Get unsorted ranks
        dtype = [('id', int), ('fitness', float)]                               # Initialize items needed for numpy sorting

        organism_id_mapping = { organism.ID : organism for organism in global_organisms }
        unsorted_rankings = [ (organism.ID, organism.fitness) for organism in global_organisms ]              # Initialize items needed for numpy sorting

        species_fitness = np.array(unsorted_rankings, dtype=dtype)              # Cast unsorted into np array for sorting
        sorted_rankings = np.sort(species_fitness, order='fitness')[::-1]             # Sort species by fitness

        for rank, (organism_id, fitness) in enumerate(sorted_rankings):   # Rank the sorted species
            organism_id_mapping[organism_id].global_rank = rank
            if not rank:
                print(organism_id_mapping[organism_id])




    def __total_average_fitness(self):
        total_average = 0.0
        for species in self.species:
            total_average += species.average_fitness

        return total_average



    def __add_to_species(self, new_organism):
        for species in self.species:
            if species.is_compatible(new_organism):
                species.progeny.append(new_organism)
                return

        # Speciation! New organism was not matched to any extant species.
        new_species = Species(new_species=True, initial_organism=new_organism)
        self.new_species.append(new_species)
