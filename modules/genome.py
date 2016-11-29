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

    def __init__(self, neurons={}, genes=[], connection_matrix=[]):

        # Create list of genes
        if not genes:
            # Create dictionary of neurons: KEY = Neuron ID; VALUE = neuron
            neurons = {neuron_id : Neuron(neuron_id) for neuron_id in range(INPUTS+OUTPUTS)}

            for neuron_id, neuron in neurons.items():
                neuron.type = 'input' if neuron_id < INPUTS else 'output'

            genes = [Gene(innovation_number=index,
                          input_neuron_id=index,
                          output_neuron_id=INPUTS) for index in range(INPUTS)]

            # Create connection matrix
            connection_matrix = np.zeros((INPUTS+OUTPUTS, INPUTS+OUTPUTS))
            # Set all connections from inputs to the output as 1
            connection_matrix[:INPUTS, INPUTS:] = 1



        self.neurons = neurons
        self.genes = genes
        self.connection_matrix = connection_matrix



        self.__generate_ave_gene_weight()

    def __repr__(self):
        return "{}".format(self.__innovation_numbers())

    def __neuron_ids(self):
        return [neuron_id for neuron_id in self.neurons.keys()]

    def __next_neuron_id(self):
        neuron_ids = self.__neuron_ids()
        new_neuron_id = max(neuron_ids)+1
        return new_neuron_id

    def __innovation_numbers(self):
        return [gene.innovation_number for gene in self.genes]

    def __next_innovation_number(self):
        innovation_numbers = self.__innovation_numbers()
        new_innovation_number = max(innovation_numbers)+1
        return new_innovation_number

    def __generate_connection_matrix(self, progeny_neurons, progeny_genes):
        new_connection_matrix = np.zeros((len(progeny_neurons), len(progeny_neurons)))
        for gene in progeny_genes:
            input_index = gene.input_neuron_id
            output_index = gene.output_neuron_id
            print("input index: {}\toutput index: {}\n".format(input_index, output_index))
            new_connection_matrix[input_index][output_index] = 1
        print("\n")

        return new_connection_matrix



    def __generate_ave_gene_weight(self):
        """
            Generate Average Gene Weight Across Genome
        """
        self.ave_gene_weight = 0.0
        for gene in self.genes:
            self.ave_gene_weight += (gene.weight / len(self.genes))


    def activate(self, information):
        """
            Activate
        """
        # Input layer
        for neuron_id, neuron in self.neurons.items():
            if neuron_id >= INPUTS:
                break

            neuron.output = information[0][neuron_id]


        # Hidden Layers
        for neuron_id, neuron in self.neurons.items():
            if neuron_id < INPUTS + OUTPUTS:
                continue

            for gene in self.genes:
                if neuron_id != gene.output_neuron_id or not gene.enabled:
                    continue
                input_neuron = self.neurons[gene.input_neuron_id]
                neuron.input += gene.weight * input_neuron.output

            neuron.activate()


        # Output Layer
        output_neuron_id = INPUTS                                               # Output neuron is at INPUT index
        output_neuron = self.neurons[output_neuron_id]
        for gene in self.genes:
            if output_neuron_id != gene.output_neuron_id or not gene.enabled:
                continue
            input_neuron = self.neurons[gene.input_neuron_id]
            output_neuron.input += gene.weight * input_neuron.output

        output_neuron.activate()



    def copy(self):
        new_neurons = copy.deepcopy(self.neurons)
        new_genes = copy.deepcopy(self.genes)
        new_connection_matrix = copy.deepcopy(self.connection_matrix)

        new_genome = Genome(new_neurons, new_genes, new_connection_matrix)
        return new_genome


    def crossover(self, other):
        # Check for common and parent-unique genes
        parent_1_genes_innovation_list = set([gene.innovation_number for gene in self.genes])
        parent_2_genes_innovation_list = set([gene.innovation_number for gene in other.genes])
        common_genes = parent_1_genes_innovation_list & parent_2_genes_innovation_list
        parent_1_unique_genes_innovation_list = parent_1_genes_innovation_list - parent_2_genes_innovation_list
        parent_2_unique_genes_innovation_list = parent_2_genes_innovation_list - parent_1_genes_innovation_list


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
            self.__assign_unique_genes(parent_1_unique_genes, progeny_neurons, progeny_genes)

        if parent_2_unique_genes:
            self.__assign_unique_genes(parent_2_unique_genes, progeny_neurons, progeny_genes)

        print("\n\n\t\tPROGENY NEURONS: {}".format(progeny_neurons))
        print("\t\tPROGENY GENES: {}\n\n".format(progeny_genes))
        progeny_connection_matrix = self.__generate_connection_matrix(progeny_neurons, progeny_genes)

        progeny_genome = Genome(progeny_neurons, progeny_genes, progeny_connection_matrix)

        return progeny_genome


    def __assign_unique_genes(self, parents_unique_genes, progeny_neurons, progeny_genes):

        for unique_gene in parents_unique_genes:
            for gene in parents_unique_genes:
                progeny_genes.append(gene)


    def __mutation_chance(self):
        return np.random.uniform()


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



        connection_weight_mutation_chance = self.__mutation_chance()
        if connection_weight_mutation_chance > CONNECTION_WEIGHT_MUTATION_RATE:
            self.__mutate_weights()                                                 # Weight mutations

        connection_mutation_chance = self.__mutation_chance()
        if connection_mutation_chance <= CONNECTION_MUTATION_RATE:
            self.__mutate_connections()                                             # Connection mutations

        neuron_mutation_chance = self.__mutation_chance()
        if neuron_mutation_chance <= NEURON_MUTATION_RATE:
            self.__mutate_nodes()                                                   # Node mutations



    def __mutate_weights(self):

        # Check every gene for chance of weight mutation
        for gene in self.genes:

            weight_mutation_chance = self.__mutation_chance()
            uniform_mutation = False

            # Check for uniform mutation
            if weight_mutation_chance <= WEIGHT_MUTATION_RATE:
                weight_change = self.__mutation_chance()
                direction_change = -1.0 if np.random.randint(2) == 0 else +1.0
                gene.weight += direction_change * weight_change
                uniform_mutation = True

            # Check for completely new random weight mutation
            if not uniform_mutation:
                chance_new_weight = self.__mutation_chance()
                if chance_new_weight <= NEW_WEIGHT_MUTATION_RATE:
                    gene.weight = np.random.randn()



    def __mutate_connections(self):
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

        """
            Mutating a connection means
                1. Adding a new link between previously unlinked nodes (e.g., valid cells in connection_matrix = 0 can be set to 1)
        """
        print("\tMutation: Connection")
        print("\t--------------------")
        print("\n")

        valid_connections = []
        for row_index, row in enumerate(self.connection_matrix):

            # Skip row corresponding to output neuron - this can never be an input to a connection node (no back propagation)
            if row_index == INPUTS:
                continue

            for col_index, value in enumerate(row):
                if value == 1:
                    continue

                if (col_index >= INPUTS) and (row_index != col_index):
                    valid_connections.append((row_index, col_index))

        if not valid_connections:
            print("\t\tNo new connections to make.")
            return


        random_connection_index = np.random.randint(len(valid_connections))
        random_connection = valid_connections[random_connection_index]

        # Create new connection gene
        input_id = random_connection[0]
        output_id = random_connection[1]

        # First, check if connection node exists but was disabled; if so, re-enable
        for gene in self.genes:
            gene_input_id = gene.input_neuron_id
            gene_output_id = gene.output_neuron_id
            if input_id == gene_input_id and output_id == gene_output_id:
                if gene.enabled == False:
                    print("\t\tRe-enabling Connection")
                    gene.enabled = True
                    self.connection_matrix[gene_input_id][gene_output_id] = 1
                    return

        print("\t\tCreating new connection between nodes {} and {}".format(input_id, output_id))

        # Generate innovation number!
        innovation_number = self.__next_innovation_number()
        new_gene = Gene(innovation_number=innovation_number,
                        input_neuron_id=input_id,
                        output_neuron_id=output_id,
                        weight=None)
        self.genes.append(new_gene)

        # Update connection_matrix
        self.connection_matrix[input_id][output_id] = 1



    def __mutate_nodes(self):
        print("\tMutation: Node")
        print("\t--------------")
        print("\n")

        # Create new neuron
        new_neuron_id = self.__next_neuron_id()
        new_neuron = Neuron(neuron_id=new_neuron_id)
        self.neurons[new_neuron_id] = new_neuron

        # Update connection_matrix for new matrix
        new_connection_matrix = np.zeros((len(self.neurons), len(self.neurons)))
        for row_index, row in enumerate(self.connection_matrix):
            for col_index, value in enumerate(row):
                new_connection_matrix[row_index][col_index] = value

        self.connection_matrix = new_connection_matrix

        # Search connection matrix for value positions
        valid_connections = []
        for row_index, row in enumerate(self.connection_matrix):

            # Skip row corresponding to output neuron - this can never be an input to a connection node (no back propagation)
            if row_index == INPUTS:
                continue

            for col_index, value in enumerate(row):
                if value == 0:
                    # We are interested in values == 1, not == 0
                    continue

                if (col_index >= INPUTS) and (row_index != col_index):
                    valid_connections.append((row_index, col_index))



        random_connection_index = np.random.randint(len(valid_connections))
        random_connection = valid_connections[random_connection_index]

        # Set I/O ids
        input_id = random_connection[0]
        output_id = random_connection[1]



        # Deactivate old connection in connection genome
        for gene in self.genes:
            gene_input_id = gene.input_neuron_id
            gene_output_id = gene.output_neuron_id
            if input_id == gene_input_id and output_id == gene_output_id:
                previous_weight = gene.weight
                gene.enabled = False

        # Update connection_matrix to reflect disable
        self.connection_matrix[input_id][output_id] = 0




        # Create 2 new connection genes
        # Gene 1

        print("\t\tCreating new connection between nodes {} and {}".format(input_id, new_neuron_id))

        # Generate innovation number!
        innovation_number = self.__next_innovation_number()
        new_gene_1 = Gene(innovation_number=innovation_number,
                        input_neuron_id=input_id,
                        output_neuron_id=new_neuron_id,
                        weight=1.0)
        self.genes.append(new_gene_1)

        # Gene 2
        print("\t\tCreating new connection between nodes {} and {}".format(new_neuron_id, output_id))

        # Generate innovation number!
        innovation_number = self.__next_innovation_number()
        new_gene_2 = Gene(innovation_number=innovation_number,
                        input_neuron_id=new_neuron_id,
                        output_neuron_id=output_id,
                        weight=previous_weight)
        self.genes.append(new_gene_2)
