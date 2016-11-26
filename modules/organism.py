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
    ID = 0

    def __init__(self, genome=None, organism_id=None):
        if not organism_id:
            organism_id = Organism.ID
            Organism.ID += 1
        self.ID = organism_id

        # Genome
        if not genome:
            genome = Genome()

        self.genome = genome

        # Additional attributes
        intra_species_rank = None


    def learn(self, information):
        # Normalize input
        information = np.asarray(information).reshape(1, -1)
        information = preprocessing.normalize(information, norm='l2')

        # Prime input layer
        self.genome.prime_inputs(information)

        # Feed forward to generate output
        self.genome.activate()


    def decision(self):
        # Obtain output from output layer
        raw_output = self.genome.neurons[INPUTS].output
        output = 1 if raw_output >= 0.5 else 0

        return output


    def mate(self, other):

        # Find genes in common
        parent_1_genome = self.genome.copy()
        parent_2_genome = other.genome.copy()
        #
        # print("Original genome ID: {}".format(id(self.genome)))
        # print("Original: {}".format(self.genome))
        # print("Copy genome ID: {}".format(id(parent_1_genome)))
        # print("Copy: {}".format(parent_1_genome))
        # print("\n")

        new_genome = parent_1_genome.crossover(parent_2_genome)

        # Mutations
        new_genome.mutate()


        progeny = Organism(genome=new_genome)
        return progeny


    def compare_genomes(self, other):
        number_excess_genes = 0
        number_disjoint_genes = 0
        W = 0
        N = 0

        organism_gene_list = [gene.innovation_number for gene in self.genome.genes]
        species_gene_list = [gene.innovation_number for gene in other.genes]

        organism_min, organism_max = min(organism_gene_list), max(organism_gene_list)
        species_min, species_max = min(species_gene_list), max(species_gene_list)

        lower_bound = max(organism_min, species_min)    # lower bound of genome with largest innovation number
        upper_bound = min(organism_max, species_max)    # upper bound of genome with smallest innovation number


        # Calculate excess genes - number of genes outside of smallest domain
        for gene in organism_gene_list:
            if gene < lower_bound or gene > upper_bound:
                number_excess_genes += 1

        for gene in species_gene_list:
            if gene < lower_bound or gene > upper_bound:
                number_excess_genes += 1


        # Calculate disjoint genes - number of genes in the gaps
        for gene in range(lower_bound, upper_bound+1):
            if (gene in organism_gene_list) and (gene not in species_gene_list):
                number_disjoint_genes += 1
            if (gene in species_gene_list) and (gene not in organism_gene_list):
                number_disjoint_genes += 1

        # Calculate difference of average gene weights of genomes
        W = self.genome.ave_gene_weight - other.ave_gene_weight

        # Calculate max length genome
        N = max(len(organism_gene_list), len(species_gene_list))

        return number_excess_genes, number_disjoint_genes, W, N


    # def __repr__(self):
    #     # return "{}".format(self.genome)
    #     pass
