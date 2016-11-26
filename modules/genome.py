from modules.gene import Gene
from modules.neuron import Neuron
from modules.config import *

import numpy as np
import copy


"""
    Need to add unique neurons during mating!
"""

class Genome(object):
    """
        The genome is a linear sequence of genes, wherein the gene indicates a single connection in the network.
        The key data of the genone is:
            1. Dictionary of genes, where
                KEY = innovation number of the gene
                VALUE = the GENE object containing the connection information

    """

    def __init__(self, neurons={}, genes=[]):

        # Create list of genes
        if not genes:
            # Create dictionary of neurons: KEY = Neuron ID; VALUE = neuron
            neurons = {neuron_id : Neuron(neuron_id) for neuron_id in range(INPUTS+OUTPUTS)}

            for neuron_id, neuron in neurons.items():
                if neuron_id < INPUTS:
                    neuron.type = 'input'
                else:
                    neuron.type = 'output'


            genes = [Gene(innovation_number=index,
                          input_neuron_id=index,
                          output_neuron_id=INPUTS) for index in range(INPUTS)]

        self.neurons = neurons
        self.genes = genes


        # Useful for mutations later on
        self.neuron_ids = [neuron_id for neuron_id in self.neurons.keys()]
        self.innovation_numbers = None
        self._generate_ave_gene_weight()

    def _generate_ave_gene_weight(self):
        self.ave_gene_weight = 0.0
        for gene in self.genes:
            self.ave_gene_weight += (gene.weight / len(self.genes))


    def prime_inputs(self, information):

        for neuron_id, neuron in self.neurons.items():
            if neuron_id < INPUTS:
                neuron.output = information[0][neuron_id]
            else:
                return





    def activate(self):

        # Hidden Layers

        for neuron_id, neuron in self.neurons.items():
            if neuron_id < INPUTS + OUTPUTS:
                continue

            for gene in self.genes:
                if neuron_id != gene.output_neuron_id or not gene.enabled:
                    continue
                input_neuron = self.neurons[gene.input_neuron_id]
                neuron.input += gene.weight * input_neuron.output

            # neuron.output = 1.0 / (1.0 + np.exp(-1.0 * neuron.input))
            neuron.output = 2.0 / (1.0 + np.exp(-4.9 * neuron.input)) - 1.0
            
            # Reset neuron.input to 0?
            neuron.input = 0.0

        # Output Layer
        output_neuron_id = INPUTS                       # Output neuron is at INPUT index
        output_neuron = self.neurons[output_neuron_id]
        for gene in self.genes:
            if output_neuron_id != gene.output_neuron_id or not gene.enabled:
                continue
            input_neuron = self.neurons[gene.input_neuron_id]
            output_neuron.input += gene.weight * input_neuron.output

        output_neuron.output = 1.0 / (1.0 + np.exp(-1.0 * output_neuron.input))

        output_neuron.input = 0.0



    def copy(self):
        new_neurons = copy.deepcopy(self.neurons)
        new_genes = copy.deepcopy(self.genes)

        new_genome = Genome(new_neurons, new_genes)
        return new_genome


    def crossover(self, other):
        # Check for common and parent-unique genes
        parent_1_genes_innovation_list = set([gene.innovation_number for gene in self.genes])
        parent_2_genes_innovation_list = set([gene.innovation_number for gene in other.genes])
        common_genes = parent_1_genes_innovation_list & parent_2_genes_innovation_list
        parent_1_unique_genes_innovation_list = parent_1_genes_innovation_list - parent_2_genes_innovation_list
        parent_2_unique_genes_innovation_list = parent_2_genes_innovation_list - parent_1_genes_innovation_list

        # print("Parent 1 Genes: {}".format(parent_1_genes_innovation_list))
        # print("Parent 2 Genes: {}".format(parent_2_genes_innovation_list))
        # print("Common Genes: {}".format(common_genes))
        # print("Parent 1 Unique Genes: {}".format(parent_1_unique_genes_innovation_list))
        # print("Parent 2 Unique Genes: {}".format(parent_2_unique_genes_innovation_list))
        #
        # print("\n")

        parent_1_genes = self.genes
        parent_2_genes = other.genes
        progeny_neurons = {}
        progeny_genes = []


        # Assign genes in common
        for gene_1 in parent_1_genes:
            gene_1_innovation_number = gene_1.innovation_number
            for gene_2 in parent_2_genes:
                gene_2_innovation_number = gene_2.innovation_number
                if gene_1_innovation_number == gene_2_innovation_number:

                    # decide which parent contributes to child genes
                    parents = [[self, gene_1], [other, gene_2]]
                    random_parent_index = np.random.randint(2)
                    parent = parents[random_parent_index][0]
                    parent_gene = parents[random_parent_index][1]

                    # Define input and output neuron id's
                    input_neuron_id = parent_gene.input_neuron_id
                    output_neuron_id = parent_gene.output_neuron_id

                    # Define input and output neurons associated with parent's gene
                    input_neuron = parent.neurons[input_neuron_id]
                    output_neuron = parent.neurons[output_neuron_id]


                    # Update progeny genes list with parent gene
                    progeny_genes.append(parent_gene)

                    # Update progeny_neuron dictionary
                    progeny_neurons[input_neuron_id] = input_neuron
                    progeny_neurons[output_neuron_id] = output_neuron

                    break

        # Assign unique genes (disjoint and excess)
        parent_1_unique_genes = [gene for gene in self.genes if gene.innovation_number in parent_1_unique_genes_innovation_list]
        parent_2_unique_genes = [gene for gene in self.genes if gene.innovation_number in parent_2_unique_genes_innovation_list]


        if parent_1_unique_genes:
            self._assign_unique_genes(parent_1_unique_genes, progeny_neurons, progeny_genes)

        if parent_2_unique_genes:
            self._assign_unique_genes(parent_2_unique_genes, progeny_neurons, progeny_genes)

        progeny_genome = Genome(progeny_neurons, progeny_genes)

        return progeny_genome


    def _assign_unique_genes(self, parents_unique_genes, progeny_neurons, progeny_genes):

        for unique_gene in parents_unique_genes:
            # print("Unique gene! {}".format(unique_gene.innovation_number))
            for gene in parents_unique_genes:
                progeny_genes.append(gene)

        # print("New progeny genes: {}".format(progeny_genes))
        """ NEED TO ADD NEURON ?? """




    def mutate(self):
        """
            There are a few types of mutations.
            A. Mutate weights of synapses
            B. Mutate connections (GENOME list is updated)  [TOPOLOGY Change]
                i. Add connection between existing neurons
                ii. Remove connection between existing neurons (i.e., set enable of a random gene as enable = False)
            C. Mutate neurons (NEURONS dict is updated; GENOME list is updated) [TOPOLOGY Change]
                i. Add neuron to NEURONS dictionary and ...
                        -- Disable previous link in GENOME and add two new links to GENOME
                ii. Remove neuron from NEURONS dictionary and ...
                        -- WE WON'T IMPLEMENT THIS RIGHT NOW since we are building up complexity rather than reducing it.
        """

        # A. Weight mutations
        for gene in self.genes:
            weight_mutation_chance = np.random.uniform()
            if weight_mutation_chance >= WEIGHT_MUTATION_RATE:
                continue
            weight_change = np.random.randn()
            gene.weight += weight_change


        # B. Connection mutations
        connection_mutation_chance = np.random.uniform()
        mutations = [self.add_connection, self.remove_connection]
        if connection_mutation_chance <= CONNECTION_MUTATION_RATE:
            mutations[np.random.randint(2)]()


        # C. Neuron mutations
        neuron_mutation_chance = np.random.uniform()
        if neuron_mutation_chance <= NEURON_MUTATION_RATE:
            self.add_neuron()



    def add_neuron(self):
        new_neuron_id = max(self.neuron_ids)+1

        neuron_added = False
        while not neuron_added:

            input_neuron_id, output_neuron_id = self.generate_io_ids()

            if self.connection_issues(input_neuron_id, output_neuron_id):
                continue

            # create new neuron
            new_neuron = Neuron(neuron_id=None)
            new_neuron.type = 'hidden'
            """ FIGURE OUT HOW TO DETERMINE ITS LAYER NUMBER! """
            new_neuron.layer_level = 0
            self.neurons[new_neuron_id] = new_neuron

            # remove previous connection gene
            connection_found = False
            for gene in self.genes:
                gene_input_id = gene.input_neuron_id
                gene_output_id = gene.output_neuron_id

                # Disable old gene
                if gene_input_id == input_neuron_id and gene_output_id == output_neuron_id:
                    gene.enabled = False

            if not connection_found:
                break


            # create 2 new connection genes
            new_gene_1 = Gene(innovation_number=self.next_innovation_number(), input_neuron_id=input_neuron_id, output_neuron_id=new_neuron_id, weight=1.0)
            new_gene_2 = Gene(innovation_number=self.next_innovation_number(), input_neuron_id=new_neuron_id, output_neuron_id=output_neuron_id)
            self.genes.append(new_gene_1)
            self.genes.append(new_gene_2)
            neuron_added = True


    def add_connection(self):
        """
            Adds a connection via
            1. Re-enabling a disabled gene or
            2. Adding an entirely new connection
            *** This only adds connections between INPUT and HIDDENS or HIDDENS and HIDDENS ***
                1. Determine the new gene's input neuron (select from input or hidden neurons)
                2. Determine the new gene's output neuron (select from hidden neurons or output neurons)
                ** Note: Make sure that the input neuron is "behind" the output neuron in the network...
                    Create a new attribute for neurons labeling their hidden layer level, and enforce
                    the rule that input neuron layer level must be GREATER than (not equal to or greater than)
                    the output_layer neuron.
        """

        connection_added = False
        while not connection_added:
            input_neuron_id, output_neuron_id = self.generate_io_ids()
            if self.connection_issues(input_neuron_id, output_neuron_id):
                continue


            # Checks to see if connetion already exists
            connection_exists_and_enabled = False
            for gene in self.genes:
                gene_input_id = gene.input_neuron_id
                gene_output_id = gene.output_neuron_id
                if gene_input_id == input_neuron_id and gene_output_id == output_neuron_id:
                    # check to see if it is already enabled:
                    if gene.enabled:
                        connection_exists_and_enabled = True
                    # If it's not enabled, enable it
                    elif not gene.enabled:
                        gene.enabled = True
                        connection_added = True
                        break
            if connection_exists_and_enabled:
                break


            # Else, create new gene
            new_gene = Gene(innovation_number=self.next_innovation_number(), input_neuron_id=input_neuron_id, output_neuron_id=output_neuron_id)
            self.genes.append(new_gene)
            connection_added = True

    def next_innovation_number(self):
        self.innovation_numbers = [gene.innovation_number for gene in self.genes]
        new_innovation_number = max(self.innovation_numbers)+1
        return new_innovation_number

    def remove_connection(self):
        """
            Removes a connection: i.e., enable = False for one of the genes, then returns
        """
        disabled_gene = False

        while not disabled_gene:
            for gene in self.genes:
                disable_connection_chance = np.random.uniform()
                if disable_connection_chance <= (1 / len(self.genes)):
                    gene.enable = False
                    disabled_gene = True
                    break


    def generate_io_ids(self):
        # Determine where neuron will be placed
        input_neuron_id = self.neuron_ids[np.random.randint(len(self.neuron_ids))]
        # print("Random input id: {}".format(input_neuron_id))


        # Determine output neuron connection
        same_id = True
        while same_id:
            output_neuron_id = self.neuron_ids[np.random.randint(len(self.neuron_ids))]
            if input_neuron_id != output_neuron_id:
                same_id = False

        # print("Random output id: {}".format(output_neuron_id))

        return input_neuron_id, output_neuron_id

    def connection_issues(self, input_neuron_id, output_neuron_id):
        # Ensure proper order of input and output: swap if necessary or continue if bad selection
        if self.neurons[input_neuron_id].type == 'input':
            if self.neurons[output_neuron_id].type == 'input':
                return True

        # Ensure input neuron isn't the network's output neuron; if so, swap the input and output
        if self.neurons[input_neuron_id].type == 'output':
            temp = input_neuron_id
            input_neuron_id = output_neuron_id
            output_neuron_id = input_neuron_id

        # Ensure hidden layer connections have correct order
        if self.neurons[input_neuron_id].type == 'hidden':
            if self.neurons[input_neuron_id].layer_level > self.neurons[output_neuron_id].layer_level:
                temp = input_neuron_id
                input_neuron_id = output_neuron_id
                output_neuron_id = input_neuron_id
            elif self.neurons[input_neuron_id].layer_level == self.neurons[output_neuron_id].layer_level:
                return True

        return False


    # def __repr__(self):
    #     # return "{}".format(self.genes)
    #     pass
