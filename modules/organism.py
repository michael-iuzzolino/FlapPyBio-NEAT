from modules.genome import Genome
from modules.neuron import Neuron
from modules.config import *

from sklearn import preprocessing
import numpy as np
np.random.seed()


class Organism(object):
    """
        The organism contains the genome and is analagous to the neural network.
        The key data it holds are:
            1. Genome containing the genes (the connection network of the neural network)
            2. List of neurons within the neural network
            3. LEARN: FlapPyBird interfaces here and feed information into the organism that is
                    then fed forward through the graph to generate an output
            4. DECISION: Output decision (flap or not flap) sent to FlapPyBird here
    """
    ID = id(0)

    def __init__(self, genome=None, organism_id=None):
        if not organism_id:
            organism_id = Organism.ID
            Organism.ID += id(1)
        self.ID = organism_id

        if not genome:
            genome = Genome()
        self.genome = genome

        self.intra_species_rank = None
        self.fitness = 0.0
        self.normalized_fitness = 0.0
        self.number_progeny = None
        



    def learn(self, information):

        information = np.asarray(information).reshape(1, -1)                    # Normalize input
        information = preprocessing.normalize(information, norm='l2')

        self.genome.activate(information)                                                  # Feed forward to generate output


    def decision(self):
        raw_output = self.genome.neurons[INPUTS].output                         # Obtain output from output layer
        output = 1 if raw_output >= 0.5 else 0

        return output


    def mate(self, other):
        parent_1_genome = self.genome.copy()
        parent_2_genome = other.genome.copy()

        new_genome = parent_1_genome.crossover(parent_2_genome)

        # Mutations
        new_genome.mutate()

        return Organism(genome=new_genome)


    def mitosis(self):
        new_genome = self.genome.copy()
        new_genome.mutate()
        return Organism(genome=new_genome)


    def compare_genomes(self, other):
        number_excess_genes = 0
        number_disjoint_genes = 0
        W = 0
        N = 0

        organism_gene_list = [gene.innovation_number for gene in self.genome.genes]
        species_gene_list = [gene.innovation_number for gene in other.genes]

        organism_min, organism_max = min(organism_gene_list), max(organism_gene_list)
        species_min, species_max = min(species_gene_list), max(species_gene_list)

        lower_bound = max(organism_min, species_min)                            # lower bound of genome with largest innovation number
        upper_bound = min(organism_max, species_max)                            # upper bound of genome with smallest innovation number

        excess_gene_test_list = organism_gene_list + species_gene_list          # Calculate excess genes - number of genes outside of smallest domain
        for gene in species_gene_list:
            if gene < lower_bound or gene > upper_bound:
                number_excess_genes += 1

        for gene in range(lower_bound, upper_bound+1):                          # Calculate disjoint genes - number of genes in the gaps
            if (gene in organism_gene_list) and (gene not in species_gene_list):
                number_disjoint_genes += 1
            if (gene in species_gene_list) and (gene not in organism_gene_list):
                number_disjoint_genes += 1

        W = np.absolute(self.genome.ave_gene_weight - other.ave_gene_weight)                 # Calculate difference of average gene weights of genomes
        N = max(len(organism_gene_list), len(species_gene_list))                # Calculate max length genome
        N = 1 if N <= 20 else N
        return number_excess_genes, number_disjoint_genes, W, N
