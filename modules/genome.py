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
    innovation_dictionary = {}

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

        self.__init_innovation_dict()

        self.__generate_ave_gene_weight()




    def __repr__(self):
        return "{}".format(self.__innovation_numbers())


    def __init_innovation_dict(self):
        Genome.innovation_dictionary = { gene.innovation_number : (gene.input_neuron_id, gene.output_neuron_id)
                                            for gene in self.genes }


    def __neuron_ids(self):
        return [neuron_id for neuron_id in self.neurons.keys()]

    def __next_neuron_id(self):
        neuron_ids = self.__neuron_ids()
        new_neuron_id = max(neuron_ids)+1
        return new_neuron_id

    def __innovation_numbers(self):
        return [gene.innovation_number for gene in self.genes]

    def __generate_innovation_number(self, new_input_id, new_output_id):

        for innovation_number, (input_id, output_id) in Genome.innovation_dictionary.items():
            if new_input_id == input_id and new_output_id == output_id:
                return innovation_number

        innovation_numbers = [key for key in Genome.innovation_dictionary.keys()]
        new_innovation_number = max(innovation_numbers)+1
        Genome.innovation_dictionary[new_innovation_number] = (new_input_id, new_output_id)

        return new_innovation_number


    def __generate_connection_matrix(self, progeny_neurons, progeny_genes):
        new_connection_matrix = np.zeros((len(progeny_neurons), len(progeny_neurons)))
        for gene in progeny_genes:
            input_index = gene.input_neuron_id
            output_index = gene.output_neuron_id
            new_connection_matrix[input_index][output_index] = 1

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
        """
            Crossover:
            Common genes: 50% chance of inheriting from one parent or the other
            Disjoint / excess genes: 50% chance of inheriting from parent

            1) Create new connection genome from parents
            2) From new connection genome, create new neurons dictionary
            3) Create new connection matrix from connection genome

            4) Create new genome
            5) return it to calling function
        """

        # 1. Create new connection genome from parents
        parent_1_genes = self.genes
        parent_2_genes = other.genes

        progeny_genes = []
        for parent_1_gene in parent_1_genes:
            gene_1_innovation = parent_1_gene.innovation_number

            for parent_2_gene in parent_2_genes:
                gene_2_innovation = parent_2_gene.innovation_number

                if gene_1_innovation == gene_2_innovation:
                    if np.random.randint(2) == 0 and parent_2_gene.enabled:
                        new_gene = parent_2_gene.copy()
                    else:
                        break

            new_gene = parent_1_gene.copy()

            progeny_genes.append(new_gene)





        # 2. Create new neuron dictionary from new connection genes
        parent_1_neurons = set([neuron_ID for neuron_ID in self.neurons.keys()])
        parent_2_neurons = set([neuron_ID for neuron_ID in other.neurons.keys()])
        neuron_ids = list(parent_1_neurons | parent_2_neurons)
        progeny_neurons = { neuron_id : Neuron(neuron_id=neuron_id) for neuron_id in neuron_ids}

        # 3. Create new connection matrix from new connection genes
        progeny_connection_matrix = np.zeros((len(progeny_neurons), len(progeny_neurons)))
        for gene in progeny_genes:
            input_id = gene.input_neuron_id
            output_id = gene.output_neuron_id
            progeny_connection_matrix[input_id, output_id] = 1

        # 4. Create new genome
        new_genome = Genome(progeny_neurons, progeny_genes, progeny_connection_matrix)



        return new_genome



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
            B. Enable / Disable links
            C. Mutate connections (GENOME list is updated)  [TOPOLOGY Change]
                i. Add connection between existing neurons
                ii. Remove connection between existing neurons (i.e., set enable of a random gene as enable = False)
            D. Mutate neurons (NEURONS dict is updated; GENOME list is updated) [TOPOLOGY Change]
                i. Add neuron to NEURONS dictionary and ...
                        -- Disable previous link in GENOME and add two new links to GENOME
                ii. Remove neuron from NEURONS dictionary and ...
                        -- WE WON'T IMPLEMENT THIS RIGHT NOW since we are building up complexity rather than reducing it.
        """

        connection_weight_mutation_chance = self.__mutation_chance()
        mut_rate = CONNECTION_WEIGHT_MUTATION_RATE*0.95 if np.random.randint(2) == 0 else CONNECTION_WEIGHT_MUTATION_RATE*1.05
        if connection_weight_mutation_chance <= mut_rate:
            self.__mutate_weights()                                                 # Weight mutations

        enable_mutation_chance = self.__mutation_chance()
        mut_rate = ENABLE_MUTATION_RATE*0.95 if np.random.randint(2) == 0 else ENABLE_MUTATION_RATE*1.05
        if enable_mutation_chance <= mut_rate:
            self.__mutate_enable(enable=True)

        disable_mutation_chance = self.__mutation_chance()
        mut_rate = DISABLE_MUTATION_RATE*0.95 if np.random.randint(2) == 0 else DISABLE_MUTATION_RATE*1.05
        if disable_mutation_chance <= mut_rate:
            self.__mutate_enable(enable=False)

        connection_mutation_chance = self.__mutation_chance()
        mut_rate = CONNECTION_MUTATION_RATE*0.95 if np.random.randint(2) == 0 else CONNECTION_MUTATION_RATE*1.05
        if connection_mutation_chance <= mut_rate:
            self.__mutate_connections()                                             # Connection mutations

        neuron_mutation_chance = self.__mutation_chance()
        mut_rate = NEURON_MUTATION_RATE*0.95 if np.random.randint(2) == 0 else NEURON_MUTATION_RATE*1.05
        if neuron_mutation_chance <= mut_rate:
            self.__mutate_nodes()                                                   # Node mutations


    def __mutate_enable(self, enable):
        candidate_genes = []
        for gene in self.genes:
            if gene.enabled != enable:
                candidate_genes.append(gene)

        if not candidate_genes:
            return

        random_candidate_index = np.random.randint(len(candidate_genes))
        random_candidate_gene = candidate_genes[random_candidate_index]
        random_candidate_gene.enabled = not gene.enabled


    def __mutate_weights(self):

        # Check every gene for chance of weight mutation
        for gene in self.genes:

            weight_mutation_chance = self.__mutation_chance()

            # Check for uniform mutation
            step_size = STEP_SIZE*.95 if np.random.randint(2) == 0 else STEP_SIZE*1.05
            if weight_mutation_chance <= WEIGHT_MUTATION_RATE:
                gene.weight += (np.random.uniform() * step_size * 2.0 - step_size) * WEIGHT_MUT_FACTOR
            else:
                gene.weight = np.random.uniform() * 4.0 - 2.0




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
                    gene.enabled = True
                    self.connection_matrix[gene_input_id][gene_output_id] = 1
                    return


        # Generate innovation number!
        innovation_number = self.__generate_innovation_number(input_id, output_id)
        new_gene = Gene(innovation_number=innovation_number,
                        input_neuron_id=input_id,
                        output_neuron_id=output_id,
                        weight=None)
        self.genes.append(new_gene)

        # Update innovation list
        Genome.innovation_dictionary[innovation_number] = (input_id, output_id)

        # Update connection_matrix
        self.connection_matrix[input_id][output_id] = 1




    def __mutate_nodes(self):


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

        # Generate innovation number!
        innovation_number_1 = self.__generate_innovation_number(input_id, new_neuron_id)

        new_gene_1 = Gene(innovation_number=innovation_number_1,
                        input_neuron_id=input_id,
                        output_neuron_id=new_neuron_id,
                        weight=1.0)
        self.genes.append(new_gene_1)

        # Update connection matrix
        self.connection_matrix[input_id][new_neuron_id] = 1


        # Gene 2
        # Generate innovation number!
        innovation_number_2 = self.__generate_innovation_number(new_neuron_id, output_id)

        new_gene_2 = Gene(innovation_number=innovation_number_2,
                          input_neuron_id=new_neuron_id,
                          output_neuron_id=output_id,
                          weight=previous_weight)
        self.genes.append(new_gene_2)
        # Update connection matrix
        self.connection_matrix[new_neuron_id][output_id] = 1
